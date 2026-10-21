#!/usr/bin/env node
import { createHash, randomUUID } from 'node:crypto';
import { createRequire } from 'node:module';
import { lstat, mkdir, open, readFile, readdir, realpath, rename, unlink, writeFile } from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { parseKnowledgeMarkdown } from '../../frontend/src/lib/knowledge-workbench.mjs';

const scriptDirectory = path.dirname(fileURLToPath(import.meta.url));
const frontendRequire = createRequire(path.resolve(scriptDirectory, '../../frontend/package.json'));
const { parseDocument } = frontendRequire('yaml');
const MAX_SOURCE_BYTES = 256 * 1024;
const MAX_MANIFEST_BYTES = 1024 * 1024;
const MAX_INDEX_BYTES = 8 * 1024 * 1024;
const MAX_CARD_BODY_CHARS = 16_000;
const MAX_CARDS = 1_000;
const CARD_ROOT = 'knowledge/cards';
const ALLOWED_PREFIXES = [
  `${CARD_ROOT}/case-summaries/`,
  `${CARD_ROOT}/practice-guides/`,
];
const LEDGER_PATH = 'knowledge/registry/card-versions.jsonl';
const MAX_LEDGER_BYTES = 1024 * 1024;
// Files at the top of knowledge/cards that are documentation, not cards. Anywhere else (including a
// same-named file in a subfolder) a Markdown file under knowledge/cards must sit in ALLOWED_PREFIXES.
const NON_CARD_FILES = new Set([
  `${CARD_ROOT}/INDEX.md`, `${CARD_ROOT}/README.md`, `${CARD_ROOT}/TEMPLATE.md`, `${CARD_ROOT}/_SOURCE-LEGEND.md`,
]);
// SYNC: must equal SOURCE_TYPES in knowhow_retrieval.py (tests/unit/test_knowhow_contract_sync.py).
const SOURCE_REF_TYPES = new Set(['lists_item', 'onenote_page', 'kb_document', 'law_rag']);
// SYNC: must equal SOURCE_ID_KEYS in knowhow_retrieval.py and KNOWHOW_SOURCE_IDS in knowledge-research.mjs
// (tests/unit/test_knowhow_contract_sync.py).
const SOURCE_ID_KEYS = Object.freeze({
  lists_item: 'list_item_id',
  onenote_page: 'onenote_id',
  kb_document: 'document_number',
  law_rag: 'law_id',
});
// SYNC: keys must equal SOURCE_REF_KEYS in knowhow_retrieval.py and KNOWHOW_SOURCE_FIELDS in
// knowledge-research.mjs (tests/unit/test_knowhow_contract_sync.py).
const SOURCE_REF_KEYS = new Set([
  'ref_type', 'list_item_id', 'onenote_id', 'source_id', 'document_number', 'kb_filename',
  'kb_verify_status', 'page_role', 'law_id', 'law_title', 'locator',
]);
// Editor-only annotations on source refs. They are dropped at build and never reach the index.
const SOURCE_REF_ANNOTATION_KEYS = new Set([
  'note', 'law_rag_status', 'retrieval', 'summary_from_kb', 'record_id', 'kb_category',
]);
// Free-text ref fields may contain "/" as ordinary notation (e.g. "D14 DCB/DOB").
const SOURCE_REF_FREE_TEXT_KEYS = new Set(['law_title', 'locator']);
// SYNC: must equal MODEL_SCOPE_KEYS in knowhow_retrieval.py and KNOWHOW_SCOPE_FIELDS in
// knowledge-research.mjs (tests/unit/test_knowhow_contract_sync.py).
const MODEL_SCOPE_KEYS = new Set([
  'conditions', 'control_methods', 'door_families', 'door_types', 'excludes', 'guide_systems',
  'lists_model_label', 'machine_room', 'may_apply_to', 'model_abbreviations', 'observed_on',
  'product_lines', 'scope_note', 'scope_status', 'scope_verified_by', 'scope_verified_at',
]);
// Only scope fields stating where a card DOES apply become search terms (mirrors
// POSITIVE_SCOPE_KEYS in knowhow_retrieval.py); excludes / may_apply_to / scope_note never do.
// SYNC: must equal POSITIVE_SCOPE_KEYS in knowhow_retrieval.py (tests/unit/test_knowhow_contract_sync.py).
const POSITIVE_SCOPE_KEYS = new Set([
  'conditions', 'control_methods', 'door_families', 'door_types', 'guide_systems',
  'lists_model_label', 'machine_room', 'model_abbreviations', 'observed_on', 'product_lines',
]);
// Verification marks decide only the Senpai model filter; they are not scoring input or search terms.
// SYNC: must equal SCOPE_VERIFICATION_KEYS in knowhow_retrieval.py (tests/unit/test_knowhow_contract_sync.py).
const SCOPE_VERIFICATION_KEYS = new Set(['scope_status', 'scope_verified_by', 'scope_verified_at']);
// SYNC: must equal SCOPE_STATUSES / SCOPE_DATE_PATTERN in knowhow_retrieval.py (tests/unit/test_knowhow_contract_sync.py).
const SCOPE_STATUSES = new Set(['verified', 'unverified']);
const SCOPE_DATE = /^\d{4}-\d{2}-\d{2}$/u;
// A verified scope only filters when one of these fields holds a recognized product or generic label
// (mirrors MODEL_CLASSIFY_KEYS / MODEL_ALIASES / GENERIC_* in knowhow_retrieval.py). Values are compared
// after NFKC + lower-casing + trimming, so the alias lists below are already normalized.
// SYNC: tests/unit/test_knowhow_contract_sync.py compares all four with the Lambda.
const MODEL_CLASSIFY_KEYS = new Set(['product_lines', 'model_abbreviations', 'lists_model_label', 'observed_on']);
const MODEL_ALIASES = Object.freeze({
  'AXIEZ': ['axiez', 'axiez(ke-wf・ke-hf)', '駅舎エレ'],
  'AXIEZ-LINKs': ['axiez-links'],
  'NEXCUBE': ['nexcube', 'nexcube limited', '特注機械室レスエレベーター'],
  'メルシティ': ['メルシティ'],
  'メルワイド': ['メルワイド'],
  'エスカレーター': ['エスカレーター', 'escalator'],
});
const GENERIC_ELEVATOR_LABEL = '全エレ機種';
const GENERIC_ESCALATOR_LABEL = '全エス機種';
const RECOGNIZED_MODEL_LABELS = new Set([
  ...Object.values(MODEL_ALIASES).flat(), GENERIC_ELEVATOR_LABEL.normalize('NFKC').toLowerCase(), GENERIC_ESCALATOR_LABEL.normalize('NFKC').toLowerCase(),
]);

