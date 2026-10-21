export type SenpaiResearchJobStatus = 'queued' | 'running' | 'completed' | 'failed';
export type SenpaiResearchStepName =
  | 'understand' | 'knowhow' | 'tech_search' | 'law_search' | 'sufficiency'
  | 'retry_search' | 'doc_page' | 'clarify' | 'synthesize' | 'verify';
export type SenpaiResearchStepStatus = 'running' | 'done' | 'skipped' | 'failed';
export type SenpaiResearchKind = 'answer' | 'clarify' | 'not_found';
export type SenpaiResearchStopReason = 'sufficient' | 'budget' | 'no_new_results' | 'clarify' | 'insufficient' | 'judgment_failed' | 'partial';
export type SenpaiResearchErrorCode = 'Timeout' | 'BudgetExceeded' | 'Internal' | 'QuestionUnavailable';
export type SenpaiResearchModelFit = 'matched' | 'general' | 'other_product' | 'unknown';

export type SenpaiResearchStep = {
  seq: number;
  step: SenpaiResearchStepName;
  labelJa: string;
  detailJa?: string;
  status: SenpaiResearchStepStatus;
  counts?: { hits?: number; selected?: number; documents?: number };
  startedAt: string;
  endedAt: string | null;
};

export type SenpaiResearchTimelineRow = {
  key: string;
  seq: number;
  step: SenpaiResearchStepName;
  labelJa: string;
  status: SenpaiResearchStepStatus;
  detailJa?: string;
  counts?: { hits?: number; selected?: number; documents?: number };
  startedAt: string;
  endedAt: string | null;
};

export type SenpaiResearchTechSource = {
  ref: string; title: string; documentName?: string; pageNumber?: number; sourceUri?: string;
};
export type SenpaiResearchLawSource = {
  ref: string; lawTitle: string; provision?: string; effectiveDate?: string; sourceUrl?: string;
};
export type SenpaiResearchUsedKnowhow = {
  ref: string; knowledgeId: string; cardVersion: number; title: string; status: 'draft' | 'approved';
  modelFit?: SenpaiResearchModelFit;
  /** UI model keys the card is scoped to; present with `modelFit: 'other_product'`. */
  modelFitProducts?: string[];
};
export type SenpaiResearchCandidateKnowhow = { knowledgeId: string; cardVersion: number; title: string };

export type SenpaiResearchUnderstanding = {
  modelType?: string | null; controlMethod?: string | null; part?: string | null;
  symptom?: string | null; situation?: string | null;
  intent?: 'procedure' | 'cause' | 'spec_value' | 'legal' | 'other';
  lawRelevant?: boolean;
};

export type SenpaiResearchResult = {
  kind: SenpaiResearchKind;
  /** Markdown text; never HTML. Empty for clarify / not_found without text. */
  answerMarkdown: string;
  clarifyQuestions: string[];
  sources: {
    tech: SenpaiResearchTechSource[];
    law: SenpaiResearchLawSource[];
    knowhow: { used: SenpaiResearchUsedKnowhow[]; candidates: SenpaiResearchCandidateKnowhow[] };
  };
  understanding?: SenpaiResearchUnderstanding;
  unverifiedRefs: string[];
  /** Present only when a technical or law search failed completely. */
  warnings?: string[];
  stopReason?: SenpaiResearchStopReason;
};

export type SenpaiResearchDebug = {
  understandingRaw?: Record<string, unknown>;
  queries?: { tech: string[]; law: string[]; knowhow?: string };
  tools?: Array<{
    seq: number; tool: string; query?: string; filters?: Record<string, unknown>;
    hits?: number; selected?: number; topScores?: number[]; ms?: number;
  }>;
  budget?: {
    searchesUsed?: number; searchesMax?: number; modelCallsUsed?: number; modelCallsMax?: number;
    elapsedMs?: number; elapsedMaxMs?: number; inputBytesMax?: number;
  };
  stages?: SenpaiResearchMeasurement[];
  progress?: SenpaiResearchMeasurement[];
  stopDetail?: 'repeated_query' | 'repeated_results' | 'no_exposed_progress' | 'search_limit' | 'model_limit' | 'time_limit' | 'input_limit';
  lastJudgment?: 'sufficient' | 'insufficient' | 'unjudged';
  grounding?: { mode: 'not_run' | 'model_verified' | 'extractive_fallback' | 'rejected'; articleMismatches?: string[]; guardReasons?: 'policy_explanation'[] };
  coverage?: { missing: string[]; supported: Array<{ id: string; kind: string; status: string; ref: string }> };
};

