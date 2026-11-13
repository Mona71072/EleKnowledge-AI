'use client';

import type { ResearchAnswer, ResearchKnowhowMatch } from '@/lib/knowledge-research.mjs';
import { KNOWHOW_NOT_OFFICIAL_NOTICE, knowhowStatusLabel, modelFitNotice, scopeUnverifiedNotice } from '@/lib/knowledge-senpai-model-fit.mjs';
import { knowhowCardAnchor } from '@/lib/citation-links.mjs';
import { sectionsToMarkdown, splitKnowhowCardBody } from '@/lib/knowhow-card-view.mjs';
import { SenpaiMarkdown } from './SenpaiMarkdown';

const NO_REFS: ReadonlySet<string> = new Set();

const scopeLabels: Record<string, string> = {
  conditions: '対象条件', control_methods: '制御方式', door_families: 'ドアの種類', door_types: 'ドア型式',
  excludes: '適用除外', guide_systems: 'ガイド方式', lists_model_label: '元記録の機種', machine_room: '機械室',
  may_apply_to: '適用可能性（未確認）', model_abbreviations: '機種略称', observed_on: '確認された対象',
  product_lines: '製品系列', scope_note: '対象範囲の補足',
  scope_status: '適用範囲の確認', scope_verified_by: '確認者', scope_verified_at: '確認日',
};
// 利用者の判断に要る対象範囲。ここにない項目（確認者・元記録の機種・英字キーのまま）は編集者向けの開閉に回す。
const READER_SCOPE_KEYS: readonly string[] = [
  'model_abbreviations', 'product_lines', 'machine_room', 'guide_systems', 'door_families', 'door_types',
  'control_methods', 'conditions', 'excludes', 'may_apply_to', 'observed_on', 'scope_note',
];
const refLabels: Record<string, string> = {
  list_item_id: 'Lists項目', onenote_id: 'OneNoteページ', source_id: '出典ID', document_number: '資料番号',
  kb_filename: 'KB資料名', kb_verify_status: 'KB確認状況', page_role: 'ページの役割', law_id: '法令ID',
  law_title: '法令名', locator: '参照箇所', knowhow_id: 'ノウハウの記録', origin: '経路',
};

// Unknown keys fall back to the raw key so a label never renders as "undefined".
function scopeLabel(key: string) {
  return scopeLabels[key] ?? key;
}

function scopeValue(key: string, value: string | string[]) {
  if (key === 'scope_status') return value === 'verified' ? '担当者確認済み' : '未確認';
  return (Array.isArray(value) ? value.join('、') : value) || '未記載';
}

function hasValue(value: string | string[]) {
  return Array.isArray(value) ? value.length > 0 : Boolean(value);
}

function ScopeList({ entries, className }: { entries: Array<[string, string | string[]]>; className: string }) {
  if (entries.length === 0) return null;
  return (
    <dl className={`grid grid-cols-[6rem_minmax(0,1fr)] gap-x-2 gap-y-1 break-words text-gray-700 ${className}`}>
      {entries.map(([key, value]) => <div key={key} className="contents"><dt className="text-gray-500">{scopeLabel(key)}</dt><dd>{scopeValue(key, value)}</dd></div>)}
    </dl>
  );
}

function CardMarkdown({ markdown, anchorPrefix }: { markdown: string; anchorPrefix: string }) {
  return <SenpaiMarkdown markdown={markdown} knownRefs={NO_REFS} anchorPrefix={anchorPrefix} variant="card" className="mt-3" />;
}