/** Today's date in UTC as YYYY-MM-DD; callers may inject another day for tests. */
function utcToday() {
  return new Date().toISOString().slice(0, 10);
}

function fail(message) {
  throw new TypeError(message);
}

function isPlainObject(value) {
  return value !== null && typeof value === 'object' && !Array.isArray(value)
    && (Object.getPrototypeOf(value) === Object.prototype || Object.getPrototypeOf(value) === null);
}

function exactKeys(value, allowed, label) {
  if (!isPlainObject(value)) fail(`${label} must be an object.`);
  for (const key of Object.keys(value)) if (!allowed.has(key)) fail(`${label} contains an unsupported field.`);
}

function digest(text) {
  return createHash('sha256').update(text).digest('hex');
}

function validIsoDate(value) {
  if (typeof value !== 'string' || !/^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d\.\d{3}Z$/.test(value)) return false;
  return Number.isFinite(Date.parse(value)) && new Date(value).toISOString() === value;
}

function validateManifest(manifest) {
  exactKeys(manifest, new Set(['schemaVersion', 'purpose', 'approvedBy', 'approvedAt', 'entries']), 'Manifest');
  if (manifest.schemaVersion !== 1 || manifest.purpose !== 'senpai-admin-navigation') fail('Manifest purpose or schema is invalid.');
  if (!Array.isArray(manifest.entries) || manifest.entries.length > MAX_CARDS) fail('Manifest entries are invalid or exceed the limit.');
  if (manifest.entries.length === 0) {
    if (manifest.approvedBy !== null || manifest.approvedAt !== null) fail('An empty manifest must not claim approval.');
  } else {
    if (typeof manifest.approvedBy !== 'string' || !manifest.approvedBy.trim() || manifest.approvedBy.trim().length > 200) {
      fail('A named reviewer is required for selected cards.');
    }
    if (!validIsoDate(manifest.approvedAt)) fail('A valid ISO approval time is required for selected cards.');
  }
  const paths = new Set();
  const ids = new Set();
  for (const entry of manifest.entries) {
    exactKeys(entry, new Set(['path', 'knowledgeId', 'cardVersion', 'sha256', 'cloudApproved']), 'Manifest entry');
    validateSelectedPath(entry.path);
    if (paths.has(entry.path)) fail('Manifest contains a duplicate path.');
    paths.add(entry.path);
    if (typeof entry.knowledgeId !== 'string' || !entry.knowledgeId.trim() || entry.knowledgeId.length > 200) fail('Manifest knowledge ID is invalid.');
    if (ids.has(entry.knowledgeId)) fail('Manifest contains a duplicate knowledge ID.');
    ids.add(entry.knowledgeId);
    if (!Number.isSafeInteger(entry.cardVersion) || entry.cardVersion < 1) fail('Manifest card version is invalid.');
    if (typeof entry.sha256 !== 'string' || !/^[a-f0-9]{64}$/.test(entry.sha256)) fail('Manifest hash is invalid.');
    if (entry.cloudApproved !== true) fail('Every selected entry requires explicit cloud approval.');
  }
  return manifest;
}

