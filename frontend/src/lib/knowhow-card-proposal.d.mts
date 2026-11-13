import type { ResearchAnswer } from './knowledge-research.mjs';

export const PROPOSAL_ANSWER_HEAD_CHARS: number;
export const PROPOSAL_MAX_SOURCES: number;

export const CHECK_DECISIONS: Readonly<{ confirm: 'confirm'; skip: 'skip' }>;
export type CheckDecision = 'confirm' | 'skip';
export function summarizeCheckDecisions(
  questionIds: ReadonlyArray<string>,
  decisions: Readonly<Record<string, CheckDecision | undefined>>,
): { total: number; confirmed: number; skipped: number; pending: number };
export function formatCheckDate(date: Date): string;
export function classifyCheckAnswer(answer: ResearchAnswer | null | undefined): 'found' | 'not_found' | 'clarify' | 'no_source';
export function classifyProposalEvidence(input: { technical?: ResearchAnswer; law?: ResearchAnswer }): 'sourced' | 'not_found' | 'no_source';
export function buildCheckProposal(input: {
  question: string;
  technical?: ResearchAnswer;
  law?: ResearchAnswer;
  checkedOn: string;
}): string;

export function applyCheckProposals(
  markdown: string,
  proposals: ReadonlyArray<{ question: string; checkedOn: string; markdown: string }>,
): { markdown: string; applied: number; skipped: number };
