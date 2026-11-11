'use client';

import Link from 'next/link';
import type { SenpaiChatLane, SenpaiChatTurn } from '@/lib/knowledge-senpai-chat.mjs';
import { modelFitNotice } from '@/lib/knowledge-senpai-model-fit.mjs';
import { SenpaiMarkdown } from './SenpaiMarkdown';
import { buildChatSessionHref } from '@/lib/chat-session-link.mjs';
import {
  researchSourceHref,
  type KnowledgeResearchMode,
  type ResearchCitationSource,
} from '@/lib/knowledge-research.mjs';

const NO_REFS: ReadonlySet<string> = new Set();

// 旧来の2レーン（技術KB・法令KB）表示。新しい画面と同じ控えめな見た目で、機能は変えない。

function sourceTitle(source: ResearchCitationSource, mode: KnowledgeResearchMode) {
  return mode === 'law'
    ? source.lawCitation?.lawTitle || source.title || source.documentName || '法令資料'
    : source.title || source.documentName || '技術資料';
}

const scopeLabels: Record<string, string> = {
  conditions: '対象条件', control_methods: '制御方式', door_families: 'ドアの種類', door_types: 'ドア型式',
  excludes: '適用除外', guide_systems: 'ガイド方式', lists_model_label: '元記録の機種', machine_room: '機械室',
  may_apply_to: '適用可能性（未確認）', model_abbreviations: '機種略称', observed_on: '確認された対象',
  product_lines: '製品系列', scope_note: '対象範囲の補足',
  scope_status: '適用範囲の確認', scope_verified_by: '確認者', scope_verified_at: '確認日',
};
const refLabels: Record<string, string> = {
  list_item_id: 'Lists項目', onenote_id: 'OneNoteページ', source_id: '出典ID', document_number: '資料番号',
  kb_filename: 'KB資料名', kb_verify_status: 'KB確認状況', page_role: 'ページの役割', law_id: '法令ID',
  law_title: '法令名', locator: '参照箇所', knowhow_id: 'ノウハウの記録', origin: '経路',
};

// Unknown keys fall back to the raw key so a label never renders as "undefined".
function scopeLabel(key: string) {
  return scopeLabels[key] ?? key;
}

function refLabel(key: string) {
  return refLabels[key] ?? key;
}

function scopeValue(key: string, value: string | string[]) {
  if (key === 'scope_status') return value === 'verified' ? '担当者確認済み' : '未確認';
  return (Array.isArray(value) ? value.join('、') : value) || '未記載';
}

function KnowhowReferences({ answer, selectedModel }: { answer: import('@/lib/knowledge-research.mjs').ResearchAnswer; selectedModel?: string }) {
  const knowhow = answer.knowhow;
  if (!knowhow) return null;
  if (knowhow.status === 'not_found') {
    return <p className="text-xs leading-5 text-gray-500">参照できるノウハウMarkdownは見つかりませんでした。この回答は技術KBの検索結果を確認してください。</p>;
  }
  return (
    <section aria-label="参照したノウハウMarkdown" className="rounded-xl bg-gray-50 p-3">
      <h5 className="text-xs font-medium text-gray-700">参照したノウハウMarkdown</h5>
      <p className="mt-1 text-xs leading-5 text-gray-500">参考候補です。技術的な根拠や承認を示しません。</p>
      <ul className="mt-2 space-y-3">
        {knowhow.matches.map((match) => (
          <li key={`${match.knowledgeId}-${match.cardVersion}`} className="rounded-lg bg-white p-3 text-xs text-gray-800">
            <div className="flex flex-wrap items-center gap-2">
              <span className="font-semibold">{match.title}</span>
              <span>v{match.cardVersion}</span>
              <span className="text-amber-700">{match.status === 'draft' ? '未承認（下書き）' : '承認済みカード・参照用のみ'}</span>
              <span className="text-gray-500">参照用のみ</span>
            </div>
            {modelFitNotice(match, selectedModel) && <p role="note" className="mt-2 text-amber-700">{modelFitNotice(match, selectedModel)}</p>}
            <details className="mt-2">
              <summary className="cursor-pointer font-medium text-gray-600">適用条件・出典と本文を確認</summary>
              <dl className="mt-2 grid grid-cols-[5rem_minmax(0,1fr)] gap-x-2 gap-y-1 break-words text-gray-700">
                <dt className="text-gray-500">ノウハウID</dt><dd>{match.knowledgeId}</dd>
                <dt className="text-gray-500">本文の識別値</dt><dd className="break-all font-mono">{match.sha256}</dd>
                {Object.entries(match.modelScope).map(([key, value]) => (
                  <div key={key} className="contents"><dt className="text-gray-500">{scopeLabel(key)}</dt><dd>{scopeValue(key, value)}</dd></div>
                ))}
              </dl>
              <ul className="mt-2 space-y-2 border-t border-gray-200 pt-2">
                {match.sourceRefs.map((ref, index) => <li key={index} className="break-words">
                  {Object.entries(ref).filter(([key]) => key !== 'ref_type').map(([key, value]) => <p key={key}>{refLabel(key)}: {value}</p>)}
                </li>)}
              </ul>
              <pre className="mt-2 whitespace-pre-wrap break-words font-sans text-gray-800">{match.body}</pre>
            </details>
          </li>
        ))}
      </ul>
      {knowhow.searchTerms.length > 0 && <p className="mt-2 text-xs text-gray-700">技術KB検索へ加えた手掛かり: {knowhow.searchTerms.join('、')}</p>}
    </section>
  );
}

