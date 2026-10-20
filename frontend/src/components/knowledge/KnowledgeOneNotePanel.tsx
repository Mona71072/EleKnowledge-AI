'use client';

import React, { useState } from 'react';

type KbStatus = 'unverified' | 'reviewed' | 'conflict';

type Placement = {
  destination: string;
  recordedAt: string;
  baseVersion: number;
  revision: number;
  text: string;
};

type Props = {
  noteText: string;
  onNoteChange: (value: string) => void;
  noteNeedsReconcile: boolean;
  kbReview: { status: KbStatus; reference: string; note: string };
  onKbReviewChange: (value: { status: KbStatus; reference: string; note: string }) => void;
  confirmed: boolean;
  onConfirmChange: (checked: boolean) => void;
  onCopy: () => void;
  canCopy: boolean;
  copied: boolean;
  placements: Placement[];
  onRecordPlacement: (destination: string) => void;
};

const inputClass = 'w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm text-gray-900 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-200';

export function KnowledgeOneNotePanel({
  noteText,
  onNoteChange,
  noteNeedsReconcile,
  kbReview,
  onKbReviewChange,
  confirmed,
  onConfirmChange,
  onCopy,
  canCopy,
  copied,
  placements,
  onRecordPlacement,
}: Props) {
  const [destination, setDestination] = useState('');
  const [error, setError] = useState('');

  const record = () => {
    setError('');
    try {
      onRecordPlacement(destination.trim());
      setDestination('');
    } catch {
      setError('URLはHTTPSまたはonenote:https形式で入力してください。現在版をコピーし、貼り付け先を確認してください。');
    }
  };

  return (
    <section className="rounded-xl border border-gray-200 bg-white shadow-sm" aria-label="OneNote追記案と確認">
      <div className="border-b border-gray-200 px-4 py-3">
        <h2 className="font-semibold text-gray-900">OneNoteへの追記案</h2>
        <p className="mt-1 text-xs text-gray-500">追記案は担当者が編集します。OneNoteへの自動書込みは行いません。</p>
      </div>
      <div className="space-y-4 p-4">
        {noteNeedsReconcile && (
          <p role="status" className="rounded-lg border border-amber-300 bg-amber-50 px-3 py-2 text-sm text-amber-950">
            本文を変更しました。追記案との整合を確認してください。
          </p>
        )}
        <div>
          <label htmlFor="knowledge-note" className="mb-1 block text-sm font-medium text-gray-800">確認・編集する文章</label>
          <textarea
            id="knowledge-note"
            aria-label="OneNoteへの追記案を編集"
            value={noteText}
            onChange={(event) => onNoteChange(event.target.value)}
            rows={8}
            className={`${inputClass} resize-y leading-6`}
          />
        </div>

        <fieldset className="space-y-3 rounded-lg border border-gray-200 p-3">
          <legend className="px-1 text-sm font-semibold text-gray-800">KB資料の手動確認</legend>
          <label htmlFor="knowledge-kb-status" className="block text-xs font-medium text-gray-600">確認状態</label>
          <select
            id="knowledge-kb-status"
            aria-label="KB資料の確認状態"
            value={kbReview.status}
            onChange={(event) => onKbReviewChange({ ...kbReview, status: event.target.value as KbStatus })}
            className={inputClass}
          >
            <option value="unverified">未確認</option>
            <option value="reviewed">本文を手動確認</option>
            <option value="conflict">食い違いあり</option>
          </select>
          <label htmlFor="knowledge-kb-reference" className="block text-xs font-medium text-gray-600">資料名・ページ・参照箇所</label>
          <input
            id="knowledge-kb-reference"
            aria-label="KB資料の参照箇所"
            value={kbReview.reference}
            onChange={(event) => onKbReviewChange({ ...kbReview, reference: event.target.value })}
            className={inputClass}
            placeholder="例: 資料番号、版、ページ、節"
          />
          <label htmlFor="knowledge-kb-note" className="block text-xs font-medium text-gray-600">確認結果・食い違い・未確認点</label>
          <textarea
            id="knowledge-kb-note"
            aria-label="KB資料の確認メモ"
            value={kbReview.note}
            onChange={(event) => onKbReviewChange({ ...kbReview, note: event.target.value })}
            rows={3}
            className={`${inputClass} resize-y`}
            placeholder="本文を見て確認した内容、条件の違い、保留点を記録します。"
          />
          <p className="text-xs text-gray-500">資料名の登録だけでは本文確認済みになりません。この欄は資料を開いたり検索したりしません。</p>
        </fieldset>

        <label className="flex items-start gap-3 rounded-lg border border-blue-200 bg-blue-50 p-3 text-sm text-blue-950">
          <input
            type="checkbox"
            aria-label="本文と追記案の整合、根拠、適用条件、共有先の読者を確認しました"
            checked={confirmed}
            onChange={(event) => onConfirmChange(event.target.checked)}
            className="mt-0.5 h-4 w-4 rounded border-blue-400 text-blue-700 focus:ring-blue-500"
          />
          <span>本文と追記案の整合、根拠、適用条件、共有先の読者を確認しました。正式な技術承認や公開を意味しません。</span>
        </label>

        <div className="flex flex-wrap items-center gap-3">
          <button
            type="button"
            onClick={onCopy}
            disabled={!canCopy}
            className="rounded-lg bg-blue-700 px-4 py-2.5 text-sm font-semibold text-white hover:bg-blue-800 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:cursor-not-allowed disabled:bg-gray-300"
          >
            確認した文章をコピー
          </button>
          <span aria-live="polite" className="text-sm text-gray-700">{copied ? '現在の版をコピー済みです。OneNoteへ貼り付けた後に掲載先を記録してください。' : '確認とKB本文の手動確認後にコピーできます。'}</span>
        </div>

        {copied && (
          <div className="space-y-2 rounded-lg border border-gray-200 p-3">
            <label htmlFor="knowledge-onenote-destination" className="block text-sm font-medium text-gray-800">貼り付けたOneNoteページのURL</label>
            <div className="flex flex-col gap-2 sm:flex-row">
              <input
                id="knowledge-onenote-destination"
                aria-label="貼り付け先のOneNoteページURL"
                value={destination}
                onChange={(event) => setDestination(event.target.value)}
                className={inputClass}
                placeholder="https://... または onenote:https://..."
                inputMode="url"
              />
              <button type="button" onClick={record} className="shrink-0 rounded-lg border border-gray-300 px-4 py-2 text-sm font-semibold text-gray-800 hover:bg-gray-50">
                追加済みとして記録
              </button>
            </div>
            {error && <p role="alert" className="text-sm text-red-700">{error}</p>}
            <p className="text-xs text-gray-500">担当者の自己申告です。掲載先の実在・テナント・書込結果は未検証です。</p>
          </div>
        )}

        {placements.length > 0 && (
          <div>
            <h3 className="mb-2 text-sm font-semibold text-gray-800">過去の掲載記録</h3>
            <ul className="space-y-2">
              {placements.map((placement, index) => (
                <li key={`${placement.recordedAt}-${index}`} className="rounded-lg bg-gray-50 p-3 text-xs text-gray-700">
                  <p className="break-all font-medium">{placement.destination}</p>
                  <p className="mt-1">原版 v{placement.baseVersion} · 作業版 {placement.revision} · {new Date(placement.recordedAt).toLocaleString('ja-JP')}</p>
                  <details className="mt-2">
                    <summary className="cursor-pointer font-medium">転記した文章</summary>
                    <pre className="mt-2 whitespace-pre-wrap break-words font-sans">{placement.text}</pre>
                  </details>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </section>
  );
}