function EditorDetails({ match, markdown, anchorPrefix, extraScope }: {
  match: ResearchKnowhowMatch; markdown: string; anchorPrefix: string; extraScope: Array<[string, string | string[]]>;
}) {
  return (
    <details className="mt-4 rounded-lg border border-gray-200 bg-gray-50 p-2">
      <summary className="cursor-pointer font-medium text-gray-600">出典・元情報（編集者向け）</summary>
      {markdown && <CardMarkdown markdown={markdown} anchorPrefix={`${anchorPrefix}-editor`} />}
      <dl className="mt-3 grid grid-cols-[6rem_minmax(0,1fr)] gap-x-2 gap-y-1 break-words text-gray-700">
        <dt className="text-gray-500">ノウハウID</dt><dd>{match.knowledgeId}</dd>
        <dt className="text-gray-500">版</dt><dd>v{match.cardVersion}</dd>
        {extraScope.map(([key, value]) => <div key={key} className="contents"><dt className="text-gray-500">{scopeLabel(key)}</dt><dd>{scopeValue(key, value)}</dd></div>)}
      </dl>
      {match.sourceRefs.length > 0 && (
        <ul className="mt-2 space-y-2 border-t border-gray-200 pt-2">
          {match.sourceRefs.map((ref, index) => <li key={index} className="break-words">
            {Object.entries(ref).filter(([key]) => key !== 'ref_type').map(([key, value]) => <p key={key}>{refLabels[key] ?? key}: {value}</p>)}
          </li>)}
        </ul>
      )}
      <p className="mt-2 break-all font-mono text-[10px] text-gray-500">本文の識別値: {match.sha256}</p>
    </details>
  );
}

function KnowhowCard({ match, selectedModel, anchorId }: { match: ResearchKnowhowMatch; selectedModel?: string; anchorId: string }) {
  const view = splitKnowhowCardBody(match.body);
  const scopeEntries = Object.entries(match.modelScope ?? {});
  const readerScope = READER_SCOPE_KEYS.flatMap((key) => {
    const value = match.modelScope?.[key];
    return value !== undefined && hasValue(value) ? [[key, value] as [string, string | string[]]] : [];
  });
  const extraScope = scopeEntries.filter(([key]) => !READER_SCOPE_KEYS.includes(key));
  const fitNotice = modelFitNotice(match, selectedModel);
  const unverifiedNotice = scopeUnverifiedNotice(match);
  return (
    <li className="rounded-lg bg-white p-3 text-xs text-gray-800">
      <div className="flex flex-wrap items-center gap-2">
        <span className="text-sm font-semibold">{match.title}</span>
        <span className="text-amber-700">{knowhowStatusLabel(match)}</span>
        <span className="text-gray-500">参照用のみ</span>
      </div>
      {fitNotice && <p role="note" className="mt-2 text-amber-700">{fitNotice}</p>}
      {unverifiedNotice && <p role="note" className="mt-1 text-gray-600">{unverifiedNotice}</p>}
      <details className="mt-2">
        <summary id={anchorId} className="cursor-pointer font-medium text-gray-600">内容と適用条件を見る</summary>
        <ScopeList entries={readerScope} className="mt-2" />
        {view.readerSections.length > 0 && <CardMarkdown markdown={sectionsToMarkdown(view.readerSections)} anchorPrefix={`card-${match.knowledgeId}`} />}
        <EditorDetails match={match} markdown={sectionsToMarkdown(view.editorSections)} anchorPrefix={`card-${match.knowledgeId}`} extraScope={extraScope} />
      </details>
    </li>
  );
}

/** 回答が参照した先輩ノウハウのカード。本文は Markdown として読みやすく表示し、出どころは入れ子の開閉に分ける。 */
export function KnowhowReferences({ answer, selectedModel, anchorPrefix }: { answer: ResearchAnswer; selectedModel?: string; anchorPrefix: string }) {
  const knowhow = answer.knowhow;
  if (!knowhow) return null;
  if (knowhow.status === 'not_found') {
    return <p className="text-xs leading-5 text-gray-500">参照できる先輩ノウハウは見つかりませんでした。この回答は技術KBの検索結果を確認してください。</p>;
  }
  return (
    <section aria-label="参照した先輩ノウハウ" className="rounded-xl bg-gray-50 p-3">
      <h5 className="text-xs font-medium text-gray-700">参照した先輩ノウハウ</h5>
      <p className="mt-1 text-xs leading-5 text-gray-500">参考候補です。{KNOWHOW_NOT_OFFICIAL_NOTICE}</p>
      <ul className="mt-2 space-y-3">
        {knowhow.matches.map((match) => (
          <KnowhowCard key={`${match.knowledgeId}-${match.cardVersion}`} match={match} selectedModel={selectedModel}
            anchorId={knowhowCardAnchor(anchorPrefix, match.knowledgeId)} />
        ))}
      </ul>
      {knowhow.searchTerms.length > 0 && <p className="mt-2 text-xs text-gray-700">技術KB検索へ加えた手掛かり: {knowhow.searchTerms.join('、')}</p>}
    </section>
  );
}
