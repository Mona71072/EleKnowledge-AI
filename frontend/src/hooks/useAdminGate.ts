'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { getUserInfo } from '@/lib/auth-helpers';

export type AdminGateState = 'loading' | 'ok' | 'denied';

/**
 * Client-side admin gate. API routes must still enforce 403 server-side.
 * Shared by AdminOnlyGuard and /admin layout so checks don't drift.
 */
export function useAdminGate(): AdminGateState {
  const router = useRouter();
  const [state, setState] = useState<AdminGateState>('loading');

  useEffect(() => {
    let cancelled = false;
    (async () => {
      const info = await getUserInfo();
      if (cancelled) return;
      if (!info) {
        router.replace('/login');
        return;
      }
      setState(info.isAdmin ? 'ok' : 'denied');
    })();
    return () => {
      cancelled = true;
    };
  }, [router]);

  return state;
}
