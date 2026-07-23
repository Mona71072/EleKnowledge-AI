'use client';

import { useEffect, useState } from 'react';
import { usePathname, useRouter } from 'next/navigation';
import Link from 'next/link';
import { getUserInfo } from '@/lib/auth-helpers';
import { AdminViewToggle } from '@/components/admin/AdminViewToggle';
import { Loading } from '@/components/ui/Loading';

/**
 * Admin console shell (A-18): guards admin access (client-side redirect; the API
 * enforces 403 server-side too), renders the home<->admin toggle and the console
 * sub-nav (dashboard / announcements).
 */
export default function AdminLayout({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const pathname = usePathname();
  const [state, setState] = useState<'loading' | 'ok' | 'denied'>('loading');
  const [name, setName] = useState('');

  useEffect(() => {
    (async () => {
      const info = await getUserInfo();
      if (!info) {
        router.replace('/login');
        return;
      }
      if (!info.isAdmin) {
        setState('denied');
        return;
      }
      setName(info.name);
      setState('ok');
    })();
  }, [router]);

  if (state === 'loading') {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <Loading size="lg" text="読み込み中..." />
      </div>
    );
  }

  if (state === 'denied') {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 px-4">
        <div className="max-w-md text-center">
          <div aria-hidden className="text-4xl mb-3">🔒</div>
          <h1 className="text-xl font-bold text-gray-900 mb-2">管理者権限が必要です</h1>
          <p className="text-sm text-gray-600 mb-4">
            この画面は運営（admin）のみ利用できます。
          </p>
          <Link href="/" className="text-blue-600 font-semibold underline underline-offset-2">
            ホームに戻る
          </Link>
        </div>
      </div>
    );
  }

  const subNav = [
    { href: '/admin/dashboard', label: '📊 ダッシュボード' },
    { href: '/admin/announcements', label: '📢 お知らせ管理' },
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex items-center justify-between gap-4">
          <h1 className="text-2xl font-bold text-gray-900">EleKnowledge</h1>
          <AdminViewToggle current="admin" />
          <div className="hidden sm:block text-sm text-gray-600">{name}</div>
        </div>
        <nav className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex gap-1" aria-label="管理コンソール">
          {subNav.map((item) => {
            const active = pathname === item.href;
            return (
              <Link
                key={item.href}
                href={item.href}
                aria-current={active ? 'page' : undefined}
                className={`px-4 py-2 text-sm border-b-2 -mb-px ${
                  active
                    ? 'border-blue-600 font-semibold text-blue-700'
                    : 'border-transparent text-gray-600 hover:text-gray-900'
                }`}
              >
                {item.label}
              </Link>
            );
          })}
        </nav>
      </header>
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">{children}</main>
    </div>
  );
}
