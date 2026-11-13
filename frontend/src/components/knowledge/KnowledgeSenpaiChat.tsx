'use client';

import { FormEvent, UIEvent, useCallback, useEffect, useRef, useState } from 'react';
import { useSenpaiHistory } from '@/hooks/useSenpaiHistory';
import { SenpaiChatView, isContinuationPaused } from './SenpaiChatView';
import type { ResendOptions } from './SenpaiChatTurn';
import { getIdToken } from '@/lib/auth-helpers';
import { createSenpaiChat, type SenpaiChatController, type SenpaiChatSnapshot } from '@/lib/knowledge-senpai-chat.mjs';
import { requestSenpaiSynthesis } from '@/lib/knowledge-senpai-synthesis.mjs';
import { runSenpaiResearch } from '@/lib/knowledge-senpai-research.mjs';
import { listFieldReports, type FieldReport } from '@/lib/knowledge-senpai-field-report.mjs';
import { queryKnowledgeSource } from '@/lib/knowledge-research.mjs';
import { attachMenuDismissal } from '@/lib/knowledge-senpai-menu.mjs';
import { nextAnnouncement } from '@/lib/knowledge-senpai-research-view.mjs';

const EMPTY_SNAPSHOT: SenpaiChatSnapshot = { turns: [], running: false };
// 「結果を残す」は SAM の SenpaiFieldReportsEnabled と合わせて有効化する（既定オフ）。
const FIELD_REPORTS_ENABLED = process.env.NEXT_PUBLIC_ENABLE_SENPAI_FIELD_REPORTS === 'true';
// 「工技先輩のまとめ」は SAM の SenpaiSynthesisEnabled と合わせて有効化する（既定オフ）。保存済みのまとめは常に表示する。
const SYNTHESIS_ENABLED = process.env.NEXT_PUBLIC_ENABLE_SENPAI_SYNTHESIS === 'true';
// 調査ジョブ（試作）は SAM の SenpaiResearchEnabled と合わせて有効化する（既定オフ）。オフなら従来の2レーン表示。
const RESEARCH_ENABLED = process.env.NEXT_PUBLIC_ENABLE_SENPAI_RESEARCH === 'true';
// D16（設計 rag-two-modes §11.13）: 先輩チャットをノウハウだけで答える。技術KB・法令KB・調査ジョブ・まとめは使わない。
const KNOWHOW_ONLY = process.env.NEXT_PUBLIC_SENPAI_KNOWHOW_ONLY === 'true';
const DEV_VIEW_STORAGE_KEY = 'senpai-research-developer-view';

function useController(
  setSnapshot: (snapshot: SenpaiChatSnapshot) => void,
  controllerRef: { current: SenpaiChatController | null },
  mountedRef: { current: boolean },
) {
  useEffect(() => {
    let mounted = true;
    mountedRef.current = true;
    const controller = createSenpaiChat({
      querySource: ({ mode, query, modelType, sessionId, senpaiConversationId, senpaiTurnId, signal }) => queryKnowledgeSource({
        baseUrl: process.env.NEXT_PUBLIC_RAG_API_URL || '',
        getToken: getIdToken,
        mode,
        query,
        ...(modelType ? { modelType } : {}),
        senpaiConversationId,
        senpaiTurnId,
        ...(sessionId ? { sessionId } : {}),
        ...(mode === 'normal' ? { includeKnowhow: true } : {}),
        ...(KNOWHOW_ONLY && mode === 'normal' ? { knowhowOnly: true } : {}),
        signal,
      }),
      ...(KNOWHOW_ONLY ? { modes: ['normal'] as const } : {}),
      ...(RESEARCH_ENABLED && !KNOWHOW_ONLY ? {
        researchSource: (request) => runSenpaiResearch({
          baseUrl: process.env.NEXT_PUBLIC_RAG_API_URL || '',
          getToken: getIdToken,
          ...request,
        }),
      } : {}),
      synthesisSource: ({ senpaiConversationId, senpaiTurnId, signal }) => requestSenpaiSynthesis({
        baseUrl: process.env.NEXT_PUBLIC_RAG_API_URL || '',
        getToken: getIdToken,
        senpaiConversationId,
        senpaiTurnId,
        signal,
      }),
      onChange: (nextSnapshot) => {
        if (mounted) setSnapshot(nextSnapshot);
      },
    });
    controllerRef.current = controller;
    setSnapshot(controller.getSnapshot());
    return () => {
      mounted = false;
      mountedRef.current = false;
      if (controllerRef.current === controller) controllerRef.current = null;
      controller.dispose();
    };
  }, [controllerRef, mountedRef, setSnapshot]);
}

