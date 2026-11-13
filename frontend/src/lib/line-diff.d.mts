export type DiffRow = {
  kind: 'same' | 'added' | 'removed';
  text: string;
  beforeLine?: number;
  afterLine?: number;
};
export type DiffSkipRow = { kind: 'skip'; count: number };
export type DiffResult = { tooLarge: boolean; rows: DiffRow[] };

export const DIFF_CONTEXT_LINES: number;
export const MAX_DIFF_CELLS: number;
export function diffLines(before: unknown, after: unknown, options?: { maxCells?: number }): DiffResult;
export function groupDiffHunks(rows: readonly DiffRow[], context?: number): Array<DiffRow | DiffSkipRow>;
export function summarizeDiff(rows: readonly DiffRow[]): { added: number; removed: number };
