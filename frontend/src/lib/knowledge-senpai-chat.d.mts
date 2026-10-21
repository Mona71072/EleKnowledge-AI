import type { KnowledgeResearchMode, ResearchAnswer } from './knowledge-research.mjs';
import type { SenpaiSynthesisInputs, SenpaiSynthesisResult } from './knowledge-senpai-synthesis.mjs';
import type {
  SenpaiResearchDebug, SenpaiResearchErrorCode, SenpaiResearchFinal, SenpaiResearchResult,
  SenpaiResearchStep, SenpaiResearchUpdate,
} from './knowledge-senpai-research.mjs';

export type SenpaiLaneStatus = 'loading' | 'success' | 'error' | 'cancelled' | 'paused';

export type SenpaiChatLane = {
  status: SenpaiLaneStatus;
  answer?: ResearchAnswer;
  message?: string;
};

export type SenpaiSynthesisState = {
  status: 'loading' | 'success' | 'error';
  /** Present on success: the saved synthesis text (also restored from history). */
  content?: string;
  messageId?: string;
  inputs?: SenpaiSynthesisInputs;
  message?: string;
};

export type SenpaiResearchState = {
  /** `cancelled` is client-side only: polling stopped, the server job may keep running. */
  status: 'queued' | 'running' | 'completed' | 'failed' | 'cancelled';
  /** Append-only step events merged by seq; empty for a turn restored from history. */
  steps: readonly SenpaiResearchStep[];
  jobId?: string;
  /** Epoch milliseconds from the controller clock; absent for restored turns. */
  startedAt?: number;
  endedAt?: number;
  /** True while a 409 (the previous job is still running on the server) is being retried. */
  waiting?: boolean;
  result?: SenpaiResearchResult;
  debug?: SenpaiResearchDebug;
  error?: { code: SenpaiResearchErrorCode | 'ClientError'; message: string };
};

export type SenpaiChatTurn = {
  id: number;
  senpaiTurnId?: string;
  /** Model filter chosen for this turn; absent when none was given. */
  modelType?: string;
  query: string;
  normal: SenpaiChatLane;
  law: SenpaiChatLane;
  /** Absent until the user asks for the combined summary (or when restoring an older history). */
  synthesis?: SenpaiSynthesisState;
  /**
   * Present when the turn ran (or was saved) as a research job. Its `normal` / `law` lanes are
   * placeholders with status `paused` and carry no answer.
   */
  research?: SenpaiResearchState;
  /** Research turn only: what the user typed as the reply to a clarify result (`query` is the composed question that was searched). */
  supplement?: string;
  /** The question that `supplement` answers. */
  supplementOf?: string;
};

export type SenpaiChatSnapshot = {
  conversationId?: string;
  /** False for a server response that explicitly reports an incomplete history. */
  complete?: boolean;
  turns: readonly SenpaiChatTurn[];
  running: boolean;
};

export type SenpaiChatQuerySource = (request: {
  mode: KnowledgeResearchMode;
  query: string;
  modelType?: string;
  sessionId?: string;
  senpaiConversationId: string;
  senpaiTurnId: string;
  signal: AbortSignal;
}) => Promise<ResearchAnswer>;

export type SenpaiChatSynthesisSource = (request: {
  senpaiConversationId: string;
  senpaiTurnId: string;
  signal: AbortSignal;
}) => Promise<SenpaiSynthesisResult>;

export type SenpaiChatResearchSource = (request: {
  question: string;
  modelType?: string;
  senpaiConversationId: string;
  senpaiTurnId: string;
  clientRequestId: string;
  signal: AbortSignal;
  onUpdate: (update: SenpaiResearchUpdate) => void;
  onWaiting?: () => void;
}) => Promise<SenpaiResearchFinal>;

export type SenpaiChatController = {
  getSnapshot(): SenpaiChatSnapshot;
  /**
   * In research mode, a send right after a clarify result is composed with the previous question
   * unless `fresh` is true (used for retries and re-asking with another model).
   */
  send(query: string, options?: { modelType?: string; fresh?: boolean; supplement?: string; supplementOf?: string }): Promise<void>;
  /**
   * Build the combined summary of a turn. Allowed only when no search is running, both lanes
   * have settled and at least one succeeded; otherwise rejects with a validation error.
   */
  synthesize(turnId: number): Promise<void>;
  cancel(): void;
  reset(): void;
  /** Replace current state from a validated server history response. */
  restore(snapshot: { conversationId: string; turns: readonly SenpaiChatTurn[]; complete: boolean }): void;
  dispose(): void;
};

export function createSenpaiChat(options: {
  /** Required unless `researchSource` is given. */
  querySource?: SenpaiChatQuerySource;
  /** When given, `send` starts a research job instead of the two lanes. */
  researchSource?: SenpaiChatResearchSource;
  /** Injectable clock (epoch milliseconds) for deterministic tests. */
  now?: () => number;
  /** Required for `synthesize`; omit to disable the summary. */
  synthesisSource?: SenpaiChatSynthesisSource;
  onChange?: (snapshot: SenpaiChatSnapshot) => void;
  /** Injectable UUID generator for deterministic tests. */
  createId?: () => string;
}): SenpaiChatController;

export const SENPAI_MODEL_TYPES: ReadonlySet<string>;

/** Returns a saved model filter only when it is one of the known UI keys; otherwise undefined. */
export function normalizeSavedModelType(value: unknown): string | undefined;
