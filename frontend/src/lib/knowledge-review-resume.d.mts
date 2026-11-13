import type { KnowledgeParsedMarkdown, KnowledgeWorkspaceState } from './knowledge-workbench.mjs';

export const MAX_REVIEW_RECORD_BYTES: number;

/** Restore a saved JSON work record. Rejects with a TypeError carrying a Japanese message. */
export function restoreReviewWorkspace(text: string): Promise<{
  parsed: KnowledgeParsedMarkdown;
  workspace: KnowledgeWorkspaceState;
}>;
