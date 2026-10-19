'use client';

import { ChangeEvent, useRef, useState } from 'react';
import {
  confirmOneNote,
  createWorkspace,
  editBody,
  editOneNoteDraft,
  exportProposal,
  markCopied,
  parseKnowledgeMarkdown,
  recordPlacement,
  setKbReview,
  type KnowledgeKbReview,
  type KnowledgeParsedMarkdown,
  type KnowledgeWorkspaceState,
} from '@/lib/knowledge-workbench.mjs';
import { KnowledgeMarkdownPanel } from './KnowledgeMarkdownPanel';
import { KnowledgeOneNotePanel } from './KnowledgeOneNotePanel';
import { KnowledgeSourcePanel } from './KnowledgeSourcePanel';
import { KnowledgeResearchWorkspace } from './KnowledgeResearchWorkspace';


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
    try {
      if (!file.name.toLowerCase().endsWith('.md')) throw new TypeError('Markdown（.md）ファイルを選んでください。');
      if (file.size > 256 * 1024) throw new TypeError('ファイルは256 KiB以下を選んでください。');
      const text = await file.text();
      if (token !== importToken.current) return;
      const nextParsed = parseKnowledgeMarkdown(text);
      const nextWorkspace = createWorkspace(nextParsed);
      setParsed(nextParsed);
      replaceWorkspace(nextWorkspace);
      setDocumentSession(token);
      setCurrentFilename(file.name);
      replaceResearchTarget(createResearchTargetContext(token, nextWorkspace.document.id, nextWorkspace.document.baseVersion, nextWorkspace.revision));
      setKbDraft(nextWorkspace.kbReview);
      setConfirmed(false);
      setMessage(`「${file.name}」を読み込みました。内容はこの画面内だけで扱われます。`);
    } catch (reason) {
      if (token !== importToken.current) return;
      const reasonText = (reason as Error).message || '';
      const guidance = reasonText.includes('256 KiB')
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
            ? '技術KB・法令KBの回答を比較し、選んだ回答を調査メモ候補としてMarkdownへ取り込みます。ファイルは選んだ後もブラウザー内だけで扱い、自分が送信する質問だけを検索APIへ送ります。'
            : '自分で選んだMarkdownを確認し、修正候補とOneNoteへの追記文を作ります。内容はサーバーへ送られず、元ファイルも変更しません。画面を閉じたり別ファイルを読み込むと、保存していない作業は消えます。'}
        </p>
        <div className="mt-4 flex flex-wrap items-center gap-3">
          <label className="inline-flex cursor-pointer items-center rounded-lg bg-blue-700 px-4 py-2.5 text-sm font-semibold text-white hover:bg-blue-800 focus-within:ring-2 focus-within:ring-blue-500 focus-within:ring-offset-2">
            Markdownを選ぶ
            <input aria-label="Markdownファイルを選択" type="file" accept=".md,text/markdown,text/plain" onChange={handleImport} disabled={busy} className="sr-only" />
          </label>
          <span className="text-sm text-gray-600">256 KiB以下の .md ファイルを1つ選択</span>
          {busy && <span role="status" className="text-sm text-gray-700">読み込み中…</span>}
          {currentFilename && <span className="rounded-full bg-white px-3 py-1.5 text-sm font-medium text-gray-800 shadow-sm">作業中: {currentFilename}</span>}
        </div>
        {message && <p role="status" className="mt-3 text-sm text-green-800">{message}</p>}
        {error && <p role="alert" className="mt-3 text-sm text-red-800">{error}</p>}
      </header>

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
              return;
            }
            if (!expectedContextKey || expectedContextKey !== target.key) {
              setMessage('対象Markdownまたは本文が変わりました。現在のファイルと本文を指定して、もう一度照合してください。');
              return;
            }
            try {
              const provenance = `> 調査対象: ${target.knowledgeId} · 原版 v${target.baseVersion} · 検索時本文編集版 ${target.manualBodyRevision}`;
              const next = editBody(current, `${current.body.trimEnd()}\n\n${provenance}\n\n${note}`);
              replaceWorkspace(next);
              setKbDraft(next.kbReview);
              setConfirmed(false);
              setError('');
              setMessage('選択した回答を調査メモ候補としてMarkdown本文へ追記しました。OneNote追記案との整合を確認してください。');
            } catch {
              setError('調査メモを取り込めませんでした。Markdown本文の上限を確認してください。');
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
          <div className="grid min-w-0 grid-cols-1 gap-5 xl:grid-cols-[minmax(16rem,0.9fr)_minmax(24rem,1.5fr)]">
            <KnowledgeSourcePanel metadata={active.document.metadata} kbStatus={active.kbReview.status} />
            <KnowledgeMarkdownPanel
              title={active.document.title}
              originalBody={parsed.body}
              body={active.body}
              onChange={(body) => {
                try {
                  const next = editBody(active, body);
                  replaceWorkspace(next);
                  replaceResearchTarget(createResearchTargetContext(documentSession, next.document.id, next.document.baseVersion, next.revision));
                  setKbDraft(next.kbReview);
                  setConfirmed(false);
                  setMessage('');
                } catch {
                  setError('本文を更新できませんでした。256 KiB以下の文章であることを確認してください。');
                }
              }}
            />
          </div>

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

          <footer className="flex flex-col justify-between gap-3 rounded-xl border border-gray-200 bg-white p-4 sm:flex-row sm:items-center">
            <div className="text-sm text-gray-700">
              <p className="font-medium">作業版 {active.revision} · 原版 {active.document.baseVersion}</p>
              <p className="mt-1 text-xs text-gray-500">MarkdownはObsidianへ持ち帰る編集候補、JSONは原版・指紋・確認・掲載記録です。元ファイルは上書きしません。</p>
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
