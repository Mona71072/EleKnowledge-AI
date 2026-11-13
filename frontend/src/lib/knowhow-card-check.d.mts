export type CheckTarget = 'normal' | 'law';
export type CheckQuestionKind = 'open_item' | 'value_check' | 'basis' | 'law' | 'manual';
export type CheckQuestion = {
  id: string;
  kind: CheckQuestionKind;
  text: string;
  targets: CheckTarget[];
  sourceSection: string;
  sourceText: string;
  selected: boolean;
};

export const MAX_CHECK_QUESTIONS: number;
export const CHECK_KINDS: readonly Exclude<CheckQuestionKind, 'manual'>[];
export const CHECK_TARGETS_BY_KIND: Readonly<Record<CheckQuestionKind, readonly CheckTarget[]>>;
export const CHECK_KIND_LABELS: Readonly<Record<CheckQuestionKind, string>>;

export function checkModelWords(frontmatter?: Record<string, unknown> | null): string[];

export function buildCheckQuestions(card: {
  frontmatter?: Record<string, unknown> | null;
  body?: unknown;
  limit?: number;
}): CheckQuestion[];

export function createManualQuestion(existing: ReadonlyArray<{ id: string }>, text: string): CheckQuestion;

export function countCheckCalls(questions: ReadonlyArray<Pick<CheckQuestion, 'selected' | 'text' | 'targets'>>): {
  questions: number;
  normal: number;
  law: number;
  total: number;
};
