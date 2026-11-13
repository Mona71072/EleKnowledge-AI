'use client';

import { Fragment, type ReactNode } from 'react';
import { ALL_MODEL_TYPES } from '@/data/kbModelTypes';
import type { SenpaiResearchState } from '@/lib/knowledge-senpai-chat.mjs';
import {
  lawSourceHref,
  SENPAI_RESEARCH_CANCELLED_MESSAGE,
  techSourceHref,
  type SenpaiResearchResult,
} from '@/lib/knowledge-senpai-research.mjs';
import {
  buildCopyText,
  clarifyAsksModel,
  modelMismatch,
  researchRefAnchor,
  sourceSummary,
  structureAnswer,
} from '@/lib/knowledge-senpai-research-view.mjs';
import { KNOWHOW_NOT_OFFICIAL_NOTICE, modelFitNotice } from '@/lib/knowledge-senpai-model-fit.mjs';
import { DisclosureChevron, RetryIcon } from './SenpaiIcons';
import { SenpaiCopyButton } from './SenpaiCopyButton';
import { SenpaiDevPanel } from './SenpaiDevPanel';
import { REF_PREFIX, REF_TONES, SenpaiMarkdown } from './SenpaiMarkdown';
import { SenpaiStepTimeline } from './SenpaiStepTimeline';

const KNOWN_MODELS: ReadonlySet<string> = new Set(ALL_MODEL_TYPES.map((model) => model.value));
// 見た目は小さいまま、押せる範囲だけ上下左右に広げる（::before）。
const textButton = 'relative rounded px-1 text-xs font-medium text-gray-700 underline underline-offset-2 before:absolute before:-inset-x-2 before:-inset-y-2.5 hover:text-gray-900 focus:outline-none focus-visible:ring-2 focus-visible:ring-violet-500';
const iconButton = 'flex h-10 w-10 items-center justify-center rounded-lg text-gray-500 hover:bg-gray-100 hover:text-gray-900 focus:outline-none focus-visible:ring-2 focus-visible:ring-violet-500';
const groupLabel = 'mt-3 text-xs font-medium text-gray-500 first:mt-0';

type Resend = (options: { query: string; modelType?: string; supplement?: string; supplementOf?: string }) => void;

function RefPill({ refId }: { refId: string }) {
  return <span className={`inline-block shrink-0 rounded px-1.5 py-0.5 text-[11px] font-medium leading-4 ${REF_TONES[refId[0]].split(' hover:')[0]}`}>{`${REF_PREFIX[refId[0]]}${refId.slice(1)}`}</span>;
}

/** 出典・ノウハウ1件の行: 番号の札 + 題名（題名そのものがリンク）+ 控えめな補足。 */
/** 補足の1語（ページ・日付・条文）。途中で折り返さない。資料名のように長いものだけ `wrap` で折り返しを許す。 */
type MetaToken = string | { text: string; wrap: true };

function MetaLine({ tokens }: { tokens: readonly MetaToken[] }) {
  if (tokens.length === 0) return null;
  return (
    <span className="ml-2 text-xs text-gray-500">
      {tokens.map((token, index) => {
        const wrap = typeof token !== 'string';
        return <Fragment key={index}>{index > 0 && '・'}<span className={wrap ? 'break-words' : 'whitespace-nowrap'}>{wrap ? token.text : token}</span></Fragment>;
      })}
    </span>
  );
}

// 行の高さはどのグループも同じ（詰めた行）。押せる範囲は ::before で上下に広げて 40px 以上にする。
function SourceRow({ id, refId, title, meta = [], linkLabel, href, children }: {
  id: string; refId: string; title: string; meta?: readonly MetaToken[]; linkLabel?: string; href?: string; children?: ReactNode;
}) {
  return (
    <li id={id} className="scroll-mt-4 flex min-w-0 items-baseline gap-2 py-0.5 text-sm leading-6">
      <RefPill refId={refId} />
      <span className="min-w-0 flex-1">
        {linkLabel && href
          ? <a href={href} target="_blank" rel="noopener noreferrer" aria-label={`${title}：${linkLabel}`} className="relative break-words text-gray-900 underline-offset-2 before:absolute before:-inset-x-1 before:-inset-y-2 hover:underline focus:outline-none focus-visible:ring-2 focus-visible:ring-violet-500">{title}</a>
          : <span className="break-words text-gray-900">{title}</span>}
        <MetaLine tokens={meta} />
        {linkLabel && !href && <span className="ml-2 text-xs text-gray-500">（リンクを確認できません）</span>}
        {children}
      </span>
    </li>
  );
}

