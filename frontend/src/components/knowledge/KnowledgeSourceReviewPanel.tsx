'use client';

import { useMemo, useRef, useState, type ChangeEvent } from 'react';
import {
  getReviewSources,
  resolveReviewSource,
  readReviewSourceSnapshot,
  MAX_SOURCE_SNAPSHOT_BYTES,
  type KnowledgeReviewSource,
  type KnowledgeSourceReviewInput,
  type KnowledgeSourceReviewRecord,
} from '@/lib/knowledge-source-review.mjs';

type ReviewOutcome = KnowledgeSourceReviewInput['outcome'];

type Props = {
  metadata: Record<string, unknown>;
  records: readonly KnowledgeSourceReviewRecord[];
  revision: number;
  onRecord: (input: KnowledgeSourceReviewInput) => boolean;
};

type LoadedExcerpt = { text: string; capturedOn: string; sourceLabel: string };

const OUTCOMES: { value: ReviewOutcome; label: string }[] = [
  { value: 'supports', label: 'カードの内容を支持する' },
  { value: 'conditions_differ', label: '適用条件が異なる' },
  { value: 'conflict', label: '内容に食い違いがある' },
  { value: 'insufficient', label: '根拠として不十分' },
];

function sourceKindLabel(source: KnowledgeReviewSource): string {
  if (source.kind === 'lists') return 'Microsoft Lists';
  if (source.kind === 'onenote') return 'OneNote';
  return '技術KB';
}

