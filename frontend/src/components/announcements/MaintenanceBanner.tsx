'use client';

import { useState } from 'react';
import {
  Announcement,
  SEVERITY_META,
  isMaintenanceActive,
  absoluteTime,
} from '@/lib/announcements';

/**
 * Full-width banner shown while a maintenance window is active.
 * `critical` severity cannot be dismissed (A-11); info/warning can.
 */
export function MaintenanceBanner({ announcements }: { announcements: Announcement[] }) {
  const [dismissed, setDismissed] = useState<Set<string>>(new Set());

  const active = announcements.filter(
    (a) => isMaintenanceActive(a) && !dismissed.has(a.announcementId)
  );
  if (active.length === 0) return null;

  return (
    <div className="space-y-px">
      {active.map((a) => {
        const sev = SEVERITY_META[a.severity];
        const canDismiss = a.severity !== 'critical';
        return (
          <div
            key={a.announcementId}
            role="alert"
            className={`border-b ${sev.bannerClassName} px-4 py-2.5`}
          >
            <div className="max-w-7xl mx-auto flex items-center gap-3 text-sm">
              <span aria-hidden className="text-base">{sev.icon}</span>
              <span className="font-semibold">[{sev.label}]</span>
              <span className="flex-1 min-w-0 truncate">
                {a.title}
                {a.startAt && a.endAt && (
                  <span className="ml-2 opacity-80" title={`${absoluteTime(a.startAt)} 〜 ${absoluteTime(a.endAt)}`}>
                    （{absoluteTime(a.startAt)} 〜 {absoluteTime(a.endAt)}）
                  </span>
                )}
              </span>
              {canDismiss && (
                <button
                  type="button"
                  aria-label="閉じる"
                  className="flex-shrink-0 rounded p-1 hover:bg-black/5 focus:outline-none focus:ring-2 focus:ring-current"
                  onClick={() =>
                    setDismissed((prev) => new Set(prev).add(a.announcementId))
                  }
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
