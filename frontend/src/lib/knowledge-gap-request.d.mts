export type KnowledgeGapRequest = { kind: 'senpai'; senpaiTurnId: string } | { kind: 'official_kb' };

/** Store one explicit, browser-local handoff marker. */
export function storeKnowledgeGapRequest(
  request: KnowledgeGapRequest | { senpaiTurnId: string },
  storage?: Pick<Storage, 'setItem'> | null,
): boolean;

/** Read and remove the one pending handoff marker, if valid. */
export function consumeKnowledgeGapRequest(
  storage?: Pick<Storage, 'getItem' | 'removeItem'> | null,
): KnowledgeGapRequest | null;
