import type { ResearchAnswer } from './knowledge-research.mjs';

export type KnowledgeComparisonStatus = 'consistent' | 'conditions_differ' | 'conflict' | 'unresolved';

export type KnowledgeComparisonAssessment = {
  status: KnowledgeComparisonStatus;
  findings: string;
  applicability: string;
  unresolvedPoints?: string;
};

export type KnowledgeComparisonInput = {
  technical: ResearchAnswer;
  law: ResearchAnswer;
  assessment: KnowledgeComparisonAssessment;
};

export class KnowledgeComparisonError extends Error {
  readonly code: 'validation';
  constructor(message: string);
}

export function buildComparisonNote(input: KnowledgeComparisonInput): string;
