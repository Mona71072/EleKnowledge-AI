'use client';

import { useEffect, useRef, useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import {
  Announcement,
  AnnouncementInput,
  AnnouncementType,
  Severity,
  AnnouncementStatus,
  TYPE_META,
  listAllAnnouncements,
  createAnnouncement,
  updateAnnouncement,
  deleteAnnouncement,
  absoluteTime,
} from '@/lib/announcements';
import { resolveAnnouncementPublishFields } from '@/lib/announcement-publish.mjs';
import { Button } from '@/components/ui/Button';
import { Loading } from '@/components/ui/Loading';

const STATUS_BADGE: Record<AnnouncementStatus, { label: string; className: string; dotClass: string }> = {
  published: { label: '公開', className: 'text-green-700 bg-green-50 border-green-200', dotClass: 'bg-green-500' },
  scheduled: { label: '予約', className: 'text-amber-800 bg-amber-50 border-amber-300', dotClass: 'bg-amber-400' },
  draft: { label: '下書き', className: 'text-gray-600 bg-gray-50 border-gray-200', dotClass: 'bg-gray-400' },
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

export default function AdminAnnouncementsPage() {
  const [list, setList] = useState<Announcement[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [form, setForm] = useState<AnnouncementInput>(emptyForm);
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

  const load = async () => {
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
  };

  useEffect(() => {
    load();
  }, []);

  const resetForm = () => {
    setForm(emptyForm);
    setEditingId(null);
    setPublishMode('now');
    setScheduleAt('');
  };

  const startEdit = (a: Announcement) => {
    setEditingId(a.announcementId);
    setForm({
      type: a.type,
      title: a.title,
      body: a.body,
      severity: a.severity,
      status: a.status,
      pinned: a.pinned,
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
    setSaving(true);
    setError(null);
    try {
      const payload: AnnouncementInput = { ...form, status };
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

  const filtered = list.filter((a) => statusFilter === 'all' || a.status === statusFilter);

  return (
    <div>
      <div className="flex flex-wrap items-center justify-between gap-3 mb-6">
        <div>
          <h2 className="text-xl font-bold text-gray-900">お知らせ管理</h2>
          <p className="text-sm text-gray-500 mt-0.5">全 {list.length} 件（表示中 {filtered.length} 件）</p>
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

      {error && (
        <div className="mb-4 rounded border border-red-300 bg-red-50 px-4 py-2 text-sm text-red-800">
          {error}
        </div>
      )}

      {/* List */}
      <div className="rounded-lg border border-gray-200 bg-white overflow-hidden mb-10">
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
                <th className="text-left font-medium px-4 py-2">タイトル</th>
                <th className="text-left font-medium px-4 py-2">公開日時</th>
                <th className="text-right font-medium px-4 py-2">操作</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {filtered.map((a) => {
                const badge = STATUS_BADGE[a.status];
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
                    <td className="px-4 py-2.5 max-w-xs truncate">
                      {a.pinned && '📌 '}
                      {a.title}
                    </td>
                    <td className="px-4 py-2.5 whitespace-nowrap text-gray-500 text-xs">
                      {a.status === 'draft' ? '—' : absoluteTime(a.publishAt)}
                    </td>
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
        <div className="flex items-center gap-2.5 mb-4">
          <h3 className="text-lg font-semibold text-gray-900">
            {editingId ? 'お知らせを編集' : '新規作成'}
          </h3>
          {editingId && (
            <span className="inline-flex items-center gap-1 rounded-full bg-blue-100 text-blue-700 text-xs font-semibold px-2.5 py-0.5">
              編集中
            </span>
          )}
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-4">
          <label className="text-sm">
            <span className="block text-gray-600 mb-1">種別</span>
            <select
              className={inputCls}
              value={form.type}
              onChange={(e) => setForm({ ...form, type: e.target.value as AnnouncementType })}
            >
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
              onChange={(e) => setForm({ ...form, severity: e.target.value as Severity })}
            >
              <option value="info">情報 (info)</option>
              <option value="warning">注意 (warning)</option>
              <option value="critical">重要 (critical)</option>
            </select>
          </label>
          <label className="text-sm flex items-end gap-2 pb-1.5">
            <input
              type="checkbox"
              checked={!!form.pinned}
              onChange={(e) => setForm({ ...form, pinned: e.target.checked })}
            />
            <span className="text-gray-700">上部に固定 (pinned)</span>
          </label>
        </div>

        <label className="block text-sm mb-4">
          <span className="flex justify-between text-gray-600 mb-1">
            <span>タイトル</span>
            <span className={form.title.length > TITLE_MAX ? 'text-red-600' : 'text-gray-400'}>
              残り {TITLE_MAX - form.title.length}字
            </span>
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
              <input
                type="radio"
                name="publishMode"
                checked={publishMode === 'now'}
                onChange={() => setPublishMode('now')}
              />
              即時公開
            </label>
            <label className="flex items-center gap-1.5">
              <input
                type="radio"
                name="publishMode"
                checked={publishMode === 'schedule'}
                onChange={() => setPublishMode('schedule')}
              />
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
          {editingId && (
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
          <div
            className="relative w-full max-w-md rounded-xl bg-white shadow-xl border border-gray-200 p-6"
            onClick={(e) => e.stopPropagation()}
          >
            <h3 className="text-lg font-bold text-gray-900 mb-2">お知らせを削除しますか？</h3>
            <p className="text-sm text-gray-600 mb-6">
              「{confirmDelete.title}」を削除します。この操作は取り消せません。
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