export type SenpaiResearchMeasurement = {
  stage?: string; action?: string; outcome?: string;
  seq?: number; round?: number; ms?: number; modelCalls?: number; searches?: number;
  searchesCharged?: number; selected?: number; newCandidateItems?: number; newExposedEvidence?: number;
  evidenceValidity?: 'unassessed'; completed?: boolean; usageMissing?: boolean;
  usage?: { inputTokens?: number; outputTokens?: number; cacheReadInputTokens?: number; cacheWriteInputTokens?: number };
};

export type SenpaiResearchError = { code: SenpaiResearchErrorCode; message: string };

export type SenpaiResearchStatusResponse = {
  jobId: string;
  status: SenpaiResearchJobStatus;
  steps: SenpaiResearchStep[];
  pollAfterMs?: number;
  result?: SenpaiResearchResult;
  error?: SenpaiResearchError;
  debug?: SenpaiResearchDebug;
};

export type SenpaiResearchFinal = {
  jobId: string;
  status: 'completed' | 'failed';
  steps: SenpaiResearchStep[];
  result?: SenpaiResearchResult;
  error?: SenpaiResearchError;
  debug?: SenpaiResearchDebug;
};

export type SenpaiResearchUpdate = { jobId: string; status: SenpaiResearchJobStatus; steps: SenpaiResearchStep[] };

type CommonOptions = {
  baseUrl: string;
  getToken: () => Promise<string | null | undefined>;
  fetchImpl?: typeof fetch;
  signal?: AbortSignal;
  timeoutMs?: number;
};

export const SENPAI_RESEARCH_ERROR_MESSAGES: Readonly<Record<SenpaiResearchErrorCode, string>>;
export const SENPAI_RESEARCH_CANCELLED_MESSAGE: string;

export function startSenpaiResearch(options: CommonOptions & {
  question: string;
  modelType?: string;
  senpaiConversationId: string;
  senpaiTurnId: string;
  clientRequestId: string;
}): Promise<{ jobId: string; status: 'queued'; pollAfterMs?: number }>;

export function getSenpaiResearchStatus(options: CommonOptions & {
  jobId: string;
  afterSeq?: number;
}): Promise<SenpaiResearchStatusResponse>;

export const START_RETRY_INTERVAL_MS: number;
export const START_RETRY_GIVE_UP_MS: number;
export function runSenpaiResearch(options: CommonOptions & {
  question: string;
  modelType?: string;
  senpaiConversationId: string;
  senpaiTurnId: string;
  clientRequestId: string;
  onUpdate?: (update: SenpaiResearchUpdate) => void;
  /** 前の調査がサーバーで続いている間（409）、開始を待つたびに呼ばれる。 */
  onWaiting?: () => void;
  retryIntervalMs?: number;
  retryGiveUpMs?: number;
  /** タブの表示・非表示を見る対象（既定は document）。 */
  visibility?: { visibilityState?: string; addEventListener?: Function; removeEventListener?: Function } | null;
  now?: () => number;
  setTimer?: (fn: () => void, delayMs: number) => unknown;
  clearTimer?: (timer: unknown) => void;
}): Promise<SenpaiResearchFinal>;

export function normalizeSenpaiResearchResult(raw: unknown): SenpaiResearchResult;
export function mergeResearchSteps(
  current: readonly SenpaiResearchStep[] | undefined,
  incoming: readonly SenpaiResearchStep[] | undefined,
): SenpaiResearchStep[];
export function buildTimelineRows(steps: readonly SenpaiResearchStep[] | undefined): SenpaiResearchTimelineRow[];
export function techSourceHref(source: { sourceUri?: string; pageNumber?: number } | null | undefined): string | undefined;
export function lawSourceHref(source: { sourceUrl?: string } | null | undefined): string | undefined;
