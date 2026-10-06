'use client';

import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import {
  Announcement,
  AnnouncementInput,
  AnnouncementType,
  Severity,
  AnnouncementStatus,
  TYPE_META,
  SEVERITY_META,
  listAllAnnouncements,
  createAnnouncement,
  updateAnnouncement,
  deleteAnnouncement,
  endAnnouncementNow,
  absoluteTime,
  isVisibleNow,
} from '@/lib/announcements';
import { ANNOUNCEMENT_TEMPLATES, getTemplate, fillTemplate, templatePlaceholders } from '@/lib/announcement-templates.mjs';
import { canEndAnnouncementNow, resolveAnnouncementPublishFields } from '@/lib/announcement-publish.mjs';
import { Button } from '@/components/ui/Button';
import { Loading } from '@/components/ui/Loading';

const STATUS_BADGE: Record<AnnouncementStatus | 'ended', { label: string; className: string; dotClass: string }> = {
  published: { label: '公開', className: 'text-green-700 bg-green-50 border-green-200', dotClass: 'bg-green-500' },
  scheduled: { label: '予約', className: 'text-amber-800 bg-amber-50 border-amber-300', dotClass: 'bg-amber-400' },
  draft: { label: '下書き', className: 'text-gray-600 bg-gray-50 border-gray-200', dotClass: 'bg-gray-400' },
  ended: { label: '終了', className: 'text-gray-500 bg-gray-50 border-gray-200', dotClass: 'bg-gray-300' },
};

const inputCls =
  'w-full border border-gray-300 rounded-lg px-3 py-2 text-sm bg-white text-gray-900 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors';

const TITLE_MAX = 120;

const emptyForm: AnnouncementInput = {
  type: 'notice',
  title: '',
  body: '',
  severity: 'info',
  status: 'draft',
  pinned: false,
  showInChat: false,
};

// datetime-local <-> ISO helpers
function toLocalInput(iso?: string): string {
  if (!iso) return '';
  const d = new Date(iso);
  const off = d.getTimezoneOffset();
  return new Date(d.getTime() - off * 60000).toISOString().slice(0, 16);
}
function fromLocalInput(v: string): string | undefined {
  return v ? new Date(v).toISOString() : undefined;
}
function nowJstLabel(): string {
  return new Date().toLocaleString('ja-JP', { month: 'numeric', day: 'numeric', hour: '2-digit', minute: '2-digit' });
}

function statusOf(a: Announcement, now: Date): AnnouncementStatus | 'ended' {
  if (a.status !== 'draft' && a.endAt && new Date(a.endAt).getTime() < now.getTime()) return 'ended';
  return a.status;
}

/**
 * お知らせ管理 v2（設計 docs/design-2026-09-10-dashboard-v2.md §10）。
 * いま表示中 → テンプレート → 一覧 → 編集フォーム。表示終了は削除ではなく endAt を今にする。
 */