function validateSelectedPath(value) {
  if (typeof value !== 'string' || value.length > 500 || value.includes('\\') || value.includes('\0')) fail('Manifest path is invalid.');
  if (path.posix.isAbsolute(value) || value.split('/').some((part) => part === '.' || part === '..' || part === '')) fail('Manifest path traversal is not allowed.');
  if (!ALLOWED_PREFIXES.some((prefix) => value.startsWith(prefix)) || !value.endsWith('.md')) fail('Manifest path is outside the approved card folders.');
  return value;
}

export function parsePublicationManifest(text) {
  if (typeof text !== 'string' || Buffer.byteLength(text, 'utf8') > MAX_MANIFEST_BYTES) fail('Manifest is missing or too large.');
  let json;
  try {
    json = JSON.parse(text);
  } catch {
    fail('Manifest must be strict JSON.');
  }
  const document = parseDocument(text, { schema: 'json', uniqueKeys: true, version: '1.2' });
  if (document.errors.length > 0 || document.warnings.length > 0) fail('Manifest contains duplicate keys or invalid JSON structure.');
  return validateManifest(json);
}

async function rootInfo(root) {
  if (typeof root !== 'string' || !root) fail('A repository root is required.');
  const absolute = path.resolve(root);
  const resolved = await realpath(absolute);
  const stats = await lstat(absolute);
  if (!stats.isDirectory() || stats.isSymbolicLink()) fail('Repository root must be a real directory.');
  return { absolute, resolved };
}

async function checkNoSymlinkPath(rootResolved, relativePath, { directory = false } = {}) {
  const candidate = path.resolve(rootResolved, ...relativePath.split('/'));
  if (candidate !== rootResolved && !candidate.startsWith(`${rootResolved}${path.sep}`)) fail('Path escapes repository root.');
  const relative = path.relative(rootResolved, candidate);
  let cursor = rootResolved;
  for (const component of relative.split(path.sep).filter(Boolean)) {
    cursor = path.join(cursor, component);
    const info = await lstat(cursor);
    if (info.isSymbolicLink()) fail('Symbolic links are not allowed in the knowledge source tree.');
    if (cursor !== candidate && !info.isDirectory()) fail('Knowledge path contains a non-directory parent.');
  }
  const finalInfo = await lstat(candidate);
  if (directory ? !finalInfo.isDirectory() : !finalInfo.isFile()) fail('Knowledge path has an invalid file type.');
  return candidate;
}

async function listMarkdownFiles(rootResolved, prefix) {
  const directoryPath = prefix.slice(0, -1);
  let base;
  try {
    base = await checkNoSymlinkPath(rootResolved, directoryPath, { directory: true });
  } catch (error) {
    if (error?.code === 'ENOENT') return [];
    throw error;
  }
  const found = [];
  const visit = async (directory, relativeDirectory) => {
    const entries = await readdir(directory, { withFileTypes: true });
    for (const entry of entries) {
      const relative = `${relativeDirectory}/${entry.name}`;
      const absolute = path.join(directory, entry.name);
      const info = await lstat(absolute);
      if (info.isSymbolicLink()) fail('Symbolic links are not allowed in the knowledge source tree.');
      if (info.isDirectory()) await visit(absolute, relative);
      else if (info.isFile() && entry.name.endsWith('.md')) found.push(relative);
    }
  };
  await visit(base, directoryPath);
  return found.sort((a, b) => a.localeCompare(b, 'en'));
}

async function readCard(rootResolved, relativePath) {
  const absolutePath = await checkNoSymlinkPath(rootResolved, relativePath);
  const info = await lstat(absolutePath);
  if (info.size > MAX_SOURCE_BYTES) fail('A Markdown source exceeds the 256 KiB limit.');
  const markdown = await readFile(absolutePath, 'utf8');
  const parsed = parseKnowledgeMarkdown(markdown);
  const metadata = parsed.metadata;
  const status = metadata.status;
  if (status !== 'draft' && status !== 'approved') fail('Markdown status is unsupported or retired.');
  if (parsed.body.length > MAX_CARD_BODY_CHARS) fail('A Markdown card body exceeds the 16,000 character limit.');
  return { parsed, metadata, markdown, sha256: digest(markdown), relativePath };
}

// SECURITY: must stay equal to or stricter than knowhow_retrieval.py so a built index passes validate_index.
const UNSAFE_SCHEME = /(?:https?:\/\/|s3:\/\/|file:\/\/|javascript:)/iu;
const PARENT_SEGMENT = /(?:^|\/)\.\.(?:\/|$)/u;

