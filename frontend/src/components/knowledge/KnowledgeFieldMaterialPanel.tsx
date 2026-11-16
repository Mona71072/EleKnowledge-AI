'use client';

import { useEffect, useRef, useState } from 'react';
import {
  MAX_FIELD_MATERIAL_EXCERPT_CHARS,
  MAX_FIELD_MATERIAL_SUMMARY_CHARS,
  insertFieldMaterialMarkdown,
  normalizeFieldMaterialMetadata,
  readFieldMaterialFile,
  validateFieldMaterialExcerpt,
  type FieldMaterialSource,
} from '@/lib/knowledge-field-material.mjs';
import { KnowledgeLineDiff } from './KnowledgeLineDiff';

const DEFAULT_TOPIC = '現場資料の適用条件と確認手順を整理する';

type SuggestInput = { topic: string; excerpt: string; title: string };

type Props = {
  body: string;
  busy: boolean;
  onApply: (expectedBody: string, nextBody: string) => boolean;
  suggest?: (input: SuggestInput, signal: AbortSignal) => Promise<string>;
};

function excerptLength(value: string): number {
  return Array.from(value).length;
}

function validExcerpt(sourceText: string, excerpt: string): boolean {
  try {
    validateFieldMaterialExcerpt(sourceText, excerpt);
    return true;
  } catch {
    return false;
  }
}

function normalizedTextareaOffsets(sourceText: string): number[] {
  const offsets = [0];
  for (let index = 0; index < sourceText.length;) {
    if (sourceText[index] === '\r' && sourceText[index + 1] === '\n') {
      index += 2;
      offsets.push(index);
    } else {
      index += 1;
      offsets.push(index);
    }
  }
  return offsets;
}

