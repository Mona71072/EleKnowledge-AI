import type { KnowledgeResearchMode, ResearchAnswer } from './knowledge-research.mjs';
import type { SenpaiSynthesisInputs, SenpaiSynthesisResult } from './knowledge-senpai-synthesis.mjs';

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

export type SenpaiChatController = {
  getSnapshot(): SenpaiChatSnapshot;
  send(query: string, options?: { modelType?: string }): Promise<void>;
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
  querySource: SenpaiChatQuerySource;
  /** Required for `synthesize`; omit to disable the summary. */
  synthesisSource?: SenpaiChatSynthesisSource;
  onChange?: (snapshot: SenpaiChatSnapshot) => void;
  /** Injectable UUID generator for deterministic tests. */
  createId?: () => string;
}): SenpaiChatController;

export const SENPAI_MODEL_TYPES: ReadonlySet<string>;

/** Returns a saved model filter only when it is one of the known UI keys; otherwise undefined. */
export function normalizeSavedModelType(value: unknown): string | undefined;