function safeScalar(value, label, { max = 200, allowSlash = false } = {}) {
  if (typeof value !== 'string' && typeof value !== 'number' && typeof value !== 'boolean') fail(`${label} must be a safe scalar.`);
  const text = String(value);
  if (!text || text.length > max || /[\u0000-\u001f\u007f]/u.test(text) || UNSAFE_SCHEME.test(text) || text.includes('\\')) fail(`${label} is invalid.`);
  if (allowSlash) {
    if (text.startsWith('/') || PARENT_SEGMENT.test(text)) fail(`${label} cannot be a path.`);
  } else if (text.includes('/')) fail(`${label} cannot contain a path.`);
  return text;
}

function sourceRefs(metadata) {
  const refs = Array.isArray(metadata.source_refs) ? metadata.source_refs : [];
  const output = [];
  for (const ref of refs) {
    if (!isPlainObject(ref)) fail('A source reference must be an object.');
    if (ref.ref_type === 'draft_record') continue;
    for (const key of Object.keys(ref)) if (!SOURCE_REF_KEYS.has(key) && !SOURCE_REF_ANNOTATION_KEYS.has(key)) fail('A source reference contains an unsupported field.');
    if (!SOURCE_REF_TYPES.has(ref.ref_type)) fail('A source reference type is unsupported.');
    const identityField = SOURCE_ID_KEYS[ref.ref_type];
    const id = ref[identityField];
    if (id === undefined || id === null) fail('A source reference is missing its stable identity.');
    const result = { ref_type: ref.ref_type };
    for (const key of ['list_item_id', 'onenote_id', 'source_id', 'document_number', 'kb_filename', 'kb_verify_status', 'page_role', 'law_id', 'law_title', 'locator']) {
      const value = ref[key];
      if (value === undefined || value === null || value === '') continue;
      result[key] = safeScalar(value, 'Source reference field', { allowSlash: SOURCE_REF_FREE_TEXT_KEYS.has(key) });
    }
    result[identityField] = safeScalar(id, 'Source identity');
    output.push(result);
  }
  if (output.length === 0) fail('A card must retain at least one original source identity.');
  if (output.length > 30) fail('A card contains too many source references.');
  return output;
}

function modelScope(metadata, today) {
  const scope = metadata.model_scope ?? {};
  if (!isPlainObject(scope)) fail('Model scope must be an object.');
  const output = {};
  for (const key of Object.keys(scope).sort()) {
    if (!MODEL_SCOPE_KEYS.has(key)) fail('Model scope contains an unsupported field.');
    const value = scope[key];
    if (typeof value === 'string') output[key] = safeScalar(value, 'Model scope value', { allowSlash: true });
    else if (Array.isArray(value) && value.length <= 20) {
      output[key] = value.map((item) => safeScalar(item, 'Model scope value', { allowSlash: true }));
    } else fail('Model scope values must be strings or bounded string arrays.');
  }
  validateScopeVerification(output, today);
  return output;
}

function normalizeModelLabel(value) {
  return value.normalize('NFKC').toLowerCase().trim();
}

function recognizedModelValues(scope) {
  return [...MODEL_CLASSIFY_KEYS].flatMap((key) => (Array.isArray(scope[key]) ? scope[key] : key in scope ? [scope[key]] : []))
    .filter((value) => RECOGNIZED_MODEL_LABELS.has(normalizeModelLabel(value)));
}

function validateScopeVerification(scope, today) {
  for (const key of SCOPE_VERIFICATION_KEYS) {
    if (key in scope && typeof scope[key] !== 'string') fail('Scope verification fields must be strings.');
  }
  const status = scope.scope_status ?? 'unverified';
  if (!SCOPE_STATUSES.has(status)) fail('scope_status must be "verified" or "unverified".');
  if (status !== 'verified') return;
  if (!scope.scope_verified_by?.trim()) fail('A verified scope requires scope_verified_by.');
  const at = scope.scope_verified_at ?? '';
  const invalidDate = `scope_verified_at は実在する日付を YYYY-MM-DD で書いてください（例: 2026-10-20）。現在の値: "${at}"`;
  if (!SCOPE_DATE.test(at)) fail(invalidDate);
  let normalized;
  try {
    normalized = new Date(`${at}T00:00:00Z`).toISOString().slice(0, 10);
  } catch {
    fail(invalidDate);
  }
  if (normalized !== at) fail(invalidDate);
  if (at > today) fail(`scope_verified_at が未来の日付です（${at} > 本日 ${today} UTC）。確認した日を書いてください。`);
  if (recognizedModelValues(scope).length === 0) {
    fail(`scope_status: verified ですが、${[...MODEL_CLASSIFY_KEYS].join(' / ')} に認識できる機種名も全機種ラベルもありません（機種フィルタが効きません）。`
      + ` 認識される値: ${Object.keys(MODEL_ALIASES).join(', ')}, ${GENERIC_ELEVATOR_LABEL}, ${GENERIC_ESCALATOR_LABEL}。表記ゆれ・誤字を直してください。`);
  }
}

