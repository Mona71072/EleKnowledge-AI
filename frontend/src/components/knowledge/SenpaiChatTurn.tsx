import type { ReactNode } from 'react';
import type { SenpaiChatTurn as Turn } from '@/lib/knowledge-senpai-chat.mjs';
import type { FieldReport } from '@/lib/knowledge-senpai-field-report.mjs';
import { LaneReply, SynthesisSection } from './SenpaiLegacyLanes';
import { SenpaiFieldReportForm } from './SenpaiFieldReportForm';
import { SenpaiResearchAnswer } from './SenpaiResearchAnswer';

export type ResendOptions = { query: string; modelType?: string };

/** 1回の相談: 右寄せの質問の吹き出しと、枠なしの回答。 */
export function SenpaiChatTurn({ turn, running, conversationId, report, onReportSent, developerView, canReport, synthesisEnabled, onSynthesize, onResend }: {
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
}) {
  const reportForm: ReactNode = canReport
    ? <SenpaiFieldReportForm conversationId={conversationId} turn={turn} sent={turn.senpaiTurnId ? report : undefined} onSent={onReportSent} />
    : null;
  return (
    <article className="space-y-6" aria-label={`相談 ${turn.id}`}>
      <div className="flex flex-col items-end gap-1">
        <div className="max-w-[85%] rounded-3xl bg-gray-100 px-4 py-2.5 text-[15px] leading-7 text-gray-900">
          <p className="whitespace-pre-wrap break-words">{turn.supplement ?? turn.query}</p>
        </div>
        {turn.supplement && <p className="text-xs text-gray-400">元の質問に補足して検索</p>}
        {turn.modelType && <p className="rounded-full bg-gray-50 px-2 py-0.5 text-[11px] text-gray-500">機種: {turn.modelType}</p>}
      </div>
      <div className="flex gap-3">
        <span aria-hidden="true" className="mt-0.5 flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-gray-900 text-[11px] font-medium text-white">工</span>
        <div className="min-w-0 flex-1">
          <h3 className="mb-1.5 text-xs font-medium text-gray-500">工技先輩</h3>
          {turn.research ? (
            <SenpaiResearchAnswer research={turn.research} anchorPrefix={`senpai-turn-${turn.id}`} selectedModel={turn.modelType} developerView={developerView} query={turn.query} onResend={onResend} actions={reportForm} />
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
              <p className="text-xs text-gray-400">各KBの回答を個別に表示しています。必要に応じて根拠と適用条件を確認してください。</p>
              {reportForm && <div className="-mx-1 flex flex-wrap items-center">{reportForm}</div>}
            </div>
          )}
        </div>
      </div>
    </article>
  );
}
