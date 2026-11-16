import type { FormEvent, RefObject, UIEvent } from 'react';
import type { SenpaiHistoryEntry } from '@/hooks/useSenpaiHistory';
import type { SenpaiChatSnapshot, SenpaiChatTurn as Turn } from '@/lib/knowledge-senpai-chat.mjs';
import type { FieldReport } from '@/lib/knowledge-senpai-field-report.mjs';
import { EXAMPLE_QUESTIONS, clarifyOriginalTruncated, clarifySupplementLimit } from '@/lib/knowledge-senpai-research-view.mjs';
import { SenpaiChatHeader } from './SenpaiChatHeader';
import { SenpaiChatTurn, type ResendOptions } from './SenpaiChatTurn';
import { SenpaiComposer } from './SenpaiComposer';
import { SenpaiConversationSidebar } from './SenpaiConversationSidebar';

export type SenpaiChatViewProps = {
  snapshot: SenpaiChatSnapshot;
  history: {
    entries: readonly SenpaiHistoryEntry[]; loading: boolean; error: string; complete: boolean;
    opening: boolean; openError: string; onRetry: () => void;
  };
  question: string;
  onQuestionChange: (value: string) => void;
  modelType: string;
  onModelChange: (value: string) => void;
  sendError: string;
  sidebarOpen: boolean;
  onOpenSidebar: () => void;
  onCloseSidebar: () => void;
  onSubmit: (event: FormEvent<HTMLFormElement>) => void;
  onCancel: () => void;
  onNewChat: () => void;
  onSelectConversation: (conversationId: string) => void;
  onSynthesize: (turnId: number) => void;
  onResend: (options: ResendOptions) => void;
  flags: { research: boolean; fieldReports: boolean; synthesis: boolean; knowhowOnly?: boolean };
  /** Matches the destination workbench's existing admin gate and feature flag. */
  canOpenGap?: boolean;
  developerView: boolean;
  onToggleDeveloperView: () => void;
  /** ⋯メニューの開閉（省略すると、ブラウザ任せの開閉になる）。 */
  menuOpen?: boolean;
  onMenuOpenChange?: (open: boolean) => void;
  reports: Readonly<Record<string, FieldReport>>;
  onReportSent: (report: FieldReport) => void;
  /** スクリーンリーダーへ知らせる短い文（調査中・結果）。進捗の途中経過は含めない。 */
  announcement?: string;
  transcriptRef?: RefObject<HTMLDivElement | null>;
  onTranscriptScroll?: (event: UIEvent<HTMLDivElement>) => void;
};

/** 「結果を残す」を出してよいターンか。別の質問を実行中でも、回答済みのターンの入力途中のフォームは消さない。 */
export function reportable(turn: Turn, fieldReports: boolean) {
  if (!fieldReports || !turn.senpaiTurnId) return false;
  // 調査ジョブの相談は、回答が出たものだけ結果を残せる（聞き返し・見つからなかった回答は対象外）。
  if (turn.research) return turn.research.status === 'completed' && turn.research.result?.kind === 'answer';
  const lanes = [turn.normal, turn.law];
  return lanes.every((lane) => lane.status !== 'loading') && lanes.some((lane) => lane.status === 'success');
}

const REMAINING_HINT_THRESHOLD = 200;

const outlineChip = 'rounded-2xl border border-gray-200 bg-white px-4 py-3 text-left text-sm leading-6 text-gray-700 hover:bg-gray-50 focus:outline-none focus-visible:ring-2 focus-visible:ring-violet-500';

function EmptyState({ research, onPick }: { research: boolean; onPick: (value: string) => void }) {
  return (
    <div className="mx-auto flex max-w-xl flex-col items-center pt-[12vh] text-center">
      <h2 className="text-2xl font-semibold text-gray-900">何を調べますか？</h2>
      <p className="mt-2 text-sm leading-6 text-gray-500">
        {research
          ? '質問を整理し、ノウハウ・技術資料・法令を調べて、1つの回答にまとめます。'
          : 'サーバーで検索が許可されたノウハウMarkdownを参考に技術KBを調べ、法令KBにも個別に問い合わせます。Markdownの編集やOneNoteへの追記は行いません。'}
      </p>
      {research && (
        <div className="mt-6 flex w-full flex-col gap-2">
          <p className="sr-only">質問の例（押すと入力欄に入ります）</p>
          {EXAMPLE_QUESTIONS.map((example) => <button key={example} type="button" onClick={() => onPick(example)} className={outlineChip}>{example}</button>)}
        </div>
      )}
    </div>
  );
}

/** 続けて質問できない相談か（履歴が途中まで・機能オフの環境の調査相談・両方の検索が失敗）。 */
export function isContinuationPaused(snapshot: SenpaiChatSnapshot, researchEnabled: boolean) {
  const latestTurn = snapshot.turns.at(-1);
  return snapshot.complete === false || (!researchEnabled && Boolean(latestTurn?.research))
    || (!snapshot.running && Boolean(latestTurn) && !latestTurn!.research
      && [latestTurn!.normal, latestTurn!.law].every((lane) => lane.status !== 'success'));
}

/**
 * 先輩チャットの画面全体。状態・通信・コントローラは持たず、props だけで描画する
 * （固定データでの画面確認やテストに使える）。
 */
