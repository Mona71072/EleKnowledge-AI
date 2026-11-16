'use client';

import { ChangeEvent, useCallback, useEffect, useRef, useState } from 'react';
import {
  addReviewComment,
  applyReviewComment,
  confirmOneNote,
  createKnowledgeDraft,
  createWorkspace,
  editBody,
  editOneNoteDraft,
  exportProposal,
  markCopied,
  MAX_MARKDOWN_DOCUMENT_BYTES,
  parseKnowledgeMarkdown,
  recordPlacement,
  recordSourceReview,
  setKbReview,
  type KnowledgeKbReview,
  type KnowledgeParsedMarkdown,
  type KnowledgeWorkspaceState,
} from '@/lib/knowledge-workbench.mjs';
import { KnowledgeMarkdownPanel } from './KnowledgeMarkdownPanel';
import { KnowledgeFieldMaterialPanel } from './KnowledgeFieldMaterialPanel';
import { KnowledgeReviewComments } from './KnowledgeReviewComments';
import { KnowledgeOneNotePanel } from './KnowledgeOneNotePanel';
import { KnowledgeSourcePanel } from './KnowledgeSourcePanel';
import { KnowledgeSourceReviewPanel } from './KnowledgeSourceReviewPanel';
import { KnowledgeResearchWorkspace } from './KnowledgeResearchWorkspace';
import { KnowhowCardCheck } from './KnowhowCardCheck';
import { checkModelWords } from '@/lib/knowhow-card-check.mjs';
import { buildResearchTargetNote } from '@/lib/knowledge-research.mjs';
import { MAX_REVIEW_RECORD_BYTES, restoreReviewWorkspace } from '@/lib/knowledge-review-resume.mjs';
import { consumeKnowledgeGapRequest, type KnowledgeGapRequest } from '@/lib/knowledge-gap-request.mjs';
import { buildFieldRewriteRequest } from '@/lib/knowhow-rewrite.mjs';
import { requestKnowhowRewrite, rewriteFailureMessage } from '@/lib/knowhow-rewrite-client.mjs';
import { formatCheckDate } from '@/lib/knowhow-card-proposal.mjs';
import { getIdToken } from '@/lib/auth-helpers';
import { MAX_FIELD_MATERIAL_SUMMARY_CHARS } from '@/lib/knowledge-field-material.mjs';

async function suggestFieldSummary(input: { topic: string; excerpt: string; title: string }, signal: AbortSignal) {
  const request = buildFieldRewriteRequest({ ...input, checkedOn: formatCheckDate(new Date()) });
  const proposal = await requestKnowhowRewrite({
    baseUrl: process.env.NEXT_PUBLIC_RAG_API_URL || '', getToken: getIdToken, request, signal,
  }).catch((reason: unknown) => { throw new Error(rewriteFailureMessage(reason)); });
  if (proposal.conflicts.length) throw new Error('資料内の条件や記述に食い違いがあります。原文を確認してください。');
  const section = proposal.sections.find(({ status }) => status === 'changed');
  if (!section?.body) throw new Error('この抜粋から要点案を作れませんでした。該当箇所を選び直すか、確認した要点を入力してください。');
  if (Array.from(section.body).length > MAX_FIELD_MATERIAL_SUMMARY_CHARS || section.warnings.length) {
    throw new Error('要点案の長さ、または数値の根拠を確認できませんでした。抜粋を選び直すか、確認した要点を入力してください。');
  }
  return section.body;
}

function downloadFile(filename: string, content: string, type: string) {
  const blob = new Blob([content], { type });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  link.remove();
  window.setTimeout(() => URL.revokeObjectURL(url), 1000);
}

function cleanFilename(value: string): string {
  return value.replace(/[^\p{L}\p{N}._-]+/gu, '-').replace(/^-+|-+$/g, '').slice(0, 100) || 'knowledge';
}

type ResearchTargetContext = {
  key: string;
  label: string;
  knowledgeId: string;
  baseVersion: number;
  manualBodyRevision: number;
};

function createResearchTargetContext(
  session: number,
  knowledgeId: string,
  baseVersion: number,
  manualBodyRevision: number,
): ResearchTargetContext {
  return {
    key: JSON.stringify([session, knowledgeId, baseVersion, manualBodyRevision]),
    label: `${knowledgeId} · 原版 v${baseVersion} · 本文編集版 ${manualBodyRevision}`,
    knowledgeId,
    baseVersion,
    manualBodyRevision,
  };
}