export function KnowledgeSourceReviewPanel({ metadata, records, revision, onRecord }: Props) {
  const sources = useMemo(() => getReviewSources(metadata), [metadata]);
  const [selectedSourceKey, setSelectedSourceKey] = useState(sources[0] ? `${sources[0].kind}:${sources[0].id}` : '');
  const [enteredSourceId, setEnteredSourceId] = useState('');
  const [loadedExcerpt, setLoadedExcerpt] = useState<LoadedExcerpt | null>(null);
  const [reviewMethod, setReviewMethod] = useState<KnowledgeSourceReviewInput['method']>('opened_original');
  const [pasteText, setPasteText] = useState('');
  const [capturedOn, setCapturedOn] = useState('');
  const [locator, setLocator] = useState('');
  const [outcome, setOutcome] = useState<ReviewOutcome | ''>('');
  const [note, setNote] = useState('');
  const [error, setError] = useState('');
  const [isReading, setIsReading] = useState(false);
  const [successRevision, setSuccessRevision] = useState<number | null>(null);
  const readToken = useRef(0);
  const selectedSource = sources.find((source) => `${source.kind}:${source.id}` === selectedSourceKey) ?? sources[0];
  const needsTypedId = selectedSource?.id === 'manual' && (selectedSource.kind === 'lists' || selectedSource.kind === 'onenote');
  const effectiveSource = selectedSource ? resolveReviewSource(selectedSource, needsTypedId ? enteredSourceId : undefined) : null;
  const navigationOnly = effectiveSource?.pageRole === 'index' || effectiveSource?.pageRole === 'empty_or_attachment_only';

  function parseSnapshot(markdown: string, source: KnowledgeReviewSource, filename: string, token: number) {
    if (token !== readToken.current) return;
    try {
      const parsed = readReviewSourceSnapshot(markdown, source);
      setLoadedExcerpt({ ...parsed, sourceLabel: filename });
      setReviewMethod('snapshot');
      setCapturedOn(parsed.capturedOn || '');
      setError('');
    } catch (loadError) {
      setLoadedExcerpt(null);
      setError(loadError instanceof Error ? loadError.message : 'Markdownを読み込めませんでした。');
    } finally {
      setIsReading(false);
    }
  }

  async function handleFileChange(event: ChangeEvent<HTMLInputElement>) {
    const file = event.currentTarget.files?.[0];
    event.currentTarget.value = '';
    if (!file || !selectedSource) return;
    if (selectedSource.kind === 'technical') {
      setError('ローカルMarkdownの取り込みはListsまたはOneNote参照に限られます。');
      return;
    }
    if (!effectiveSource) {
      setError(selectedSource.kind === 'lists' ? 'Listsの項目番号を入力してください。' : 'OneNoteのページIDを入力してください。');
      return;
    }
    const token = ++readToken.current;
    setIsReading(true);
    setError('');
    setLoadedExcerpt(null);
    setCapturedOn('');
    if (file.size > MAX_SOURCE_SNAPSHOT_BYTES) {
      setIsReading(false);
      setError(`ファイルは${Math.floor(MAX_SOURCE_SNAPSHOT_BYTES / 1024)}KB以下にしてください。`);
      return;
    }
    if (!/\.(?:md|markdown)$/iu.test(file.name)) {
      setIsReading(false);
      setError('対応するMarkdownファイル（.md）を選んでください。');
      return;
    }
    try {
      parseSnapshot(await file.text(), effectiveSource, file.name, token);
    } catch {
      if (token === readToken.current) {
        setIsReading(false);
        setError('選んだファイルを読み込めませんでした。');
      }
    }
  }

  function loadPastedSnapshot() {
    if (!selectedSource || selectedSource.kind === 'technical') return;
    if (!effectiveSource) {
      setError(selectedSource.kind === 'lists' ? 'Listsの項目番号を入力してください。' : 'OneNoteのページIDを入力してください。');
      return;
    }
    const token = ++readToken.current;
    setIsReading(false);
    setLoadedExcerpt(null);
    setCapturedOn('');
    setError('');
    if (new TextEncoder().encode(pasteText).byteLength > MAX_SOURCE_SNAPSHOT_BYTES) {
      setError(`貼り付ける内容は${Math.floor(MAX_SOURCE_SNAPSHOT_BYTES / 1024)}KB以下にしてください。`);
      return;
    }
    parseSnapshot(pasteText, effectiveSource, '貼り付けたMarkdown', token);
  }

  function recordReview(method: KnowledgeSourceReviewInput['method']) {
    if (!selectedSource || !effectiveSource) {
      setError(selectedSource?.kind === 'lists' ? 'Listsの項目番号を入力してください。' : '有効な参照先IDを入力してください。');
      return;
    }
    if (!outcome) {
      setError('カードとの照合結果を選んでください。');
      return;
    }
    if (method === 'snapshot' && !loadedExcerpt) {
      setError('参照先が一致するスナップショットを先に読み込んでください。');
      return;
    }
    const cleanNote = note.trim();
    const cleanLocator = locator.trim();
    if (!cleanNote) {
      setError('確認内容を短く記録してください。');
      return;
    }
    if (!cleanLocator) {
      setError('確認したファイル名またはページ・項目を記録してください。');
      return;
    }
    const sourceDate = method === 'snapshot' ? loadedExcerpt?.capturedOn : capturedOn;
    const succeeded = onRecord({
      source: effectiveSource,
      method,
      ...(sourceDate ? { capturedOn: sourceDate } : {}),
      locator: cleanLocator,
      outcome,
      note: cleanNote,
      recordedAt: new Date().toISOString(),
    });
    if (succeeded) {
      setError('');
      setNote('');
      setSuccessRevision(revision);
    } else {
      setError('照合記録を保存できませんでした。入力内容を確認してください。');
    }
  }

  return (
    <section className="rounded-xl border border-gray-200 bg-white shadow-sm" aria-label="技術資料との照合">
      <div className="border-b border-gray-200 px-4 py-3">
        <h2 className="font-semibold text-gray-900">技術資料との照合</h2>
        <p className="mt-1 text-xs text-gray-600">Lists・OneNote・技術KBの原資料を確認し、カードとの関係を記録します。記録は確認者の判断で、承認を意味しません。</p>
      </div>
      <div className="space-y-4 p-4 text-sm">
        {sources.length === 0 ? (
          <p className="text-gray-600">このカードに照合できる資料の参照先はありません。</p>
        ) : (
          <>
            <div>
              <label htmlFor="review-source" className="mb-1 block text-xs font-medium text-gray-700">照合する参照先</label>
              <select id="review-source" value={selectedSource ? `${selectedSource.kind}:${selectedSource.id}` : ''} onChange={(event) => {
                readToken.current += 1;
                setIsReading(false);
                setSelectedSourceKey(event.target.value);
                setEnteredSourceId('');
                setLoadedExcerpt(null);
                setReviewMethod('opened_original');
                setPasteText('');
                setLocator('');
                setCapturedOn('');
                setOutcome('');
                setNote('');
                setError('');
                setSuccessRevision(null);
              }} className="w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-gray-900">
                {sources.map((source) => <option key={`${source.kind}:${source.id}`} value={`${source.kind}:${source.id}`}>{sourceKindLabel(source)} · {source.label}</option>)}
              </select>
            </div>

            {needsTypedId && selectedSource && (
              <div>
                <label htmlFor="review-source-id" className="mb-1 block text-xs font-medium text-gray-700">追加する参照先ID</label>
                <input id="review-source-id" value={enteredSourceId} onChange={(event) => {
                  readToken.current += 1;
                  setIsReading(false);
                  setEnteredSourceId(event.target.value);
                  setLoadedExcerpt(null);
                  setReviewMethod('opened_original');
                  setPasteText('');
                  setLocator('');
                  setCapturedOn('');
                  setOutcome('');
                  setNote('');
                  setError('');
                  setSuccessRevision(null);
                }} className="w-full max-w-full rounded-lg border border-gray-300 px-3 py-2" placeholder={selectedSource.kind === 'lists' ? 'Listsの項目番号' : 'OneNoteのページID'} />
              </div>
            )}

            {navigationOnly && <p className="rounded-lg bg-amber-50 p-3 text-xs leading-5 text-amber-950">索引・添付ページは参照用です。本文があるページを開き、その出典で照合してください。</p>}
            {effectiveSource?.pageRole === 'hybrid' && <p className="text-xs leading-5 text-gray-700">目次と本文があるページです。カードに該当する本文の箇所を記録してください。</p>}

            {selectedSource?.kind !== 'technical' && <div className="rounded-lg border border-gray-200 bg-gray-50 p-3">
              <p className="font-medium text-gray-900">資料の内容を取り込む</p>
              <p className="mt-1 text-xs leading-5 text-gray-600">ListsまたはOneNoteの参照先について、選んだMarkdownだけをこの画面で読みます。通信や共有は行いません。参照先IDが一致する項目だけを表示します。</p>
              <label className="mt-3 inline-flex cursor-pointer items-center rounded-md border border-gray-300 bg-white px-3 py-2 text-xs font-medium text-gray-800 hover:bg-gray-100">
                ローカルのMarkdownを選ぶ
                <input type="file" accept=".md,.markdown,text/markdown,text/plain" onChange={handleFileChange} className="sr-only" aria-label="照合するMarkdownファイルを選ぶ" />
              </label>
              <label htmlFor="review-paste" className="mb-1 mt-3 block text-xs font-medium text-gray-700">ファイルがない場合はMarkdownを貼り付け</label>
              <textarea id="review-paste" value={pasteText} onChange={(event) => setPasteText(event.target.value)} rows={4} className="w-full rounded-lg border border-gray-300 bg-white px-3 py-2 font-mono text-xs" placeholder="参照先に対応するMarkdownを貼り付け" />
              <button type="button" onClick={loadPastedSnapshot} className="mt-2 rounded-md border border-gray-300 bg-white px-3 py-2 text-xs font-medium text-gray-800 hover:bg-gray-100">貼り付けたMarkdownを照合</button>
            </div>}

            {loadedExcerpt && (
              <div role="region" className="rounded-lg border border-blue-200 bg-blue-50 p-3" aria-label="読み込んだ資料の抜粋">
                <div className="flex flex-wrap justify-between gap-2 text-xs text-blue-950">
                  <span className="font-semibold">資料の抜粋（表示のみ）</span>
                  <span>スナップショット日: {loadedExcerpt.capturedOn || '記録なし'}</span>
                </div>
                <p className="mt-1 text-xs text-blue-900">{loadedExcerpt.sourceLabel}</p>
                <pre className="mt-2 max-h-64 overflow-auto whitespace-pre-wrap break-words rounded bg-white p-3 font-sans text-xs leading-5 text-gray-900">{loadedExcerpt.text}</pre>
              </div>
            )}

            <div className="grid gap-3 sm:grid-cols-2">
              <div>
                <label htmlFor="review-method" className="mb-1 block text-xs font-medium text-gray-700">確認方法</label>
                <select id="review-method" value={reviewMethod} onChange={(event) => {
                  const method = event.target.value as KnowledgeSourceReviewInput['method'];
                  setReviewMethod(method);
                  if (method === 'opened_original') {
                    setLoadedExcerpt(null);
                    setCapturedOn('');
                  }
                }} className="w-full max-w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-gray-900">
                  {loadedExcerpt && <option value="snapshot">読み込んだスナップショットを確認</option>}
                  <option value="opened_original">原資料を別途開いて確認</option>
                </select>
              </div>
              <div>
                <label htmlFor="review-captured-on" className="mb-1 block text-xs font-medium text-gray-700">資料の日付</label>
                {reviewMethod === 'snapshot' ? <p id="review-captured-on" className="rounded-lg border border-gray-200 bg-gray-50 px-3 py-2 text-gray-700">{capturedOn || '記録なし'}</p> : <input id="review-captured-on" type="date" value={capturedOn} onChange={(event) => setCapturedOn(event.target.value)} className="w-full max-w-full rounded-lg border border-gray-300 px-3 py-2" />}
              </div>
            </div>
            <div>
              <label htmlFor="review-locator" className="mb-1 block text-xs font-medium text-gray-700">ファイル名、ページ名、または項目ID</label>
              <input id="review-locator" value={locator} onChange={(event) => setLocator(event.target.value)} maxLength={300} className="w-full max-w-full rounded-lg border border-gray-300 px-3 py-2" placeholder={selectedSource?.kind === 'lists' ? '例: 項目123の対策欄' : selectedSource?.kind === 'onenote' ? '例: ページ名・確認した節' : '例: 資料番号・改訂版・ページ'} />
            </div>
            <div>
              <label htmlFor="review-outcome" className="mb-1 block text-xs font-medium text-gray-700">カードとの照合結果</label>
              <select id="review-outcome" value={outcome} onChange={(event) => setOutcome(event.target.value as ReviewOutcome | '')} className="w-full max-w-full rounded-lg border border-gray-300 bg-white px-3 py-2">
                <option value="">照合結果を選択してください</option>
                {OUTCOMES.filter((item) => !navigationOnly || item.value === 'insufficient').map((item) => <option key={item.value} value={item.value}>{item.label}</option>)}
              </select>
            </div>
            <div>
              <label htmlFor="review-note" className="mb-1 block text-xs font-medium text-gray-700">確認メモ</label>
              <textarea id="review-note" value={note} onChange={(event) => setNote(event.target.value)} rows={3} maxLength={500} className="w-full rounded-lg border border-gray-300 px-3 py-2" placeholder="確認した事実や条件の違いを簡潔に記録" />
              <p className="mt-1 text-right text-[11px] text-gray-500">{note.length}/500</p>
            </div>
            {isReading && <p role="status" className="text-sm text-blue-800">選んだファイルを確認しています…</p>}
            {successRevision !== null && <p role="status" className="text-sm text-green-800">照合記録を作業版 {successRevision} に記録しました。</p>}
            {error && <p role="alert" className="text-sm text-red-700">{error}</p>}
            <div className="flex flex-wrap gap-2">
              <button type="button" disabled={isReading} onClick={() => recordReview(reviewMethod)} className="rounded-md bg-blue-700 px-4 py-2 font-medium text-white hover:bg-blue-800 disabled:cursor-not-allowed disabled:opacity-50">照合記録を追加</button>
            </div>
          </>
        )}

        <div>
          <h3 className="mb-2 text-xs font-semibold text-gray-700">このカードの照合記録</h3>
          {records.length === 0 ? <p className="text-xs text-gray-500">照合記録はまだありません。</p> : (
            <ol className="space-y-2">
              {records.map((record, index) => (
                <li key={`${record.revision}-${record.recordedAt}-${index}`} className="rounded-lg border border-gray-200 px-3 py-2">
                  <div className="flex flex-wrap justify-between gap-1">
                    <p className="font-medium text-gray-900">{record.source.label} · {OUTCOMES.find((item) => item.value === record.outcome)?.label ?? record.outcome}</p>
                    <p className="text-xs text-gray-500">作業版 {record.revision} · {record.recordedAt}</p>
                  </div>
                  <p className="mt-1 text-xs text-gray-600">{record.method === 'snapshot' ? 'スナップショット' : '原資料を確認'} · {record.locator}{record.capturedOn ? ` · 資料日 ${record.capturedOn}` : ''}</p>
                  <p className="mt-2 whitespace-pre-wrap text-sm text-gray-800">{record.note}</p>
                </li>
              ))}
            </ol>
          )}
          <p className="mt-2 text-[11px] text-gray-500">現在の作業版: {revision} · 照合の記録はカード内容の更新・承認を自動では行いません。</p>
        </div>
      </div>
    </section>
  );
}
