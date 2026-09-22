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
 * Cognito のメール関連エラーの分類（issue #99）。
 *
 * - 'daily-limit'      : Cognito 既定メールの日次上限（1 ユーザープール 50 通/日）。本文に "Exceeded daily email limit"。
 *                        例外名は LimitExceededException でも CodeDeliveryFailureException でも来るため本文で判定する
 * - 'attempt-limit'    : 同一利用者の試行回数制限（LimitExceededException / TooManyRequestsException で本文が上記以外）
 * - 'delivery-failure' : 確認コードの配信失敗（CodeDeliveryFailureException で本文が上記以外）
 * - 'user-not-found'   : 対象ユーザーが存在しない（再送でサインアップ未完了の場合など）
 * - 'unknown'          : その他
 *
 * 注意: SignUp が daily-limit で失敗しても、ユーザーは UNCONFIRMED で作成済みの場合がある。
 * 「登録全体が失敗した」と扱って新規登録を繰り返させず、翌日に確認画面の再送へ誘導する。
 */
export type AuthErrorKind = 'daily-limit' | 'attempt-limit' | 'delivery-failure' | 'user-not-found' | 'unknown';

export function classifyAuthError(err: unknown): AuthErrorKind {
  const name = (err as { name?: string } | null)?.name ?? '';
  const message = ((err as { message?: string } | null)?.message ?? '').toLowerCase();
  if (message.includes('daily email limit') || message.includes('exceeded daily')) return 'daily-limit';
  if (name === 'LimitExceededException' || name === 'TooManyRequestsException') return 'attempt-limit';
  if (name === 'CodeDeliveryFailureException') return 'delivery-failure';
  if (name === 'UserNotFoundException') return 'user-not-found';
  return 'unknown';
}

/** 例外名・本文・呼び出した API を console に残す（問い合わせ時の切り分け用。トークン等は含めない）。 */
export function logAuthError(api: string, err: unknown): void {
  const e = err as { name?: string; message?: string } | null;
  console.error('[auth]', { api, name: e?.name, message: e?.message, kind: classifyAuthError(err) });
}

export const EMAIL_DELIVERY_LIMIT_MESSAGE =
  '本日のメール送信数が上限に達したため、確認コードを送信できませんでした。お手数ですが明日以降に再度お試しください。';
export const EMAIL_DELIVERY_LIMIT_SIGNUP_HINT =
  'アカウントは作成済みの場合があります。明日、確認画面の「確認コードを再送信」から続きを行ってください。' +
  '「アカウントが見つかりません」と表示された場合のみ、最初から登録し直してください。';
export const ATTEMPT_LIMIT_MESSAGE = '試行回数が多すぎます。しばらく時間をおいてからもう一度お試しください。';
export const DELIVERY_FAILURE_MESSAGE =
  '確認コードのメールを送信できませんでした。メールアドレスをご確認のうえ、しばらくしてから再度お試しください。';

/** 想定外のエラーに、問い合わせ時の切り分け用にエラー名を添える。 */
export function withErrorName(base: string, err: unknown): string {
  const name = (err as { name?: string } | null)?.name;
  return name ? `${base}（エラー: ${name}）` : base;
}