export default function AdminAnnouncementsPage() {
  const [list, setList] = useState<Announcement[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [form, setForm] = useState<AnnouncementInput>(emptyForm);
  const [templateName, setTemplateName] = useState<string | null>(null);
  const [publishMode, setPublishMode] = useState<'now' | 'schedule'>('now');
  const [scheduleAt, setScheduleAt] = useState('');
  const [saving, setSaving] = useState(false);
  const [confirmDelete, setConfirmDelete] = useState<Announcement | null>(null);
  const [statusFilter, setStatusFilter] = useState<'all' | AnnouncementStatus>('all');
  const formRef = useRef<HTMLDivElement>(null);
  const titleInputRef = useRef<HTMLInputElement>(null);

  const scrollToForm = () => {
    setTimeout(() => {
      formRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' });
      titleInputRef.current?.focus();
    }, 50);
  };

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await listAllAnnouncements();
      setList(res.announcements);
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  const resetForm = () => {
    setForm(emptyForm);
    setEditingId(null);
    setTemplateName(null);
    setPublishMode('now');
    setScheduleAt('');
  };

  const applyTemplate = useCallback((key: string) => {
    const t = getTemplate(key);
    if (!t) return;
    setEditingId(null);
    setTemplateName(t.name);
    setForm({
      type: t.type,
      title: fillTemplate(t.title, { 日付: nowJstLabel().split(' ')[0] }),
      body: fillTemplate(t.body, { 時刻: nowJstLabel() }),
      severity: t.severity,
      status: 'draft',
      pinned: t.pinned,
      showInChat: t.showInChat,
    });
    setPublishMode('now');
    setScheduleAt('');
    scrollToForm();
  }, []);

  // ダッシュボード「いま」からの導線: /admin/announcements?template=incident
  useEffect(() => {
    if (typeof window === 'undefined') return;
    const key = new URLSearchParams(window.location.search).get('template');
    if (key) {
      applyTemplate(key);
      window.history.replaceState({}, '', window.location.pathname);
    }
  }, [applyTemplate]);

  const startEdit = (a: Announcement) => {
    setEditingId(a.announcementId);
    setTemplateName(null);
    setForm({
      type: a.type,
      title: a.title,
      body: a.body,
      severity: a.severity,
      status: a.status,
      pinned: a.pinned,
      showInChat: a.showInChat ?? a.severity === 'critical',
      startAt: a.startAt,
      endAt: a.endAt,
      publishAt: a.publishAt,
    });
    if (a.status === 'scheduled' && a.publishAt) {
      setPublishMode('schedule');
      setScheduleAt(toLocalInput(a.publishAt));
    } else {
      setPublishMode('now');
      setScheduleAt('');
    }
    scrollToForm();
  };

  const submit = async (status: AnnouncementStatus) => {
    if (!form.title.trim()) {
      setError('タイトルを入力してください');
      return;
    }
    if (form.type === 'maintenance' && (!form.startAt || !form.endAt)) {
      setError('メンテナンスは開始・終了日時が必要です');
      return;
    }
    if (status === 'published' && publishMode === 'schedule' && !scheduleAt) {
      setError('予約公開するには日時を指定してください');
      return;
    }
    const holes = [...templatePlaceholders(form.title), ...templatePlaceholders(form.body)];
    if (status === 'published' && holes.length > 0) {
      setError(`テンプレートの穴が埋まっていません: ${holes.map((h) => `{{${h}}}`).join(' ')}`);
      return;
    }
    setSaving(true);
    setError(null);
    try {
      const payload: AnnouncementInput = { ...form, status };
      if (form.type !== 'maintenance') {
        // 表示終了は全種別で使う。空にしたときは '' を送り、サーバー側で属性を消す
        payload.endAt = form.endAt || '';
        delete payload.startAt;
      }
      if (status === 'published') {
        const resolved = resolveAnnouncementPublishFields({
          requestedStatus: status,
          publishMode,
          scheduleAt,
          editingId,
          existingStatus: form.status,
          existingPublishAt: form.publishAt,
        });
        payload.status = resolved.status;
        payload.publishAt = resolved.publishAt;
      }
      if (editingId) {
        await updateAnnouncement(editingId, payload);
      } else {
        await createAnnouncement(payload);
      }
      resetForm();
      await load();
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setSaving(false);
    }
  };

  const endNow = async (a: Announcement) => {
    setError(null);
    try {
      await endAnnouncementNow(a.announcementId);
      if (editingId === a.announcementId) resetForm();
      await load();
    } catch (e) {
      setError((e as Error).message);
    }
  };

  const doDelete = async () => {
    if (!confirmDelete) return;
    try {
      await deleteAnnouncement(confirmDelete.announcementId);
      setConfirmDelete(null);
      if (editingId === confirmDelete.announcementId) resetForm();
      await load();
    } catch (e) {
      setError((e as Error).message);
    }
  };

  const now = useMemo(() => new Date(), [list]); // eslint-disable-line react-hooks/exhaustive-deps
  const active = useMemo(
    () =>
      list
        .filter((a) => isVisibleNow(a, now))
        .sort((a, b) => ({ critical: 0, warning: 1, info: 2 }[a.severity] - { critical: 0, warning: 1, info: 2 }[b.severity]) || b.publishAt.localeCompare(a.publishAt)),
    [list, now],
  );
  const filtered = list.filter((a) => statusFilter === 'all' || a.status === statusFilter);
  const holes = [...templatePlaceholders(form.title), ...templatePlaceholders(form.body)];

  return (
    <div>
      <div className="flex flex-wrap items-center justify-between gap-3 mb-6">
        <div>
          <h2 className="text-xl font-bold text-gray-900">お知らせ管理</h2>
          <p className="text-sm text-gray-500 mt-0.5">
            障害中・受付停止を利用者に伝える。文面は型から。表示終了は削除ではなく終了日時で · 全 {list.length} 件
          </p>
        </div>
        <div className="flex items-center gap-3">
          <label className="text-sm text-gray-600">
            状態:
            <select
              className="ml-2 border border-gray-300 rounded-lg px-2.5 py-1.5 text-sm bg-white focus:outline-none focus:ring-2 focus:ring-blue-500"
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value as typeof statusFilter)}
            >
              <option value="all">すべて</option>
              <option value="published">公開</option>
              <option value="scheduled">予約</option>
              <option value="draft">下書き</option>
            </select>
          </label>
          <Button
            variant="primary"
            size="sm"
            onClick={() => {
              resetForm();
              scrollToForm();
            }}
          >
            <svg className="w-4 h-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden>
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
            新規作成
          </Button>
        </div>
      </div>

      {error && <div className="mb-4 rounded border border-red-300 bg-red-50 px-4 py-2 text-sm text-red-800">{error}</div>}

      {/* いま表示中 */}
      <section className="mb-6">
        <h3 className="text-[13px] font-semibold text-gray-900 tracking-wide mb-2">
          いま表示中 <span className="ml-2 text-xs font-normal text-gray-500">公開中かつ未終了。戻し忘れをここで見る</span>
        </h3>
        <div className="rounded-lg border border-gray-200 bg-white divide-y divide-gray-100">
          {loading && list.length === 0 ? (
            <div className="p-4">
              <Loading text="読み込み中..." />
            </div>
          ) : active.length === 0 ? (
            <div className="px-4 py-3 text-sm text-gray-500">表示中の告知はありません</div>
          ) : (
            active.map((a) => {
              const sev = SEVERITY_META[a.severity];
              return (
                <div key={a.announcementId} className="grid grid-cols-1 md:grid-cols-[auto_1fr_auto_auto] gap-x-3 gap-y-1 items-center px-4 py-2 text-sm">
                  <span className={`inline-flex items-center gap-1 rounded border px-1.5 py-0.5 text-[11px] font-semibold ${sev.className}`}>
                    <span aria-hidden>{sev.icon}</span>
                    {sev.label}
                  </span>
                  <span className="min-w-0 truncate">
                    {a.pinned && '📌 '}
                    {a.title} <span className="text-xs text-gray-500">· {absoluteTime(a.publishAt)} から</span>
                  </span>
                  <span className={`text-[11px] rounded border px-1.5 whitespace-nowrap ${a.showInChat ? 'border-gray-700 text-gray-800 font-semibold' : 'border-gray-300 text-gray-600'}`}>
                    {a.showInChat ? 'ホーム + チャット' : 'ホーム'}
                  </span>
                  <span className="flex gap-2">
                    <Button variant="outline" size="sm" onClick={() => startEdit(a)}>
                      編集
                    </Button>
                    {canEndAnnouncementNow(a, now.getTime()) ? (
                      <Button variant="outline" size="sm" onClick={() => endNow(a)}>
                        表示終了
                      </Button>
                    ) : (
                      <Button
                        variant="outline"
                        size="sm"
                        title="開始前のメンテナンスは表示終了できません。取りやめる場合は削除してください"
                        onClick={() => setConfirmDelete(a)}
                      >
                        削除（開始前）
                      </Button>
                    )}
                  </span>
                </div>
              );
            })
          )}
        </div>
      </section>

      {/* テンプレート */}
      <section className="mb-6">
        <h3 className="text-[13px] font-semibold text-gray-900 tracking-wide mb-2">
          テンプレート <span className="ml-2 text-xs font-normal text-gray-500">種別・重要度・固定・表示先のプリセット付き。{'{{ }}'} の穴だけ埋める</span>
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-3">
          {ANNOUNCEMENT_TEMPLATES.map((t) => {
            const sev = SEVERITY_META[t.severity];
            return (
              <div key={t.key} className="rounded-lg border border-gray-200 bg-white p-3.5 flex flex-col gap-1.5">
                <div className="flex items-center justify-between gap-2">
                  <span className="font-semibold text-sm">{t.name}</span>
                  <span className={`inline-flex items-center gap-1 rounded border px-1.5 py-0.5 text-[11px] font-semibold ${sev.className}`}>
                    <span aria-hidden>{sev.icon}</span>
                    {sev.label}
                  </span>
                </div>
                <div className="text-[11.5px] text-gray-500">
                  {TYPE_META[t.type].label} · {t.pinned ? '固定' : '固定なし'} · {t.showInChat ? 'ホーム + チャット' : 'ホーム'}
                </div>
                <div className="text-xs text-gray-600">開く契機: {t.when}</div>
                <div className="mt-auto flex justify-end">
                  <Button variant={t.key === 'incident' ? 'primary' : 'outline'} size="sm" onClick={() => applyTemplate(t.key)}>
                    この型で作る
                  </Button>
                </div>
              </div>
            );
          })}
        </div>
      </section>

      {/* List */}
      <div className="rounded-lg border border-gray-200 bg-white overflow-x-auto mb-10">
        {loading ? (
          <div className="p-8 flex justify-center">
            <Loading text="読み込み中..." />
          </div>
        ) : filtered.length === 0 ? (
          <div className="p-8 text-center text-sm text-gray-500">お知らせがありません。</div>
        ) : (
          <table className="w-full text-sm">
            <thead className="bg-gray-50 text-gray-500 text-xs">
              <tr>
                <th className="text-left font-medium px-4 py-2">状態</th>
                <th className="text-left font-medium px-4 py-2">種別</th>
                <th className="text-left font-medium px-4 py-2">重要度</th>
                <th className="text-left font-medium px-4 py-2">タイトル</th>
                <th className="text-left font-medium px-4 py-2">表示先</th>
                <th className="text-left font-medium px-4 py-2">公開日時</th>
                <th className="text-left font-medium px-4 py-2">表示終了</th>
                <th className="text-left font-medium px-4 py-2">作成者</th>
                <th className="text-right font-medium px-4 py-2">操作</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {filtered.map((a) => {
                const badge = STATUS_BADGE[statusOf(a, now)];
                const sev = SEVERITY_META[a.severity];
                return (
                  <tr
                    key={a.announcementId}
                    className={`hover:bg-gray-50 transition-colors ${editingId === a.announcementId ? 'bg-blue-50/60' : ''}`}
                  >
                    <td className="px-4 py-2.5 whitespace-nowrap">
                      <span className={`inline-flex items-center gap-1.5 rounded-full px-2 py-0.5 text-xs font-medium border ${badge.className}`}>
                        <span aria-hidden className={`w-1.5 h-1.5 rounded-full ${badge.dotClass}`} />
                        {badge.label}
                      </span>
                    </td>
                    <td className="px-4 py-2.5 whitespace-nowrap">
                      {TYPE_META[a.type].icon} {TYPE_META[a.type].label}
                    </td>
                    <td className="px-4 py-2.5 whitespace-nowrap">
                      <span className={`inline-flex items-center gap-1 rounded border px-1.5 py-0.5 text-[11px] font-semibold ${sev.className}`}>
                        <span aria-hidden>{sev.icon}</span>
                        {sev.label}
                      </span>
                    </td>
                    <td className="px-4 py-2.5 max-w-xs truncate">
                      {a.pinned && '📌 '}
                      {a.title}
                    </td>
                    <td className="px-4 py-2.5 whitespace-nowrap text-xs text-gray-600">{a.showInChat ? 'ホーム + チャット' : 'ホーム'}</td>
                    <td className="px-4 py-2.5 whitespace-nowrap text-gray-500 text-xs">{a.status === 'draft' ? '—' : absoluteTime(a.publishAt)}</td>
                    <td className="px-4 py-2.5 whitespace-nowrap text-gray-500 text-xs">{a.endAt ? absoluteTime(a.endAt) : '—'}</td>
                    <td className="px-4 py-2.5 whitespace-nowrap text-gray-500 text-xs">{a.createdBy ? a.createdBy.slice(0, 8) : '—'}</td>
                    <td className="px-4 py-2.5 whitespace-nowrap text-right">
                      <button
                        className="p-1.5 rounded-md text-gray-400 hover:text-blue-600 hover:bg-blue-50 transition-colors"
                        onClick={() => startEdit(a)}
                        aria-label="編集"
                        title="編集"
                      >
                        <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                        </svg>
                      </button>
                      <button
                        className="p-1.5 rounded-md text-gray-400 hover:text-red-600 hover:bg-red-50 transition-colors ml-1"
                        onClick={() => setConfirmDelete(a)}
                        aria-label="削除"
                        title="削除"
                      >
                        <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                        </svg>
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        )}
      </div>

      {/* Form */}
      <div
        ref={formRef}
        className={`rounded-lg border bg-white p-6 scroll-mt-36 transition-colors ${
          editingId ? 'border-blue-300 ring-2 ring-blue-100' : 'border-gray-200'
        }`}
      >
        <div className="flex flex-wrap items-center gap-2.5 mb-4">
          <h3 className="text-lg font-semibold text-gray-900">{editingId ? 'お知らせを編集' : '新規作成'}</h3>
          {editingId && (
            <span className="inline-flex items-center gap-1 rounded-full bg-blue-100 text-blue-700 text-xs font-semibold px-2.5 py-0.5">編集中</span>
          )}
          {templateName && !editingId && (
            <span className="inline-flex items-center gap-1 rounded-full bg-gray-100 text-gray-700 text-xs font-semibold px-2.5 py-0.5">型: {templateName}</span>
          )}
          {holes.length > 0 && (
            <span className="text-xs text-amber-800">
              穴が残っています: {holes.map((h) => `{{${h}}}`).join(' ')}（公開前に埋める）
            </span>
          )}
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-4 gap-4 mb-4">
          <label className="text-sm">
            <span className="block text-gray-600 mb-1">種別</span>
            <select className={inputCls} value={form.type} onChange={(e) => setForm({ ...form, type: e.target.value as AnnouncementType })}>
              <option value="notice">お知らせ</option>
              <option value="update">アップデート</option>
              <option value="maintenance">メンテナンス</option>
            </select>
          </label>
          <label className="text-sm">
            <span className="block text-gray-600 mb-1">重要度</span>
            <select
              className={inputCls}
              value={form.severity}
              onChange={(e) => {
                const severity = e.target.value as Severity;
                setForm({ ...form, severity, showInChat: severity === 'critical' ? true : form.showInChat });
              }}
            >
              <option value="info">情報 (info)</option>
              <option value="warning">注意 (warning)</option>
              <option value="critical">重要 (critical)</option>
            </select>
          </label>
          {form.type !== 'maintenance' && (
            <label className="text-sm">
              <span className="block text-gray-600 mb-1">表示終了（任意）</span>
              <input
                type="datetime-local"
                className={inputCls}
                value={toLocalInput(form.endAt)}
                onChange={(e) => setForm({ ...form, endAt: fromLocalInput(e.target.value) })}
              />
            </label>
          )}
          <div className="text-sm flex flex-col justify-end gap-1.5 pb-1.5">
            <label className="flex items-center gap-2">
              <input type="checkbox" checked={!!form.showInChat} onChange={(e) => setForm({ ...form, showInChat: e.target.checked })} />
              <span className="text-gray-700">チャット画面にも表示</span>
            </label>
            <label className="flex items-center gap-2">
              <input type="checkbox" checked={!!form.pinned} onChange={(e) => setForm({ ...form, pinned: e.target.checked })} />
              <span className="text-gray-700">上部に固定 (pinned)</span>
            </label>
          </div>
        </div>

        <label className="block text-sm mb-4">
          <span className="flex justify-between text-gray-600 mb-1">
            <span>タイトル</span>
            <span className={form.title.length > TITLE_MAX ? 'text-red-600' : 'text-gray-400'}>残り {TITLE_MAX - form.title.length}字</span>
          </span>
          <input
            ref={titleInputRef}
            className={inputCls}
            maxLength={TITLE_MAX}
            value={form.title}
            onChange={(e) => setForm({ ...form, title: e.target.value })}
            placeholder="お知らせのタイトル"
          />
        </label>

        {form.type === 'maintenance' && (
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-4">
            <label className="text-sm">
              <span className="block text-gray-600 mb-1">メンテ開始</span>
              <input
                type="datetime-local"
                className={inputCls}
                value={toLocalInput(form.startAt)}
                onChange={(e) => setForm({ ...form, startAt: fromLocalInput(e.target.value) })}
              />
            </label>
            <label className="text-sm">
              <span className="block text-gray-600 mb-1">メンテ終了</span>
              <input
                type="datetime-local"
                className={inputCls}
                value={toLocalInput(form.endAt)}
                onChange={(e) => setForm({ ...form, endAt: fromLocalInput(e.target.value) })}
              />
            </label>
          </div>
        )}

        {/* Body + live preview */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-4">
          <label className="text-sm">
            <span className="block text-gray-600 mb-1">本文 (Markdown)</span>
            <textarea
              className={`${inputCls} font-mono h-56 resize-y`}
              value={form.body}
              onChange={(e) => setForm({ ...form, body: e.target.value })}
              placeholder={'## 見出し\n- 箇条書き\n本文を Markdown で記述できます。'}
            />
          </label>
          <div className="text-sm">
            <span className="block text-gray-600 mb-1">プレビュー</span>
            <div className="border border-gray-200 rounded px-3 py-2 h-56 overflow-y-auto bg-gray-50 prose prose-sm max-w-none">
              {form.body ? (
                <ReactMarkdown remarkPlugins={[remarkGfm]}>{form.body}</ReactMarkdown>
              ) : (
                <span className="text-gray-400">プレビューがここに表示されます</span>
              )}
            </div>
          </div>
        </div>

        {/* Publish timing */}
        <div className="mb-6">
          <span className="block text-sm text-gray-600 mb-1">公開タイミング</span>
          <div className="flex flex-wrap items-center gap-4 text-sm">
            <label className="flex items-center gap-1.5">
              <input type="radio" name="publishMode" checked={publishMode === 'now'} onChange={() => setPublishMode('now')} />
              即時公開
            </label>
            <label className="flex items-center gap-1.5">
              <input type="radio" name="publishMode" checked={publishMode === 'schedule'} onChange={() => setPublishMode('schedule')} />
              予約公開
            </label>
            {publishMode === 'schedule' && (
              <input
                type="datetime-local"
                className="border border-gray-300 rounded-lg px-2.5 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                value={scheduleAt}
                onChange={(e) => setScheduleAt(e.target.value)}
              />
            )}
          </div>
        </div>

        <div className="flex flex-wrap gap-3">
          <Button variant="secondary" onClick={() => submit('draft')} disabled={saving}>
            下書き保存
          </Button>
          <Button variant="primary" onClick={() => submit('published')} disabled={saving}>
            {publishMode === 'schedule' ? '予約する' : '公開する'}
          </Button>
          {(editingId || templateName) && (
            <Button variant="ghost" onClick={resetForm} disabled={saving}>
              キャンセル
            </Button>
          )}
        </div>
      </div>

      {/* Delete confirmation */}
      {confirmDelete && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center px-4"
          role="dialog"
          aria-modal="true"
          aria-label="削除の確認"
          onClick={() => setConfirmDelete(null)}
        >
          <div className="absolute inset-0 bg-black/40" />
          <div className="relative w-full max-w-md rounded-xl bg-white shadow-xl border border-gray-200 p-6" onClick={(e) => e.stopPropagation()}>
            <h3 className="text-lg font-bold text-gray-900 mb-2">お知らせを削除しますか？</h3>
            <p className="text-sm text-gray-600 mb-6">
              「{confirmDelete.title}」を削除します。この操作は取り消せません。
              {canEndAnnouncementNow(confirmDelete)
                ? '表示だけ止めたい場合は「表示終了」を使ってください。'
                : '開始前のメンテナンスは表示終了できないため、取りやめる場合は削除します。'}
            </p>
            <div className="flex justify-end gap-3">
              <Button variant="ghost" onClick={() => setConfirmDelete(null)}>
                キャンセル
              </Button>
              <Button variant="danger" onClick={doDelete}>
                削除する
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