/** 回答で使ったノウハウだけを「ノ1 題名 未承認」で出す。使っていなければ何も出さない（詳細は開発者表示）。 */
function KnowhowUsed({ result, prefix, selectedModel }: { result: SenpaiResearchResult; prefix: string; selectedModel?: string }) {
  const { used } = result.sources.knowhow;
  if (used.length === 0) return null;
  return (
    <section aria-label="ノウハウ">
      <h5 className={groupLabel}>ノウハウ</h5>
      <p className="text-xs text-gray-500">{KNOWHOW_NOT_OFFICIAL_NOTICE}</p>
      <ul>
        {used.map((card) => {
          const notice = modelFitNotice(card, selectedModel);
          return (
            <SourceRow key={card.ref} id={researchRefAnchor(prefix, card.ref)} refId={card.ref} title={card.title}>
              {card.status === 'draft' && <span className="ml-2 rounded bg-gray-100 px-1 text-[10px] text-gray-600">未承認</span>}
              {notice && <span role="note" className="block text-xs text-gray-500">{notice}</span>}
            </SourceRow>
          );
        })}
      </ul>
    </section>
  );
}

/**
 * 技術資料・法令・ノウハウの出典一覧を、1つの閉じた開閉にまとめる。
 * 回答本文は常に表示し、出典一覧は必要なときだけ開く。
 * 本文の番号（技1・法1・ノ1）を押したときは、開閉が開いて該当の行へ移動する。
 */
/** 出典の一覧だけを閉じた開閉の中に入れる。回答の本文（結論・根拠と手順）は常に見える。 */
function SourcesDisclosure({ result, prefix, selectedModel }: { result: SenpaiResearchResult; prefix: string; selectedModel?: string }) {
  const { tech, law } = result.sources;
  const summary = sourceSummary(result);
  if (!summary) return null;
  return (
    <section aria-label="出典" className="border-t border-gray-100 pt-1"><details className="group">
      <summary className="flex min-h-10 cursor-pointer list-none items-center gap-1.5 text-xs text-gray-500 hover:text-gray-900 focus:outline-none focus-visible:ring-2 focus-visible:ring-violet-500 [&::-webkit-details-marker]:hidden">
        <DisclosureChevron />
        <span className="underline-offset-2 group-hover:underline">{summary}</span>
      </summary>
      <div className="space-y-1 pb-1">
      {tech.length > 0 && (
        <section aria-label="技術資料の出典">
          <h5 className={groupLabel}>技術資料</h5>
          <ul>
            {tech.map((source) => (
              <SourceRow key={source.ref} id={researchRefAnchor(prefix, source.ref)} refId={source.ref}
                title={source.title || source.documentName || '技術資料'}
                meta={[
                  ...(source.pageNumber ? [`${source.pageNumber}ページ`] : []),
                  ...(source.documentName && source.documentName !== source.title ? [{ text: source.documentName, wrap: true as const }] : []),
                ]}
                linkLabel="資料を開く" href={techSourceHref(source)} />
            ))}
          </ul>
        </section>
      )}
      {law.length > 0 && (
        <section aria-label="法令の出典">
          <h5 className={groupLabel}>法令</h5>
          <ul>
            {law.map((source) => (
              <SourceRow key={source.ref} id={researchRefAnchor(prefix, source.ref)} refId={source.ref} title={source.lawTitle}
                meta={[...(source.provision ? [source.provision] : []), ...(source.effectiveDate ? [`施行日 ${source.effectiveDate}`] : [])]}
                linkLabel="e-Govで開く" href={lawSourceHref(source)} />
            ))}
          </ul>
        </section>
      )}
      <KnowhowUsed result={result} prefix={prefix} selectedModel={selectedModel} />
      </div>
    </details></section>
  );
}

