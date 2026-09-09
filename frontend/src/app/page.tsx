'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { getCurrentUser, fetchUserAttributes, signOut } from 'aws-amplify/auth';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Loading } from '@/components/ui/Loading';
import { InfoModal, InfoModalPayload } from '@/components/ui/InfoModal';
import { getUserInfo } from '@/lib/auth-helpers';
import { getAnnouncements, Announcement } from '@/lib/announcements';
import { AnnouncementsSection } from '@/components/announcements/AnnouncementsSection';
import { MaintenanceBanner } from '@/components/announcements/MaintenanceBanner';
import { AdminViewToggle } from '@/components/admin/AdminViewToggle';

const GUIDE_COLLAPSED_KEY = 'home:guideCollapsed';

const QUICK_QUESTIONS = [
  'KE-LG の据付で注意すべきポイントは？',
  '異音が出るときに最初に確認する項目は？',
  'エラーコードの原因と対処を手順で教えて',
];

function getGreeting(): string {
  const h = new Date().getHours();
  if (h >= 5 && h < 11) return 'おはようございます';
  if (h >= 11 && h < 18) return 'こんにちは';
  return 'こんばんは';
}

export default function HomePage() {
  const router = useRouter();
  const [userAttributes, setUserAttributes] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [isDevBypass, setIsDevBypass] = useState(false);
  const [isAdmin, setIsAdmin] = useState(false);
  const [announcements, setAnnouncements] = useState<Announcement[]>([]);
  const [annLoading, setAnnLoading] = useState(true);
  const [annError, setAnnError] = useState<string | null>(null);
  const [infoModal, setInfoModal] = useState<InfoModalPayload | null>(null);
  const [quickQuestion, setQuickQuestion] = useState('');
  const [guideOpen, setGuideOpen] = useState(false);

  useEffect(() => {
    checkUser();
    // 初回訪問時はガイドを開いた状態にする（以降はユーザーの操作を記憶）
    setGuideOpen(window.localStorage.getItem(GUIDE_COLLAPSED_KEY) !== '1');
  }, []);

  // Admin membership + announcements feed (independent of the auth-attribute path)
  useEffect(() => {
    (async () => {
      const info = await getUserInfo();
      if (info) setIsAdmin(info.isAdmin);
    })();
    // バナーは期間中のメンテ告知を新しい告知に押し出されずに拾う必要があるため広めに取得し、
    // 一覧側は先頭 5 件だけ表示する（issue #94 B1）
    getAnnouncements(30)
      .then((res) => setAnnouncements(res.announcements))
      .catch((e) => setAnnError((e as Error).message))
      .finally(() => setAnnLoading(false));
  }, []);

  const checkUser = async () => {
    // 開発モード: 認証をスキップする場合
    const skipAuth = process.env.NEXT_PUBLIC_SKIP_AUTH === 'true';
    const canBypassAuth = skipAuth && process.env.NODE_ENV !== 'production';
    setIsDevBypass(canBypassAuth);

    if (skipAuth && !canBypassAuth) {
      console.warn('[HomePage] NEXT_PUBLIC_SKIP_AUTH is enabled, but bypass is disabled in production.');
    }

    if (canBypassAuth) {
      setUserAttributes({
        email: 'dev@example.com',
        name: '開発ユーザー',
      });
      setLoading(false);
      return;
    }

    try {
      await getCurrentUser();
      const attributes = await fetchUserAttributes();
      setUserAttributes(attributes);
    } catch (err) {
      router.push('/login');
    } finally {
      setLoading(false);
    }
  };

  const handleSignOut = async () => {
    try {
      await signOut();
      router.push('/login');
    } catch (err) {
      console.error('Sign out error:', err);
    }
  };

  const goToChat = (question?: string) => {
    const q = (question ?? quickQuestion).trim();
    router.push(q ? `/chat?q=${encodeURIComponent(q)}` : '/chat');
  };

  const toggleGuide = () => {
    setGuideOpen((prev) => {
      window.localStorage.setItem(GUIDE_COLLAPSED_KEY, prev ? '1' : '0');
      return !prev;
    });
  };

  const scrollToHero = () => {
    document.getElementById('home-hero')?.scrollIntoView({ behavior: 'smooth', block: 'start' });
  };

  const displayName = userAttributes?.name || userAttributes?.email || 'ユーザー';

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <Loading size="lg" text="読み込み中..." />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Active-maintenance banner (critical cannot be dismissed) */}
      <MaintenanceBanner announcements={announcements} />

      {/* Header */}
      <header className="sticky top-0 z-40 bg-white/90 backdrop-blur border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-3 flex justify-between items-center gap-4">
          <div className="flex items-center gap-2.5 min-w-0">
            <div className="flex items-center justify-center h-9 w-9 rounded-lg bg-gradient-to-br from-blue-600 to-indigo-600 text-white flex-shrink-0" aria-hidden>
              <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
            </div>
            <div className="min-w-0">
              <div className="text-lg font-bold text-gray-900 leading-tight truncate">EleKnowledge</div>
              <div className="hidden sm:block text-[11px] text-gray-500 leading-tight">昇降機ナレッジ検索</div>
            </div>
          </div>

          {/* Admin-only view toggle (home <-> admin console) */}
          {isAdmin && <AdminViewToggle current="home" />}

          <div className="flex items-center gap-3 flex-shrink-0">
            <div className="hidden sm:block text-right leading-tight">
              <div className="text-sm font-semibold text-gray-900">{displayName}</div>
              <div className="text-xs text-gray-500">{userAttributes?.email || ''}</div>
            </div>
            <Button onClick={handleSignOut} variant="outline" size="sm">
              ログアウト
            </Button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {isDevBypass && (
          <div className="mb-6 rounded-lg border border-yellow-200 bg-yellow-50 p-4 text-sm text-yellow-900">
            <div className="flex items-start gap-2">
              <svg className="w-5 h-5 text-yellow-700 mt-0.5 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01M12 3a9 9 0 100 18 9 9 0 000-18z" />
              </svg>
              <div>
                <div className="font-semibold">開発モード</div>
                <div className="text-yellow-800">認証スキップが有効です（本番環境では無効化してください）。</div>
              </div>
            </div>
          </div>
        )}

        {/* Hero: greeting + quick-ask */}
        <section
          id="home-hero"
          aria-labelledby="hero-heading"
          className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-blue-600 via-indigo-600 to-indigo-700 px-6 py-8 sm:px-10 sm:py-10 mb-8 shadow-lg scroll-mt-24"
        >
          {/* Decorative circles */}
          <div aria-hidden className="pointer-events-none absolute -top-16 -right-16 h-56 w-56 rounded-full bg-white/10" />
          <div aria-hidden className="pointer-events-none absolute -bottom-24 -left-10 h-64 w-64 rounded-full bg-white/5" />

          <div className="relative">
            <h2 id="hero-heading" className="text-2xl sm:text-3xl font-bold text-white">
              {getGreeting()}、{displayName}さん
            </h2>
            <p className="mt-1.5 text-blue-100 text-sm sm:text-base">
              困りごとをそのまま入力してください。技術資料を検索し、根拠つきで回答します。
            </p>

            <form
              className="mt-5 flex flex-col sm:flex-row gap-2 max-w-3xl"
              onSubmit={(e) => {
                e.preventDefault();
                goToChat();
              }}
            >
              <div className="relative flex-1">
                <svg
                  aria-hidden
                  className="absolute left-3.5 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-4.35-4.35M17 10.5a6.5 6.5 0 11-13 0 6.5 6.5 0 0113 0z" />
                </svg>
                <input
                  type="text"
                  value={quickQuestion}
                  onChange={(e) => setQuickQuestion(e.target.value)}
                  placeholder="例: KE-LG の据付で注意すべきポイントは？"
                  aria-label="チャットへの質問"
                  className="w-full rounded-xl border-0 bg-white pl-11 pr-4 py-3.5 text-sm sm:text-base text-gray-900 placeholder:text-gray-400 shadow-md focus:outline-none focus:ring-2 focus:ring-white/70"
                />
              </div>
              <Button
                type="submit"
                variant="primary"
                size="lg"
                className="bg-gray-900 hover:bg-gray-800 focus:ring-white shadow-md flex-shrink-0"
              >
                質問する
                <svg className="ml-2 w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden>
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                </svg>
              </Button>
            </form>

            <div className="mt-4 flex flex-wrap items-center gap-2">
              <span className="text-xs text-blue-100">質問例:</span>
              {QUICK_QUESTIONS.map((q) => (
                <button
                  key={q}
                  type="button"
                  onClick={() => goToChat(q)}
                  className="rounded-full bg-white/15 hover:bg-white/25 text-white text-xs px-3 py-1.5 transition-colors focus:outline-none focus:ring-2 focus:ring-white/70"
                >
                  {q}
                </button>
              ))}
            </div>
          </div>
        </section>

        {/* Feature Cards */}
        <section aria-labelledby="features-heading" className="mb-8">
          <h2 id="features-heading" className="text-lg font-semibold text-gray-900 mb-3">
            機能
          </h2>
          <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
            <Link href="/chat" className="group block h-full">
              <Card variant="default" padding="md" className="h-full group-hover:shadow-xl transition-all duration-300 transform group-hover:-translate-y-1 border-2 border-transparent group-hover:border-blue-200">
                <div className="flex items-start justify-between">
                  <div className="flex items-center justify-center h-14 w-14 rounded-xl bg-gradient-to-br from-blue-500 to-blue-600 text-white mb-4 group-hover:from-blue-600 group-hover:to-blue-700 transition-all duration-300 shadow-md">
                    <svg className="h-7 w-7" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
                    </svg>
                  </div>
                  <span className="inline-flex items-center px-3 py-1.5 bg-green-100 text-green-800 text-xs font-semibold rounded-full border border-green-200">
                    <svg className="w-3 h-3 mr-1" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                    </svg>
                    利用可能
                  </span>
                </div>
                <h3 className="text-xl font-semibold text-gray-900 group-hover:text-blue-600 transition-colors mb-2">RAGチャット</h3>
                <p className="text-sm text-gray-600 leading-relaxed">
                  Knowledge Base を検索して、参考資料（根拠）つきで質問に回答します。資料タイプや機種での絞り込みにも対応。
                </p>
                <div className="mt-4 inline-flex items-center text-sm font-semibold text-blue-600 group-hover:text-blue-700">
                  今すぐ開く
                  <svg className="ml-1 w-4 h-4 transition-transform group-hover:translate-x-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden>
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                  </svg>
                </div>
              </Card>
            </Link>

            {isAdmin ? (
              <Link href="/troubleshooting" className="group block h-full">
                <Card variant="default" padding="md" className="h-full group-hover:shadow-xl transition-all duration-300 transform group-hover:-translate-y-1 border-2 border-transparent group-hover:border-purple-200">
                  <div className="flex items-start justify-between">
                    <div className="flex items-center justify-center h-14 w-14 rounded-xl bg-gradient-to-br from-purple-500 to-purple-600 text-white mb-4 group-hover:from-purple-600 group-hover:to-purple-700 transition-all duration-300 shadow-md">
                      <svg className="h-7 w-7" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                      </svg>
                    </div>
                    <span className="inline-flex items-center px-3 py-1.5 bg-purple-100 text-purple-800 text-xs font-semibold rounded-full border border-purple-200">
                      <svg className="w-3 h-3 mr-1" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z" clipRule="evenodd" />
                      </svg>
                      開発中
                    </span>
                  </div>
                  <h3 className="text-xl font-semibold text-gray-900 group-hover:text-purple-600 transition-colors mb-2">トラブルシューティング</h3>
                  <p className="text-sm text-gray-600 leading-relaxed">
                    現場トラブルの原因分析と対処方法を提案します。工事番号や機種・エラーコードから横断検索。
                  </p>
                  <div className="mt-4 inline-flex items-center text-sm font-semibold text-purple-600 group-hover:text-purple-700">
                    開く（管理者向け）
                    <svg className="ml-1 w-4 h-4 transition-transform group-hover:translate-x-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden>
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                    </svg>
                  </div>
                </Card>
              </Link>
            ) : (
              <Card variant="default" padding="md" className="h-full bg-gray-50 border border-dashed border-gray-300">
                <div className="flex items-start justify-between">
                  <div className="flex items-center justify-center h-14 w-14 rounded-xl bg-gray-300 text-gray-500 mb-4">
                    <svg className="h-7 w-7" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                    </svg>
                  </div>
                  <span className="inline-flex items-center px-3 py-1.5 bg-gray-200 text-gray-600 text-xs font-semibold rounded-full border border-gray-300">
                    <svg className="w-3 h-3 mr-1" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M5 9V7a5 5 0 0110 0v2a2 2 0 012 2v5a2 2 0 01-2 2H5a2 2 0 01-2-2v-5a2 2 0 012-2zm8-2v2H7V7a3 3 0 016 0z" clipRule="evenodd" />
                    </svg>
                    開発中
                  </span>
                </div>
                <h3 className="text-xl font-semibold text-gray-500 mb-2">トラブルシューティング</h3>
                <p className="text-sm text-gray-500 leading-relaxed">
                  現場トラブルの原因分析と対処方法の提案機能を準備中です。公開までしばらくお待ちください。
                </p>
              </Card>
            )}
          </div>
        </section>

        {/* はじめてガイド（折りたたみ・状態を記憶） — 機能の直後に配置 */}
        <section aria-labelledby="guide-heading" className="mb-8">
          <div className="rounded-xl border border-gray-200 bg-white shadow-sm overflow-hidden">
            <button
              type="button"
              onClick={toggleGuide}
              aria-expanded={guideOpen}
              aria-controls="guide-body"
              className="w-full flex items-center justify-between gap-3 px-5 py-4 text-left hover:bg-gray-50 transition-colors focus:outline-none focus:ring-2 focus:ring-inset focus:ring-blue-500"
            >
              <div className="flex items-center gap-2.5 min-w-0 flex-1">
                <svg className="w-5 h-5 text-blue-600 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden>
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                </svg>
                <h2 id="guide-heading" className="text-base font-semibold text-gray-900 leading-snug">
                  はじめての方へ — 使い方ガイド
                </h2>
              </div>
              <svg
                className={`w-5 h-5 text-gray-400 flex-shrink-0 transition-transform ${guideOpen ? 'rotate-180' : ''}`}
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
                aria-hidden
              >
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
              </svg>
            </button>

            {guideOpen && (
              <div id="guide-body" className="px-5 pb-5 border-t border-gray-100 bg-gray-50/50">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-4 items-stretch">
                  <div className="flex flex-col rounded-lg border border-gray-200 bg-white p-4 h-full">
                    <div className="inline-flex items-center justify-center w-7 h-7 rounded-full bg-blue-600 text-white text-xs font-bold mb-2">1</div>
                    <div className="font-semibold text-gray-900">質問する</div>
                    <p className="mt-1.5 text-sm text-gray-600 leading-relaxed flex-1">
                      困りごとをそのまま入力します。ページ上部の検索ボックスや RAGチャットから始められます。
                    </p>
                    <button
                      type="button"
                      onClick={scrollToHero}
                      className="mt-3 text-sm font-semibold text-blue-600 hover:text-blue-700 underline underline-offset-2 text-left"
                    >
                      検索ボックスへ移動
                    </button>
                  </div>
                  <div className="flex flex-col rounded-lg border border-gray-200 bg-white p-4 h-full">
                    <div className="inline-flex items-center justify-center w-7 h-7 rounded-full bg-blue-600 text-white text-xs font-bold mb-2">2</div>
                    <div className="font-semibold text-gray-900">根拠を確認する</div>
                    <p className="mt-1.5 text-sm text-gray-600 leading-relaxed flex-1">
                      回答に表示される参考資料（引用）を確認し、現場判断に活用します。
                    </p>
                    <button
                      className="mt-3 text-sm font-semibold text-blue-600 hover:text-blue-700 underline underline-offset-2 text-left"
                      type="button"
                      onClick={() =>
                        setInfoModal({
                          title: '根拠（参考資料）の見方',
                          description: 'チャット画面で「参考資料」から資料名を確認できます。必要ならフィルターで資料タイプ/モデルを指定して再質問できます。',
                          bullets: [
                            '参考資料の上位3件をまず確認',
                            '必要なら「さらに表示」で追加資料も確認',
                            'フィルター指定で資料のブレを減らす',
                          ],
                        })
                      }
                    >
                      参考資料の見方
                    </button>
                  </div>
                  <div className="flex flex-col rounded-lg border border-gray-200 bg-white p-4 h-full">
                    <div className="inline-flex items-center justify-center w-7 h-7 rounded-full bg-blue-600 text-white text-xs font-bold mb-2">3</div>
                    <div className="font-semibold text-gray-900">絞り込む</div>
                    <p className="mt-1.5 text-sm text-gray-600 leading-relaxed flex-1">
                      資料タイプや機種のフィルターを指定すると、回答の精度が上がります。
                    </p>
                    <button
                      className="mt-3 text-sm font-semibold text-blue-600 hover:text-blue-700 underline underline-offset-2 text-left"
                      type="button"
                      onClick={() =>
                        setInfoModal({
                          title: 'Knowledge Base について',
                          description: 'Knowledge Baseは、回答の根拠となる技術資料の集合です。開発者が資料を登録・管理しており、あなたはチャットで質問することで、これらの資料を検索して回答を得られます。',
                          bullets: [
                            '技術資料（マニュアル/据付基準など）が登録されています',
                            '資料タイプ/製品/モデルでフィルター検索が可能です',
                            '回答には参考資料（根拠）が自動で表示されます',
                          ],
                        })
                      }
                    >
                      Knowledge Baseとは
                    </button>
                  </div>
                </div>
              </div>
            )}
          </div>
        </section>

        {/* 運営からのお知らせ */}
        <AnnouncementsSection
          announcements={announcements.slice(0, 5)}
          loading={annLoading}
          error={annError}
        />
      </main>

      {/* Info Modal */}
      {infoModal && <InfoModal payload={infoModal} onClose={() => setInfoModal(null)} />}
    </div>
  );
}
