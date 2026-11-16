// カード本文の「AI による書き換え案」の純粋関数をまとめて公開する入口。
// 実装は役割ごとに分けている（節の選別 / 要求 / 応答の検証 / 反映）。
export {
  REWRITE_LIMITS,
  REWRITE_TARGET_HEADINGS,
  charCount,
  findRewriteBodyProblem,
  findRewriteStructureProblem,
  hasNewLinkOrHtml,
  hasSuspiciousText,
  isUnsafeDisplayText,
  readSections,
  selectRewriteSections,
} from './knowhow-rewrite-sections.mjs';
export { buildFieldRewriteRequest, buildRewriteEvidence, buildRewriteHistory, buildRewriteRequest, buildRewriteRetryRequest, isRewriteEnabled, validateRewriteInstruction } from './knowhow-rewrite-request.mjs';
export {
  buildAcceptedRewrites,
  buildConflictOpenItem,
  describeRewriteWarning,
  normalizeRewriteResponse,
  summarizeRewriteDecisions,
} from './knowhow-rewrite-response.mjs';
export { applySectionRewrites, composeCardEdits } from './knowhow-rewrite-apply.mjs';
