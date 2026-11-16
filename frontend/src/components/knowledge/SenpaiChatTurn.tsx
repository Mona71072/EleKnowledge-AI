import { memo, type ReactNode } from 'react';
import type { SenpaiChatTurn as Turn } from '@/lib/knowledge-senpai-chat.mjs';
import type { FieldReport } from '@/lib/knowledge-senpai-field-report.mjs';
import { LaneReply, SynthesisSection } from './SenpaiLegacyLanes';
import { SenpaiFieldReportForm } from './SenpaiFieldReportForm';
import { SenpaiResearchAnswer } from './SenpaiResearchAnswer';
import { storeKnowledgeGapRequest, storeResearchQuery } from '@/lib/knowledge-gap-request.mjs';

/** 通常チャットを、質問本文をURLに含めず、じっくり調べるを選んで開く。 */
export function researchHref() {
  return '/chat?research=1';
}

/** 聞き直し・もう一度試す。補足つきの相談では、検索に使う質問（query）のほかに補足も渡して、同じ見え方で残す。 */
export type ResendOptions = { query: string; modelType?: string; supplement?: string; supplementOf?: string };

/** 1回の相談: 右寄せの質問の吹き出しと、枠なしの回答。 */
export const SenpaiChatTurn = memo(function SenpaiChatTurn({ turn, running, conversationId, report, onReportSent, developerView, canReport, synthesisEnabled, onSynthesize, onResend, knowhowOnly, canOpenGap }: {
  turn: Turn;
  running: boolean;
  conversationId?: string;
  report?: FieldReport;
  onReportSent: (report: FieldReport) => void;
  developerView: boolean;
  /** 「結果を残す」を出してよい状態か（機能フラグ・回答の状態を含めて呼び出し側が判断する）。 */
  canReport: boolean;
  synthesisEnabled: boolean;
  onSynthesize: (turnId: number) => void;
  /** 最新の調査の相談にだけ渡す（聞き直し・もう一度試す）。 */
  onResend?: (options: ResendOptions) => void;
  /** D16: ノウハウだけで答える画面。法令KBの回答がある過去の相談は従来の 2 列で表示する。 */
  knowhowOnly?: boolean;
  canOpenGap?: boolean;
}) {
  const resend = onResend
    ? (options: ResendOptions) => onResend({ ...options, ...(turn.supplement && turn.supplementOf ? { supplement: turn.supplement, supplementOf: turn.supplementOf } : {}) })
    : undefined;
  const reportForm: ReactNode = canReport
    ? <SenpaiFieldReportForm conversationId={conversationId} turn={turn} sent={turn.senpaiTurnId ? report : undefined} onSent={onReportSent} />
    : null;
  const legacyGap = !turn.research && turn.normal.status === 'success' && turn.law.status === 'success'
    && turn.normal.answer?.responseType === 'not_found' && turn.law.answer?.responseType === 'not_found';
  const knowhowOnlyGap = knowhowOnly && !turn.research && turn.normal.status === 'success'
    && turn.normal.answer?.responseType === 'not_found'
    && turn.normal.answer.knowhow?.status === 'not_found'
    && turn.normal.answer.knowhow.matches.length === 0;
  return (
    <article className="space-y-6" aria-label={`相談 ${turn.id}`}>
      <div className="flex flex-col items-end gap-1">
        <div className="max-w-[85%] rounded-3xl bg-gray-100 px-4 py-2.5 text-[15px] leading-7 text-gray-900">
          <p className="whitespace-pre-wrap break-words">{turn.supplement ?? turn.query}</p>
        </div>
        {turn.supplement && <p className="text-xs text-gray-500">元の質問に補足して検索</p>}
        {turn.modelType && <p className="rounded-full bg-gray-50 px-2 py-0.5 text-[11px] text-gray-500">機種: {turn.modelType}</p>}
      </div>
      <div className="flex gap-3">
        <span aria-hidden="true" className="mt-0.5 flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-gray-900 text-[11px] font-medium text-white">工</span>
        <div className="min-w-0 flex-1">
          <h3 className="mb-1.5 text-xs font-medium text-gray-500">工技先輩</h3>
          {turn.research ? (
            <SenpaiResearchAnswer research={turn.research} anchorPrefix={`senpai-turn-${turn.id}`} selectedModel={turn.modelType} developerView={developerView} query={turn.query} senpaiTurnId={turn.senpaiTurnId} canOpenGap={canOpenGap} onResend={resend} actions={reportForm} />
          ) : knowhowOnly && turn.law.status !== 'success' ? (
            <div className="space-y-4">
              <section aria-label="ノウハウからの回答" className="min-w-0 space-y-2">
                <h4 className="text-xs font-medium text-gray-500">ノウハウ</h4>
                <LaneReply lane={turn.normal} mode="normal" selectedModel={turn.modelType} label="ノウハウ" />
              </section>
              {canOpenGap && knowhowOnlyGap && turn.senpaiTurnId && <a href="/admin/knowledge/research" onClick={() => storeKnowledgeGapRequest({ senpaiTurnId: turn.senpaiTurnId! })} className="inline-flex min-h-8 items-center text-xs text-gray-600 underline underline-offset-2 hover:text-gray-900">不足を確認する</a>}
              {turn.normal.status !== 'loading' && (
                <p className="text-xs text-gray-500">
                  技術資料・法令で確かめるときは{' '}
                  <a href={researchHref()} onClick={(event) => { if (!storeResearchQuery(turn.query)) event.preventDefault(); }} className="text-gray-800 underline underline-offset-2">じっくり調べるで確かめる</a>
                  （通常チャットに質問を入れて開きます。送信すると、じっくり調べるの回数を使います）
                </p>
              )}
              {reportForm && <div className="-mx-1 flex flex-wrap items-center">{reportForm}</div>}
            </div>
          ) : (
            <div className="space-y-4">
              <SynthesisSection turn={turn} running={running} onSynthesize={onSynthesize} synthesisEnabled={synthesisEnabled} />
              <div className="grid gap-6 md:grid-cols-2">
                <section aria-label="技術KBからの回答" className="min-w-0 space-y-2">
                  <h4 className="text-xs font-medium text-gray-500">技術KB</h4>
                  <LaneReply lane={turn.normal} mode="normal" selectedModel={turn.modelType} />
                </section>
                <section aria-label="法令KBからの回答" className="min-w-0 space-y-2">
                  <h4 className="text-xs font-medium text-gray-500">法令KB</h4>
                  <LaneReply lane={turn.law} mode="law" />
                </section>
              </div>
              <p className="text-xs text-gray-500">各KBの回答を個別に表示しています。必要に応じて根拠と適用条件を確認してください。</p>
              {canOpenGap && legacyGap && turn.senpaiTurnId && <a href="/admin/knowledge/research" onClick={() => storeKnowledgeGapRequest({ senpaiTurnId: turn.senpaiTurnId! })} className="inline-flex min-h-8 items-center text-xs text-gray-600 underline underline-offset-2 hover:text-gray-900">不足を確認する</a>}
              {reportForm && <div className="-mx-1 flex flex-wrap items-center">{reportForm}</div>}
            </div>
          )}
        </div>
      </div>
    </article>
  );
});
