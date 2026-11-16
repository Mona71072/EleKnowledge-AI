import { memo, useMemo } from 'react';
import { annotateInlineChanges, diffLines, groupDiffHunks, summarizeDiff } from '../../lib/line-diff.mjs';
import { listChangedSections } from '../../lib/knowledge-diff-sections.mjs';
import type { DiffRow, InlineSegment } from '../../lib/line-diff.mjs';

type Props = {
  before: string;
  after: string;
  label?: string;
  /** 対になった削除行・追加行で、行内の変わった部分だけを濃い背景で強調する。既定はオフ。 */
  inlineHighlight?: boolean;
  onSectionSelect?: (sectionId: string) => void;
};

/** 原文と修正案を行ごとに比較し、変更箇所の前後3行と件数を表示する。 */
export function KnowledgeLineDiff({ before, after, label = '原文と修正案の差分', inlineHighlight = false, onSectionSelect }: Props) {
  // before / after が同じなら再計算しない（本文の編集以外の再描画で、行ごとの差分を作り直さない）。
  const { diff, counts, rows, changedSections } = useMemo(() => {
    const computed = diffLines(before, after);
    return computed.tooLarge
      ? { diff: computed, counts: null, rows: [], changedSections: [] }
      : {
        diff: computed,
        counts: summarizeDiff(computed.rows),
        rows: groupDiffHunks(inlineHighlight ? annotateInlineChanges(computed.rows) : computed.rows),
        changedSections: onSectionSelect ? listChangedSections(before, after, computed.rows) : [],
      };
  }, [before, after, inlineHighlight, onSectionSelect]);

  if (diff.tooLarge || counts === null) {
    return (
      <section aria-label={label} className="space-y-3">
        <p role="status" className="text-sm text-amber-900">差分が大きいため全文を表示しています。</p>
        <div className="grid min-w-0 grid-cols-1 gap-3 lg:grid-cols-2">
          <TextVersion label="変更前" text={before} />
          <TextVersion label="変更後" text={after} />
        </div>
      </section>
    );
  }

  if (counts.added + counts.removed === 0) {
    return <p className="text-sm text-gray-600">変更はありません。</p>;
  }

  return (
    <section aria-label={label} className="space-y-3">
      {onSectionSelect && changedSections.length > 0 && (
        <nav aria-label="変更した節" data-testid="changed-section-shortcuts" className="rounded-lg border border-blue-100 bg-blue-50/60 p-3">
          <p className="mb-2 text-xs font-semibold text-gray-700">変更した節</p>
          <ul className="flex flex-wrap gap-2">
            {changedSections.map((section) => (
              <li key={`${section.label}-${section.status}`}>
                {section.status === 'changed' && onSectionSelect ? (
                  <button type="button" data-testid="changed-section-shortcut" data-section-label={section.label}
                    data-section-status="changed" onClick={() => onSectionSelect(section.sectionId)}
                    className="rounded-full border border-blue-300 bg-white px-3 py-1 text-left text-xs font-medium text-blue-900 hover:bg-blue-100 focus:outline-none focus:ring-2 focus:ring-blue-500">
                    「{section.label}」にコメント
                  </button>
                ) : (
                  <span data-testid="changed-section-shortcut" data-section-label={section.label}
                    data-section-status={section.status}
                    className={`inline-flex rounded-full px-3 py-1 text-xs ${section.status === 'removed' ? 'bg-red-100 text-red-900' : 'bg-amber-100 text-amber-950'}`}>
                    {section.status === 'removed' ? `「${section.label}」は削除` : `「${section.label}」は重複のため選べません`}
                  </span>
                )}
              </li>
            ))}
          </ul>
        </nav>
      )}
      <p className="flex flex-wrap gap-x-3 gap-y-1 text-sm font-medium" aria-live="polite">
        <span className="text-green-800">追加{counts.added}行</span>
        <span className="text-red-800">削除{counts.removed}行</span>
      </p>
      <div className="max-h-[34rem] min-w-0 overflow-auto rounded-lg border border-gray-200 bg-gray-50 p-3 font-mono text-xs leading-6" role="list" aria-label="差分の行">
        <div aria-hidden="true" className="mb-1 grid min-w-[15rem] grid-cols-[3rem_3rem_minmax(0,1fr)] border-b border-gray-300 pb-1 font-sans text-[0.65rem] font-semibold leading-4 text-gray-600">
          <span className="text-center">変更前</span>
          <span className="text-center">変更後</span>
          <span>内容</span>
        </div>
        {rows.map((row, index) => renderRow(row, index))}
      </div>
    </section>
  );
}

function renderRow(row: DiffRow | { kind: 'skip'; count: number }, index: number) {
  if (row.kind === 'skip') {
    return <p key={`skip-${index}`} role="listitem" aria-label={`省略、ほか ${row.count} 行`} className="py-1 text-center text-gray-500">ほか {row.count} 行</p>;
  }

  const isAdded = row.kind === 'added';
  const isRemoved = row.kind === 'removed';
  const sign = isAdded ? '+' : isRemoved ? '−' : ' ';
  const label = isAdded ? '追加' : isRemoved ? '削除' : '変更なし';
  const beforeLabel = row.beforeLine ? `変更前${row.beforeLine}行目` : '';
  const afterLabel = row.afterLine ? `変更後${row.afterLine}行目` : '';
  const lineLabels = [beforeLabel, afterLabel].filter(Boolean).join('、');
  const color = isAdded ? 'bg-green-50 text-green-950' : isRemoved ? 'bg-red-50 text-red-950' : 'text-gray-700';

  return (
    <div key={`${row.kind}-${index}`} role="listitem" aria-label={`${label}、${lineLabels}`} className={`grid min-w-[15rem] grid-cols-[3rem_3rem_minmax(0,1fr)] ${color}`}>
      <span aria-hidden="true" className="select-none text-center text-gray-500">{row.beforeLine ?? '—'}</span>
      <span aria-hidden="true" className="select-none text-center text-gray-500">{row.afterLine ?? '—'}</span>
      <span className="min-w-0 whitespace-pre-wrap break-words"><span aria-hidden="true" className="mr-2 inline-block w-3 select-none text-center text-gray-500">{sign}</span>{row.segments ? renderSegments(row.segments, isAdded) : row.text || ' '}</span>
    </div>
  );
}

function renderSegments(segments: InlineSegment[], added: boolean) {
  const mark = added ? 'bg-green-300 text-green-950' : 'bg-red-300 text-red-950';
  return segments.map((segment, index) => (segment.changed
    ? <mark key={index} className={`rounded-sm px-0.5 ${mark}`}>{segment.text}</mark>
    : <span key={index}>{segment.text}</span>));
}

const TextVersion = memo(function TextVersion({ label, text }: { label: string; text: string }) {
  return (
    <section className="min-w-0 rounded-lg border border-gray-200 bg-white p-3" aria-label={label}>
      <h3 className="mb-2 text-sm font-semibold text-gray-800">{label}</h3>
      <pre className="max-h-[34rem] overflow-auto whitespace-pre-wrap break-words font-mono text-xs leading-6 text-gray-800">{text}</pre>
    </section>
  );
});
