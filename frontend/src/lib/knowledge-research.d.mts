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
  signal?: AbortSignal;
  timeoutMs?: number;
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
