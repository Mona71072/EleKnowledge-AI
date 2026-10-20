'use client';

import { useState } from 'react';
import { ALL_MODEL_TYPES } from '@/data/kbModelTypes';
import { getIdToken } from '@/lib/auth-helpers';
import type { SenpaiChatTurn } from '@/lib/knowledge-senpai-chat.mjs';
import {
  FIELD_REPORT_CONDITION_MAX,
  FIELD_REPORT_FINDING_MAX,
  FIELD_REPORT_REACTION_LABELS,
  FIELD_REPORT_REVIEW_STATE_LABELS,
  buildFieldReportPayload,
  createFieldReportDraft,
  fieldReportCards,
  submitFieldReport,
  validateFieldReportDraft,
  type FieldReport,
  type FieldReportDraft,
  type FieldReportPayload,
  type FieldReportReaction,
} from '@/lib/knowledge-senpai-field-report.mjs';

const REACTIONS: FieldReportReaction[] = ['matched', 'not_matched', 'unsure'];
const fieldClass = 'w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm text-gray-900 focus:border-violet-500 focus:outline-none focus:ring-2 focus:ring-violet-200';
const modelLabel = (value?: string) => ALL_MODEL_TYPES.find((model) => model.value === value)?.label ?? '指定しない';

function SentReport({ report }: { report: FieldReport }) {
  return (
    <p role="status" className="rounded-lg border border-emerald-200 bg-emerald-50 p-3 text-xs leading-5 text-emerald-950">
      この相談の結果を送信済みです（{FIELD_REPORT_REVIEW_STATE_LABELS[report.reviewState]}）。担当者が確認するまで、ノウハウには反映されません。
    </p>
  );
}

function Preview({ payload, titles }: { payload: FieldReportPayload; titles: Record<string, string> }) {
  return (
    <dl className="grid grid-cols-[7rem_minmax(0,1fr)] gap-x-2 gap-y-1 rounded-lg border border-gray-200 bg-white p-3 text-xs text-gray-800">
      <dt className="text-gray-500">何が分かったか</dt><dd className="whitespace-pre-wrap break-words">{payload.finding}</dd>
      <dt className="text-gray-500">どの条件か</dt><dd className="whitespace-pre-wrap break-words">{payload.condition || '（未記入）'}</dd>
      <dt className="text-gray-500">機種</dt><dd>{modelLabel(payload.modelType)}</dd>
      <dt className="text-gray-500">ノウハウ</dt>
      <dd>{payload.cardReactions.length === 0 ? '（反応なし）' : (
        <ul className="space-y-0.5">{payload.cardReactions.map((r) => <li key={r.knowledgeId}>{titles[r.knowledgeId] || r.knowledgeId} v{r.cardVersion}: {FIELD_REPORT_REACTION_LABELS[r.reaction]}</li>)}</ul>
      )}</dd>
    </dl>
  );
}

/**
 * 「結果を残す」: short, user-confirmed observation for one Senpai turn.
 * Nothing is sent until the user opens the form, reviews the preview and presses send.
 */
