import type { CheckDecision } from './knowhow-card-proposal.mjs';

export type RewriteSection = { heading: string; body: string };
export type RewriteExcludedReason = 'duplicate' | 'empty' | 'too_long' | 'total_too_long';
export type RewriteExcluded = { heading: string; reason: RewriteExcludedReason };
export type RewriteSource = { title: string; page?: number };
export type RewriteLane = 'technical' | 'law' | 'field';
export type RewriteEvidenceItem = {
  /** 画面側の対応づけ用。API には送らない。 */
  questionId: string;
  question: string;
  lane: RewriteLane;
  checkedOn: string;
  answer: string;
  sources: RewriteSource[];
};
export type RewriteRequest = {
  knowledgeId: string;
  cardVersion: number;
  targets: RewriteSection[];
  context: RewriteSection[];
  evidence: Array<Omit<RewriteEvidenceItem, 'questionId'>>;
};
export type RewriteEvidenceRef = { number: number; questionId: string; question: string };
export type RewritePlan = {
  request: RewriteRequest | null;
  evidenceRefs: RewriteEvidenceRef[];
  evidenceOmitted: number;
  excluded: RewriteExcluded[];
  /** 作れない理由。作れるときは空文字。 */
  blocker: string;
};

export type RewriteWarning = { code: string; values: string[] };
export type RewriteSectionResult = {
  heading: string;
  status: 'changed' | 'unchanged' | 'rejected';
  /** changed のときだけ。 */
  body?: string;
  /** changed のときだけ。案を作った時点の節の本文。 */
  baseBody?: string;
  reason?: string;
  evidence: number[];
  warnings: RewriteWarning[];
};
export type RewriteConflict = { heading: string | null; description: string; evidence: number[] };
export type RewriteProposal = {
  knowledgeId: string;
  cardVersion: number;
  bases: RewriteSection[];
  sections: RewriteSectionResult[];
  conflicts: RewriteConflict[];
};

export const REWRITE_TARGET_HEADINGS: readonly string[];
export const REWRITE_LIMITS: Readonly<{
  knowledgeIdPattern: RegExp;
  cardVersionMax: number;
  targetMax: number;
  targetBodyChars: number;
  targetTotalChars: number;
  contextMax: number;
  contextHeadingChars: number;
  contextBodyChars: number;
  contextTotalChars: number;
  evidenceMax: number;
  questionChars: number;
  answerChars: number;
  sourcesMax: number;
  sourceTitleChars: number;
  responseBodyChars: number;
  reasonChars: number;
}>;

export function isRewriteEnabled(value: unknown): boolean;
export function charCount(text: string): number;
export function readSections(markdown: unknown): {
  lines: string[];
  sections: Array<{ heading: string; headingIndex: number; start: number; end: number; body: string }>;
};
export function selectRewriteSections(body: string): { targets: RewriteSection[]; context: RewriteSection[]; excluded: RewriteExcluded[] };
export type RewriteBodyProblem = 'empty' | 'too_long' | 'heading_in_body' | 'unclosed_fence' | 'suspicious_text' | 'link_or_html';
export function findRewriteStructureProblem(body: unknown): Exclude<RewriteBodyProblem, 'suspicious_text' | 'link_or_html'> | null;
export function findRewriteBodyProblem(body: unknown, original?: string): RewriteBodyProblem | null;
export function hasSuspiciousText(text: unknown): boolean;
export function hasNewLinkOrHtml(text: string, original?: string): boolean;
export function isUnsafeDisplayText(text: string): boolean;

export function buildRewriteEvidence(input: {
  questions: ReadonlyArray<{ id: string; text: string; targets: readonly string[] }>;
  tasks: ReadonlyArray<{ questionId: string; mode: string; result?: unknown }>;
  decisions: Readonly<Record<string, CheckDecision | undefined>>;
}): RewriteEvidenceItem[];
export function buildRewriteRequest(input: {
  frontmatter: Record<string, unknown> | null | undefined;
  body: string;
  evidence: readonly RewriteEvidenceItem[];
}): RewritePlan;
export function buildFieldRewriteRequest(input: { topic?: string; title: string; excerpt: string; checkedOn: string }): RewriteRequest;

export function describeRewriteWarning(warning: { code: string; values?: readonly string[] }): string;
export function normalizeRewriteResponse(data: unknown, request: RewriteRequest): RewriteProposal | null;
export function buildConflictOpenItem(conflict: { description: string }): string;
export function summarizeRewriteDecisions(
  headings: readonly string[],
  decisions: Readonly<Record<string, CheckDecision | undefined>>,
): { total: number; confirmed: number; skipped: number; pending: number };
export function buildAcceptedRewrites(
  proposal: RewriteProposal,
  decisions: Readonly<Record<string, CheckDecision | undefined>>,
  conflictDecisions: Readonly<Record<number, CheckDecision | undefined>>,
): RewriteSection[];

export function applySectionRewrites(
  markdown: string,
  accepted: readonly RewriteSection[],
  expectedBody: string,
): { markdown: string; applied: number; stale: string[] };
export function composeCardEdits(
  body: string,
  edits: {
    rewrites: readonly RewriteSection[];
    expectedBody: string;
    proposals: ReadonlyArray<{ question: string; checkedOn: string; markdown: string }>;
  },
): { markdown: string; rewritten: number; stale: string[]; applied: number; skipped: number };