function safeDownloadName(filename: string): string {
  const base = filename.replace(/[\\/:*?"<>|\u0000-\u001f]/gu, '_').trim() || 'field-material.txt';
  return base.toLowerCase().endsWith('.md') || base.toLowerCase().endsWith('.txt') ? base : `${base}.txt`;
}

export function KnowledgeFieldMaterialPanel({ body, busy, onApply, suggest }: Props) {
  const [source, setSource] = useState<FieldMaterialSource | null>(null);
  const [baseBody, setBaseBody] = useState(body);
  const [excerpt, setExcerpt] = useState('');
  const [title, setTitle] = useState('');
  const [version, setVersion] = useState('');
  const [locator, setLocator] = useState('');
  const [referenceUrl, setReferenceUrl] = useState('');
  const [summary, setSummary] = useState('');
  const [summaryOrigin, setSummaryOrigin] = useState<'manual' | 'ai'>('manual');
  const [reviewed, setReviewed] = useState(false);
  const [aiConsent, setAiConsent] = useState(false);
  const [topic, setTopic] = useState(DEFAULT_TOPIC);
  const [suggestion, setSuggestion] = useState('');
  const [isSuggesting, setIsSuggesting] = useState(false);
  const [error, setError] = useState('');
  const [applyMessage, setApplyMessage] = useState('');
  const [previewMarkdown, setPreviewMarkdown] = useState('');
  const [previewError, setPreviewError] = useState('');
  const previewRef = useRef<HTMLTextAreaElement>(null);
  const originalFileRef = useRef<File | null>(null);
  const requestRef = useRef<AbortController | null>(null);
  const requestVersion = useRef(0);
  const fileReadVersion = useRef(0);

  const aiEnabled = process.env.NEXT_PUBLIC_ENABLE_KNOWHOW_REWRITE === 'true' && Boolean(suggest);
  const excerptIsValid = Boolean(source && excerpt.trim() && validExcerpt(source.text, excerpt));
  const bodyChanged = Boolean(source && baseBody !== body);

  function invalidateSuggestion() {
    requestVersion.current += 1;
    requestRef.current?.abort();
    requestRef.current = null;
    setIsSuggesting(false);
    setSuggestion('');
    setAiConsent(false);
  }

  function resetDraft(nextSource: FieldMaterialSource | null, nextBody = body) {
    fileReadVersion.current += 1;
    originalFileRef.current = null;
    invalidateSuggestion();
    setSource(nextSource);
    setBaseBody(nextBody);
    setExcerpt('');
    setTitle(nextSource?.filename.replace(/\.(md|txt)$/iu, '') ?? '');
    setVersion('');
    setLocator('');
    setReferenceUrl('');
    setSummary('');
    setSummaryOrigin('manual');
    setReviewed(false);
    setTopic(DEFAULT_TOPIC);
    setError('');
    setApplyMessage('');
    setPreviewMarkdown('');
    setPreviewError('');
  }

  useEffect(() => () => {
    requestVersion.current += 1;
    fileReadVersion.current += 1;
    requestRef.current?.abort();
  }, []);

  async function handleFileChange(event: React.ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    event.target.value = '';
    if (!file) return;
    resetDraft(null);
    const readVersion = fileReadVersion.current;
    setError('');
    try {
      const loaded = await readFieldMaterialFile(file);
      if (fileReadVersion.current !== readVersion) return;
      resetDraft(loaded, body);
      originalFileRef.current = file;
    } catch (cause) {
      if (fileReadVersion.current !== readVersion) return;
      setError(cause instanceof Error ? cause.message : 'ファイルを読み込めませんでした。');
    }
  }

  function updateExcerpt(value: string) {
    invalidateSuggestion();
    setExcerpt(value);
    setReviewed(false);
    setSummary('');
    setSummaryOrigin('manual');
    setPreviewMarkdown('');
    setApplyMessage('');
  }

  function updateAttribution(field: 'title' | 'version' | 'locator' | 'url', value: string) {
    invalidateSuggestion();
    if (field === 'title') setTitle(value);
    else if (field === 'version') setVersion(value);
    else if (field === 'locator') setLocator(value);
    else setReferenceUrl(value);
    setReviewed(false);
    setPreviewMarkdown('');
    setApplyMessage('');
    if (summaryOrigin === 'ai') {
      setSummary('');
      setSummaryOrigin('manual');
    }
  }

  function updateTopic(value: string) {
    invalidateSuggestion();
    setTopic(value);
    setReviewed(false);
    setPreviewMarkdown('');
    if (summaryOrigin === 'ai') {
      setSummary('');
      setSummaryOrigin('manual');
    }
  }

  function useSelectedExcerpt() {
    const textarea = previewRef.current;
    if (!textarea || !source) return;
    const offsets = normalizedTextareaOffsets(source.text);
    const start = offsets[textarea.selectionStart];
    const end = offsets[textarea.selectionEnd];
    const selected = start === undefined || end === undefined ? '' : source.text.slice(start, end);
    if (!selected) {
      setError('資料プレビューで抜粋する範囲を選択してください。');
      return;
    }
    updateExcerpt(selected);
    setError('');
  }

  function downloadOriginal() {
    const file = originalFileRef.current;
    if (!source || !file) return;
    const href = URL.createObjectURL(file);
    const anchor = document.createElement('a');
    anchor.href = href;
    anchor.download = safeDownloadName(source.filename);
    anchor.click();
    window.setTimeout(() => URL.revokeObjectURL(href), 1000);
  }

  async function requestSuggestion() {
    if (!suggest || !source || !excerptIsValid || !aiConsent || !topic.trim()) return;
    invalidateSuggestion();
    const versionAtStart = requestVersion.current;
    const controller = new AbortController();
    requestRef.current = controller;
    setIsSuggesting(true);
    setError('');
    try {
      const result = await suggest({ topic: topic.trim(), excerpt, title: title.trim() }, controller.signal);
      if (controller.signal.aborted || requestVersion.current !== versionAtStart) return;
      setSuggestion(result);
    } catch (cause) {
      if (!controller.signal.aborted && requestVersion.current === versionAtStart) {
        setError(cause instanceof Error ? cause.message : 'AIの提案を取得できませんでした。');
      }
    } finally {
      if (requestVersion.current === versionAtStart) {
        requestRef.current = null;
        setIsSuggesting(false);
      }
    }
  }

  function applySuggestion() {
    if (!suggestion) return;
    setSummary(suggestion);
    setSummaryOrigin('ai');
    setSuggestion('');
    setReviewed(false);
    setPreviewMarkdown('');
  }

  function buildPreview() {
    if (!source || !excerptIsValid) {
      setPreviewError('資料に含まれる抜粋を確認してください。');
      return;
    }
    try {
      const metadata = normalizeFieldMaterialMetadata({ title, version, locator, url: referenceUrl }, source);
      const nextMarkdown = insertFieldMaterialMarkdown(baseBody, summary, metadata, { reviewed });
      setPreviewMarkdown(nextMarkdown);
      setPreviewError('');
      setApplyMessage('');
    } catch (cause) {
      setPreviewMarkdown('');
      setPreviewError(cause instanceof Error ? cause.message : '変更案を作成できませんでした。');
    }
  }

  function applyPreview() {
    if (!previewMarkdown || bodyChanged || busy) return;
    const applied = onApply(baseBody, previewMarkdown);
    setApplyMessage(applied ? '変更案を作業中のMarkdownへ反映しました。' : '本文が更新されています。最新の本文で資料を読み込み直してください。');
    if (!applied) setPreviewMarkdown('');
  }

  return (
    <section className="rounded-xl border border-gray-200 bg-white shadow-sm" aria-label="現場資料の取り込み">
      <div className="border-b border-gray-200 px-4 py-3">
        <h2 className="font-semibold text-gray-900">現場資料の取り込み</h2>
        <p className="mt-1 text-xs text-gray-600">選んだファイルはこの画面内だけで扱います。抜粋以外の原文とカード本文をAIへ送りません。</p>
      </div>
      <div className="space-y-4 p-4 text-sm">
        <div className="flex flex-wrap items-center gap-2">
          <label className="inline-flex cursor-pointer items-center rounded-md border border-gray-300 bg-white px-3 py-2 text-xs font-medium text-gray-800 hover:bg-gray-50">
            ローカルのMDまたはTXTを選ぶ
            <input aria-label="現場資料ファイルを選ぶ" type="file" accept=".md,.txt,text/markdown,text/plain" onChange={handleFileChange} className="sr-only" disabled={busy} />
          </label>
          {source && <button type="button" onClick={downloadOriginal} className="rounded-md border border-gray-300 px-3 py-2 text-xs font-medium text-gray-800 hover:bg-gray-50">原本をダウンロード</button>}
          {source && <button type="button" onClick={() => resetDraft(null)} className="rounded-md px-2 py-2 text-xs text-gray-600 hover:bg-gray-100">資料を解除</button>}
        </div>

        {source && <div className="space-y-3">
          <dl className="grid grid-cols-[5rem_minmax(0,1fr)] gap-x-3 gap-y-1 rounded-lg bg-gray-50 px-3 py-2 text-xs">
            <dt className="text-gray-500">ファイル</dt><dd className="break-all text-gray-800">{source.filename}</dd>
            <dt className="text-gray-500">資料ID</dt><dd className="font-mono text-gray-800">local-sha256:{source.sha256.slice(0, 12)}</dd>
            <dt className="text-gray-500">SHA-256</dt><dd className="break-all font-mono text-gray-600">{source.sha256}</dd>
          </dl>
          <div>
            <label htmlFor="field-material-preview" className="mb-1 block text-xs font-medium text-gray-700">選んだ資料のプレビュー</label>
            <textarea id="field-material-preview" ref={previewRef} value={source.text} readOnly rows={5} className="w-full rounded-lg border border-gray-300 bg-gray-50 p-3 font-mono text-xs leading-5 text-gray-800" />
            <button type="button" onClick={useSelectedExcerpt} className="mt-2 rounded-md border border-gray-300 px-3 py-1.5 text-xs font-medium text-gray-700 hover:bg-gray-50">選択範囲を抜粋にする</button>
          </div>
          <div>
            <label htmlFor="field-material-excerpt" className="mb-1 block text-xs font-medium text-gray-700">抜粋（資料から正確に選択、最大2,000文字）</label>
            <textarea id="field-material-excerpt" value={excerpt} onChange={(event) => updateExcerpt(event.target.value)} rows={3} maxLength={6000} className="w-full rounded-lg border border-gray-300 p-3 font-mono text-xs leading-5" placeholder="プレビューで範囲を選択するか、資料と同じ文を入力" />
            <p className="mt-1 text-right text-[11px] text-gray-500">{excerptLength(excerpt)}/{MAX_FIELD_MATERIAL_EXCERPT_CHARS.toLocaleString('ja-JP')}文字 · {excerptIsValid ? '資料内で一致' : '資料内の完全一致を確認してください'}</p>
          </div>

          <details>
            <summary className="cursor-pointer text-xs font-medium text-gray-700">出典情報を入力</summary>
            <div className="mt-3 grid gap-3 sm:grid-cols-2">
              <label className="text-xs text-gray-700">資料名<input value={title} onChange={(event) => updateAttribution('title', event.target.value)} maxLength={160} className="mt-1 w-full rounded-md border border-gray-300 px-3 py-2 text-sm" /></label>
              <label className="text-xs text-gray-700">版<input value={version} onChange={(event) => updateAttribution('version', event.target.value)} maxLength={80} className="mt-1 w-full rounded-md border border-gray-300 px-3 py-2 text-sm" placeholder="例: 2026年版、改訂3" /></label>
              <label className="text-xs text-gray-700">ページ・項目などの場所<input value={locator} onChange={(event) => updateAttribution('locator', event.target.value)} maxLength={300} className="mt-1 w-full rounded-md border border-gray-300 px-3 py-2 text-sm" placeholder="例: 4ページ、点検表の行12" /></label>
              <label className="text-xs text-gray-700 sm:col-span-2">確認済みの参照URL（任意）<input value={referenceUrl} onChange={(event) => updateAttribution('url', event.target.value)} maxLength={2000} inputMode="url" className="mt-1 w-full rounded-md border border-gray-300 px-3 py-2 text-sm" placeholder="https://…" /></label>
            </div>
          </details>

          <div>
            <label htmlFor="field-material-summary" className="mb-1 block text-xs font-medium text-gray-700">要約案（手で編集）</label>
            <textarea id="field-material-summary" value={summary} onChange={(event) => { setSummary(event.target.value); setSummaryOrigin('manual'); setReviewed(false); setPreviewMarkdown(''); }} rows={3} className="w-full rounded-lg border border-gray-300 p-3 text-sm leading-5" placeholder="抜粋から確認できる手順や条件を要約" />
            <p className="mt-1 text-right text-[11px] text-gray-500">{excerptLength(summary)}/{MAX_FIELD_MATERIAL_SUMMARY_CHARS}文字</p>
          </div>

          {aiEnabled && <div className="rounded-lg border border-gray-200 bg-gray-50 p-3">
            <p className="text-xs font-semibold text-gray-800">AIで要約案を作る</p>
            <label htmlFor="field-material-topic" className="mb-1 mt-2 block text-xs text-gray-700">確認テーマ</label>
            <input id="field-material-topic" value={topic} onChange={(event) => updateTopic(event.target.value)} maxLength={200} className="w-full rounded-md border border-gray-300 bg-white px-3 py-2 text-sm" />
            <label className="mt-2 flex items-start gap-2 text-xs leading-5 text-gray-700"><input type="checkbox" checked={aiConsent} onChange={(event) => setAiConsent(event.target.checked)} className="mt-1" />選んだ抜粋と確認テーマをAIへ送ってよいことを確認した</label>
            <p className="mt-1 text-[11px] text-gray-500">送信する情報: 確認テーマ、資料名、選択した抜粋だけ。原本全体と作業中のカード本文は送信しません。</p>
            <p className="mt-1 text-[11px] text-gray-500">AI利用料金が発生する場合があります。</p>
            <button type="button" onClick={requestSuggestion} disabled={!aiConsent || !excerptIsValid || !topic.trim() || isSuggesting} className="mt-2 rounded-md border border-gray-300 bg-white px-3 py-1.5 text-xs font-medium text-gray-700 disabled:opacity-50">{isSuggesting ? '提案を作成中…' : '要約案を作る'}</button>
            {isSuggesting && <button type="button" onClick={invalidateSuggestion} className="ml-2 rounded-md px-3 py-1.5 text-xs text-gray-700 hover:bg-white">キャンセル</button>}
            {suggestion && <div className="mt-2 rounded-md border border-blue-200 bg-white p-3"><p className="whitespace-pre-wrap text-sm text-gray-800">{suggestion}</p><button type="button" onClick={applySuggestion} className="mt-2 rounded-md border border-blue-300 px-3 py-1.5 text-xs font-medium text-blue-900">要約欄へ反映</button></div>}
          </div>}

          <label className="flex items-start gap-2 text-xs leading-5 text-gray-700"><input type="checkbox" checked={reviewed} onChange={(event) => { setReviewed(event.target.checked); setPreviewMarkdown(''); }} className="mt-1" />要約案と資料の抜粋を確認した</label>
          <div className="flex flex-wrap gap-2">
            <button type="button" onClick={buildPreview} disabled={!reviewed || !excerptIsValid || !summary.trim() || excerptLength(summary) > MAX_FIELD_MATERIAL_SUMMARY_CHARS} className="rounded-md bg-blue-700 px-3 py-2 text-xs font-medium text-white hover:bg-blue-800 disabled:cursor-not-allowed disabled:opacity-50">変更案をプレビュー</button>
            <button type="button" onClick={applyPreview} disabled={!previewMarkdown || bodyChanged || busy} className="rounded-md border border-blue-700 px-3 py-2 text-xs font-medium text-blue-800 hover:bg-blue-50 disabled:cursor-not-allowed disabled:opacity-50">作業中のMarkdownに反映</button>
          </div>
          {bodyChanged && <p role="status" className="text-xs text-amber-800">作業中の本文が資料を読み込んだ後に変わりました。安全のため、最新の本文で資料を読み込み直してください。</p>}
          {previewError && <p role="alert" className="text-xs text-red-700">{previewError}</p>}
          {applyMessage && <p role="status" className="text-xs text-gray-700">{applyMessage}</p>}
          {previewMarkdown && <div>
            <h3 className="mb-1 text-xs font-semibold text-gray-800">変更差分</h3>
            <KnowledgeLineDiff before={baseBody} after={previewMarkdown} />
            <details className="mt-2">
              <summary className="cursor-pointer text-xs font-medium text-gray-700">変更後のMarkdown全文を表示</summary>
              <textarea aria-label="変更後のMarkdownプレビュー" value={previewMarkdown} readOnly rows={10} className="mt-2 w-full rounded-lg border border-gray-300 bg-gray-50 p-3 font-mono text-xs leading-5 text-gray-800" />
            </details>
          </div>}
        </div>}
        {error && <p role="alert" className="text-xs text-red-700">{error}</p>}
      </div>
    </section>
  );
}
