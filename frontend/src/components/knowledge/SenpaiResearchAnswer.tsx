'use client';

import type { ReactNode } from 'react';
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
  splitAnswerSections,
} from '@/lib/knowledge-senpai-research-view.mjs';
import { modelFitNotice } from '@/lib/knowledge-senpai-model-fit.mjs';
import { RetryIcon } from './SenpaiIcons';
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

function SourceRow({ id, refId, title, meta, linkLabel, href, children }: {
  id: string; refId: string; title: string; meta?: string; linkLabel?: string; href?: string; children?: ReactNode;
}) {
  return (
    <li id={id} className="scroll-mt-4 flex min-w-0 items-baseline gap-2 py-1 text-sm">
      <RefPill refId={refId} />
      <span className="min-w-0 flex-1">
        <span className="break-words text-gray-900">{title}</span>
        {meta && <span className="ml-2 break-words text-xs text-gray-500">{meta}</span>}
        {children}
      </span>
      {linkLabel && (href
        ? <a href={href} target="_blank" rel="noopener noreferrer" aria-label={`${title}：${linkLabel}`} title={linkLabel} className={`${textButton} shrink-0 no-underline hover:underline`}>開く</a>
        : <span className="shrink-0 text-xs text-gray-500">（安全なリンクを確認できません）</span>)}
    </li>
  );
}

function KnowhowDisclosure({ result, prefix, selectedModel }: { result: SenpaiResearchResult; prefix: string; selectedModel?: string }) {
  const { used, candidates } = result.sources.knowhow;
  // 聞き返し・見つからなかった回答では、使ったノウハウが無ければ出さない。
  if (result.kind !== 'answer' && used.length === 0) return null;
  if (used.length === 0 && candidates.length === 0) return <p className="text-xs text-gray-500">ノウハウは参照していません</p>;
  const notices = used.map((card) => modelFitNotice(card, selectedModel));
  return (
    <details open={notices.some(Boolean)} aria-label="ノウハウ（未承認・参考）" className="text-sm">
      <summary className="cursor-pointer text-xs font-medium text-gray-600 hover:text-gray-900">ノウハウ {used.length + candidates.length}件（未承認・参考）</summary>
      <div className="mt-1">
        <p className="text-xs text-gray-500">探索の手掛かりで、技術的な根拠や承認を示しません。</p>
        <h5 className={groupLabel}>回答で使ったノウハウ</h5>
        {used.length === 0 ? <p className="py-1 text-xs text-gray-500">ノウハウは参照していません</p> : (
          <ul>
            {used.map((card, index) => (
              <SourceRow key={card.ref} id={researchRefAnchor(prefix, card.ref)} refId={card.ref} title={card.title}
                meta={`v${card.cardVersion}・${card.status === 'draft' ? '未承認（下書き）' : '承認済みカード・参照用のみ'}・${card.knowledgeId}`}>
                {notices[index] && <span role="note" className="mt-0.5 block text-xs text-amber-700">{notices[index]}</span>}
              </SourceRow>
            ))}
          </ul>
        )}
        {candidates.length > 0 && (
          <>
            <h5 className={groupLabel}>候補として渡したが使わなかったノウハウ</h5>
            <ul className="text-xs text-gray-500">
              {candidates.map((card) => <li key={`${card.knowledgeId}-${card.cardVersion}`} className="break-words py-0.5">{card.title}（{card.knowledgeId} v{card.cardVersion}）</li>)}
            </ul>
          </>
        )}
      </div>
    </details>
  );
}