function searchTerms(parsed, scope) {
  const candidates = [parsed.title];
  for (const key of ['symptoms', 'keywords', 'aliases', 'tags']) {
    const value = parsed.metadata[key];
    if (typeof value === 'string') candidates.push(value);
    else if (Array.isArray(value)) candidates.push(...value);
  }
  for (const [key, value] of Object.entries(scope)) {
    if (!POSITIVE_SCOPE_KEYS.has(key)) continue;
    candidates.push(...(Array.isArray(value) ? value : [value]));
  }
  const terms = [];
  const seen = new Set();
  for (const item of candidates) {
    if (typeof item !== 'string' || !item.trim()) continue;
    const text = item.trim();
    if (text.length > 200) fail('A search term exceeds the 200 character limit.');
    if (!seen.has(text)) {
      seen.add(text);
      terms.push(text);
    }
  }
  if (terms.length > 100) fail('A card contains too many search terms.');
  return terms;
}

function duplicateIdMessage(id, firstPath, secondPath) {
  return `The inventory contains a duplicate knowledge ID "${id}": ${firstPath} and ${secondPath}.`;
}

export async function inventoryKnowhowCards(root) {
  const { resolved } = await rootInfo(root);
  const paths = (await Promise.all(ALLOWED_PREFIXES.map((prefix) => listMarkdownFiles(resolved, prefix)))).flat().sort();
  if (paths.length > MAX_CARDS) fail('The knowledge inventory exceeds 1,000 cards.');
  const idPaths = new Map();
  const cards = [];
  const errors = [];
  for (const relativePath of paths) {
    try {
      const { parsed, metadata, sha256 } = await readCard(resolved, relativePath);
      if (idPaths.has(parsed.id)) fail(duplicateIdMessage(parsed.id, idPaths.get(parsed.id), relativePath));
      idPaths.set(parsed.id, relativePath);
      cards.push({ path: relativePath, knowledgeId: parsed.id, cardVersion: parsed.version, sha256, title: parsed.title, status: metadata.status });
    } catch (error) {
      if (String(error.message).includes('duplicate knowledge ID')) throw error;
      errors.push({ path: relativePath, reason: 'parse_or_validation_error' });
    }
  }
  return { schemaVersion: 1, generatedAt: new Date().toISOString(), cards, errors };
}

function stableJson(value) {
  if (Array.isArray(value)) return `[${value.map(stableJson).join(',')}]`;
  if (isPlainObject(value)) return `{${Object.keys(value).sort().map((key) => `${JSON.stringify(key)}:${stableJson(value[key])}`).join(',')}}`;
  return JSON.stringify(value);
}

function indexCard({ parsed, metadata, sha256 }, today) {
  const refs = sourceRefs(metadata);
  const scope = modelScope(metadata, today);
  return {
    knowledgeId: parsed.id,
    cardVersion: parsed.version,
    sha256,
    title: safeScalar(parsed.title, 'Card title (URL, backslash, control character or path is not allowed)', { max: 400, allowSlash: true }),
    status: metadata.status,
    usage: 'navigation_only',
    body: parsed.body,
    searchTerms: searchTerms(parsed, scope),
    sourceRefs: refs,
    modelScope: scope,
  };
}

function assembleIndex(cards, generatedAt) {
  const selected = [...cards].sort((left, right) => left.knowledgeId.localeCompare(right.knowledgeId, 'en') || left.cardVersion - right.cardVersion);
  const indexVersion = `sha256:${digest(stableJson(selected))}`;
  const result = { schemaVersion: 1, indexVersion, generatedAt, cards: selected };
  if (Buffer.byteLength(JSON.stringify(result), 'utf8') > MAX_INDEX_BYTES) fail('The generated index exceeds the 8 MiB limit.');
  return result;
}

export async function buildKnowhowIndex({ root, manifest, generatedAt = new Date().toISOString(), today = utcToday() }) {
  validateManifest(manifest);
  if (!validIsoDate(generatedAt)) fail('generatedAt must be an ISO timestamp.');
  const { resolved } = await rootInfo(root);
  const selected = [];
  for (const entry of manifest.entries) {
    const { parsed, metadata, markdown, sha256 } = await readCard(resolved, entry.path);
    if (parsed.id !== entry.knowledgeId || parsed.version !== entry.cardVersion || sha256 !== entry.sha256) {
      fail('A selected card does not match its approved ID, version, and hash.');
    }
    selected.push(indexCard({ parsed, metadata, sha256 }, today));
  }
  return assembleIndex(selected, generatedAt);
}