export function SenpaiChatView({ snapshot, history, flags, canOpenGap = false, transcriptRef, onTranscriptScroll, ...props }: SenpaiChatViewProps) {
  const latestTurn = snapshot.turns.at(-1);
  // 調査ジョブの相談は、完了・失敗・中止のどれでも次の質問を送れる。機能がオフの環境では続けられない。
  const researchUnavailable = !flags.research && Boolean(latestTurn?.research);
  const continuationPaused = isContinuationPaused(snapshot, flags.research);
  const disabled = snapshot.running || continuationPaused || history.opening;
  const disclaimer = flags.knowhowOnly
    ? 'ノウハウは正規文書ではありません。重要な判断は出典の正規文書で確認してください'
    : flags.research
    ? '重要な判断は出典で確認してください（ノウハウは未承認）'
    : 'ローカルファイルは送信されません。重要な判断は出典で確認してください';
  const answeringClarify = latestTurn?.research?.status === 'completed' && latestTurn.research.result?.kind === 'clarify';
  // 聞き返しへの補足は、元の質問の先頭を残すぶん入力できる文字数が小さくなる。残りと、省略される場合の注意を出す。
  const clarifyOriginal = answeringClarify ? latestTurn.query : undefined;
  const supplementLimit = clarifyOriginal === undefined ? undefined : clarifySupplementLimit(clarifyOriginal);
  const supplementLength = Array.from(props.question).length;
  // 残りが十分あるうちは何も出さない。上限が近づいたときだけ知らせる。
  const remaining = supplementLimit === undefined ? undefined : Math.max(0, supplementLimit - supplementLength);
  const limitHint = remaining !== undefined && remaining <= REMAINING_HINT_THRESHOLD ? `補足はあと${remaining.toLocaleString('ja-JP')}文字まで入力できます` : undefined;
  const limitWarning = clarifyOriginal !== undefined && clarifyOriginalTruncated(clarifyOriginal, props.question)
    ? '元の質問が長いため、検索では元の質問の後半が省略されます。' : undefined;
  const placeholder = answeringClarify ? '補足を入力（例: AXIEZ、走行中に発生）' : '質問を入力';

  return (
    <section aria-label="先輩チャット" className="flex h-dvh min-h-[24rem] flex-col overflow-hidden bg-white text-gray-900">
      <div className="relative flex min-h-0 flex-1 overflow-hidden">
        <SenpaiConversationSidebar open={props.sidebarOpen} entries={history.entries} selectedId={snapshot.conversationId} loading={history.loading} error={history.error} complete={history.complete} onNew={props.onNewChat} onSelect={props.onSelectConversation} onClose={props.onCloseSidebar} onRetry={history.onRetry} />
        <main inert={props.sidebarOpen} className="flex min-w-0 flex-1 flex-col">
          <SenpaiChatHeader
            sidebarOpen={props.sidebarOpen} onOpenSidebar={props.onOpenSidebar} onNewChat={props.onNewChat}
            newChatDisabled={snapshot.turns.length === 0 && !snapshot.running && !history.opening}
            showDeveloperToggle={flags.research} developerView={props.developerView} onToggleDeveloperView={props.onToggleDeveloperView}
            menuOpen={props.menuOpen} onMenuOpenChange={props.onMenuOpenChange}
          />
          {history.openError && <p role="alert" className="px-4 py-2 text-center text-sm text-red-700">{history.openError}</p>}
          {history.opening && <p role="status" className="px-4 py-2 text-center text-sm text-gray-500">相談履歴を開いています…</p>}
          <div ref={transcriptRef} onScroll={onTranscriptScroll} className="min-h-0 flex-1 overflow-y-auto px-4 py-4 sm:px-6">
            <div className="mx-auto max-w-3xl space-y-10">
              {snapshot.turns.length === 0
                ? <EmptyState research={flags.research} onPick={props.onQuestionChange} />
                : snapshot.turns.map((turn) => (
                  <SenpaiChatTurn
                    key={`${snapshot.conversationId ?? 'new'}-${turn.id}`} turn={turn} running={snapshot.running}
                    conversationId={snapshot.conversationId} report={turn.senpaiTurnId ? props.reports[turn.senpaiTurnId] : undefined}
                    onReportSent={props.onReportSent} developerView={flags.research && props.developerView}
                    canReport={reportable(turn, flags.fieldReports)} synthesisEnabled={flags.synthesis}
                    onSynthesize={props.onSynthesize} knowhowOnly={flags.knowhowOnly} canOpenGap={canOpenGap}
                    onResend={turn.research && turn === latestTurn && !snapshot.running ? props.onResend : undefined}
                  />
                ))}
              {continuationPaused && (
                <p role="status" className="text-center text-sm text-gray-500">
                  {snapshot.complete === false ? '相談履歴の一部を確認できないため、表示のみ利用できます。' : researchUnavailable ? '調査機能が無効の環境では、調査ジョブの相談に続けて質問できません。' : '両方の検索が失敗または中止されたため、この相談では続けて質問できません。'}内容を確認し、「新しい相談」から再開してください。
                </p>
              )}
            </div>
          </div>
          {/* 画面の変化のうち、開始と結果だけを1回ずつ読み上げる。途中の手順や経過秒数は通知しない。 */}
          <p role="status" aria-live="polite" className="sr-only">{props.announcement ?? ''}</p>
          <SenpaiComposer
            question={props.question} onQuestionChange={props.onQuestionChange} modelType={props.modelType} onModelChange={props.onModelChange}
            disabled={disabled} running={snapshot.running} sendError={props.sendError} disclaimer={disclaimer} placeholder={placeholder}
            maxLength={supplementLimit} hint={limitHint} warning={limitWarning}
            onSubmit={props.onSubmit} onCancel={props.onCancel}
          />
        </main>
      </div>
    </section>
  );
}