export function KnowledgeWorkbench({ research = false }: { research?: boolean }) {
  const [parsed, setParsed] = useState<KnowledgeParsedMarkdown | null>(null);
  const [workspace, setWorkspace] = useState<KnowledgeWorkspaceState | null>(null);
  const workspaceRef = useRef<KnowledgeWorkspaceState | null>(null);
  const [kbDraft, setKbDraft] = useState<KnowledgeKbReview>({ status: 'unverified', reference: '', note: '' });
  const [confirmed, setConfirmed] = useState(false);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);
  const [documentSession, setDocumentSession] = useState(0);
  const [cardCheckRevision, setCardCheckRevision] = useState(0);
  const [researchTarget, setResearchTarget] = useState<ResearchTargetContext | null>(null);
  const researchTargetRef = useRef<ResearchTargetContext | null>(null);
  const [currentFilename, setCurrentFilename] = useState('');
  const [cardSearchMounted, setCardSearchMounted] = useState(false);
  const [manualResearchMounted, setManualResearchMounted] = useState(false);
  const [oneNoteMounted, setOneNoteMounted] = useState(false);
  const [gapOrigin, setGapOrigin] = useState<KnowledgeGapRequest['kind'] | null>(null);
  const [newCardTitle, setNewCardTitle] = useState('');
  const [commentFocusRequest, setCommentFocusRequest] = useState<{ sectionId: string; request: number } | null>(null);
  const commentFocusSequence = useRef(0);
  const importToken = useRef(0);

  useEffect(() => {
    const gap = research ? consumeKnowledgeGapRequest() : null;
    if (gap) setGapOrigin(gap.kind);
  }, [research]);

  const replaceWorkspace = (next: KnowledgeWorkspaceState) => {
    workspaceRef.current = next;
    setWorkspace(next);
  };

  const replaceResearchTarget = (next: ResearchTargetContext | null) => {
    researchTargetRef.current = next;
    setResearchTarget(next);
  };

  const requestCommentFocus = useCallback((sectionId: string) => {
    setCommentFocusRequest({ sectionId, request: ++commentFocusSequence.current });
  }, []);

  const openWorkspace = (nextParsed: KnowledgeParsedMarkdown, nextWorkspace: KnowledgeWorkspaceState, token: number, filename: string) => {
    setParsed(nextParsed);
    replaceWorkspace(nextWorkspace);
    setDocumentSession(token);
    setCommentFocusRequest(null);
    setCurrentFilename(filename);
    replaceResearchTarget(createResearchTargetContext(token, nextWorkspace.document.id, nextWorkspace.document.baseVersion, nextWorkspace.revision));
    setKbDraft(nextWorkspace.kbReview);
    setConfirmed(false);
  };

  const handleImport = async (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.currentTarget.files?.[0];
    event.currentTarget.value = '';
    if (!file) return;
    const token = ++importToken.current;
    setError('');
    setMessage('');
    setBusy(true);
    const isPacket = research && /\.json$/iu.test(file.name);
    try {
      if (!isPacket && !file.name.toLowerCase().endsWith('.md')) throw new TypeError('Markdown（.md）ファイルを選んでください。');
      if (file.size > (isPacket ? MAX_REVIEW_RECORD_BYTES : MAX_MARKDOWN_DOCUMENT_BYTES)) throw new TypeError('ファイルが大きすぎます。');
      const text = await file.text();
      const restored = isPacket ? await restoreReviewWorkspace(text) : null;
      if (token !== importToken.current) return;
      const nextParsed = restored?.parsed ?? parseKnowledgeMarkdown(text);
      const nextWorkspace = restored?.workspace ?? createWorkspace(nextParsed);
      openWorkspace(nextParsed, nextWorkspace, token, file.name);
      setMessage(isPacket ? 'JSON作業記録を開きました。原文と差分、コメントを復元しました。'
        : `「${file.name}」を読み込みました。内容はこの画面内だけで扱われます。`);
    } catch (reason) {
      if (token !== importToken.current) return;
      const reasonText = (reason as Error).message || '';
      const guidance = isPacket ? 'この画面で保存した4 MiB以下のJSON作業記録を選んでください。'
        : reasonText.includes('大きすぎます')
        ? '320 KiB以下のMarkdownを選んでください。本文は256 KiBまでです。'
        : reasonText.includes('Markdown（.md）')
          ? 'Markdown（.md）ファイルを選んでください。'
          : 'MarkdownのID・版・タイトルとYAML形式を確認してください。';
      const retained = currentFilename ? `現在の作業は「${currentFilename}」のままです。` : '現在の作業はありません。';
      setError(`読み込めませんでした。${guidance} ${retained}`);
    } finally {
      if (token === importToken.current) setBusy(false);
    }
  };

  const updateKbDraft = (nextDraft: KnowledgeKbReview) => {
    setKbDraft(nextDraft);
    setConfirmed(false);
    setMessage('');
    const current = workspaceRef.current;
    if (!current) return;
    try {
      const updated = setKbReview(current, nextDraft);
      replaceWorkspace(updated);
    } catch {
      // Incomplete form edits must invalidate any prior review or copy state.
      const invalidated = setKbReview(current, { status: 'unverified' });
      replaceWorkspace(invalidated);
    }
  };

  const copyCurrent = async () => {
    const current = workspaceRef.current;
    if (!current || current.reviewedRevision !== current.revision || !confirmed) return;
    const expectedRevision = current.revision;
    const expectedSession = importToken.current;
    setError('');
    try {
      if (!navigator.clipboard?.writeText) throw new Error('このブラウザーではクリップボードを使えません。');
      await navigator.clipboard.writeText(current.noteText);
      const latest = workspaceRef.current;
      if (importToken.current !== expectedSession || latest?.document.id !== current.document.id) return;
      if (latest !== current || latest.revision !== expectedRevision || latest.reviewedRevision !== expectedRevision) {
        setMessage('コピー中に内容が変更されたため、現在版のコピー済み状態にはしません。最新の文章を確認して、もう一度コピーしてください。');
        return;
      }
      replaceWorkspace(markCopied(latest, expectedRevision));
      setMessage('確認した版をコピーしました。OneNoteへ貼り付けた後、掲載先を記録してください。');
    } catch {
      if (importToken.current === expectedSession && workspaceRef.current === current) {
        setError('コピーできませんでした。ブラウザーのクリップボード利用設定を確認してください。');
      }
    }
  };

  const addPlacement = (destination: string) => {
    const current = workspaceRef.current;
    if (!current) return;
    const next = recordPlacement(current, { destination, recordedAt: new Date().toISOString() });
    replaceWorkspace(next);
    setMessage('担当者によるOneNote掲載記録を残しました。');
  };

  const saveProposal = async (format: 'markdown' | 'json') => {
    const current = workspaceRef.current;
    if (!current) return;
    const expectedRevision = current.revision;
    const expectedSession = importToken.current;
    setError('');
    try {
      const packet = await exportProposal(current);
      const reviewRecord = format === 'json' ? JSON.stringify(packet, null, 2) : null;
      if (reviewRecord !== null) await restoreReviewWorkspace(reviewRecord);
      const latest = workspaceRef.current;
      if (importToken.current !== expectedSession || latest?.document.id !== current.document.id) return;
      if (latest !== current || latest.revision !== expectedRevision || packet.proposal.revision !== expectedRevision) {
        setMessage('保存準備中に内容が変更されたため、ファイルを作成しませんでした。最新の版からもう一度保存してください。');
        return;
      }
      if (reviewRecord === null) {
        downloadFile(`${cleanFilename(current.document.id)}-proposal-v${expectedRevision}.md`, packet.proposal.markdown, 'text/markdown;charset=utf-8');
        setMessage('draft状態の修正候補Markdownを保存しました。元ファイルは変更していません。');
      } else {
        downloadFile(`${cleanFilename(current.document.id)}-proposal-v${expectedRevision}.json`, reviewRecord, 'application/json;charset=utf-8');
        setMessage('原文・修正案・確認結果を含むJSON作業記録を保存しました。承認・公開状態には登録されません。');
      }
    } catch (reason) {
      if (importToken.current === expectedSession && workspaceRef.current === current) {
        setError(format === 'json' && reason instanceof TypeError
          ? `JSON作業記録を保存できませんでした。${reason.message} 本文は「修正したMarkdownを保存」で保存できます。`
          : '修正候補を保存できませんでした。内容を確認して、もう一度お試しください。');
      }
    }
  };

  const confirm = (checked: boolean) => {
    setConfirmed(false);
    const current = workspaceRef.current;
    if (!current) return;
    if (!checked) {
      setMessage('');
      try {
        const next = setKbReview(current, current.kbReview);
        replaceWorkspace(next);
        setMessage('確認を解除しました。現在版の確認・コピー状態は失効しました。');
      } catch {
        setError('確認状態を解除できませんでした。現在版を確認してください。');
      }
      return;
    }
    try {
      const next = confirmOneNote(current, { checked: true, noteReconciled: true });
      replaceWorkspace(next);
      setConfirmed(true);
      setMessage('現在版の本文と追記案の整合、根拠・適用条件・共有先を確認しました。');
    } catch {
      setError('確認できませんでした。KBの確認状態・参照先・確認メモを見直してください。');
    }
  };

  const active = workspace;
  const copied = Boolean(active && active.copiedRevision === active.revision);
  const canCopy = Boolean(!busy && active && confirmed && active.reviewedRevision === active.revision && active.kbReview.status === 'reviewed');

  const updateBody = (body: string, expectedBody?: string) => {
    const current = workspaceRef.current;
    if (busy || !current || current.document !== active?.document || (expectedBody !== undefined && current.body !== expectedBody)) return false;
    try {
      const next = editBody(current, body);
      replaceWorkspace(next);
      setCardCheckRevision((revision) => revision + 1);
      replaceResearchTarget(createResearchTargetContext(documentSession, next.document.id, next.document.baseVersion, next.revision));
      setKbDraft(next.kbReview);
      setConfirmed(false);
      setMessage('');
      setError('');
      return true;
    } catch {
      setError('本文を更新できませんでした。256 KiB以下の文章であることを確認してください。');
      return false;
    }
  };

  const oneNotePanel = active ? (
    <KnowledgeOneNotePanel
      key={`${documentSession}-${active.copiedRevision ?? 'none'}`}
      noteText={active.noteText}
      noteNeedsReconcile={active.noteNeedsReconcile}
      onNoteChange={(text) => {
        try {
          const next = editOneNoteDraft(active, text);
          replaceWorkspace(next);
          setKbDraft(next.kbReview);
          setConfirmed(false);
          setMessage('');
        } catch {
          setError('追記案を更新できませんでした。256 KiB以下の文章であることを確認してください。');
        }
      }}
      kbReview={kbDraft}
      onKbReviewChange={updateKbDraft}
      confirmed={confirmed && active.reviewedRevision === active.revision}
      onConfirmChange={confirm}
      onCopy={copyCurrent}
      canCopy={canCopy}
      copied={copied}
      placements={active.placements}
      onRecordPlacement={addPlacement}
    />
  ) : null;

  return (
    <div className="space-y-6">
      <header className="rounded-xl border border-blue-200 bg-blue-50 p-5">
        <p className="text-xs font-semibold uppercase tracking-wide text-blue-800">担当者の確認用</p>
        <h1 className="mt-1 text-2xl font-bold text-gray-950">{research ? '工技先輩（開発中）' : 'ノウハウ確認'}</h1>
        <p className="mt-2 max-w-4xl text-sm leading-6 text-gray-700">
          {research
            ? 'カードを開くか新規下書きを作成し、技術KB・OneNote・Listsや現場資料を根拠に本文を編集できます。'
            : '自分で選んだMarkdownを確認し、修正候補とOneNoteへの追記文を作ります。内容はサーバーへ送られず、元ファイルも変更しません。画面を閉じたり別ファイルを読み込むと、保存していない作業は消えます。'}
        </p>
        <div className="mt-4 flex flex-wrap items-center gap-3">
          <label className="inline-flex cursor-pointer items-center rounded-lg bg-blue-700 px-4 py-2.5 text-sm font-semibold text-white hover:bg-blue-800 focus-within:ring-2 focus-within:ring-blue-500 focus-within:ring-offset-2">
            Markdownを選ぶ
            <input aria-label="Markdownファイルを選択" type="file" accept=".md,text/markdown,text/plain" onChange={handleImport} disabled={busy} className="sr-only" />
          </label>
          {research && (
            <label className="inline-flex cursor-pointer items-center rounded-lg border border-blue-300 bg-white px-4 py-2.5 text-sm font-semibold text-blue-900 hover:bg-blue-100 focus-within:ring-2 focus-within:ring-blue-500">
              JSON作業記録を開く
              <input aria-label="JSON作業記録を開く" type="file" accept=".json,application/json" onChange={handleImport} disabled={busy} className="sr-only" />
            </label>
          )}
          <span className="text-sm text-gray-600">.md ファイルを1つ選択（本文256 KiB・全体320 KiBまで）</span>
          {busy && <span role="status" className="text-sm text-gray-700">読み込み中…</span>}
          {currentFilename && <span className="rounded-full bg-white px-3 py-1.5 text-sm font-medium text-gray-800 shadow-sm">作業中: {currentFilename}</span>}
        </div>
        {gapOrigin && <p className="mt-3 rounded-md bg-white p-3 text-sm text-blue-950">
          {gapOrigin === 'official_kb' ? '通常の技術KBチャットで根拠が見つからなかった相談から開きました。' : '先輩チャットで情報が見つからなかった相談から開きました。'}
          {' '}既存カードを選ぶか、新規カードの下書きを作成してください。
        </p>}
        {research && !active && (
          <details open={gapOrigin ? true : undefined} className="mt-3 max-w-lg rounded-md border border-blue-200 bg-white p-3">
            <summary className="cursor-pointer text-sm font-semibold text-blue-950">新規カードを作成</summary>
            <form className="mt-3 flex flex-wrap items-end gap-2" onSubmit={(event) => {
              event.preventDefault();
              if (busy || workspaceRef.current) return;
              try {
                const draft = createKnowledgeDraft(newCardTitle);
                openWorkspace(draft, createWorkspace(draft), ++importToken.current, draft.title);
                setNewCardTitle('');
                setError('');
                setMessage('新規の下書きを作成しました。');
              } catch (reason) {
                setError(reason instanceof TypeError ? reason.message : '新規の下書きを作成できませんでした。');
              }
            }}>
              <label className="min-w-0 flex-1 text-sm">カードのタイトル
                <input className="mt-1 block w-full rounded border border-gray-300 px-2 py-1.5" value={newCardTitle}
                  maxLength={200} onChange={(event) => setNewCardTitle(event.target.value)} required />
              </label>
              <button type="submit" disabled={busy} className="rounded bg-blue-700 px-3 py-2 text-sm font-semibold text-white">下書きを作成</button>
            </form>
          </details>
        )}
        {message && <p role="status" className="mt-3 text-sm text-green-800">{message}</p>}
        {error && <p role="alert" className="mt-3 text-sm text-red-800">{error}</p>}
        {research && active && (
          <nav aria-label="カード更新の操作" className="mt-4 flex flex-wrap gap-x-5 gap-y-2 text-sm font-semibold text-blue-800">
            <a href="#review-card-sources" className="underline underline-offset-2">出典を確認・本文を編集</a>
            <a href="#review-card-comments" className="underline underline-offset-2">コメントから追記案を作る</a>
            <a href="#review-field-material" className="underline underline-offset-2">現場資料を使う</a>
            <a href="#save-card-draft" className="underline underline-offset-2">修正案を保存</a>
          </nav>
        )}
      </header>

      {active && parsed && (
        <div id="review-card-sources" className={`grid min-w-0 scroll-mt-36 grid-cols-1 gap-5 ${research ? 'lg:grid-cols-[minmax(0,1.5fr)_minmax(18rem,0.9fr)]' : 'lg:grid-cols-[minmax(16rem,0.9fr)_minmax(24rem,1.5fr)]'}`}>
          {research ? (
            <>
              <KnowledgeMarkdownPanel title={active.document.title} originalBody={parsed.body} body={active.body} onChange={updateBody}
                onSectionSelect={requestCommentFocus} />
              <div className="min-w-0 space-y-4">
                <KnowledgeSourceReviewPanel
                  key={documentSession}
                  metadata={active.document.metadata}
                  records={active.sourceReviews}
                  revision={active.revision}
                  onRecord={(input) => {
                    const current = workspaceRef.current;
                    if (busy || !current || current.document !== active.document || current.revision !== active.revision) return false;
                    try {
                      replaceWorkspace(recordSourceReview(current, input));
                      setError('');
                      return true;
                    } catch {
                      setError('照合記録を追加できませんでした。出典と参照箇所、確認メモを確認してください。');
                      return false;
                    }
                  }}
                />
                <details id="optional-metadata" className="rounded-xl border border-gray-200 bg-white px-4 py-3">
                  <summary className="cursor-pointer text-sm font-medium text-gray-800">元カードに記録された出典と適用条件</summary>
                  <div className="mt-3"><KnowledgeSourcePanel metadata={active.document.metadata} kbStatus={active.kbReview.status} /></div>
                </details>
              </div>
            </>
          ) : (
            <>
              <KnowledgeSourcePanel metadata={active.document.metadata} kbStatus={active.kbReview.status} />
              <KnowledgeMarkdownPanel title={active.document.title} originalBody={parsed.body} body={active.body} onChange={updateBody} />
            </>
          )}
        </div>
      )}

      {research && active && (
        <div id="review-card-comments" className="scroll-mt-36">
          <KnowledgeReviewComments
            key={documentSession}
            body={active.body}
            focusRequest={commentFocusRequest}
            title={active.document.title}
            modelWords={checkModelWords(active.document.metadata)}
            bodyRevision={cardCheckRevision}
            busy={busy}
            comments={active.reviewComments}
            onAdd={(input) => {
              const current = workspaceRef.current;
              if (!current || current.document !== active.document || busy) return false;
              try {
                replaceWorkspace(addReviewComment(current, input));
                return true;
              } catch {
                return false;
              }
            }}
            onApply={(id, expectedBody, body) => {
              const current = workspaceRef.current;
              if (!current || current.document !== active.document || busy) return false;
              try {
                const next = applyReviewComment(current, id, expectedBody, body);
                replaceWorkspace(next);
                setCardCheckRevision((revision) => revision + 1);
                replaceResearchTarget(createResearchTargetContext(documentSession, next.document.id, next.document.baseVersion, next.revision));
                setKbDraft(next.kbReview);
                setConfirmed(false);
                setError('');
                setMessage('コメントへの追記案を対象の節に反映しました。Markdown本文の差分から確認できます。');
                window.requestAnimationFrame(() => document.getElementById('review-card-sources')?.scrollIntoView({ behavior: 'smooth', block: 'start' }));
                return true;
              } catch {
                return false;
              }
            }}
          />
        </div>
      )}

      {research && active && (
        <div id="review-field-material" className="scroll-mt-36">
          <KnowledgeFieldMaterialPanel key={documentSession} body={active.body} busy={busy}
            suggest={process.env.NEXT_PUBLIC_ENABLE_KNOWHOW_FIELD_MATERIAL === 'true' ? suggestFieldSummary : undefined}
            onApply={(expectedBody, nextBody) => updateBody(nextBody, expectedBody)} />
        </div>
      )}

      {active && parsed && (
        <footer id="save-card-draft" className="flex scroll-mt-36 flex-col justify-between gap-3 rounded-xl border border-blue-200 bg-blue-50 p-4 sm:flex-row sm:items-center">
          <div className="text-sm text-gray-700">
            <p className="font-medium">作業版 {active.revision} · 原版 {active.document.baseVersion}</p>
            <p className="mt-1 text-xs text-gray-600">編集候補は元ファイルを上書きせず、Markdownまたは作業記録として保存します。</p>
          </div>
          <div className="flex flex-wrap gap-2">
            <button type="button" onClick={() => saveProposal('markdown')} disabled={busy} className="rounded-lg bg-blue-700 px-4 py-2.5 text-sm font-semibold text-white hover:bg-blue-800 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:cursor-not-allowed disabled:opacity-50">
              修正したMarkdownを保存
            </button>
            <button type="button" onClick={() => saveProposal('json')} disabled={busy} className="rounded-lg border border-gray-300 bg-white px-4 py-2.5 text-sm font-semibold text-gray-800 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:cursor-not-allowed disabled:opacity-50">
              JSON作業記録を保存
            </button>
          </div>
        </footer>
      )}

      {research && parsed && active && (
        <details id="optional-card-search" onToggle={(event) => { if (event.currentTarget.open) setCardSearchMounted(true); }} className="scroll-mt-36 rounded-xl border border-gray-200 bg-white px-4 py-3">
          <summary className="cursor-pointer font-semibold text-gray-900">カードを一括照合（任意）</summary>
          {cardSearchMounted && (
            <div className="mt-4">
              <KnowhowCardCheck
                key={documentSession}
                frontmatter={parsed.frontmatter}
                body={active.body}
                originalBody={parsed.body}
                busy={busy}
                onAdopt={(expectedBody, body, applied, skipped, rewritten) => {
                  const current = workspaceRef.current;
                  if (!current || current.document !== active.document || current.body !== expectedBody) {
                    setError('対象の本文が変わりました。もう一度「差分を確認」してください。');
                    return false;
                  }
                  try {
                    const next = editBody(current, body);
                    replaceWorkspace(next);
                    setCardCheckRevision((revision) => revision + 1);
                    replaceResearchTarget(createResearchTargetContext(documentSession, next.document.id, next.document.baseVersion, next.revision));
                    setKbDraft(next.kbReview);
                    setConfirmed(false);
                    setError('');
                    const duplicateNote = skipped ? `重複した${skipped}件は省きました。` : '';
                    const done = [applied ? `追記案${applied}件` : '', rewritten ? `本文${rewritten}節の書き換え` : ''].filter(Boolean).join('と');
                    setMessage(`${done}を編集中の本文に反映しました。${duplicateNote}「修正案を保存」から書き出せます。`);
                    return true;
                  } catch {
                    setError('追記案を取り込めませんでした。本文が256 KiB以下になるよう追記案を選び直してください。');
                    return false;
                  }
                }}
              />
            </div>
          )}
        </details>
      )}

      {research && (
        <details id="optional-manual-research" onToggle={(event) => { if (event.currentTarget.open) setManualResearchMounted(true); }} className="rounded-xl border border-gray-200 bg-white px-4 py-3">
          <summary className="cursor-pointer font-semibold text-gray-900">質問を入力してKBを調べる（任意）</summary>
          {manualResearchMounted && (
            <div className="mt-4">
            <KnowledgeResearchWorkspace
              canAdopt={Boolean(active)}
              contextKey={researchTarget?.key ?? null}
              targetLabel={researchTarget?.label ?? ''}
              onAdopt={(note, expectedContextKey) => {
                const current = workspaceRef.current;
                const target = researchTargetRef.current;
                if (!current || !target) {
                  setMessage('調査メモを取り込むには、先にMarkdownを選んでください。');
                  return false;
                }
                if (!expectedContextKey || expectedContextKey !== target.key) {
                  setMessage('対象Markdownまたは本文が変わりました。現在のファイルと本文を指定して、もう一度照合してください。');
                  return false;
                }
                try {
                  const provenance = buildResearchTargetNote(target);
                  const next = editBody(current, `${current.body.trimEnd()}\n\n${provenance}\n\n${note}`);
                  replaceWorkspace(next);
                  setCardCheckRevision((revision) => revision + 1);
                  setKbDraft(next.kbReview);
                  setConfirmed(false);
                  setError('');
                  setMessage('調査メモ候補をMarkdown本文へ追記しました。OneNote追記案との整合を確認してください。');
                  return true;
                } catch {
                  setError('調査メモを取り込めませんでした。Markdown本文の上限を確認してください。');
                  return false;
                }
              }}
            />
            </div>
          )}
        </details>
      )}

      {!active || !parsed ? (
        <div className="rounded-xl border border-dashed border-gray-300 bg-white px-6 py-12 text-center">
          <h2 className="font-semibold text-gray-900">Markdownを選ぶと確認を始められます</h2>
          <p className="mt-2 text-sm text-gray-600">知識カードの原文や出典は自動では読み込みません。</p>
        </div>
      ) : (
        <>
          {research ? (
            <details id="optional-onenote" onToggle={(event) => { if (event.currentTarget.open) setOneNoteMounted(true); }} className="rounded-xl border border-gray-200 bg-white px-4 py-3">
              <summary className="cursor-pointer font-semibold text-gray-900">OneNoteへの転記（任意）</summary>
              {oneNoteMounted && <div className="mt-4 space-y-4">
                {oneNotePanel}
              </div>}
            </details>
          ) : (
            oneNotePanel
          )}
        </>
      )}
    </div>
  );
}
