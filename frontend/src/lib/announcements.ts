import { getIdToken, authHeaders } from './auth-helpers';

const API_URL = process.env.NEXT_PUBLIC_APP_API_URL || '';

export type AnnouncementType = 'update' | 'maintenance' | 'notice';
export type Severity = 'info' | 'warning' | 'critical';
export type AnnouncementStatus = 'draft' | 'scheduled' | 'published';

export interface Announcement {
  announcementId: string;
  type: AnnouncementType;
  title: string;
  body: string;
  severity: Severity;
  status: AnnouncementStatus;
  publishAt: string;
  startAt?: string;
  endAt?: string;
  pinned?: boolean;
  createdBy?: string;
  createdAt?: string;
  updatedAt?: string;
}

export interface AnnouncementsResponse {
  announcements: Announcement[];
  serverTime: string;
}

export interface AnnouncementInput {
  type: AnnouncementType;
  title: string;
  body: string;
  severity: Severity;
  status: AnnouncementStatus;
  publishAt?: string;
  startAt?: string;
  endAt?: string;
  pinned?: boolean;
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const token = await getIdToken();
  const res = await fetch(`${API_URL}${path}`, {
    ...init,
    headers: {
      'Content-Type': 'application/json',
      ...authHeaders(token),
      ...(init?.headers || {}),
    },
  });
  if (!res.ok) {
    let message = `Request failed (${res.status})`;
    try {
      const data = await res.json();
      message = data.message || data.error || message;
    } catch {
      /* ignore */
    }
    const err = new Error(message) as Error & { status?: number };
    err.status = res.status;
    throw err;
  }
  return res.json() as Promise<T>;
}

/** Public feed: currently-published announcements. */
export function getAnnouncements(limit = 10): Promise<AnnouncementsResponse> {
  return request<AnnouncementsResponse>(`/announcements?limit=${limit}`);
}

/** Admin: list every announcement across all statuses. */
export function listAllAnnouncements(): Promise<{ announcements: Announcement[] }> {
  return request<{ announcements: Announcement[] }>(`/admin/announcements`);
}

/** Admin: create. */
export function createAnnouncement(input: AnnouncementInput) {
  return request<{ announcementId: string; status: string }>(`/admin/announcements`, {
    method: 'POST',
    body: JSON.stringify(input),
  });
}

/** Admin: update. */
export function updateAnnouncement(id: string, input: Partial<AnnouncementInput>) {
  return request<{ announcementId: string; status: string }>(`/admin/announcements/${id}`, {
    method: 'PUT',
    body: JSON.stringify(input),
  });
}

/** Admin: delete. */
export function deleteAnnouncement(id: string) {
  return request<{ message: string }>(`/admin/announcements/${id}`, { method: 'DELETE' });
}

// ---- presentation helpers -------------------------------------------------

export const TYPE_META: Record<AnnouncementType, { label: string; icon: string }> = {
  update: { label: 'アップデート', icon: '✨' },
  maintenance: { label: 'メンテナンス', icon: '🔧' },
  notice: { label: 'お知らせ', icon: 'ℹ️' },
};

// Severity uses icon + label + color (never color alone) — WCAG 1.4.1.
export const SEVERITY_META: Record<
  Severity,
  { label: string; icon: string; className: string; bannerClassName: string }
> = {
  info: {
    label: '情報',
    icon: 'ℹ️',
    className: 'text-blue-800 bg-blue-50 border-blue-200',
    bannerClassName: 'bg-blue-50 border-blue-300 text-blue-900',
  },
  warning: {
    label: '注意',
    icon: '⚠️',
    className: 'text-amber-900 bg-amber-50 border-amber-300',
    bannerClassName: 'bg-amber-50 border-amber-400 text-amber-900',
  },
  critical: {
    label: '重要',
    icon: '⛔',
    className: 'text-red-800 bg-red-50 border-red-300',
    bannerClassName: 'bg-red-50 border-red-400 text-red-900',
  },
};

/** Relative time in Japanese ("3日前"), with absolute fallback for the title attr. */
export function relativeTime(iso: string, now: Date = new Date()): string {
  const then = new Date(iso);
  const diffMs = now.getTime() - then.getTime();
  const min = Math.floor(diffMs / 60000);
  if (min < 1) return 'たった今';
  if (min < 60) return `${min}分前`;
  const hours = Math.floor(min / 60);
  if (hours < 24) return `${hours}時間前`;
  const days = Math.floor(hours / 24);
  if (days < 7) return `${days}日前`;
  const weeks = Math.floor(days / 7);
  if (weeks < 5) return `${weeks}週間前`;
  const months = Math.floor(days / 30);
  if (months < 12) return `${months}ヶ月前`;
  return `${Math.floor(days / 365)}年前`;
}

export function absoluteTime(iso: string): string {
  const d = new Date(iso);
  return d.toLocaleString('ja-JP', { dateStyle: 'medium', timeStyle: 'short' });
}

/** Days until a future date, floored at 0. Used for maintenance countdown. */
export function daysUntil(iso: string, now: Date = new Date()): number {
  const diff = new Date(iso).getTime() - now.getTime();
  return Math.max(0, Math.ceil(diff / (24 * 60 * 60 * 1000)));
}

/** Announcement is an active maintenance window right now. */
export function isMaintenanceActive(a: Announcement, now: Date = new Date()): boolean {
  if (a.type !== 'maintenance' || !a.startAt || !a.endAt) return false;
  const t = now.getTime();
  return new Date(a.startAt).getTime() <= t && t <= new Date(a.endAt).getTime();
}