function Sources({ result, prefix, selectedModel }: { result: SenpaiResearchResult; prefix: string; selectedModel?: string }) {
  const { tech, law } = result.sources;
  const knowhow = <KnowhowDisclosure result={result} prefix={prefix} selectedModel={selectedModel} />;
  return (
    <section aria-label="出典" className="space-y-1 border-t border-gray-100 pt-3">
      {(tech.length > 0 || law.length > 0) && <h4 className="text-sm font-semibold text-gray-900">出典</h4>}
      {tech.length > 0 && (
        <section aria-label="技術資料の出典">
          <h5 className={groupLabel}>技術資料（{tech.length}）</h5>
          <ul>
            {tech.map((source) => (
              <SourceRow key={source.ref} id={researchRefAnchor(prefix, source.ref)} refId={source.ref}
                title={source.title || source.documentName || '技術資料'}
                meta={[source.pageNumber ? `${source.pageNumber}ページ` : '', source.documentName && source.documentName !== source.title ? source.documentName : ''].filter(Boolean).join('・') || undefined}
                linkLabel="資料を開く" href={techSourceHref(source)} />
            ))}
          </ul>
        </section>
      )}
      {law.length > 0 && (
        <section aria-label="法令の出典">
          <h5 className={groupLabel}>法令（{law.length}）</h5>
          <ul>
            {law.map((source) => (
              <SourceRow key={source.ref} id={researchRefAnchor(prefix, source.ref)} refId={source.ref} title={source.lawTitle}
                meta={[source.provision, source.effectiveDate ? `施行日 ${source.effectiveDate}` : ''].filter(Boolean).join('・') || undefined}
                linkLabel="e-Govで開く" href={lawSourceHref(source)} />
            ))}
          </ul>
        </section>
      )}
      <div className="pt-2">{knowhow}</div>
    </section>
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

/** 結論を冒頭の文に、補足（食い違い・次に確認すること）を1つの控えめなブロックに、残りを見出しつきの文章にする。 */
function AnswerText({ result, prefix }: { result: SenpaiResearchResult; prefix: string }) {
  const refs = knownRefs(result);
  const titles = refTitles(result);
  const sections = splitAnswerSections(result.answerMarkdown);
  if (!sections) return <SenpaiMarkdown markdown={result.answerMarkdown} knownRefs={refs} anchorPrefix={prefix} refTitles={titles} />;
  const notes = sections.filter((section) => section.kind === 'caution' || section.kind === 'todo');
  return (
    <div>
      {sections.filter((section) => section.kind !== 'caution' && section.kind !== 'todo').map((section, index) => (
        <section key={index} aria-label={section.heading} className={index === 0 ? '' : 'mt-5'}>
          {section.kind === 'normal' && section.heading && <h5 className="mb-1 text-sm font-semibold text-gray-900">{section.heading}</h5>}
          {section.body && <SenpaiMarkdown markdown={section.body} knownRefs={refs} anchorPrefix={prefix} refTitles={titles} className={section.kind === 'conclusion' ? 'font-medium' : ''} />}
        </section>
      ))}
      {notes.length > 0 && (
        <aside aria-label="補足" className="mt-5 space-y-3 rounded-xl bg-gray-50 px-4 py-3">
          {notes.map((section) => (
            <section key={section.heading} aria-label={section.heading}>
              <h5 className="text-xs font-semibold text-gray-600">{section.heading}</h5>
              {section.body && <SenpaiMarkdown markdown={section.body} knownRefs={refs} anchorPrefix={prefix} refTitles={titles} variant="plain" />}
            </section>
          ))}
        </aside>
      )}
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
      {onResend && <p className="mt-2 text-sm text-gray-500">下の入力欄に答えを書いて送ると、元の質問に補足して調べ直します。</p>}
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
        <p role="note" className="text-sm text-amber-700">
          質問では {mismatch.detected} と読めますが、選択中の機種は {mismatch.selected} です。
          {onResend && query && <button type="button" onClick={() => onResend({ query, modelType: mismatch.detected })} className={`ml-2 ${textButton}`}>{mismatch.detected}で聞き直す</button>}
        </p>
      )}
      {(result.warnings ?? []).map((warning, index) => <p key={`${index}-${warning}`} role="note" className="text-xs text-amber-700">{warning}</p>)}
      {result.stopReason === 'budget' && <p className="text-xs text-gray-500">時間の上限に達したため、確認できた範囲でまとめています</p>}
      {result.kind === 'clarify' && <ClarifyBlock result={result} prefix={prefix} query={query} onResend={onResend} />}
      {result.kind === 'not_found' && (
        <p className="text-[15px] leading-7 text-gray-900">該当する情報を確認できませんでした。質問の言い換えや、機種の指定を試してください。</p>
      )}
      {result.kind === 'answer' && <AnswerText result={result} prefix={prefix} />}
      <Sources result={result} prefix={prefix} selectedModel={noticeModel} />
      {result.kind === 'answer' && (
        <div role="group" aria-label="回答の操作" className="-mx-1 flex flex-wrap items-center gap-1">
          <SenpaiCopyButton getText={() => buildCopyText(result)} />
          {actions}
          {onResend && query && (
            <button type="button" aria-label="もう一度調べる" title="もう一度調べる" onClick={() => onResend({ query, ...(selectedModel ? { modelType: selectedModel } : {}) })} className={iconButton}><RetryIcon /></button>
          )}
        </div>
      )}
    </div>
  );
}

/**
 * 調査ジョブの1回分の表示。進捗の1行 → 1つの統一回答 → 出典。
 * `developerView` のときだけ、debug と生の段階イベントを足す。
 * `onResend` は最新の相談にだけ渡す（聞き直し・もう一度試す）。中止は入力欄の停止ボタンだけ。
 * `actions` は操作列（コピーなど）の横に並べる追加のボタン（結果を残す）。
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
      {developerView && <SenpaiDevPanel debug={research.debug} steps={research.steps} unverifiedRefs={research.result?.unverifiedRefs} />}
    </div>
  );
}