export function LaneReply({ lane, mode, selectedModel }: { lane: SenpaiChatLane; mode: KnowledgeResearchMode; selectedModel?: string }) {
  const name = mode === 'law' ? '法令KB' : '技術KB';
  if (lane.status === 'loading') return <p role="status" className="text-sm text-gray-600">{name}を検索しています…</p>;
  if (lane.status === 'error') return <p role="alert" className="text-sm text-red-700">{lane.message || `${name}への問い合わせに失敗しました。設定・通信状態を確認してください。`}</p>;
  if (lane.status === 'cancelled') return <p role="status" className="text-sm text-gray-600">{name}への検索は中止されました。</p>;
  if (lane.status === 'paused') return <p role="status" className="text-sm text-gray-500">{lane.message || `${name}への続きの質問を停止しています。新しい相談を始めてください。`}</p>;

  const answer = lane.answer;
  if (!answer) return <p className="text-sm text-gray-600">{name}から回答がありません。</p>;
  const sources = answer.sourceDocuments || [];
  const candidates = answer.pageCandidates || [];
  return (
    <div className="space-y-3">
      {answer.responseType === 'not_found' ? (
        <p className="text-sm text-gray-900">このKBでは該当情報を確認できませんでした。</p>
      ) : answer.responseType === 'clarify' ? (
        <div className="text-sm text-gray-900">
          <p className="font-semibold">条件の確認が必要です</p>
          {answer.clarifyQuestions.length > 0 && <ul className="mt-2 list-disc space-y-1 pl-5">{answer.clarifyQuestions.map((question, index) => <li key={`${index}-${question}`}>{question}</li>)}</ul>}
        </div>
      ) : (
        answer.content
          ? <SenpaiMarkdown markdown={answer.content} knownRefs={NO_REFS} anchorPrefix={`lane-${mode}`} variant="plain" />
          : <p className="text-sm leading-6 text-gray-800">回答本文がありません。</p>
      )}
      {mode === 'normal' && <KnowhowReferences answer={answer} selectedModel={selectedModel} />}
      {sources.length > 0 && (
        <div className="border-t border-gray-200 pt-2">
          <h5 className="mb-1 text-xs font-medium text-gray-500">{mode === 'law' ? '法令の出典' : '技術資料の出典'}</h5>
          <ul className="space-y-1 text-xs">
            {sources.map((source, index) => {
              const href = researchSourceHref(source, mode);
              return (
                <li key={`${source.documentName || source.title || mode}-${index}`} className="break-words">
                  {href
                    ? <a href={href} target="_blank" rel="noopener noreferrer" className="text-gray-800 underline underline-offset-2">{sourceTitle(source, mode)}{source.pageNumber ? ` · ${source.pageNumber}ページ` : ''}</a>
                    : <span className="text-gray-700">{sourceTitle(source, mode)}（安全なリンクを確認できません）</span>}
                  {mode === 'law' && source.lawCitation && <dl className="mt-1 grid grid-cols-[3.5rem_minmax(0,1fr)] gap-x-2 gap-y-0.5 text-gray-600">
                    {source.lawCitation.lawNumber && <><dt className="text-gray-500">法令番号</dt><dd>{source.lawCitation.lawNumber}</dd></>}
                    {(source.lawCitation.provisionReference || source.lawCitation.provisionType) && <><dt className="text-gray-500">条文</dt><dd>{source.lawCitation.provisionReference || source.lawCitation.provisionType}</dd></>}
                    {source.lawCitation.effectiveDate && <><dt className="text-gray-500">施行日</dt><dd>{source.lawCitation.effectiveDate}</dd></>}
                  </dl>}
                </li>
              );
            })}
          </ul>
        </div>
      )}
      {candidates.length > 0 && (
        <div className="border-t border-gray-200 pt-2">
          <h5 className="mb-1 text-xs font-medium text-gray-500">ページ候補（参考）</h5>
          <ul className="space-y-1 text-xs">
            {candidates.map((source, index) => {
              const href = researchSourceHref(source, mode);
              const title = `${sourceTitle(source, mode)}${source.pageNumber ? ` · ${source.pageNumber}ページ` : ''}`;
              return <li key={`${source.documentName || source.title || mode}-candidate-${index}`} className="break-words">{href ? <a href={href} target="_blank" rel="noopener noreferrer" className="text-gray-800 underline underline-offset-2">{title}</a> : <span className="text-gray-700">{title}（安全なリンクを確認できません）</span>}{source.snippet && <p className="mt-1 whitespace-pre-wrap text-gray-600">{source.snippet}</p>}</li>;
            })}
          </ul>
        </div>
      )}
      {answer.sessionId && (
        <Link href={buildChatSessionHref(answer.sessionId, mode)} className="inline-flex text-xs text-gray-500 underline underline-offset-2">
          {mode === 'law' ? '法令チャットの履歴を開く' : '技術チャットの履歴を開く'}
        </Link>
      )}
    </div>
  );
}

