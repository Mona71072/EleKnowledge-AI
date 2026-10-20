export type KnowledgeResearchMode = 'normal' | 'law';
export type KnowledgeResearchResponseType = 'pages' | 'clarify' | 'not_found';
export type KnowledgeResearchErrorCode =
  | 'auth'
  | 'unavailable'
  | 'timeout'
  | 'cancelled'
  | 'server'
  | 'invalid_response'
  | 'config'
  | 'validation';

export type ResearchLawCitation = {
  lawId: string;
  lawTitle: string;
  lawNumber: string;
  effectiveDate: string;
  provisionType: string;
  provisionReference?: string;
  sourceUrl: string;
};

export type ResearchCitationSource = {
  documentName?: string;
  title?: string;
  category?: string;
  modelType?: string;
  pageNumber?: number;
  relevance?: number;
  snippet?: string;
  hasImage?: boolean;
  source_action?: string;
  referenceCoverage?: string;
  referenceCoverageReason?: string;
  lowConfidence?: boolean;
  sourceUri?: string;
  lawCitation?: ResearchLawCitation;
};

export type ResearchSource = ResearchCitationSource;
export type ResearchPageCandidate = ResearchCitationSource & { lowConfidence?: boolean };

export type ResearchKnowhowMatch = {
  knowledgeId: string;
  cardVersion: number;
  sha256: string;
  title: string;
  status: 'draft' | 'approved';
  usage: 'navigation_only';
  body: string;
  searchTerms: string[];
  sourceRefs: Array<Record<string, string>>;
  modelScope: Record<string, unknown>;
};

export type ResearchKnowhow = {
  status: 'matched' | 'not_found';
  indexVersion: string;
  matches: ResearchKnowhowMatch[];
  /** Search hints actually added to the technical KB query by the server. */
  searchTerms: string[];
};

export type ResearchAnswer = {
  mode: KnowledgeResearchMode;
  query: string;
  content: string;
  responseType: KnowledgeResearchResponseType;
  sessionId: string;
  messageId: string;
  /** Time the browser received the RAG HTTP response, recorded locally. */
  receivedAt: string;
  /** Original API response timestamp, retained only when it is valid ISO-8601. */
  responseTimestamp?: string;
  sourceDocuments: ResearchSource[];
  pageCandidates: ResearchPageCandidate[];
  clarifyQuestions: string[];
  /** Present only when the caller explicitly requested Markdown retrieval. */
  knowhow?: ResearchKnowhow;
};

export class KnowledgeResearchError extends Error {
  readonly code: KnowledgeResearchErrorCode;
  constructor(code: KnowledgeResearchErrorCode, message: string);
}

export function queryKnowledgeSource(options: {
  baseUrl: string;
  getToken: () => Promise<string | null | undefined>;
  fetchImpl?: typeof fetch;
  mode: KnowledgeResearchMode;
  query: string;
  /** Continue an existing session for the same mode only. */
  sessionId?: string;
  signal?: AbortSignal;
  timeoutMs?: number;
  /** Retrieve the server-authorized Markdown index for normal mode only. */
  includeKnowhow?: boolean;
}): Promise<ResearchAnswer>;

export function researchSourceHref(
  source: ResearchCitationSource | null | undefined,
  mode: KnowledgeResearchMode,
): string | undefined;

export function buildResearchNote(answer: ResearchAnswer): string;

export function buildResearchTargetNote(target: {
  knowledgeId: string;
  baseVersion: number;
  manualBodyRevision: number;
}): string;