async function writePrivateOutput(root, filename, value) {
  const { resolved } = await rootInfo(root);
  const privateDirectory = path.join(resolved, '.private-knowhow');
  try {
    const info = await lstat(privateDirectory);
    if (info.isSymbolicLink() || !info.isDirectory()) fail('Private output directory must be a real directory.');
  } catch (error) {
    if (error?.code !== 'ENOENT') throw error;
    await mkdir(privateDirectory, { mode: 0o700 });
  }
  const outputPath = path.join(privateDirectory, filename);
  const temporaryPath = path.join(privateDirectory, `.${filename}.${randomUUID()}.tmp`);
  let handle;
  try {
    handle = await open(temporaryPath, 'wx', 0o600);
    await handle.writeFile(`${JSON.stringify(value, null, 2)}\n`, 'utf8');
    await handle.close();
    handle = undefined;
    await rename(temporaryPath, outputPath);
  } catch (error) {
    if (handle) await handle.close().catch(() => {});
    await unlink(temporaryPath).catch(() => {});
    throw error;
  }
}

async function resolveEvalIndexPath(rootResolved, evalIndexPath) {
  const target = path.resolve(evalIndexPath);
  const parent = await realpath(path.dirname(target)).catch(() => fail('The eval index folder does not exist.'));
  const resolvedTarget = path.join(parent, path.basename(target));
  const tmpRoot = await realpath(os.tmpdir());
  const inside = (base, candidate) => candidate === base || candidate.startsWith(`${base}${path.sep}`);
  if (inside(rootResolved, resolvedTarget)) fail('The eval index must not be written inside the repository root.');
  if (!inside(tmpRoot, resolvedTarget)) fail('The eval index must be written inside the OS temporary directory.');
  try {
    if ((await lstat(resolvedTarget)).isSymbolicLink()) fail('The eval index path must not be a symbolic link.');
  } catch (error) {
    if (error?.code !== 'ENOENT') throw error;
  }
  return resolvedTarget;
}

async function writeEvalIndex(outputPath, value) {
  const handle = await open(outputPath, 'w', 0o600);
  try {
    await handle.chmod(0o600);
    await handle.writeFile(`${JSON.stringify(value, null, 2)}\n`, 'utf8');
  } finally {
    await handle.close();
  }
}

async function listCardPaths(resolved) {
  const paths = (await Promise.all(ALLOWED_PREFIXES.map((prefix) => listMarkdownFiles(resolved, prefix)))).flat().sort();
  if (paths.length > MAX_CARDS) fail('The knowledge inventory exceeds 1,000 cards.');
  return paths;
}

/** Markdown files under knowledge/cards that are neither in an approved folder nor a known non-card file. */
async function listStrayCardFiles(resolved) {
  const all = await listMarkdownFiles(resolved, `${CARD_ROOT}/`);
  return all.filter((file) => !ALLOWED_PREFIXES.some((prefix) => file.startsWith(prefix)) && !NON_CARD_FILES.has(file));
}

/** Validate each card through the build code path plus file-name and duplicate-ID rules. */
async function evaluateCards(resolved, paths, today) {
  const idPaths = new Map();
  const records = [];
  const failures = [];
  for (const relativePath of paths) {
    try {
      const card = await readCard(resolved, relativePath);
      const { parsed, sha256 } = card;
      if (idPaths.has(parsed.id)) fail(duplicateIdMessage(parsed.id, idPaths.get(parsed.id), relativePath));
      idPaths.set(parsed.id, relativePath);
      const base = path.posix.basename(relativePath, '.md');
      if (base !== parsed.id) fail(`The file name "${base}.md" must equal knowledge_id "${parsed.id}". ファイル名か knowledge_id のどちらかを直してください。`);
      records.push({ relativePath, knowledgeId: parsed.id, cardVersion: parsed.version, sha256, index: indexCard(card, today) });
    } catch (error) {
      failures.push({ path: relativePath, reason: String(error?.message ?? error) });
    }
  }
  return { records, failures };
}

const LEDGER_REGENERATE_HINT = '`node scripts/knowledge/build-senpai-index.mjs ledger .` で ledger を再生成してください';
const HEX64 = /^[a-f0-9]{64}$/u;

function parseLedger(text) {
  const entries = new Map();
  for (const [position, line] of text.split('\n').entries()) {
    if (!line.trim()) continue;
    let item;
    try {
      item = JSON.parse(line);
    } catch {
      fail(`${position + 1} 行目が JSON ではありません`);
    }
    if (!isPlainObject(item) || Object.keys(item).join(',') !== 'knowledgeId,cardVersion,sha256'
      || typeof item.knowledgeId !== 'string' || !Number.isSafeInteger(item.cardVersion) || item.cardVersion < 1
      || typeof item.sha256 !== 'string' || !HEX64.test(item.sha256)) fail(`${position + 1} 行目の形式が不正です`);
    if (entries.has(item.knowledgeId)) fail(`${item.knowledgeId} が重複しています`);
    entries.set(item.knowledgeId, item);
  }
  return entries;
}

