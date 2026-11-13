import type { ResearchAnswer } from './knowledge-research.mjs';

export type CommentReviewSection = { id: string; label: string; line: number };

export const MAX_REVIEW_COMMENT_CHARS: 900;
export const MAX_COMMENT_ADDITION_CHARS: 6000;

export function listCommentSections(body: unknown): CommentReviewSection[];
export function findCommentSection(body: unknown, sectionId: string, expectedLabel?: string): CommentReviewSection | undefined;

export function buildCommentResearchQuery(input: {
  title: string;
  sectionLabel: string;
  comment: string;
  modelWords?: readonly string[];
}): string;

export function buildCommentAddition(
  body: string,
  sectionId: string,
  answer: ResearchAnswer,
  draftText: string | undefined,
  checkedOn: string,
): string;

export function buildConfirmedCommentBody(
  body: string,
  sectionId: string,
  entries: ReadonlyArray<{ answer: ResearchAnswer; text: string; decision: 'confirm' | 'skip' | undefined }>,
): { body: string; applied: number };
