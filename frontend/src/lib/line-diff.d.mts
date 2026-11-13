export type DiffRow = {
  kind: 'same' | 'added' | 'removed';
  text: string;
  beforeLine?: number;
  afterLine?: number;
  /** 行内で変わった部分。対になった削除行・追加行にだけ付く。 */
  segments?: InlineSegment[];
};
export type InlineSegment = { text: string; changed: boolean };
export type DiffSkipRow = { kind: 'skip'; count: number };
export type DiffResult = { tooLarge: boolean; rows: DiffRow[] };

export const DIFF_CONTEXT_LINES: number;
export const MAX_DIFF_CELLS: number;
export function diffLines(before: unknown, after: unknown, options?: { maxCells?: number }): DiffResult;
export function groupDiffHunks(rows: readonly DiffRow[], context?: number): Array<DiffRow | DiffSkipRow>;
export function summarizeDiff(rows: readonly DiffRow[]): { added: number; removed: number };

export const MAX_INLINE_LINE_CHARS: number;
export function diffInline(before: string, after: string, options?: { maxChars?: number }): { before: InlineSegment[]; after: InlineSegment[]; cells: number } | null;
export function annotateInlineChanges(rows: readonly DiffRow[]): DiffRow[];
