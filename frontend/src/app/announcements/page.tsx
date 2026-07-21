'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { getAnnouncements, Announcement, AnnouncementType, TYPE_META } from '@/lib/announcements';
import { AnnouncementsSection } from '@/components/announcements/AnnouncementsSection';

const TABS: { key: 'all' | AnnouncementType; label: string }[] = [
  { key: 'all', label: 'すべて' },
  { key: 'update', label: 'アップデート' },
  { key: 'maintenance', label: 'メンテナンス' },
  { key: 'notice', label: 'お知らせ' },
];

export default function AnnouncementsListPage() {
  const [all, setAll] = useState<Announcement[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [tab, setTab] = useState<'all' | AnnouncementType>('all');

  useEffect(() => {
    getAnnouncements(50)
      .then((res) => setAll(res.announcements))
      .catch((e) => setError((e as Error).message))
      .finally(() => setLoading(false));
  }, []);

  const filtered = tab === 'all' ? all : all.filter((a) => a.type === tab);

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex items-center justify-between">
          <h1 className="text-2xl font-bold text-gray-900">EleKnowledge</h1>
          <Link href="/" className="text-sm text-blue-600 font-semibold underline underline-offset-2">
            ← ホームに戻る
          </Link>
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex gap-1 mb-4 border-b border-gray-200" role="tablist" aria-label="種別">
          {TABS.map((t) => (
            <button
              key={t.key}
              role="tab"
              aria-selected={tab === t.key}
              onClick={() => setTab(t.key)}
              className={`px-4 py-2 text-sm border-b-2 -mb-px ${
                tab === t.key
                  ? 'border-blue-600 font-semibold text-blue-700'
                  : 'border-transparent text-gray-600 hover:text-gray-900'
              }`}
            >
              {t.key === 'all' ? t.label : `${TYPE_META[t.key as AnnouncementType].icon} ${t.label}`}
            </button>
          ))}
        </div>

        <AnnouncementsSection
          announcements={filtered}
          loading={loading}
          error={error}
          showSeeAll={false}
          max={50}
        />
      </main>
    </div>
  );
}
