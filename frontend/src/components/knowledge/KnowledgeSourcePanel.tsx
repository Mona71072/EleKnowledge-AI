'use client';

type Metadata = Record<string, unknown>;
type SourceRef = Record<string, unknown>;

type Props = {
  metadata: Metadata;
  kbStatus: 'unverified' | 'reviewed' | 'conflict';
};

function textValue(value: unknown): string {
  if (typeof value === 'string' || typeof value === 'number' || typeof value === 'boolean') return String(value);
  if (Array.isArray(value)) return value.map(textValue).filter(Boolean).join('、');
  if (value && typeof value === 'object') return JSON.stringify(value, null, 2);
  return '—';
}

function displayValue(value: unknown): string {
  const text = textValue(value);
  return text.trim() ? text : '—';
}

function objectRows(value: unknown): SourceRef[] {
  return Array.isArray(value) ? value.filter((row): row is SourceRef => Boolean(row && typeof row === 'object' && !Array.isArray(row))) : [];
}

function sourceLabel(ref: SourceRef): string {
  const kind = ref.ref_type;
  if (kind === 'lists_item') return `Lists §${displayValue(ref.list_item_id)}`;
  if (kind === 'onenote_page') return `OneNote ${displayValue(ref.onenote_id)}`;
  if (kind === 'kb_document') return `KB ${displayValue(ref.document_number)}`;
  if (kind === 'law_rag') return `法令RAG ${displayValue(ref.law_title || ref.law_id)}`;
  if (kind === 'draft_record') return `照合用写し ${displayValue(ref.record_id)}`;
  return `参照元 ${displayValue(kind)}`;
}

function statusLabel(status: string): string {
  if (status === 'content_reviewed') return 'カード上で本文確認済み';
  if (status === 'catalog_matched') return 'カタログ一致（本文未確認）';
  if (status === 'catalog_ambiguous') return '候補複数';
  if (status === 'not_in_catalog') return 'カタログ未収載';
  return '未確認';
}

export function KnowledgeSourcePanel({ metadata, kbStatus }: Props) {
  const refs = objectRows(metadata.source_refs);
  const evidenceSources = objectRows(metadata.evidence_sources);
  const kbRefs = refs.filter((ref) => ref.ref_type === 'kb_document');
  const identity = [metadata.knowledge_id, metadata.record_id].filter((value) => typeof value === 'string' && value.trim()).join(' / ');
  const version = metadata.card_version ?? metadata.record_version;
  const scope = metadata.model_scope;

  return (
    <section className="rounded-xl border border-gray-200 bg-white shadow-sm" aria-label="原版と出典">
      <div className="border-b border-gray-200 px-4 py-3">
        <h2 className="font-semibold text-gray-900">原版と出典</h2>
        <p className="mt-1 text-xs text-gray-500">ファイルを選んだ時点の情報です。共有や承認の状態には使いません。</p>
      </div>
      <div className="space-y-4 p-4 text-sm">
        <dl className="grid grid-cols-[6rem_minmax(0,1fr)] gap-x-3 gap-y-2">
          <dt className="text-gray-500">ID</dt><dd className="break-words text-gray-900">{identity || '—'}</dd>
          <dt className="text-gray-500">版</dt><dd className="text-gray-900">{displayValue(version)}</dd>
          <dt className="text-gray-500">種別</dt><dd className="break-words text-gray-900">{displayValue(metadata.kind || metadata.record_type)}</dd>
          <dt className="text-gray-500">原文状態</dt><dd className="text-gray-900">{displayValue(metadata.status)}</dd>
          <dt className="text-gray-500">対象条件</dt><dd className="whitespace-pre-wrap break-words text-gray-900">{displayValue(scope)}</dd>
        </dl>

        <div>
          <h3 className="mb-2 text-xs font-semibold uppercase tracking-wide text-gray-500">Markdownに記録された出典</h3>
          {refs.length || evidenceSources.length ? (
            <div className="space-y-3">
              {refs.length > 0 && <ul className="space-y-2">
              {refs.map((ref, index) => (
                <li key={`${String(ref.ref_type)}-${index}`} className="rounded-lg bg-gray-50 px-3 py-2">
                  <div className="font-medium text-gray-900">{sourceLabel(ref)}</div>
                  {ref.ref_type === 'kb_document' && (
                    <div className="mt-1 text-xs text-gray-600">
                      {displayValue(ref.kb_filename)} · {statusLabel(String(ref.kb_verify_status || 'pending'))}
                    </div>
                  )}
                  {ref.ref_type === 'kb_document' && typeof ref.summary_from_kb === 'string' && ref.summary_from_kb.trim() && (
                    <p className="mt-2 whitespace-pre-wrap text-xs text-gray-700">{ref.summary_from_kb}</p>
                  )}
                </li>
              ))}
              </ul>}
              {evidenceSources.length > 0 && (
                <div>
                  <h4 className="mb-2 text-xs font-semibold text-gray-600">根拠記録</h4>
                  <ul className="space-y-2">
                    {evidenceSources.map((source, index) => (
                      <li key={`${String(source.source_id)}-${index}`} className="rounded-lg border border-gray-200 px-3 py-2">
                        <p className="font-medium text-gray-900">{displayValue(source.title || source.source_id)}</p>
                        <p className="mt-1 text-xs text-gray-600">{displayValue(source.source_type)} · {displayValue(source.accessed_at)}</p>
                        {Boolean(source.source_id && source.title) && <p className="mt-1 break-all font-mono text-[11px] text-gray-500">{String(source.source_id)}</p>}
                        {source.supports !== undefined && <p className="mt-2 whitespace-pre-wrap text-xs leading-5 text-gray-700">根拠: {displayValue(source.supports)}</p>}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          ) : <p className="text-gray-500">出典・根拠記録はありません。</p>}
        </div>

        <div className={`rounded-lg border px-3 py-2 text-xs ${kbStatus === 'reviewed' ? 'border-green-200 bg-green-50 text-green-900' : kbStatus === 'conflict' ? 'border-red-200 bg-red-50 text-red-900' : 'border-amber-200 bg-amber-50 text-amber-900'}`}>
          <p className="font-semibold">今回のKB確認: {kbStatus === 'reviewed' ? '担当者が本文を手動確認' : kbStatus === 'conflict' ? '食い違いあり' : '未確認'}</p>
          {kbRefs.length > 0 && <p className="mt-1">カード側の状態: {kbRefs.map((ref) => statusLabel(String(ref.kb_verify_status || 'pending'))).join(' / ')}</p>}
          <p className="mt-1">この画面はKBを検索・取得していません。</p>
        </div>
      </div>
    </section>
  );
}
