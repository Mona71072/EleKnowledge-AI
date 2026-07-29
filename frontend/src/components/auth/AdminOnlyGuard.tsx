'use client';

import Link from 'next/link';
import { Loading } from '@/components/ui/Loading';
import { useAdminGate } from '@/hooks/useAdminGate';

interface AdminOnlyGuardProps {
  children: React.ReactNode;
  title?: string;
  description?: string;
  backHref?: string;
  backLabel?: string;
}

/**
 * Client-side admin gate for non-/admin shells (e.g. troubleshooting).
 * API routes must enforce the same rule server-side; this is UI-assist only.
 * Gate logic is shared with /admin layout via useAdminGate.
 */
export function AdminOnlyGuard({
  children,
  title = '管理者権限が必要です',
  description = 'この機能は開発中のため、管理者のみ利用できます。',
  backHref = '/',
  backLabel = 'ホームに戻る',
}: AdminOnlyGuardProps) {
  const state = useAdminGate();

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
          <div
            aria-hidden
            className="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-full bg-gray-200 text-gray-500"
          >
            <svg className="h-7 w-7" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"
              />
            </svg>
          </div>
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
