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
  sessionId?: string;
  senpaiConversationId: string;
  senpaiTurnId: string;
  signal: AbortSignal;
}) => Promise<ResearchAnswer>;

export type SenpaiChatController = {
  getSnapshot(): SenpaiChatSnapshot;
  send(query: string): Promise<void>;
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