function knownRefs(result: SenpaiResearchResult) {
  return new Set([
    ...result.sources.tech.map((source) => source.ref),
    ...result.sources.law.map((source) => source.ref),
    ...result.sources.knowhow.used.map((card) => card.ref),
  ]);
}

function refTitles(result: SenpaiResearchResult) {
  return Object.fromEntries([
    ...result.sources.tech.map((source) => [source.ref, source.title || source.documentName || '技術資料']),
    ...result.sources.law.map((source) => [source.ref, `${source.lawTitle}${source.provision ? ` ${source.provision}` : ''}`]),
    ...result.sources.knowhow.used.map((card) => [card.ref, card.title]),
  ]);
}

function AnswerMarkdown({ result, prefix, body, variant }: { result: SenpaiResearchResult; prefix: string; body: string; variant?: 'plain' | 'lead' }) {
  return <SenpaiMarkdown markdown={body} knownRefs={knownRefs(result)} anchorPrefix={prefix} refTitles={refTitles(result)} variant={variant} />;
}

/**
 * 結論（先頭の文）→ 根拠と手順（書かれたままの段落・番号つき/箇条書き）→ 確認が必要な点（控えめなブロック）。
 * 見出しは出さない。旧形式の回答は同じ3つに寄せる。
 */
function AnswerText({ result, prefix }: { result: SenpaiResearchResult; prefix: string }) {
  const parts = structureAnswer(result.answerMarkdown);
  if (!parts) return <AnswerMarkdown result={result} prefix={prefix} body={result.answerMarkdown} />;
  return (
    <div className="space-y-4">
      {parts.lead && <AnswerMarkdown result={result} prefix={prefix} body={parts.lead} variant="lead" />}
      {parts.evidence && <AnswerMarkdown result={result} prefix={prefix} body={parts.evidence} />}
      {parts.notes && <aside aria-label="確認が必要な点" className="rounded-xl bg-gray-50 px-4 py-3"><h5 className={groupLabel}>確認が必要な点</h5><AnswerMarkdown result={result} prefix={prefix} body={parts.notes} variant="plain" /></aside>}
    </div>
  );
}

function ClarifyBlock({ result, prefix, query, onResend }: { result: SenpaiResearchResult; prefix: string; query?: string; onResend?: Resend }) {
  const hasQuestions = result.clarifyQuestions.length > 0;
  return (
    <div className="text-[15px] leading-7 text-gray-900">
      <p className="font-medium">条件の確認が必要です</p>
      {hasQuestions
        ? <ul className="mt-1 list-disc space-y-0.5 pl-5 marker:text-gray-400">{result.clarifyQuestions.map((question, index) => <li key={`${index}-${question}`}>{question}</li>)}</ul>
        : result.answerMarkdown.trim() && <AnswerText result={result} prefix={prefix} />}
      {/* 最新の相談だけが続きを受け付ける（onResend が渡るのは最新の相談だけ）。古い聞き返しには出さない。 */}
      {onResend && <p className="mt-2 text-sm text-gray-500">下の入力欄に答えを書いてください。</p>}
      {onResend && query && clarifyAsksModel(result) && (
        <div className="mt-2 flex flex-wrap gap-2" role="group" aria-label="機種を選んで聞き直す">
          {ALL_MODEL_TYPES.map((model) => (
            <button key={model.value} type="button" onClick={() => onResend({ query, modelType: model.value })} className="min-h-10 rounded-full border border-gray-300 bg-white px-3 text-xs text-gray-700 hover:bg-gray-50 focus:outline-none focus-visible:ring-2 focus-visible:ring-violet-500">{model.label}</button>
          ))}
        </div>
      )}
    </div>
  );
}

