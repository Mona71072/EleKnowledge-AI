'use client';

import { ChangeEvent, useRef, useState } from 'react';
import {
  addReviewComment,
  applyReviewComment,
  confirmOneNote,
  createWorkspace,
  editBody,
  editOneNoteDraft,
  exportProposal,
  markCopied,
  parseKnowledgeMarkdown,
  recordPlacement,
  recordSourceReview,
  setKbReview,
  type KnowledgeKbReview,
  type KnowledgeParsedMarkdown,
  type KnowledgeWorkspaceState,
} from '@/lib/knowledge-workbench.mjs';
import { KnowledgeMarkdownPanel } from './KnowledgeMarkdownPanel';
import { KnowledgeReviewComments } from './KnowledgeReviewComments';
import { KnowledgeOneNotePanel } from './KnowledgeOneNotePanel';
import { KnowledgeSourcePanel } from './KnowledgeSourcePanel';
import { KnowledgeSourceReviewPanel } from './KnowledgeSourceReviewPanel';
import { KnowledgeResearchWorkspace } from './KnowledgeResearchWorkspace';
import { KnowhowCardCheck } from './KnowhowCardCheck';
import { checkModelWords } from '@/lib/knowhow-card-check.mjs';
import { buildResearchTargetNote } from '@/lib/knowledge-research.mjs';
import { restoreReviewWorkspace } from '@/lib/knowledge-review-resume.mjs';


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
  const importToken = useRef(0);

  const replaceWorkspace = (next: KnowledgeWorkspaceState) => {
    workspaceRef.current = next;
    setWorkspace(next);
  };

  const replaceResearchTarget = (next: ResearchTargetContext | null) => {
    researchTargetRef.current = next;
    setResearchTarget(next);
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
      if (file.size > (isPacket ? 4 * 1024 * 1024 : 256 * 1024)) throw new TypeError('ファイルが大きすぎます。');
      const text = await file.text();
      const restored = isPacket ? await restoreReviewWorkspace(text) : null;
      if (token !== importToken.current) return;
      const nextParsed = restored?.parsed ?? parseKnowledgeMarkdown(text);
      const nextWorkspace = restored?.workspace ?? createWorkspace(nextParsed);
      setParsed(nextParsed);
      replaceWorkspace(nextWorkspace);
      setDocumentSession(token);
      setCurrentFilename(file.name);
      replaceResearchTarget(createResearchTargetContext(token, nextWorkspace.document.id, nextWorkspace.document.baseVersion, nextWorkspace.revision));
      setKbDraft(nextWorkspace.kbReview);
      setConfirmed(false);
      setMessage(isPacket ? 'JSON作業記録を開きました。原文と差分、コメントを復元しました。'
        : `「${file.name}」を読み込みました。内容はこの画面内だけで扱われます。`);
    } catch (reason) {
      if (token !== importToken.current) return;
      const reasonText = (reason as Error).message || '';
      const guidance = isPacket ? 'この画面で保存した4 MiB以下のJSON作業記録を選んでください。'
        : reasonText.includes('大きすぎます')
        ? '256 KiB以下のMarkdownを選んでください。'
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
      const latest = workspaceRef.current;
      if (importToken.current !== expectedSession || latest?.document.id !== current.document.id) return;
      if (latest !== current || latest.revision !== expectedRevision || packet.proposal.revision !== expectedRevision) {
        setMessage('保存準備中に内容が変更されたため、ファイルを作成しませんでした。最新の版からもう一度保存してください。');
        return;
      }
      if (format === 'markdown') {
        downloadFile(`${cleanFilename(current.document.id)}-proposal-v${expectedRevision}.md`, packet.proposal.markdown, 'text/markdown;charset=utf-8');
        setMessage('draft状態の修正候補Markdownを保存しました。元ファイルは変更していません。');
      } else {
        downloadFile(`${cleanFilename(current.document.id)}-proposal-v${expectedRevision}.json`, JSON.stringify(packet, null, 2), 'application/json;charset=utf-8');
        setMessage('原文・修正案・確認結果を含むJSON作業記録を保存しました。承認・公開状態には登録されません。');
      }
    } catch {
      if (importToken.current === expectedSession && workspaceRef.current === current) {
        setError('修正候補を保存できませんでした。内容を確認して、もう一度お試しください。');
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

  return (
    <div className="space-y-6">
      <header className="rounded-xl border border-blue-200 bg-blue-50 p-5">
        <p className="text-xs font-semibold uppercase tracking-wide text-blue-800">担当者の確認用</p>
        <h1 className="mt-1 text-2xl font-bold text-gray-950">{research ? '工技先輩（開発中）' : 'ノウハウ確認'}</h1>
        <p className="mt-2 max-w-4xl text-sm leading-6 text-gray-700">
          {research
            ? '既存カードを選び、技術KB・OneNote・Listsの資料と照らし合わせて本文を更新します。カードの修正案と出典ごとの確認記録を保存できます。'
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
          <span className="text-sm text-gray-600">256 KiB以下の .md ファイルを1つ選択</span>
          {busy && <span role="status" className="text-sm text-gray-700">読み込み中…</span>}
          {currentFilename && <span className="rounded-full bg-white px-3 py-1.5 text-sm font-medium text-gray-800 shadow-sm">作業中: {currentFilename}</span>}
        </div>
        {message && <p role="status" className="mt-3 text-sm text-green-800">{message}</p>}
        {error && <p role="alert" className="mt-3 text-sm text-red-800">{error}</p>}
        {research && active && (
          <nav aria-label="カード更新の操作" className="mt-4 flex flex-wrap gap-x-5 gap-y-2 text-sm font-semibold text-blue-800">
            <a href="#review-card-sources" className="underline underline-offset-2">出典を確認・本文を編集</a>
            <a href="#review-card-comments" className="underline underline-offset-2">コメントから追記案を作る</a>
            <a href="#search-card-sources" className="underline underline-offset-2">技術KB・法令KBを調べる</a>
            <a href="#save-card-draft" className="underline underline-offset-2">修正案を保存</a>
          </nav>
        )}
      </header>

      {active && parsed && (
        <div id="review-card-sources" className="grid min-w-0 scroll-mt-36 grid-cols-1 gap-5 lg:grid-cols-[minmax(16rem,0.9fr)_minmax(24rem,1.5fr)]">
          {research ? (
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
          ) : <KnowledgeSourcePanel metadata={active.document.metadata} kbStatus={active.kbReview.status} />}
          <KnowledgeMarkdownPanel
            title={active.document.title}
            originalBody={parsed.body}
            body={active.body}
            onChange={(body) => {
              try {
                const next = editBody(active, body);
                replaceWorkspace(next);
                setCardCheckRevision((revision) => revision + 1);
                replaceResearchTarget(createResearchTargetContext(documentSession, next.document.id, next.document.baseVersion, next.revision));
                setKbDraft(next.kbReview);
                setConfirmed(false);
                setMessage('');
                setError('');
              } catch {
                setError('本文を更新できませんでした。256 KiB以下の文章であることを確認してください。');
              }
            }}
          />
        </div>
      )}

      {research && active && (
        <div id="review-card-comments" className="scroll-mt-36">
          <KnowledgeReviewComments
            key={documentSession}
            body={active.body}
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
                return true;
              } catch {
                return false;
              }
            }}
          />
        </div>
      )}

      {research && parsed && active && (
        <div id="search-card-sources" className="scroll-mt-36">
          <KnowhowCardCheck
            key={documentSession}
            frontmatter={parsed.frontmatter}
            body={active.body}
            originalBody={parsed.body}
            busy={busy}
            onAdopt={(expectedBody, body, applied, skipped) => {
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
                setMessage(`追記案${applied}件を編集中の本文に反映しました。${duplicateNote}ページ下部から修正候補を保存できます。`);
                return true;
              } catch {
                setError('追記案を取り込めませんでした。本文が256 KiB以下になるよう追記案を選び直してください。');
                return false;
              }
            }}
          />
        </div>
      )}

      {research && (
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
      )}

      {!active || !parsed ? (
        <div className="rounded-xl border border-dashed border-gray-300 bg-white px-6 py-12 text-center">
          <h2 className="font-semibold text-gray-900">Markdownを選ぶと確認を始められます</h2>
          <p className="mt-2 text-sm text-gray-600">知識カードの原文や出典は自動では読み込みません。</p>
        </div>
      ) : (
        <>
          {research && (
            <details className="rounded-xl border border-gray-200 bg-white px-4 py-3">
              <summary className="cursor-pointer font-medium text-gray-900">元のカードに記録された出典と適用条件</summary>
              <div className="mt-3"><KnowledgeSourcePanel metadata={active.document.metadata} kbStatus={active.kbReview.status} /></div>
            </details>
          )}

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

          <footer id="save-card-draft" className="flex scroll-mt-36 flex-col justify-between gap-3 rounded-xl border border-gray-200 bg-white p-4 sm:flex-row sm:items-center">
            <div className="text-sm text-gray-700">
              <p className="font-medium">作業版 {active.revision} · 原版 {active.document.baseVersion}</p>
              <p className="mt-1 text-xs text-gray-500">MarkdownはObsidianへ持ち帰る編集候補、JSONには原版・指紋・出典の確認記録・コメント・掲載記録を保存します。元ファイルは上書きしません。</p>
            </div>
            <div className="flex flex-wrap gap-2">
              <button type="button" onClick={() => saveProposal('markdown')} disabled={busy} className="rounded-lg bg-blue-700 px-4 py-2.5 text-sm font-semibold text-white hover:bg-blue-800 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:cursor-not-allowed disabled:opacity-50">
                修正したMarkdownを保存
              </button>
              <button type="button" onClick={() => saveProposal('json')} disabled={busy} className="rounded-lg border border-gray-300 px-4 py-2.5 text-sm font-semibold text-gray-800 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:cursor-not-allowed disabled:opacity-50">
                JSON作業記録を保存
              </button>
            </div>
          </footer>
        </>
      )}
    </div>
  );
}
