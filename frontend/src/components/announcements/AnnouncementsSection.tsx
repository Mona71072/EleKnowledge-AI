'use client';

import { useEffect, useMemo, useState } from 'react';
import Link from 'next/link';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { getCurrentUser } from 'aws-amplify/auth';
import { announcementDate, loadReadAnnouncementIds, markAnnouncementRead } from '@/lib/announcement-display.mjs';
import {
  Announcement,
  TYPE_META,
  SEVERITY_META,
  absoluteTime,
  daysUntil,
} from '@/lib/announcements';

interface Props {
  announcements: Announcement[];
  loading?: boolean;
  error?: string | null;
  /** show the "すべて見る" link (hidden on the dedicated list page) */
  showSeeAll?: boolean;
  max?: number;
}

export function AnnouncementsSection({
  announcements,
  loading = false,
  error = null,
  showSeeAll = true,
  max = 5,
}: Props) {
  const [readKey, setReadKey] = useState<string | null>(null);
  const [readIds, setReadIds] = useState<string[]>([]);
  const [selected, setSelected] = useState<Announcement | null>(null);

  useEffect(() => {
    let cancelled = false;
    getCurrentUser().then((user) => {
      if (cancelled) return;
      const key = `announcements:readIds:${user.userId}`;
      setReadKey(key);
      setReadIds((current) => [...new Set([...current, ...loadReadAnnouncementIds(key)])]);
    }).catch(() => {
      // Keep read state in memory if identity cannot be resolved.
    });
    return () => { cancelled = true; };
  }, []);

  useEffect(() => {
    if (!readKey) return;
    const syncRead = (event: StorageEvent) => {
      if (event.key === readKey || event.key === null) {
        setReadIds(loadReadAnnouncementIds(readKey));
      }
    };
    window.addEventListener('storage', syncRead);
    return () => window.removeEventListener('storage', syncRead);
  }, [readKey]);

  useEffect(() => {
    if (!readKey || readIds.length === 0) return;
    // Persist clicks made while the authenticated identity was still loading.
    const mergedIds = markAnnouncementRead(readKey, readIds[0], readIds);
    if (mergedIds.length !== readIds.length) setReadIds(mergedIds);
  }, [readKey, readIds]);

  useEffect(() => {
    if (!selected) return;
    const onKey = (e: KeyboardEvent) => e.key === 'Escape' && setSelected(null);
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [selected]);

  const items = useMemo(() => announcements.slice(0, max), [announcements, max]);
  const unreadCount = useMemo(
    () =>
      announcements.filter((a) => !readIds.includes(a.announcementId)).length,
    [announcements, readIds]
  );

  const isNew = (a: Announcement) => !readIds.includes(a.announcementId);
  const openAnnouncement = (a: Announcement) => {
    setSelected(a);
    setReadIds((current) => [...new Set([...current, a.announcementId])]);
  };

  return (
    <section aria-labelledby="announcements-heading" className="mb-8">
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <span aria-hidden className="text-lg">📢</span>
          <h2 id="announcements-heading" className="text-lg font-semibold text-gray-900">
            運営からのお知らせ
          </h2>
          {unreadCount > 0 && (
            <span className="inline-flex items-center gap-1 rounded-full bg-red-100 text-red-700 text-xs font-semibold px-2 py-0.5 border border-red-200">
              <span aria-hidden>🔴</span> 新着 {unreadCount}件
            </span>
          )}
        </div>
        {showSeeAll && (
          <Link
            href="/announcements"
            className="text-sm font-semibold text-blue-600 hover:text-blue-700 underline underline-offset-2"
          >
            すべて見る →
          </Link>
        )}
      </div>

      <div className="rounded-lg border border-gray-200 bg-white divide-y divide-gray-100">
        {loading ? (
          <div className="p-4 space-y-3" aria-busy="true" aria-label="読み込み中">
            {[0, 1, 2].map((i) => (
              <div key={i} className="h-5 bg-gray-100 rounded animate-pulse" />
            ))}
          </div>
        ) : error ? (
          <div className="p-6 text-sm text-red-700">お知らせを読み込めませんでした：{error}</div>
        ) : items.length === 0 ? (
          <div className="p-8 text-center text-sm text-gray-500">
            <div aria-hidden className="text-2xl mb-2">🕊️</div>
            現在お知らせはありません。
          </div>
        ) : (
          items.map((a) => {
            const type = TYPE_META[a.type];
            const sev = SEVERITY_META[a.severity];
            const upcoming =
              a.type === 'maintenance' && a.startAt && new Date(a.startAt) > new Date()
                ? daysUntil(a.startAt)
                : null;
            return (
              <button
                key={a.announcementId}
                type="button"
                onClick={() => openAnnouncement(a)}
                className="w-full text-left px-4 py-3 flex items-center gap-3 hover:bg-gray-50 focus:outline-none focus:bg-blue-50"
              >
                {a.pinned && <span aria-label="固定" title="固定" className="flex-shrink-0">📌</span>}
                <span aria-hidden className="flex-shrink-0">{type.icon}</span>
                <span
                  className={`flex-shrink-0 inline-flex items-center gap-1 rounded px-1.5 py-0.5 text-xs font-medium border ${sev.className}`}
                >
                  <span aria-hidden>{sev.icon}</span>
                  {type.label}
                </span>
                <span className="flex-1 min-w-0 truncate text-sm text-gray-900">{a.title}</span>
                {upcoming !== null && (
                  <span className="flex-shrink-0 text-xs font-semibold text-amber-700">
                    あと{upcoming}日
                  </span>
                )}
                <span
                  className="flex-shrink-0 text-xs text-gray-500"
                  title={announcementDate(a.publishAt)}
                >
                  {announcementDate(a.publishAt)}
                </span>
                {isNew(a) && (
                  <span className="flex-shrink-0 rounded bg-red-500 text-white text-[10px] font-bold px-1.5 py-0.5">
                    NEW
                  </span>
                )}
              </button>
            );
          })
        )}
      </div>

      {/* Detail modal */}
      {selected && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center px-4 py-6"
          role="dialog"
          aria-modal="true"
          aria-label={selected.title}
          onClick={() => setSelected(null)}
        >
          <div className="absolute inset-0 bg-black/40" />
          <div
            className="relative w-full max-w-2xl mx-auto rounded-xl bg-white shadow-xl border border-gray-200 p-6 max-h-[80vh] overflow-y-auto"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-start justify-between gap-4 mb-3">
              <div className="flex items-center gap-2 flex-wrap">
                <span aria-hidden>{TYPE_META[selected.type].icon}</span>
                <span
                  className={`inline-flex items-center gap-1 rounded px-1.5 py-0.5 text-xs font-medium border ${SEVERITY_META[selected.severity].className}`}
                >
                  <span aria-hidden>{SEVERITY_META[selected.severity].icon}</span>
                  {TYPE_META[selected.type].label}
                </span>
                <h3 className="text-lg font-bold text-gray-900">{selected.title}</h3>
              </div>
              <button
                type="button"
                aria-label="閉じる"
                className="flex-shrink-0 p-1.5 rounded-lg text-gray-400 hover:bg-gray-100 hover:text-gray-700"
                onClick={() => setSelected(null)}
              >
                <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            <div className="text-xs text-gray-500 mb-4" title={announcementDate(selected.publishAt)}>
              {announcementDate(selected.publishAt)}
              {selected.startAt && selected.endAt && (
                <span className="ml-2">
                  ／ 期間: {absoluteTime(selected.startAt)} 〜 {absoluteTime(selected.endAt)}
                </span>
              )}
            </div>
            {/* react-markdown does not render raw HTML by default -> safe */}
            <div className="announcement-markdown text-gray-800">
              <ReactMarkdown remarkPlugins={[remarkGfm]}>{selected.body}</ReactMarkdown>
            </div>
          </div>
        </div>
      )}
    </section>
  );
}
