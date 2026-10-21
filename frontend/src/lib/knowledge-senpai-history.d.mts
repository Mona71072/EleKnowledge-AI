import type { SenpaiChatTurn } from './knowledge-senpai-chat.mjs';

export type SenpaiConversationSummary = {
  conversationId: string;
  title: string;
  createdAt: string;
  lastMessageTime: string;
  messageCount: number;
  daysUntilDeletion: number;
};

export type SenpaiConversationHistory = {
  conversationId: string;
  turns: SenpaiChatTurn[];
  complete: boolean;
};

export type SenpaiHistoryRequestOptions = {
  baseUrl: string;
  getToken: () => Promise<string | null | undefined>;
  fetchImpl?: typeof fetch;
  signal?: AbortSignal;
  timeoutMs?: number;
};

export function getSenpaiConversations(options: SenpaiHistoryRequestOptions): Promise<{
  sessions: SenpaiConversationSummary[];
  complete: boolean;
}>;

export function readSenpaiConversation(options: SenpaiHistoryRequestOptions & {
  conversationId: string;
}): Promise<SenpaiConversationHistory>;
