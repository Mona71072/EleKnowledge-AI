#!/usr/bin/env node
import { createHash, randomUUID } from 'node:crypto';
import { createRequire } from 'node:module';
import { lstat, mkdir, open, readFile, readdir, realpath, rename, unlink } from 'node:fs/promises';
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
const SOURCE_REF_TYPES = new Set(['lists_item', 'onenote_page', 'kb_document', 'law_rag']);
const SOURCE_REF_KEYS = new Set([
  'ref_type', 'list_item_id', 'onenote_id', 'source_id', 'document_number', 'kb_filename',
  'kb_verify_status', 'page_role', 'law_id', 'law_title', 'locator',
]);
const MODEL_SCOPE_KEYS = new Set([
  'conditions', 'control_methods', 'door_families', 'door_types', 'excludes', 'guide_systems',
  'lists_model_label', 'machine_room', 'may_apply_to', 'model_abbreviations', 'observed_on',
  'product_lines', 'scope_note',
]);

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

function safeScalar(value, label, { max = 200, allowPath = false } = {}) {
  if (typeof value !== 'string' && typeof value !== 'number' && typeof value !== 'boolean') fail(`${label} must be a safe scalar.`);
  const text = String(value);
  if (!text || text.length > max || /[\u0000-\u001f\u007f]/u.test(text) || /https?:\/\//iu.test(text)) fail(`${label} is invalid.`);
  if (!allowPath && /[\\/]/u.test(text)) fail(`${label} cannot contain a path.`);
  return text;
}

function sourceRefs(metadata) {
  const refs = Array.isArray(metadata.source_refs) ? metadata.source_refs : [];
  const output = [];
  for (const ref of refs) {
    if (!isPlainObject(ref)) fail('A source reference must be an object.');
    if (ref.ref_type === 'draft_record') continue;
    for (const key of Object.keys(ref)) if (!SOURCE_REF_KEYS.has(key)) fail('A source reference contains an unsupported field.');
    if (!SOURCE_REF_TYPES.has(ref.ref_type)) fail('A source reference type is unsupported.');
    let identityField;
    if (ref.ref_type === 'lists_item') identityField = 'list_item_id';
    else if (ref.ref_type === 'onenote_page') identityField = 'onenote_id';
    else if (ref.ref_type === 'kb_document') identityField = 'document_number';
    else identityField = 'law_id';
    const id = ref[identityField];
    if (id === undefined || id === null) fail('A source reference is missing its stable identity.');
    const result = { ref_type: ref.ref_type };
    for (const key of ['list_item_id', 'onenote_id', 'source_id', 'document_number', 'kb_filename', 'kb_verify_status', 'page_role', 'law_id', 'law_title', 'locator']) {
      const value = ref[key];
      if (value === undefined || value === null || value === '') continue;
      result[key] = safeScalar(value, 'Source reference field');
    }
    result[identityField] = safeScalar(id, 'Source identity');
    output.push(result);
  }
  if (output.length === 0) fail('A card must retain at least one original source identity.');
  if (output.length > 30) fail('A card contains too many source references.');
  return output;
}

function modelScope(metadata) {
  const scope = metadata.model_scope ?? {};
  if (!isPlainObject(scope)) fail('Model scope must be an object.');
  const output = {};
  for (const key of Object.keys(scope).sort()) {
    if (!MODEL_SCOPE_KEYS.has(key)) fail('Model scope contains an unsupported field.');
    const value = scope[key];
    if (typeof value === 'string') output[key] = safeScalar(value, 'Model scope value');
    else if (Array.isArray(value) && value.length <= 20) {
      output[key] = value.map((item) => safeScalar(item, 'Model scope value'));
    } else fail('Model scope values must be strings or bounded string arrays.');
  }
  return output;
}

function searchTerms(parsed, scope) {
  const candidates = [parsed.title];
  for (const key of ['symptoms', 'keywords', 'aliases', 'tags']) {
    const value = parsed.metadata[key];
    if (typeof value === 'string') candidates.push(value);
    else if (Array.isArray(value)) candidates.push(...value);
  }
  for (const value of Object.values(scope)) candidates.push(...(Array.isArray(value) ? value : [value]));
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

export async function inventoryKnowhowCards(root) {
  const { resolved } = await rootInfo(root);
  const paths = (await Promise.all(ALLOWED_PREFIXES.map((prefix) => listMarkdownFiles(resolved, prefix)))).flat().sort();
  if (paths.length > MAX_CARDS) fail('The knowledge inventory exceeds 1,000 cards.');
  const ids = new Set();
  const cards = [];
  const errors = [];
  for (const relativePath of paths) {
    try {
      const { parsed, metadata, sha256 } = await readCard(resolved, relativePath);
      if (ids.has(parsed.id)) fail('The inventory contains a duplicate knowledge ID.');
      ids.add(parsed.id);
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

export async function buildKnowhowIndex({ root, manifest, generatedAt = new Date().toISOString() }) {
  validateManifest(manifest);
  if (!validIsoDate(generatedAt)) fail('generatedAt must be an ISO timestamp.');
  const { resolved } = await rootInfo(root);
  const selected = [];
  for (const entry of manifest.entries) {
    const { parsed, metadata, markdown, sha256 } = await readCard(resolved, entry.path);
    if (parsed.id !== entry.knowledgeId || parsed.version !== entry.cardVersion || sha256 !== entry.sha256) {
      fail('A selected card does not match its approved ID, version, and hash.');
    }
    const refs = sourceRefs(metadata);
    const scope = modelScope(metadata);
    selected.push({
      knowledgeId: parsed.id,
      cardVersion: parsed.version,
      sha256,
      title: parsed.title,
      status: metadata.status,
      usage: 'navigation_only',
      body: parsed.body,
      searchTerms: searchTerms(parsed, scope),
      sourceRefs: refs,
      modelScope: scope,
    });
  }
  selected.sort((left, right) => left.knowledgeId.localeCompare(right.knowledgeId, 'en') || left.cardVersion - right.cardVersion);
  const indexVersion = `sha256:${digest(stableJson(selected))}`;
  const result = { schemaVersion: 1, indexVersion, generatedAt, cards: selected };
  if (Buffer.byteLength(JSON.stringify(result), 'utf8') > MAX_INDEX_BYTES) fail('The generated index exceeds the 8 MiB limit.');
  return result;
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

async function main(args) {
  const [command, root = process.cwd(), manifestPath] = args;
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
  fail('Usage: build-senpai-index.mjs inventory <root> | build <root> <manifest.json>');
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  main(process.argv.slice(2)).catch((error) => {
    process.stderr.write(`Knowledge index operation failed: ${error.message}\n`);
    process.exitCode = 1;
  });
}
