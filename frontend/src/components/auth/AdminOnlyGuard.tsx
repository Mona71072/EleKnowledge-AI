'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { getUserInfo } from '@/lib/auth-helpers';
import { Loading } from '@/components/ui/Loading';

interface AdminOnlyGuardProps {
  children: React.ReactNode;
  title?: string;
  description?: string;
  backHref?: string;
  backLabel?: string;
}

/**
 * Client-side admin gate for features still under development.
 * API routes must enforce the same rule server-side; this is UI-assist only.
 */
export function AdminOnlyGuard({
  children,
  title = '管理者権限が必要です',
  description = 'この機能は開発中のため、管理者のみ利用できます。',
  backHref = '/',
  backLabel = 'ホームに戻る',
}: AdminOnlyGuardProps) {
  const router = useRouter();
  const [state, setState] = useState<'loading' | 'ok' | 'denied'>('loading');

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
          <h1 className="text-xl font-bold text-gray-900 mb-2">{title}</h1>
          <p className="text-sm text-gray-600 mb-4">{description}</p>
          <Link href={backHref} className="text-blue-600 font-semibold underline underline-offset-2">
            {backLabel}
          </Link>
        </div>
      </div>
    );
  }

  return <>{children}</>;
}