/** Reports the caller already sent for the open conversation, keyed by senpaiTurnId. */
const NO_REPORTS: Readonly<Record<string, FieldReport>> = Object.freeze({});

function useFieldReports(conversationId: string | undefined, running: boolean) {
  // 送信済みの印は相談ごとに持つ。相談が変わったときだけ捨て、質問の実行中・再取得中は保つ。
  const [store, setStore] = useState<{ conversationId?: string; reports: Readonly<Record<string, FieldReport>> }>({ reports: NO_REPORTS });
  const reports = store.conversationId === conversationId ? store.reports : NO_REPORTS;
  const merge = useCallback((incoming: Readonly<Record<string, FieldReport>>) => {
    setStore((current) => ({
      conversationId,
      reports: { ...(current.conversationId === conversationId ? current.reports : NO_REPORTS), ...incoming },
    }));
  }, [conversationId]);
  useEffect(() => {
    if (!FIELD_REPORTS_ENABLED || !conversationId || running) return undefined;
    const controller = new AbortController();
    listFieldReports({
      baseUrl: process.env.NEXT_PUBLIC_RAG_API_URL || '', getToken: getIdToken, conversationId, signal: controller.signal,
    }).then((byTurn) => {
      if (!controller.signal.aborted) merge(byTurn);
    }).catch(() => {
      // Missing "sent" marks only re-show the form; the server keeps one report per turn.
    });
    return () => controller.abort();
  }, [conversationId, running, merge]);
  const markSent = useCallback((report: FieldReport) => merge({ [report.senpaiTurnId]: report }), [merge]);
  return { reports, markSent };
}

/** ⋯メニューを、メニューの外側のクリック・タップと Escape で閉じる。 */
function useMenuDismissal(open: boolean, setOpen: (open: boolean) => void) {
  useEffect(() => {
    if (!open || typeof document === 'undefined') return undefined;
    return attachMenuDismissal(document, (reason) => {
      setOpen(false);
      // Escape で閉じたら、メニューを開いたボタンへフォーカスを戻す。
      if (reason === 'escape') document.querySelector<HTMLElement>('[data-senpai-menu] > summary')?.focus();
    });
  }, [open, setOpen]);
}

/** 「開発者表示」の切り替え。保存できない環境（プライベートモード等）でも画面は動く。 */
function useDeveloperView() {
  const [enabled, setEnabled] = useState(false);
  useEffect(() => {
    try {
      if (window.localStorage.getItem(DEV_VIEW_STORAGE_KEY) === 'true') setEnabled(true);
    } catch {
      // 保存値を読めなければ既定（一般表示）のままにする。
    }
  }, []);
  function toggle() {
    const next = !enabled;
    setEnabled(next);
    try {
      window.localStorage.setItem(DEV_VIEW_STORAGE_KEY, String(next));
    } catch {
      // 保存に失敗しても、今の画面の切り替えは有効。
    }
  }
  return { enabled, toggle };
}