async function readLedger(resolved) {
  let file;
  try {
    file = await checkNoSymlinkPath(resolved, LEDGER_PATH);
  } catch (error) {
    if (error?.code === 'ENOENT') return undefined;
    throw error;
  }
  if ((await lstat(file)).size > MAX_LEDGER_BYTES) fail('ledger が大きすぎます');
  return parseLedger(await readFile(file, 'utf8'));
}

function ledgerEntryProblem(record, entry) {
  if (!entry) return `ledger に未登録のカードです: ${LEDGER_REGENERATE_HINT}`;
  if (entry.cardVersion === record.cardVersion) {
    return entry.sha256 === record.sha256 ? undefined
      : `内容が変わったのに card_version が同じです（v${record.cardVersion}）: card_version を上げてから ledger を再生成してください`;
  }
  if (entry.cardVersion < record.cardVersion) return `ledger が古いです（ledger v${entry.cardVersion} / カード v${record.cardVersion}）: ${LEDGER_REGENERATE_HINT}`;
  return `card_version が下がっています（ledger v${entry.cardVersion} > カード v${record.cardVersion}）: card_version は下げられません`;
}

/** Compare cards with the committed version ledger; returns per-card and ledger-level failures. */
async function checkLedger(resolved, records, hasCardFailures) {
  let ledger;
  try {
    ledger = await readLedger(resolved);
  } catch (error) {
    return { cardProblems: new Map(), general: [{ path: LEDGER_PATH, reason: `ledger を読めません（${error.message}）: ${LEDGER_REGENERATE_HINT}` }] };
  }
  if (!ledger) return { cardProblems: new Map(), general: [{ path: LEDGER_PATH, reason: `ledger がありません: ${LEDGER_REGENERATE_HINT}` }] };
  const cardProblems = new Map();
  for (const record of records) {
    const problem = ledgerEntryProblem(record, ledger.get(record.knowledgeId));
    if (problem) cardProblems.set(record.relativePath, problem);
  }
  const general = [];
  if (!hasCardFailures) {
    const present = new Set(records.map((record) => record.knowledgeId));
    for (const id of ledger.keys()) {
      if (!present.has(id)) general.push({ path: LEDGER_PATH, reason: `カード ${id} が存在しないのに ledger に残っています: ${LEDGER_REGENERATE_HINT}` });
    }
  }
  return { cardProblems, general };
}

/**
 * Validate every inventoried card individually through the same code path as `build`.
 * Needs no manifest and writes nothing unless `evalIndexPath` is given. SECURITY: that
 * index holds unapproved card bodies for local evaluation only and must never be uploaded.
 * Also fails for Markdown files under knowledge/cards outside the approved folders, file names
 * that differ from knowledge_id, and (unless `ledger: false`) content changes without a
 * card_version bump against knowledge/registry/card-versions.jsonl.
 */
export async function checkKnowhowCards(root, { evalIndexPath, generatedAt = new Date().toISOString(), ledger = true, today = utcToday() } = {}) {
  const { resolved } = await rootInfo(root);
  const outputPath = evalIndexPath === undefined ? undefined : await resolveEvalIndexPath(resolved, evalIndexPath);
  const paths = await listCardPaths(resolved);
  const strays = await listStrayCardFiles(resolved);
  const evaluated = await evaluateCards(resolved, paths, today);
  const failures = [...evaluated.failures];
  let records = evaluated.records;
  for (const stray of strays) {
    failures.push({ path: stray, reason: `knowledge/cards の承認済みフォルダー（case-summaries / practice-guides）の外にあるため検査・取込の対象外になります。正しいフォルダーへ移すか削除してください。` });
  }
  if (ledger) {
    const { cardProblems, general } = await checkLedger(resolved, records, failures.length > 0);
    for (const [cardPath, reason] of cardProblems) failures.push({ path: cardPath, reason });
    failures.push(...general);
    records = records.filter((record) => !cardProblems.has(record.relativePath));
  }
  failures.sort((left, right) => left.path.localeCompare(right.path, 'en'));
  const result = { total: paths.length + strays.length, valid: records.length, failures };
  if (outputPath) {
    await writeEvalIndex(outputPath, assembleIndex(records.map((record) => record.index), generatedAt));
    result.evalIndexPath = outputPath;
  }
  return result;
}

/**
 * Regenerate knowledge/registry/card-versions.jsonl (knowledgeId, cardVersion, sha256 per card).
 * Refuses when a card's content changed without a card_version bump relative to the existing ledger.
 */
