'use client';

import type { SenpaiResearchDebug, SenpaiResearchStep } from '@/lib/knowledge-senpai-research.mjs';

const tableHead = 'border border-gray-200 bg-white px-2 py-1 text-left font-medium';
const tableCell = 'border border-gray-200 px-2 py-1 align-top break-words';

function json(value: unknown) {
  return JSON.stringify(value, null, 2);
}

/** 開発者表示。整理結果・検索語・道具ごとの結果・予算・生の段階イベントを、畳める中立のパネルに並べる。 */
export function SenpaiDevPanel({ debug, steps, unverifiedRefs }: {
  debug?: SenpaiResearchDebug;
  steps: readonly SenpaiResearchStep[];
  unverifiedRefs?: readonly string[];
}) {
  const budget = debug?.budget;
  return (
    <section aria-label="開発者表示" className="rounded-xl border border-gray-200 bg-gray-50 font-mono text-[11px] leading-5 text-gray-700">
      <details open>
        <summary className="cursor-pointer select-none px-3 py-2 font-sans text-xs font-medium text-gray-600">開発者表示</summary>
        <div className="space-y-3 px-3 pb-3">
          {!debug && <p className="font-sans">デバッグ情報はありません（復元した相談や、管理者以外の応答には含まれません）。</p>}
          {debug?.understandingRaw && (
            <div><h5 className="font-sans font-medium">質問の整理（understandingRaw）</h5><pre className="mt-1 overflow-x-auto whitespace-pre-wrap break-words rounded-lg bg-white p-2">{json(debug.understandingRaw)}</pre></div>
          )}
          {debug?.queries && (
            <div>
              <h5 className="font-sans font-medium">検索語</h5>
              <dl className="mt-1 grid grid-cols-[4rem_minmax(0,1fr)] gap-x-2 gap-y-1">
                <dt className="text-gray-500">技術</dt><dd className="break-words">{debug.queries.tech.join(' / ') || '（なし）'}</dd>
                <dt className="text-gray-500">法令</dt><dd className="break-words">{debug.queries.law.join(' / ') || '（なし）'}</dd>
                <dt className="text-gray-500">ノウハウ</dt><dd className="break-words">{debug.queries.knowhow || '（なし）'}</dd>
              </dl>
            </div>
          )}
          {debug?.tools && (
            <div className="overflow-x-auto">
              <h5 className="font-sans font-medium">道具の呼び出し</h5>
              <table className="mt-1 min-w-full border-collapse">
                <thead><tr>{['#', '道具', '検索語', '絞り込み', '取得', '採用', '上位スコア', '時間(ms)'].map((name) => <th key={name} scope="col" className={tableHead}>{name}</th>)}</tr></thead>
                <tbody>
                  {debug.tools.map((tool, index) => (
                    <tr key={`${index}-${tool.seq}-${tool.tool}`}>
                      <td className={tableCell}>{tool.seq}</td>
                      <td className={tableCell}>{tool.tool}</td>
                      <td className={tableCell}>{tool.query ?? '–'}</td>
                      <td className={tableCell}>{tool.filters ? json(tool.filters) : '–'}</td>
                      <td className={tableCell}>{tool.hits ?? '–'}</td>
                      <td className={tableCell}>{tool.selected ?? '–'}</td>
                      <td className={tableCell}>{tool.topScores ? tool.topScores.join(', ') : '–'}</td>
                      <td className={tableCell}>{tool.ms ?? '–'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
          {budget && (
            <div>
              <h5 className="font-sans font-medium">予算の使用量</h5>
              <dl className="mt-1 grid grid-cols-[9rem_minmax(0,1fr)] gap-x-2 gap-y-1">
                <dt className="text-gray-500">検索</dt><dd>{budget.searchesUsed ?? '–'} / {budget.searchesMax ?? '–'} 回</dd>
                <dt className="text-gray-500">モデル呼び出し</dt><dd>{budget.modelCallsUsed ?? '–'} / {budget.modelCallsMax ?? '–'} 回</dd>
                <dt className="text-gray-500">経過時間</dt><dd>{budget.elapsedMs ?? '–'} / {budget.elapsedMaxMs ?? '–'} ms</dd>
              </dl>
            </div>
          )}
          {unverifiedRefs && unverifiedRefs.length > 0 && <p>照合で外した参照: {unverifiedRefs.join('、')}</p>}
          <details>
            <summary className="cursor-pointer font-sans font-medium">生の段階イベント（{steps.length}）</summary>
            <pre className="mt-1 overflow-x-auto whitespace-pre-wrap break-words rounded-lg bg-white p-2">{steps.length ? json(steps) : '（保存されていません）'}</pre>
          </details>
        </div>
      </details>
    </section>
  );
}
