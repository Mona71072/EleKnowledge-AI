export type SenpaiSynthesisInputs = {
  /** True when the technical-KB answer was part of the synthesis. */
  normal: boolean;
  /** True when the law-KB answer was part of the synthesis. */
  law: boolean;
  knowhowCount: number;
};

export type SenpaiSynthesisResult = {
  senpaiConversationId: string;
  senpaiTurnId: string;
  messageId: string;
  content: string;
  inputs: SenpaiSynthesisInputs;
  timestamp: string;
};

export type SenpaiSynthesisRequestOptions = {
  baseUrl: string;
  getToken: () => Promise<string | null | undefined>;
  fetchImpl?: typeof fetch;
  senpaiConversationId: string;
  senpaiTurnId: string;
  signal?: AbortSignal;
  timeoutMs?: number;
};

/** Requests the server-side synthesis of one saved Senpai turn (admin, dev only). */
export function requestSenpaiSynthesis(options: SenpaiSynthesisRequestOptions): Promise<SenpaiSynthesisResult>;
