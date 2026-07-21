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