function ResultBody({ result, prefix, selectedModel, query, onResend, actions }: {
  result: SenpaiResearchResult; prefix: string; selectedModel?: string; query?: string; onResend?: Resend; actions?: ReactNode;
}) {
  const mismatch = modelMismatch(result, selectedModel, KNOWN_MODELS);
  // 機種を選んでいない相談でも、質問から読めた機種があれば、別機種の事例の注意に使う。
  const noticeModel = selectedModel ?? result.understanding?.modelType ?? undefined;
  return (
    <div className="space-y-4">
      {mismatch && (
        <p role="note" className="flex items-start gap-1.5 text-xs leading-6 text-gray-600">
          <span aria-hidden="true" className="mt-2 inline-block h-1.5 w-1.5 shrink-0 rounded-full bg-amber-500" />
          <span className="min-w-0">
            質問では {mismatch.detected} と読めますが、選択中の機種は {mismatch.selected} です。
            {onResend && query && <button type="button" onClick={() => onResend({ query, modelType: mismatch.detected })} className={`ml-1 ${textButton}`}>{mismatch.detected}で聞き直す</button>}
          </span>
        </p>
      )}
      {(result.warnings ?? []).map((warning, index) => <p key={`${index}-${warning}`} role="note" className="text-xs text-amber-700">{warning}</p>)}
      {result.stopReason === 'budget' && <p className="text-xs text-gray-500">時間の上限に達したため、確認できた範囲でまとめています</p>}
      {result.kind === 'clarify' && <ClarifyBlock result={result} prefix={prefix} query={query} onResend={onResend} />}
      {result.kind === 'not_found' && (
        <p className="text-[15px] leading-7 text-gray-900">該当する情報を確認できませんでした。質問の言い換えや、機種の指定を試してください。</p>
      )}
      {result.kind === 'answer' && <AnswerText result={result} prefix={prefix} />}
      <SourcesDisclosure result={result} prefix={prefix} selectedModel={noticeModel} />
      {result.kind === 'answer' && (
        <div role="group" aria-label="回答の操作" className="-mx-1 flex flex-wrap items-center gap-1">
          <SenpaiCopyButton getText={() => buildCopyText(result)} />
          {onResend && query && (
            <button type="button" aria-label="もう一度調べる" title="もう一度調べる" onClick={() => onResend({ query, ...(selectedModel ? { modelType: selectedModel } : {}) })} className={iconButton}><RetryIcon /></button>
          )}
          {actions}
        </div>
      )}
    </div>
  );
}

/**
 * 調査ジョブの1回分の表示。進捗の1行 → 常時表示する統一回答 → 閉じた「根拠と出典」。
 * `developerView` のときだけ、debug と生の段階イベントを足す。
 * `onResend` は最新の相談にだけ渡す（聞き直し・もう一度試す）。中止は入力欄の停止ボタンだけ。
 * `actions` は操作列（コピー・もう一度調べる）の後ろに並べる追加のボタン（結果を残す）。
 */
export function SenpaiResearchAnswer({ research, anchorPrefix, selectedModel, developerView, query, onResend, actions }: {
  research: SenpaiResearchState;
  anchorPrefix: string;
  selectedModel?: string;
  developerView: boolean;
  query?: string;
  onResend?: Resend;
  actions?: ReactNode;
}) {
  const retry = onResend && query
    ? <button type="button" onClick={() => onResend({ query, ...(selectedModel ? { modelType: selectedModel } : {}) })} className={`ml-2 ${textButton}`}>もう一度試す</button>
    : null;
  return (
    <div className="space-y-4">
      <SenpaiStepTimeline research={research} />
      {research.status === 'failed' && (
        <p role="alert" className="text-sm text-red-700">{research.error?.message || '調査に失敗しました。時間をおいて再度お試しください'}{retry}</p>
      )}
      {research.status === 'cancelled' && (
        <p role="status" className="text-sm text-gray-600">{SENPAI_RESEARCH_CANCELLED_MESSAGE}{retry}</p>
      )}
      {research.status === 'completed' && research.result && (
        <ResultBody result={research.result} prefix={anchorPrefix} selectedModel={selectedModel} query={query} onResend={onResend} actions={actions} />
      )}
      {developerView && <SenpaiDevPanel debug={research.debug} steps={research.steps} unverifiedRefs={research.result?.unverifiedRefs} knowhow={research.result?.sources.knowhow} />}
    </div>
  );
}
