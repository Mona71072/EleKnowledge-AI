'use client';

import { useEffect, useRef, useState } from 'react';
import { ALL_MODEL_TYPES } from '@/data/kbModelTypes';
import { NoteIcon } from './SenpaiIcons';
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
// 3択の切り替えに収まる短い表示。送信前の確認では FIELD_REPORT_REACTION_LABELS を使う。
const SEGMENT_LABELS: Record<FieldReportReaction, string> = { matched: '当てはまった', not_matched: '当てはまらなかった', unsure: '分からない' };
const fieldClass = 'w-full rounded-xl border border-gray-300 bg-white px-3 py-2 text-sm text-gray-900 focus:border-gray-400 focus:outline-none focus-visible:ring-2 focus-visible:ring-violet-500';
const primaryButton = 'min-h-9 rounded-full bg-gray-900 px-4 text-xs font-medium text-white hover:bg-gray-700 focus:outline-none focus-visible:ring-2 focus-visible:ring-violet-500 disabled:opacity-50';
const quietButton = 'min-h-9 rounded-full px-3 text-xs font-medium text-gray-600 hover:bg-gray-100 focus:outline-none focus-visible:ring-2 focus-visible:ring-violet-500 disabled:opacity-50';
const modelLabel = (value?: string) => ALL_MODEL_TYPES.find((model) => model.value === value)?.label ?? '指定しない';

function SentReport({ report }: { report: FieldReport }) {
  return (
    <p role="status" className="basis-full text-xs leading-5 text-gray-500">
      この相談の結果を送信済みです（{FIELD_REPORT_REVIEW_STATE_LABELS[report.reviewState]}）。担当者が確認するまで、ノウハウには反映されません。
    </p>
  );
}

function Preview({ payload, titles }: { payload: FieldReportPayload; titles: Record<string, string> }) {
  return (
    <dl className="grid grid-cols-[7rem_minmax(0,1fr)] gap-x-2 gap-y-1 rounded-xl bg-white p-3 text-xs text-gray-800">
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
  const findingRef = useRef<HTMLTextAreaElement | null>(null);
  const triggerRef = useRef<HTMLButtonElement | null>(null);
  const wasOpen = useRef(false);
  // 開いたら最初の入力欄へ、閉じたら開いたボタンへフォーカスを移す。
  useEffect(() => {
    if (open) findingRef.current?.focus();
    else if (wasOpen.current) triggerRef.current?.focus();
    wasOpen.current = open;
  }, [open]);
  if (sent) return <SentReport report={sent} />;
  if (!conversationId || !turn.senpaiTurnId) return null;
  const cards = fieldReportCards(turn);
  const titles = Object.fromEntries(cards.map((card) => [card.knowledgeId, card.title]));
  const idPrefix = `field-report-${turn.id}`;

  if (!open) {
    return (
      <button type="button" ref={triggerRef} onClick={() => { setDraft(createFieldReportDraft(turn)); setOpen(true); }} className="inline-flex min-h-10 items-center gap-1.5 rounded-lg px-2 text-xs font-medium text-gray-600 hover:bg-gray-100 hover:text-gray-900 focus:outline-none focus-visible:ring-2 focus-visible:ring-violet-500">
        <NoteIcon />結果を残す
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
    <section aria-label="結果を残す" className="my-2 w-full basis-full space-y-3 rounded-2xl bg-gray-50 p-4">
      <div>
        <h4 className="text-sm font-semibold text-gray-900">結果を残す（未確認の報告として保存）</h4>
        <p className="mt-1 text-xs leading-5 text-gray-500">実際に分かったことだけを短く残してください。相談や回答の本文は送りません。担当者が確認するまでノウハウには反映されません。顧客名・個人名・物件名は書かないでください。</p>
      </div>
      <div className="space-y-1">
        <label htmlFor={`${idPrefix}-finding`} className="block text-xs font-medium text-gray-700">何が分かったか（必須）</label>
        <textarea id={`${idPrefix}-finding`} ref={findingRef} rows={3} maxLength={FIELD_REPORT_FINDING_MAX} value={draft.finding} onChange={(event) => update({ finding: event.target.value })} placeholder="例: 記載の手順で症状が変わった／別の確認が必要だった" className={fieldClass} />
      </div>
      <div className="space-y-1">
        <label htmlFor={`${idPrefix}-condition`} className="block text-xs font-medium text-gray-700">どの条件か（任意）</label>
        <textarea id={`${idPrefix}-condition`} rows={2} maxLength={FIELD_REPORT_CONDITION_MAX} value={draft.condition} onChange={(event) => update({ condition: event.target.value })} placeholder="例: 制御方式、ドアの種類、作業の段階など" className={fieldClass} />
      </div>
      <div className="flex flex-wrap items-center gap-2">
        <label htmlFor={`${idPrefix}-model`} className="text-xs font-medium text-gray-700">機種</label>
        <select id={`${idPrefix}-model`} value={draft.modelType} onChange={(event) => update({ modelType: event.target.value })} className="rounded-xl border border-gray-300 bg-white px-2 py-1.5 text-sm text-gray-900 focus:outline-none focus-visible:ring-2 focus-visible:ring-violet-500">
          <option value="">指定しない</option>
          {ALL_MODEL_TYPES.map((model) => <option key={model.value} value={model.value}>{model.label}</option>)}
        </select>
      </div>
      {cards.length > 0 && (
        <fieldset className="space-y-2">
          <legend className="text-xs font-medium text-gray-700">参照したノウハウは、この条件で当てはまりましたか（任意）</legend>
          {cards.map((card) => (
            <div key={card.knowledgeId} className="rounded-xl bg-white p-2 text-xs">
              <p className="font-semibold text-gray-900">{card.title} <span className="font-normal text-gray-500">v{card.cardVersion}</span></p>
              <div className="mt-2 flex flex-wrap items-center gap-2">
                <div role="radiogroup" aria-label={`${card.title}への反応`} className="inline-flex overflow-hidden rounded-full border border-gray-300 bg-white">
                  {REACTIONS.map((reaction) => (
                    <label key={reaction} className="relative flex min-h-10 cursor-pointer items-center border-l border-gray-200 px-3 text-xs text-gray-700 first:border-l-0 has-[:checked]:bg-gray-900 has-[:checked]:text-white has-[:focus-visible]:ring-2 has-[:focus-visible]:ring-inset has-[:focus-visible]:ring-violet-500">
                      <input type="radio" className="sr-only" name={`${idPrefix}-${card.knowledgeId}`} value={reaction} checked={draft.reactions[card.knowledgeId] === reaction} onChange={() => update({ reactions: { ...draft.reactions, [card.knowledgeId]: reaction } })} />
                      {SEGMENT_LABELS[reaction]}
                    </label>
                  ))}
                </div>
                {draft.reactions[card.knowledgeId] && (
                  <button type="button" onClick={() => update({ reactions: { ...draft.reactions, [card.knowledgeId]: '' } })} className="min-h-10 rounded px-2 text-xs text-gray-500 underline focus:outline-none focus-visible:ring-2 focus-visible:ring-violet-500">選択を外す</button>
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
          ? <button type="button" onClick={send} disabled={sending} className={primaryButton}>{sending ? '送信しています…' : 'この内容で送る'}</button>
          : <button type="button" onClick={confirm} className={primaryButton}>内容を確認する</button>}
        <button type="button" onClick={() => { setOpen(false); setPreview(null); setError(''); }} disabled={sending} className={quietButton}>やめる</button>
      </div>
    </section>
  );
}
