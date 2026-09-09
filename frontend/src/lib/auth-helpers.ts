import { fetchAuthSession } from 'aws-amplify/auth';

const ADMIN_GROUP = process.env.NEXT_PUBLIC_ADMIN_GROUP || 'admin';

function devBypass(): boolean {
  return (
    process.env.NEXT_PUBLIC_SKIP_AUTH === 'true' &&
    process.env.NODE_ENV !== 'production'
  );
}

export interface UserInfo {
  email: string;
  name: string;
  isAdmin: boolean;
}

/** Cognito ID token as a bearer string (or null when unauthenticated). */
export async function getIdToken(): Promise<string | null> {
  if (devBypass()) return 'dev-token';
  try {
    const session = await fetchAuthSession();
    return session.tokens?.idToken?.toString() || null;
  } catch {
    return null;
  }
}

/** Resolve identity + admin membership from the Cognito ID token claims. */
export async function getUserInfo(): Promise<UserInfo | null> {
  if (devBypass()) {
    // Toggle admin in dev via NEXT_PUBLIC_DEV_ADMIN=true
    return {
      email: 'dev@example.com',
      name: '開発ユーザー',
      isAdmin: process.env.NEXT_PUBLIC_DEV_ADMIN === 'true',
    };
  }
  try {
    const session = await fetchAuthSession();
    const payload = session.tokens?.idToken?.payload as Record<string, unknown> | undefined;
    if (!payload) return null;
    const rawGroups = payload['cognito:groups'];
    const groups = Array.isArray(rawGroups)
      ? (rawGroups as string[])
      : typeof rawGroups === 'string'
        ? rawGroups.split(',').map((g) => g.trim())
        : [];
    return {
      email: (payload.email as string) || '',
      name: (payload.name as string) || (payload.email as string) || 'ユーザー',
      isAdmin: groups.includes(ADMIN_GROUP),
    };
  } catch {
    return null;
  }
}

export function authHeaders(token: string | null): Record<string, string> {
  return token ? { Authorization: `Bearer ${token}` } : {};
}

/**
 * Cognito の既定メール送信は 1 ユーザープールあたり 1 日 50 通で止まる（確認コード・再送・パスワード再設定が共有）。
 * 上限超過や配信失敗のとき Amplify が投げるエラー名を判定する。issue #99。
 */
export function isEmailDeliveryLimitError(err: unknown): boolean {
  const name = (err as { name?: string } | null)?.name ?? '';
  const message = ((err as { message?: string } | null)?.message ?? '').toLowerCase();
  // 日次上限の超過は「配信失敗」として返る（本文に daily email limit）。
  // LimitExceededException は同一利用者の試行回数制限で別原因のため、ここには含めない。
  return (
    name === 'CodeDeliveryFailureException' ||
    message.includes('daily email limit') ||
    message.includes('exceeded daily')
  );
}

/** 同一利用者の再送・試行が多すぎるときの Cognito エラー（上限超過とは別原因）。 */
export function isAttemptLimitError(err: unknown): boolean {
  const name = (err as { name?: string } | null)?.name ?? '';
  return name === 'LimitExceededException' || name === 'TooManyRequestsException';
}

export const ATTEMPT_LIMIT_MESSAGE = '試行回数が多すぎます。しばらく時間をおいてからもう一度お試しください。';

/** 想定外のエラーに、問い合わせ時の切り分け用にエラー名を添える。 */
export function withErrorName(base: string, err: unknown): string {
  const name = (err as { name?: string } | null)?.name;
  return name ? `${base}（エラー: ${name}）` : base;
}

export const EMAIL_DELIVERY_LIMIT_MESSAGE =
  '本日のメール送信数が上限に達したため、確認コードを送信できませんでした。お手数ですが明日以降に再度お試しください。' +
  '（既に登録操作を行った方は、翌日に「確認コードを再送信」から続きを行えます）';
