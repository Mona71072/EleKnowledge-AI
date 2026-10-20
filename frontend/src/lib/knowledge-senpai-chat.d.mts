import type { KnowledgeResearchMode, ResearchAnswer } from './knowledge-research.mjs';

export type SenpaiLaneStatus = 'loading' | 'success' | 'error' | 'cancelled' | 'paused';

export type SenpaiChatLane = {
  status: SenpaiLaneStatus;
  answer?: ResearchAnswer;
  message?: string;
};

export type SenpaiChatTurn = {
  id: number;
  query: string;
  normal: SenpaiChatLane;
  law: SenpaiChatLane;
};

export type SenpaiChatSnapshot = {
  turns: readonly SenpaiChatTurn[];
  running: boolean;
};

export type SenpaiChatQuerySource = (request: {
  mode: KnowledgeResearchMode;
  query: string;
  sessionId?: string;
  signal: AbortSignal;
}) => Promise<ResearchAnswer>;

export type SenpaiChatController = {
  getSnapshot(): SenpaiChatSnapshot;
  send(query: string): Promise<void>;
  cancel(): void;
  reset(): void;
  dispose(): void;
};

export function createSenpaiChat(options: {
  querySource: SenpaiChatQuerySource;
  onChange?: (snapshot: SenpaiChatSnapshot) => void;
}): SenpaiChatController;