export function KnowledgeSenpaiChat() {
  const [snapshot, setSnapshot] = useState<SenpaiChatSnapshot>(EMPTY_SNAPSHOT);
  const [question, setQuestion] = useState('');
  const [modelType, setModelType] = useState('');
  const [sendError, setSendError] = useState('');
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [menuOpen, setMenuOpen] = useState(false);
  const controllerRef = useRef<SenpaiChatController | null>(null);
  const mountedRef = useRef(false);
  const requestIdRef = useRef(0);
  const transcriptRef = useRef<HTMLDivElement | null>(null);
  const nearBottomRef = useRef(true);
  const scrollAfterSendRef = useRef(false);
  useController(setSnapshot, controllerRef, mountedRef);
  const history = useSenpaiHistory(snapshot, controllerRef);
  // 調査の開始と結果だけをスクリーンリーダーへ知らせる（描画中に、実行中フラグが変わった瞬間だけ更新する）。
  const [announced, setAnnounced] = useState({ running: false, text: '' });
  if (announced.running !== snapshot.running) {
    setAnnounced({ running: snapshot.running, text: nextAnnouncement(announced.running, snapshot, announced.text) });
  }
  const fieldReports = useFieldReports(snapshot.conversationId, snapshot.running);
  const developerView = useDeveloperView();
  useEffect(() => {
    const transcript = transcriptRef.current;
    if (!transcript) return;
    if (scrollAfterSendRef.current || nearBottomRef.current) {
      transcript.scrollTop = transcript.scrollHeight;
      nearBottomRef.current = true;
    }
    scrollAfterSendRef.current = false;
  }, [snapshot]);
  useMenuDismissal(menuOpen, setMenuOpen);
  const continuationPaused = isContinuationPaused(snapshot, RESEARCH_ENABLED && !KNOWHOW_ONLY);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const query = question.trim();
    if (!query || snapshot.running || continuationPaused || history.opening || !controllerRef.current) return;
    const controller = controllerRef.current;
    const requestId = ++requestIdRef.current;
    setSendError('');
    setQuestion('');
    scrollAfterSendRef.current = true;
    try {
      await controller.send(query, ...(modelType ? [{ modelType }] : []));
    } catch (error) {
      const code = (error as { code?: string } | null)?.code;
      if (mountedRef.current && controllerRef.current === controller && requestIdRef.current === requestId) {
        // 送れなかった質問は消さずに入力欄へ戻す（その間に新しく入力していれば、そちらを優先する）。
        setQuestion((current) => current || query);
        setSendError(code === 'validation' ? '質問を送信できませんでした。入力内容を確認してください。' : '質問を送信できませんでした。時間をおいて再度お試しください。');
      }
    }
  }

  function startNewChat() {
    requestIdRef.current += 1;
    history.resetSelection();
    controllerRef.current?.reset();
    setQuestion('');
    setSendError('');
    setSnapshot(EMPTY_SNAPSHOT);
    setSidebarOpen(false);
  }

  function openSavedChat(conversationId: string) {
    if (conversationId === snapshot.conversationId && !history.opening) {
      setSidebarOpen(false);
      return;
    }
    requestIdRef.current += 1;
    setQuestion('');
    setSendError('');
    setSidebarOpen(false);
    nearBottomRef.current = true;
    void history.openConversation(conversationId);
  }

  const requestSynthesis = useCallback((turnId: number) => {
    // The controller keeps the failure on the turn's synthesis lane; nothing else to show here.
    controllerRef.current?.synthesize(turnId).catch(() => {});
  }, []);

  function resend({ query, modelType: resendModel, supplement, supplementOf }: ResendOptions) {
    const controller = controllerRef.current;
    if (!controller || snapshot.running || history.opening) return;
    const requestId = ++requestIdRef.current;
    setSendError('');
    setModelType(resendModel ?? '');
    scrollAfterSendRef.current = true;
    controller.send(query, { ...(resendModel ? { modelType: resendModel } : {}), fresh: true, ...(supplement && supplementOf ? { supplement, supplementOf } : {}) }).catch(() => {
      if (mountedRef.current && controllerRef.current === controller && requestIdRef.current === requestId) {
        setSendError('質問を送信できませんでした。時間をおいて再度お試しください。');
      }
    });
  }

  function cancelSearch() {
    requestIdRef.current += 1;
    controllerRef.current?.cancel();
  }

  function onTranscriptScroll(event: UIEvent<HTMLDivElement>) {
    const transcript = event.currentTarget;
    nearBottomRef.current = transcript.scrollHeight - transcript.scrollTop - transcript.clientHeight < 80;
  }

  return (
    <SenpaiChatView
      snapshot={snapshot}
      history={{ entries: history.entries, loading: history.loading, error: history.error, complete: history.complete, opening: history.opening, openError: history.openError, onRetry: history.refresh }}
      question={question}
      onQuestionChange={setQuestion}
      modelType={modelType}
      onModelChange={setModelType}
      sendError={sendError}
      sidebarOpen={sidebarOpen}
      onOpenSidebar={() => setSidebarOpen(true)}
      onCloseSidebar={() => setSidebarOpen(false)}
      onSubmit={submit}
      onCancel={cancelSearch}
      onNewChat={startNewChat}
      onSelectConversation={openSavedChat}
      onSynthesize={requestSynthesis}
      onResend={resend}
      flags={{ research: RESEARCH_ENABLED && !KNOWHOW_ONLY, fieldReports: FIELD_REPORTS_ENABLED, synthesis: SYNTHESIS_ENABLED && !KNOWHOW_ONLY, knowhowOnly: KNOWHOW_ONLY }}
      developerView={developerView.enabled}
      onToggleDeveloperView={developerView.toggle}
      menuOpen={menuOpen}
      onMenuOpenChange={setMenuOpen}
      reports={fieldReports.reports}
      onReportSent={fieldReports.markSent}
      announcement={announced.text}
      transcriptRef={transcriptRef}
      onTranscriptScroll={onTranscriptScroll}
    />
  );
}