export async function writeKnowhowLedger(root, { today = utcToday() } = {}) {
  const { resolved } = await rootInfo(root);
  const { records, failures } = await evaluateCards(resolved, await listCardPaths(resolved), today);
  if (failures.length > 0) {
    fail(`カードに失敗があるため ledger を作れません（先に check を直してください）: ${failures.slice(0, 5).map((item) => `${item.path}: ${item.reason}`).join(' / ')}`);
  }
  let existing = new Map();
  try {
    existing = (await readLedger(resolved)) ?? existing;
  } catch {
    existing = new Map();
  }
  const refused = records.map((record) => ({ record, problem: ledgerEntryProblem(record, existing.get(record.knowledgeId)) }))
    .filter(({ record, problem }) => existing.has(record.knowledgeId)
      && (existing.get(record.knowledgeId).cardVersion >= record.cardVersion) && problem);
  if (refused.length > 0) {
    fail(`ledger を再生成できません: ${refused.slice(0, 5).map(({ record, problem }) => `${record.relativePath}: ${problem}`).join(' / ')}`);
  }
  const lines = records.map(({ knowledgeId, cardVersion, sha256 }) => ({ knowledgeId, cardVersion, sha256 }))
    .sort((left, right) => (left.knowledgeId < right.knowledgeId ? -1 : left.knowledgeId > right.knowledgeId ? 1 : 0))
    .map((entry) => JSON.stringify(entry));
  const target = path.join(resolved, ...LEDGER_PATH.split('/'));
  await mkdir(path.dirname(target), { recursive: true });
  const temporary = `${target}.${randomUUID()}.tmp`;
  try {
    await writeFile(temporary, `${lines.join('\n')}\n`, { encoding: 'utf8', flag: 'wx' });
    await rename(temporary, target);
  } catch (error) {
    await unlink(temporary).catch(() => {});
    throw error;
  }
  return { path: LEDGER_PATH, count: lines.length };
}

function parseCheckArgs(args) {
  const options = { root: undefined, evalIndexPath: undefined, json: false, ledger: true };
  for (let position = 0; position < args.length; position += 1) {
    const arg = args[position];
    if (arg === '--json') options.json = true;
    else if (arg === '--no-ledger') options.ledger = false;
    else if (arg === '--eval-index') {
      options.evalIndexPath = args[position + 1];
      position += 1;
      if (!options.evalIndexPath) fail('--eval-index requires a path.');
    } else if (arg.startsWith('--') || options.root !== undefined) fail('Usage: build-senpai-index.mjs check <root> [--eval-index <path>] [--json] [--no-ledger]');
    else options.root = arg;
  }
  return { ...options, root: options.root ?? process.cwd() };
}

async function runCheck(args) {
  const options = parseCheckArgs(args);
  const result = await checkKnowhowCards(options.root, { evalIndexPath: options.evalIndexPath, ledger: options.ledger });
  if (options.json) {
    process.stdout.write(`${JSON.stringify(result, null, 2)}\n`);
  } else {
    process.stdout.write(`Check: ${result.valid}/${result.total} cards valid; ${result.failures.length} failed. Body text was not printed.\n`);
    for (const failure of result.failures) process.stdout.write(`  FAIL ${failure.path}: ${failure.reason}\n`);
    if (result.evalIndexPath) {
      process.stdout.write(`評価用索引を書き出しました: ${result.evalIndexPath}\n`);
      process.stdout.write('警告: この索引は未承認の全有効カード本文を含むローカル評価専用です。アップロード・共有・コミットしないでください。\n');
    }
  }
  if (result.failures.length > 0) process.exitCode = 1;
}

async function main(args) {
  if (args[0] === 'check') {
    await runCheck(args.slice(1));
    return;
  }
  const [command, root = process.cwd(), manifestPath] = args;
  if (command === 'ledger' && !manifestPath) {
    const written = await writeKnowhowLedger(root);
    process.stdout.write(`Ledger written: ${written.count} cards in ${written.path}. Commit it with the card changes.\n`);
    return;
  }
  if (command === 'inventory' && !manifestPath) {
    const inventory = await inventoryKnowhowCards(root);
    await writePrivateOutput(root, 'inventory.json', inventory);
    process.stdout.write(`Inventory complete: ${inventory.cards.length} valid metadata records; ${inventory.errors.length} parse/validation errors. Body text was not printed.\n`);
    return;
  }
  if (command === 'build' && manifestPath) {
    const text = await readFile(path.resolve(manifestPath), 'utf8');
    const manifest = parsePublicationManifest(text);
    const index = await buildKnowhowIndex({ root, manifest });
    await writePrivateOutput(root, 'index.json', index);
    process.stdout.write(`Index built: ${index.cards.length} explicitly selected cards; index ${index.indexVersion}. No upload was performed.\n`);
    return;
  }
  fail('Usage: build-senpai-index.mjs inventory <root> | build <root> <manifest.json> | ledger <root> | check <root> [--eval-index <path>] [--json] [--no-ledger]');
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  main(process.argv.slice(2)).catch((error) => {
    process.stderr.write(`Knowledge index operation failed: ${error.message}\n`);
    process.exitCode = 1;
  });
}
