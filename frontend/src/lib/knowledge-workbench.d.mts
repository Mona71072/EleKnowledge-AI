export type KnowledgeKbReviewStatus = 'unverified' | 'reviewed' | 'conflict';

export type KnowledgeParsedMarkdown = {
  id: string;
  version: number;
  title: string;
  body: string;
  frontmatter: Record<string, unknown>;
  metadata: Record<string, unknown>;
  originalMarkdown: string;
};

export type KnowledgeKbReview = {
  status: KnowledgeKbReviewStatus;
  reference: string;
  note: string;
};

export type KnowledgePlacementReceipt = {
  destination: string;
  recordedAt: string;
  baseVersion: number;
  revision: number;
  text: string;
};

export type KnowledgeWorkspaceState = {
  document: {
    id: string;
    baseVersion: number;
    title: string;
    baseMarkdown: string;
    metadata: Record<string, unknown>;
  };
  body: string;
  noteText: string;
  kbReview: KnowledgeKbReview;
  revision: number;
  reviewedRevision: number | null;
  copiedRevision: number | null;
  placements: KnowledgePlacementReceipt[];
};

export type KnowledgeProposalPacket = {
  format: 'eleknowledge-knowledge-proposal/v1';
  base: {
    id: string;
    version: number;
    markdown: string;
    metadata: Record<string, unknown>;
  };
  proposal: {
    revision: number;
    markdown: string;
    oneNoteText: string;
    publishable: false;
    state: 'working-proposal';
  };
  reviewedRevision: number | null;
  copiedRevision: number | null;
  placements: Array<KnowledgePlacementReceipt & { knowledgeId: string; textSha256: string }>;
  kbReview: KnowledgeKbReview;
  hashes: {
    baseMarkdownSha256: string;
    bodySha256: string;
    oneNoteTextSha256: string;
  };
};

export function parseKnowledgeMarkdown(markdown: string): KnowledgeParsedMarkdown;
export function createWorkspace(parsed: KnowledgeParsedMarkdown): KnowledgeWorkspaceState;
export function editBody(state: KnowledgeWorkspaceState, body: string): KnowledgeWorkspaceState;
export function editOneNoteDraft(state: KnowledgeWorkspaceState, text: string): KnowledgeWorkspaceState;
export function setKbReview(
  state: KnowledgeWorkspaceState,
  review: { status: KnowledgeKbReviewStatus; reference?: string; note?: string },
): KnowledgeWorkspaceState;
export function confirmOneNote(
  state: KnowledgeWorkspaceState,
  confirmation: { checked: true },
): KnowledgeWorkspaceState;
export function markCopied(state: KnowledgeWorkspaceState, expectedRevision: number): KnowledgeWorkspaceState;
export function recordPlacement(
  state: KnowledgeWorkspaceState,
  placement: { destination: string; recordedAt: string },
): KnowledgeWorkspaceState;
export function exportProposal(state: KnowledgeWorkspaceState): Promise<KnowledgeProposalPacket>;