function canSynthesize(turn: SenpaiChatTurn, running: boolean, synthesisEnabled: boolean) {
  const lanes = [turn.normal, turn.law];
  return synthesisEnabled && !running && Boolean(turn.senpaiTurnId)
    && lanes.every((lane) => lane.status !== 'loading')
    && lanes.some((lane) => lane.status === 'success')
    && turn.synthesis?.status !== 'loading' && turn.synthesis?.status !== 'success';
}

export function SynthesisSection({ turn, running, onSynthesize, synthesisEnabled }: {
  turn: SenpaiChatTurn;
  running: boolean;
  synthesisEnabled: boolean;
  onSynthesize: (turnId: number) => void;
}) {
  const synthesis = turn.synthesis;
  const button = canSynthesize(turn, running, synthesisEnabled) && (
    <button type="button" onClick={() => onSynthesize(turn.id)} className="min-h-8 rounded-full border border-gray-300 bg-white px-3 text-xs text-gray-700 hover:bg-gray-50 focus:outline-none focus-visible:ring-2 focus-visible:ring-violet-500">工技先輩のまとめを作る</button>
  );
  if (!synthesis) return button ? <div className="mb-3">{button}</div> : null;
  if (synthesis.status === 'loading') return <p role="status" className="mb-3 text-sm text-gray-500">まとめを作成しています…</p>;
  if (synthesis.status === 'error') {
    return (
      <div className="mb-3 space-y-2">
        <p role="alert" className="text-sm text-red-700">{synthesis.message || 'まとめを作成できませんでした。時間をおいて再度お試しください。'}</p>
        {button}
      </div>
    );
  }
  const inputs = synthesis.inputs;
  return (
    <section aria-label="工技先輩のまとめ" className="mb-3 rounded-2xl bg-gray-50 p-4">
      <h4 className="text-sm font-semibold text-gray-900">工技先輩のまとめ（試作・開発中）</h4>
      <p className="mt-1 text-xs leading-5 text-gray-500">下の2つの回答を組み合わせただけの文章です。内容は必ず各回答の出典で確認してください。ノウハウは未承認の参考情報で、根拠にはなりません。</p>
      <p className="mt-3 whitespace-pre-wrap break-words text-sm leading-6 text-gray-900">{synthesis.content}</p>
      {inputs && (
        <p className="mt-3 text-xs text-gray-500">
          {!inputs.normal && '技術KBの回答は使っていません。'}{!inputs.law && '法令KBの回答は使っていません。'}
          {inputs.knowhowCount > 0 && `ノウハウ候補${inputs.knowhowCount}件を参考として含めています。`}
        </p>
      )}
    </section>
  );
}
