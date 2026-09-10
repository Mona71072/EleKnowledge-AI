'use client';

import { useState } from 'react';
import Link from 'next/link';
import {
  Announcement,
  SEVERITY_META,
  isMaintenanceActive,
  isNoticeActiveInChat,
  absoluteTime,
} from '@/lib/announcements';

/**
 * チャット画面の帯（設計 2026-09-10 dashboard v2 §10.4）。
 * 期間中のメンテナンスと、showInChat の告知（障害中・復旧など）を出す。
 * critical は閉じられない（MaintenanceBanner と同じ規則）。
 */
export function NoticeBanner({ announcements }: { announcements: Announcement[] }) {
  const [dismissed, setDismissed] = useState<Set<string>>(new Set());

  const active = announcements.filter(
    (a) => (isMaintenanceActive(a) || isNoticeActiveInChat(a)) && !dismissed.has(a.announcementId),
  );
  if (active.length === 0) return null;

  return (
    <div className="space-y-px flex-shrink-0">
      {active.map((a) => {
        const sev = SEVERITY_META[a.severity];
        const canDismiss = a.severity !== 'critical';
        return (
          <div key={a.announcementId} role="alert" className={`border-b ${sev.bannerClassName} px-4 py-2`}>
            <div className="max-w-7xl mx-auto flex items-center gap-3 text-sm">
              <span aria-hidden className="text-base">
                {sev.icon}
              </span>
              <span className="font-semibold">[{sev.label}]</span>
              <span className="flex-1 min-w-0 truncate">
                {a.title}
                {a.type === 'maintenance' && a.startAt && a.endAt && (
                  <span className="ml-2 opacity-80" title={`${absoluteTime(a.startAt)} 〜 ${absoluteTime(a.endAt)}`}>
                    （{absoluteTime(a.startAt)} 〜 {absoluteTime(a.endAt)}）
                  </span>
                )}
              </span>
              <Link href="/announcements" className="flex-shrink-0 text-xs underline underline-offset-2 opacity-80 hover:opacity-100">
                詳細
              </Link>
              {canDismiss && (
                <button
                  type="button"
                  aria-label="閉じる"
                  className="flex-shrink-0 rounded p-1 hover:bg-black/5 focus:outline-none focus:ring-2 focus:ring-current"
                  onClick={() => setDismissed((prev) => new Set(prev).add(a.announcementId))}
                >
                  <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              )}
            </div>
          </div>
        );
      })}
    </div>
  );
}