export function SenpaiFieldReportForm({ conversationId, turn, sent, onSent }: {
  conversationId?: string;
  turn: SenpaiChatTurn;
  sent?: FieldReport;
  onSent: (report: FieldReport) => void;
}) {
  const [open, setOpen] = useState(false);
  const [draft, setDraft] = useState<FieldReportDraft>(() => createFieldReportDraft(turn));
  const [preview, setPreview] = useState<FieldReportPayload | null>(null);
  const [error, setError] = useState('');
  const [sending, setSending] = useState(false);
  if (sent) return <SentReport report={sent} />;
  if (!conversationId || !turn.senpaiTurnId) return null;
  const cards = fieldReportCards(turn);
  const titles = Object.fromEntries(cards.map((card) => [card.knowledgeId, card.title]));
  const idPrefix = `field-report-${turn.id}`;

  if (!open) {
    return (
      <button type="button" onClick={() => { setDraft(createFieldReportDraft(turn)); setOpen(true); }} className="rounded-lg border border-emerald-300 bg-white px-3 py-1.5 text-xs font-semibold text-emerald-900 hover:bg-emerald-50 focus:outline-none focus:ring-2 focus:ring-emerald-400">
        結果を残す
      </button>
    );
  }

  function update(patch: Partial<FieldReportDraft>) {
    setDraft((current) => ({ ...current, ...patch }));
    setPreview(null);
    setError('');
  }

  function confirm() {
    const errors = validateFieldReportDraft(draft);
    if (errors.length > 0) { setError(errors[0]); return; }
    try {
      setPreview(buildFieldReportPayload({ conversationId: conversationId!, turn, draft }));
    } catch (failure) {
      setError((failure as Error).message || '入力内容を確認してください');
    }
  }

  async function send() {
    if (!preview || sending) return;
    setSending(true);
    setError('');
    try {
      const report = await submitFieldReport({ baseUrl: process.env.NEXT_PUBLIC_RAG_API_URL || '', getToken: getIdToken, payload: preview });
      onSent(report);
    } catch (failure) {
      const known = failure as { code?: string; message?: string };
      setError(known?.code && known.message ? known.message : '結果を送信できませんでした。時間をおいてお試しください');
    } finally {
      setSending(false);
    }
  }

  return (
    <section aria-label="結果を残す" className="space-y-3 rounded-xl border border-emerald-200 bg-emerald-50/60 p-4">
      <div>
        <h4 className="text-sm font-bold text-emerald-950">結果を残す（未確認の報告として保存）</h4>
        <p className="mt-1 text-xs leading-5 text-emerald-900">実際に分かったことだけを短く残してください。相談や回答の本文は送りません。担当者が確認するまでノウハウには反映されません。顧客名・個人名・物件名は書かないでください。</p>
      </div>
      <div className="space-y-1">
        <label htmlFor={`${idPrefix}-finding`} className="block text-xs font-semibold text-gray-800">何が分かったか（必須）</label>
        <textarea id={`${idPrefix}-finding`} rows={3} maxLength={FIELD_REPORT_FINDING_MAX} value={draft.finding} onChange={(event) => update({ finding: event.target.value })} placeholder="例: 記載の手順で症状が変わった／別の確認が必要だった" className={fieldClass} />
      </div>
      <div className="space-y-1">
        <label htmlFor={`${idPrefix}-condition`} className="block text-xs font-semibold text-gray-800">どの条件か（任意）</label>
        <textarea id={`${idPrefix}-condition`} rows={2} maxLength={FIELD_REPORT_CONDITION_MAX} value={draft.condition} onChange={(event) => update({ condition: event.target.value })} placeholder="例: 制御方式、ドアの種類、作業の段階など" className={fieldClass} />
      </div>
      <div className="flex flex-wrap items-center gap-2">
        <label htmlFor={`${idPrefix}-model`} className="text-xs font-semibold text-gray-800">機種</label>
        <select id={`${idPrefix}-model`} value={draft.modelType} onChange={(event) => update({ modelType: event.target.value })} className="rounded-lg border border-gray-300 bg-white px-2 py-1 text-sm text-gray-900">
          <option value="">指定しない</option>
          {ALL_MODEL_TYPES.map((model) => <option key={model.value} value={model.value}>{model.label}</option>)}
        </select>
      </div>
      {cards.length > 0 && (
        <fieldset className="space-y-2">
          <legend className="text-xs font-semibold text-gray-800">参照したノウハウは、この条件で当てはまりましたか（任意）</legend>
          {cards.map((card) => (
            <div key={card.knowledgeId} className="rounded-lg border border-gray-200 bg-white p-2 text-xs">
              <p className="font-semibold text-gray-900">{card.title} <span className="font-normal text-gray-500">v{card.cardVersion}</span></p>
              <div className="mt-1 flex flex-wrap gap-3" role="radiogroup" aria-label={`${card.title}への反応`}>
                {REACTIONS.map((reaction) => (
                  <label key={reaction} className="inline-flex items-center gap-1">
                    <input type="radio" name={`${idPrefix}-${card.knowledgeId}`} value={reaction} checked={draft.reactions[card.knowledgeId] === reaction} onChange={() => update({ reactions: { ...draft.reactions, [card.knowledgeId]: reaction } })} />
                    {FIELD_REPORT_REACTION_LABELS[reaction]}
                  </label>
                ))}
                {draft.reactions[card.knowledgeId] && (
                  <button type="button" onClick={() => update({ reactions: { ...draft.reactions, [card.knowledgeId]: '' } })} className="text-gray-600 underline">選択を外す</button>
                )}
              </div>
            </div>
          ))}
        </fieldset>
      )}
      {preview && (
        <div className="space-y-2">
          <p className="text-xs font-semibold text-gray-800">次の内容を送信します。よろしければ「この内容で送る」を押してください。</p>
          <Preview payload={preview} titles={titles} />
        </div>
      )}
      {error && <p role="alert" className="text-xs text-red-700">{error}</p>}
      <div className="flex flex-wrap gap-2">
        {preview
          ? <button type="button" onClick={send} disabled={sending} className="rounded-lg bg-emerald-700 px-3 py-1.5 text-xs font-semibold text-white hover:bg-emerald-800 disabled:opacity-50">{sending ? '送信しています…' : 'この内容で送る'}</button>
          : <button type="button" onClick={confirm} className="rounded-lg bg-emerald-700 px-3 py-1.5 text-xs font-semibold text-white hover:bg-emerald-800">内容を確認する</button>}
        <button type="button" onClick={() => { setOpen(false); setPreview(null); setError(''); }} disabled={sending} className="rounded-lg border border-gray-300 bg-white px-3 py-1.5 text-xs font-semibold text-gray-800 hover:bg-gray-100 disabled:opacity-50">やめる</button>
      </div>
    </section>
  );
}
