'use client';

import { useEffect, useState } from 'react';
import type { SenpaiResearchState } from '@/lib/knowledge-senpai-chat.mjs';
import { buildTimelineRows, type SenpaiResearchStepStatus, type SenpaiResearchStep } from '@/lib/knowledge-senpai-research.mjs';
import { formatElapsed, isRedundantDetail, stepRowLabel } from '@/lib/knowledge-senpai-research-view.mjs';

const STATUS_VIEW: Record<SenpaiResearchStepStatus, { icon: string; label: string; className: string }> = {
  running: { icon: '●', label: '実行中', className: 'animate-pulse motion-reduce:animate-none text-violet-600' },
  done: { icon: '✓', label: '完了', className: 'text-gray-500' },
  skipped: { icon: '–', label: '省略', className: 'text-gray-500' },
  failed: { icon: '✕', label: '失敗', className: 'text-red-600' },
};

function useNow(active: boolean) {
  const [now, setNow] = useState(() => Date.now());
  useEffect(() => {
    if (!active || typeof window === 'undefined') return undefined;
    setNow(Date.now());
    const id = window.setInterval(() => setNow(Date.now()), 1000);
    return () => window.clearInterval(id);
  }, [active]);
  return now;
}

function elapsedMs(research: Pick<SenpaiResearchState, 'startedAt' | 'endedAt'>, steps: readonly SenpaiResearchStep[], now: number) {
  const first = steps.length ? Date.parse(steps[0].startedAt) : Number.NaN;
  const start = research.startedAt ?? first;
  if (!Number.isFinite(start)) return undefined;
  return (research.endedAt ?? now) - start;
}

type Rows = ReturnType<typeof buildTimelineRows>;

function StepList({ rows, active }: { rows: Rows; active: boolean }) {
  const hasDetail = (row: Rows[number]) => Boolean(row.detailJa) && !isRedundantDetail(row);
  return (
    <ol aria-label="調査の進み具合" className="mt-2 space-y-1 border-l border-gray-200 pl-3">
      {rows.map((row) => {
        const view = STATUS_VIEW[row.status];
        const current = active && row.status === 'running';
        return (
          <li key={row.key} aria-current={current ? 'step' : undefined} className={`flex items-baseline gap-2 text-xs ${current ? 'font-medium text-gray-900' : 'text-gray-700'}`}>
            <span role="img" aria-label={view.label} className={`w-3 shrink-0 text-center ${view.className}`}>{view.icon}</span>
            <span className="min-w-0 flex-1">
              {stepRowLabel(row)}
              {hasDetail(row) && <span title={row.detailJa} className="line-clamp-1 block break-all font-normal text-gray-500">{row.detailJa}</span>}
            </span>
          </li>
        );
      })}
    </ol>
  );
}

const textButton = 'rounded px-2 text-xs text-gray-500 underline-offset-2 hover:text-gray-900 hover:underline focus:outline-none focus-visible:ring-2 focus-visible:ring-violet-500';

/**
 * 調査の進み具合を1行で示す。実行中は「現在の手順…」と経過時間、終わったら「14秒・7手順で調査」。
 * 「詳細」から手順の一覧を開ける。
 */
export function SenpaiStepTimeline({ research }: {
  research: Pick<SenpaiResearchState, 'status' | 'steps' | 'startedAt' | 'endedAt' | 'waiting'>;
}) {
  const active = research.status === 'queued' || research.status === 'running';
  const now = useNow(active);
  const rows = buildTimelineRows(research.steps);
  const elapsed = elapsedMs(research, research.steps, now);

  if (active) {
    const current = [...rows].reverse().find((row) => row.status === 'running');
    return (
      // 進捗はスクリーンリーダーに逐一通知しない（開始と結果だけを、画面全体の通知欄が1回ずつ読み上げる）。
      <div className="text-sm text-gray-900">
        <details className="min-w-0">
          <summary className="flex min-h-10 cursor-pointer list-none flex-wrap items-center gap-x-2 gap-y-0.5 [&::-webkit-details-marker]:hidden">
            <span aria-hidden="true" className="inline-block h-2 w-2 shrink-0 animate-pulse motion-reduce:animate-none rounded-full bg-violet-500" />
            <span className="min-w-0 break-words font-medium">{research.waiting ? '前の調査の終了を待っています…' : current ? `${current.labelJa}…` : '調査を開始しています…'}</span>
            {elapsed !== undefined && <span aria-hidden="true" className="text-xs text-gray-500">経過 {formatElapsed(elapsed)}</span>}
            <span className={textButton}>詳細</span>
          </summary>
          {rows.length > 0 && <StepList rows={rows} active />}
        </details>
      </div>
    );
  }
  if (rows.length === 0) return null;
  return (
    <details className="text-xs text-gray-500">
      <summary className="flex min-h-10 cursor-pointer list-none items-center [&::-webkit-details-marker]:hidden">
        <span className="underline-offset-2 hover:text-gray-900 hover:underline">
          {elapsed !== undefined && `${formatElapsed(elapsed)}・`}{rows.length}手順で調査
        </span>
      </summary>
      <StepList rows={rows} active={false} />
    </details>
  );
}
