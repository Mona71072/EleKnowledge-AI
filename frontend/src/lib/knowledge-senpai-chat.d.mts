import type { KnowledgeResearchMode, ResearchAnswer } from './knowledge-research.mjs';

export type SenpaiLaneStatus = 'loading' | 'success' | 'error' | 'cancelled' | 'paused';

export type SenpaiChatLane = {
  status: SenpaiLaneStatus;
  answer?: ResearchAnswer;
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

export type SenpaiChatController = {
  getSnapshot(): SenpaiChatSnapshot;
  send(query: string, options?: { modelType?: string }): Promise<void>;
  cancel(): void;
  reset(): void;
  /** Replace current state from a validated server history response. */
  restore(snapshot: { conversationId: string; turns: readonly SenpaiChatTurn[]; complete: boolean }): void;
  dispose(): void;
};

export function createSenpaiChat(options: {
  querySource: SenpaiChatQuerySource;
  onChange?: (snapshot: SenpaiChatSnapshot) => void;
  /** Injectable UUID generator for deterministic tests. */
  createId?: () => string;
}): SenpaiChatController;

export const SENPAI_MODEL_TYPES: ReadonlySet<string>;

/** Returns a saved model filter only when it is one of the known UI keys; otherwise undefined. */
export function normalizeSavedModelType(value: unknown): string | undefined;
