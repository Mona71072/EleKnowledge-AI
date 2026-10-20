'use client';

import { useRef, useState } from 'react';
import { buildComparisonNote, type KnowledgeComparisonStatus } from '@/lib/knowledge-comparison.mjs';
import type { ResearchAnswer } from '@/lib/knowledge-research.mjs';

type Status = KnowledgeComparisonStatus;
type Props = {
  technical: ResearchAnswer;
  law: ResearchAnswer;
  contextKey: string;
  targetLabel: string;
  onAdopt: (note: string, contextKey: string) => boolean;
};

const statusLabels: Record<Status, string> = {
  consistent: '一致している',
  conditions_differ: '条件が違う',
  conflict: '食い違いあり',
  unresolved: '判断保留',
};
const textareaClass = 'w-full rounded-lg border border-gray-300 bg-white px-3 py-2.5 text-sm text-gray-900 focus:border-violet-500 focus:outline-none focus:ring-2 focus:ring-violet-200';

export function KnowledgeComparisonPanel({ technical, law, contextKey, targetLabel, onAdopt }: Props) {
  const [status, setStatus] = useState<Status>('unresolved');
  const [findings, setFindings] = useState('');
  const [applicability, setApplicability] = useState('');
  const [unresolvedPoints, setUnresolvedPoints] = useState('');
  const [imported, setImported] = useState(false);
  const [error, setError] = useState('');
  const [message, setMessage] = useState('');
  const adopting = useRef(false);
  const pointsRequired = status === 'conflict' || status === 'unresolved';
  const fieldsValid = Boolean(
    findings.trim()
      && findings.length <= 4000
      && applicability.trim()
      && applicability.length <= 4000
      && (!pointsRequired || (unresolvedPoints.trim() && unresolvedPoints.length <= 4000)),
  );

  const update = (setter: (value: string) => void) => (value: string) => {
    setter(value);
    setImported(false);
    setError('');
    setMessage('');
  };

  const adopt = () => {
    if (!fieldsValid || adopting.current || imported) return;
    adopting.current = true;
    setError('');
    setMessage('');
    try {
      const note = buildComparisonNote({
        technical,
        law,
        assessment: { status, findings, applicability, unresolvedPoints },
      });
      if (!onAdopt(note, contextKey)) {
        setError('Markdownへ追記できませんでした。対象文書と本文サイズを確認してください。');
        return;
      }
      setImported(true);
      setMessage('照合まとめをMarkdownへ取り込みました。AI回答の比較メモとして担当者確認を続けてください。');
    } catch {
      setError('照合まとめを作れませんでした。入力内容と回答ペアを確認してください。');
    } finally {
      adopting.current = false;
    }
  };

  return (
    <section className="space-y-4 rounded-xl border border-violet-300 bg-white p-4 shadow-sm sm:p-5" aria-label="担当者による照合まとめ">
      <header className="flex flex-wrap items-center justify-between gap-2">
        <div>
          <h3 className="font-semibold text-gray-950">担当者による照合まとめ</h3>
          <p className="mt-1 text-sm text-gray-700">AI回答の暫定比較・未承認です。原資料本文の確認、技術承認、法的判断ではありません。</p>
        </div>
        <span className="rounded-full bg-amber-100 px-2.5 py-1 text-xs font-semibold text-amber-950">AI回答比較・未承認</span>
      </header>

      {targetLabel && <p className="rounded-lg bg-gray-50 px-3 py-2 text-xs text-gray-700">対象: {targetLabel}</p>}

      <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
        <div>
          <label htmlFor="knowledge-comparison-status" className="mb-1 block text-sm font-medium text-gray-800">照合結果</label>
          <select
            id="knowledge-comparison-status"
            aria-label="照合結果"
            value={status}
            onChange={(event) => {
              setStatus(event.target.value as Status);
              setImported(false);
              setError('');
              setMessage('');
            }}
            className={textareaClass}
          >
            {Object.entries(statusLabels).map(([value, label]) => <option key={value} value={value}>{label}</option>)}
          </select>
        </div>
        <p className="self-end text-xs leading-5 text-gray-600">回答の違いと根拠を確認し、担当者の判断を記録します。AIはこの内容を生成しません。</p>
      </div>

      <div className="space-y-3">
        <div>
          <label htmlFor="knowledge-comparison-findings" className="mb-1 block text-sm font-medium text-gray-800">比較して分かったこと <span className="text-red-700">必須</span></label>
          <textarea id="knowledge-comparison-findings" aria-label="比較して分かったこと" value={findings} onChange={(event) => update(setFindings)(event.target.value)} rows={4} maxLength={4000} className={textareaClass} placeholder="両方の回答で共通する点、異なる点、根拠の強さを記録します。" />
          <p className="mt-1 text-right text-xs text-gray-500">{findings.length}/4000</p>
        </div>
        <div>
          <label htmlFor="knowledge-comparison-applicability" className="mb-1 block text-sm font-medium text-gray-800">適用条件・対象外 <span className="text-red-700">必須</span></label>
          <textarea id="knowledge-comparison-applicability" aria-label="適用条件・対象外" value={applicability} onChange={(event) => update(setApplicability)(event.target.value)} rows={4} maxLength={4000} className={textareaClass} placeholder="機種、作業条件、現場条件など適用範囲と対象外を記録します。" />
          <p className="mt-1 text-right text-xs text-gray-500">{applicability.length}/4000</p>
        </div>
        <div>
          <label htmlFor="knowledge-comparison-unresolved" className="mb-1 block text-sm font-medium text-gray-800">未確認事項・次に確認すること {pointsRequired ? <span className="text-red-700">必須</span> : <span className="text-gray-500">任意</span>}</label>
          <textarea id="knowledge-comparison-unresolved" aria-label="未確認事項・次に確認すること" value={unresolvedPoints} onChange={(event) => update(setUnresolvedPoints)(event.target.value)} rows={3} maxLength={4000} className={textareaClass} placeholder="確認先、追加で見る資料、確認が必要な条件を記録します。" />
          <p className="mt-1 text-right text-xs text-gray-500">{unresolvedPoints.length}/4000</p>
        </div>
      </div>

      {(error || message) && <p role={error ? 'alert' : 'status'} className={`rounded-lg p-3 text-sm ${error ? 'border border-red-200 bg-red-50 text-red-900' : 'border border-green-200 bg-green-50 text-green-900'}`}>{error || message}</p>}
      <div className="flex flex-wrap items-center gap-3">
        <button type="button" onClick={adopt} disabled={!fieldsValid || imported} className="rounded-lg bg-violet-700 px-4 py-2.5 text-sm font-semibold text-white hover:bg-violet-800 focus:outline-none focus:ring-2 focus:ring-violet-500 disabled:cursor-not-allowed disabled:opacity-50">
          {imported ? '照合まとめを取り込み済み' : '照合まとめをMarkdownへ取り込む'}
        </button>
        <span className="text-xs text-gray-600">入力は質問送信されず、選んだMarkdownの編集案にだけ追記されます。</span>
      </div>
    </section>
  );
}
