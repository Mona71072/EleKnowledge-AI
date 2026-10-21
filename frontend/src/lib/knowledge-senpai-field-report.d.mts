import type { SenpaiChatTurn } from './knowledge-senpai-chat.mjs';

export type FieldReportReaction = 'matched' | 'not_matched' | 'unsure';
export type FieldReportReviewState = 'unconfirmed' | 'awaiting_review' | 'reflected' | 'held_or_rejected';

export const FIELD_REPORT_REACTIONS: ReadonlySet<FieldReportReaction>;
export const FIELD_REPORT_REVIEW_STATES: ReadonlySet<FieldReportReviewState>;
export const FIELD_REPORT_REACTION_LABELS: Readonly<Record<FieldReportReaction, string>>;
export const FIELD_REPORT_REVIEW_STATE_LABELS: Readonly<Record<FieldReportReviewState, string>>;
export const FIELD_REPORT_FINDING_MAX: number;
export const FIELD_REPORT_CONDITION_MAX: number;

export type FieldReportCard = { knowledgeId: string; cardVersion: number; title: string };

export type FieldReportDraft = {
  finding: string;
  condition: string;
  /** UI model key or '' for none. Starts as the model chosen for the turn. */
  modelType: string;
  /** knowledgeId → reaction; '' or absent means the card is not sent. */
  reactions: Record<string, FieldReportReaction | ''>;
};

export type FieldReportPayload = {
  senpaiConversationId: string;
  senpaiTurnId: string;
  finding: string;
  condition?: string;
  modelType?: string;
  cardReactions: Array<{ knowledgeId: string; cardVersion: number; reaction: FieldReportReaction }>;
  confirmed: true;
};

export type FieldReport = {
  reportId: string;
  senpaiConversationId: string;
  senpaiTurnId: string;
  createdAt: string;
  finding: string;
  condition?: string;
  modelType?: string;
  reviewState: FieldReportReviewState;
  cardReactions: FieldReportPayload['cardReactions'];
};

type RequestOptions = {
  baseUrl: string;
  getToken: () => Promise<string | null | undefined>;
  fetchImpl?: typeof fetch;
  signal?: AbortSignal;
  timeoutMs?: number;
};

export function fieldReportCards(turn: SenpaiChatTurn): FieldReportCard[];
export function createFieldReportDraft(turn: SenpaiChatTurn): FieldReportDraft;
export function validateFieldReportDraft(draft: FieldReportDraft): string[];
export function buildFieldReportPayload(options: { conversationId: string; turn: SenpaiChatTurn; draft: FieldReportDraft }): FieldReportPayload;
export function submitFieldReport(options: RequestOptions & { payload: FieldReportPayload }): Promise<FieldReport>;
export function listFieldReports(options: RequestOptions & { conversationId: string }): Promise<Record<string, FieldReport>>;
