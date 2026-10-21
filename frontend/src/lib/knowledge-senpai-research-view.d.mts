export function researchRefAnchor(prefix: string, ref: string): string;
export function linkResearchRefs(markdown: string | undefined, knownRefs: ReadonlySet<string>, anchorPrefix: string): string;
export function formatElapsed(ms: number): string;

import type { SenpaiResearchResult, SenpaiResearchStepStatus, SenpaiResearchStepName } from './knowledge-senpai-research.mjs';
export function stepRowLabel(row: { step: SenpaiResearchStepName | string; status: SenpaiResearchStepStatus; labelJa: string }): string;
export type SenpaiStructuredAnswer = { lead: string; evidence: string; notes: string };
export function structureAnswer(markdown: string | undefined): SenpaiStructuredAnswer | null;
export const CLARIFY_ORIGINAL_RESERVE: number;
export function clarifySupplementLimit(original: string): number;
export function clarifyOriginalTruncated(original: string, supplement: string): boolean;
export function composeClarifyQuestion(original: string, supplement: string): string;
export function splitClarifyQuestion(query: string): { original: string; supplement: string } | null;
export function nextAnnouncement(
  wasRunning: boolean,
  snapshot: { running: boolean; turns: readonly { research?: { status: string; result?: { kind?: string } }; normal?: { status: string }; law?: { status: string } }[] },
  current?: string,
): string;
export function clarifyAsksModel(result: Pick<SenpaiResearchResult, 'clarifyQuestions' | 'answerMarkdown'>): boolean;
export function modelMismatch(
  result: Pick<SenpaiResearchResult, 'understanding'>,
  selectedModel: string | undefined,
  knownModels: ReadonlySet<string>,
): { detected: string; selected: string } | null;
export function sourceSummary(result: Pick<SenpaiResearchResult, 'sources'>): string | null;
export function buildCopyText(result: SenpaiResearchResult): string;
export function copyText(text: string, clipboard?: { writeText(text: string): Promise<void> }): Promise<boolean>;
export const EXAMPLE_QUESTIONS: readonly string[];
export function isRedundantDetail(row: { step: string; status: SenpaiResearchStepStatus; labelJa: string; detailJa?: string }): boolean;
