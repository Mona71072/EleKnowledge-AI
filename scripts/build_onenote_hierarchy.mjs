import { createHash } from 'node:crypto';
import { readdir, readFile, stat, writeFile } from 'node:fs/promises';
import path from 'node:path';
import process from 'node:process';

const excludedDirectories = new Set([
  '.obsidian',
  'OneNote',
  'OneNote_RecycleBin',
  '添付画像',
  '整備済み資料',
]);

async function walkMarkdown(root, excluded = false) {
  const results = [];
  const entries = await readdir(root, { withFileTypes: true });

  for (const entry of entries) {
    const entryPath = path.join(root, entry.name);
    if (entry.isDirectory()) {
      if (!excludedDirectories.has(entry.name)) {
        results.push(...await walkMarkdown(entryPath, excluded));
      }
    } else if (entry.isFile() && entry.name.toLowerCase().endsWith('.md')) {
      results.push(entryPath);
    }
  }

  return results;
}

async function readFrontmatter(filePath) {
  const text = await readFile(filePath, 'utf8');
  const match = text.match(/^---\r?\n([\s\S]*?)\r?\n---(?:\r?\n|$)/);
  return match?.[1] ?? '';
}

function yamlScalar(frontmatter, key) {
  const escapedKey = key.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  const match = frontmatter.match(new RegExp(`^${escapedKey}:\\s*(.*?)\\s*$`, 'm'));
  if (!match) return null;

  const value = match[1].trim();
  if (value.length >= 2 && ['"', "'"].includes(value[0]) && value.at(-1) === value[0]) {
    return value.slice(1, -1);
  }
  return value || null;
}

async function readPageMetadata(filePath) {
  const frontmatter = await readFrontmatter(filePath);
  return {
    onenoteId: yamlScalar(frontmatter, 'onenote_id') ?? yamlScalar(frontmatter, 'onenote-id'),
    snapshotType: yamlScalar(frontmatter, 'snapshot_type'),
  };
}

async function loadSnapshotPages(snapshotRoot) {
  const entries = await readdir(snapshotRoot, { withFileTypes: true });
  const pages = [];

  for (const entry of entries) {
    if (!entry.isFile() || !entry.name.toLowerCase().endsWith('.md')) continue;
    const filePath = path.join(snapshotRoot, entry.name);
    const metadata = await readPageMetadata(filePath);
    if (metadata.snapshotType !== 'onenote_source_page') continue;
    if (!metadata.onenoteId) {
      throw new Error(`OneNote snapshot is missing an ID: ${entry.name}`);
    }
    pages.push({ filename: entry.name, onenoteId: metadata.onenoteId });
  }

  const ids = pages.map(page => page.onenoteId);
  if (new Set(ids).size !== ids.length) {
    throw new Error('OneNote snapshot contains duplicate onenote_id values');
  }
  return pages;
}

async function indexVaultPages(vaultRoot) {
  const sourcePages = new Map();
  const markdownFiles = await walkMarkdown(vaultRoot);

  for (const filePath of markdownFiles) {
    const { onenoteId } = await readPageMetadata(filePath);
    if (!onenoteId) continue;
    const candidates = sourcePages.get(onenoteId) ?? [];
    candidates.push(filePath);
    sourcePages.set(onenoteId, candidates);
  }

  return sourcePages;
}

async function parentPageIds(vaultRoot, relativePath, includedIds) {
  const parts = relativePath.split(path.sep);
  const directoryIds = [];
  const unresolvedContainerKeys = [];

  for (let index = 1; index < parts.length - 1; index += 1) {
    const parentPath = path.join(
      vaultRoot,
      ...parts.slice(0, index),
      `${parts[index]}.md`,
    );
    const exists = await stat(parentPath).then(() => true).catch(() => false);
    const { onenoteId } = exists ? await readPageMetadata(parentPath) : { onenoteId: null };
    directoryIds.push(onenoteId);
    if (!onenoteId) {
      const relativeDirectory = path.relative(vaultRoot, path.dirname(parentPath));
      unresolvedContainerKeys.push(opaqueKey(relativeDirectory));
    }
  }

  return {
    ancestorIds: directoryIds.filter(Boolean),
    immediateParentId: directoryIds.at(-1) ?? null,
    unresolvedContainerKeys,
    excludedAncestorIds: directoryIds.filter(id => id && !includedIds.has(id)),
  };
}

function opaqueKey(value) {
  return createHash('sha256').update(value.toLocaleLowerCase('ja-JP')).digest('hex').slice(0, 20);
}

async function buildManifest(vaultRoot, snapshotRoot) {
  const snapshotPages = await loadSnapshotPages(snapshotRoot);
  const includedIds = new Set(snapshotPages.map(page => page.onenoteId));
  const sourcePages = await indexVaultPages(vaultRoot);
  const records = [];

  for (const page of snapshotPages) {
    const candidates = sourcePages.get(page.onenoteId) ?? [];
    const record = {
      onenote_id: page.onenoteId,
      section_key: null,
      section_id: null,
      parent_onenote_id: null,
      ancestor_onenote_ids: [],
      excluded_parent_ids: [],
      parent_container_keys: [],
      parent_content_status: "unknown",
      page_level: null,
      page_order: null,
      hierarchy_status: 'unmatched_in_vault',
    };

    if (candidates.length !== 1) {
      if (candidates.length > 1) record.hierarchy_status = 'ambiguous_source_id';
      records.push(record);
      continue;
    }

    const sourcePath = candidates[0];
    const relativePath = path.relative(vaultRoot, sourcePath);
    const parts = relativePath.split(path.sep);
    if (parts.length < 2) {
      record.hierarchy_status = 'section_unknown';
      records.push(record);
      continue;
    }

    record.section_key = opaqueKey(parts[0]);
    const parents = await parentPageIds(vaultRoot, relativePath, includedIds);
    record.ancestor_onenote_ids = parents.ancestorIds;
    record.parent_onenote_id = parents.immediateParentId;
    record.excluded_parent_ids = parents.excludedAncestorIds;
    record.parent_container_keys = parents.unresolvedContainerKeys;
    record.parent_content_status = parents.immediateParentId
      ? (includedIds.has(parents.immediateParentId) ? "included" : "excluded_from_snapshot")
      : (parents.unresolvedContainerKeys.length ? "container_without_page_id" : "none");

    if (parts.length === 2) {
      record.page_level = 0;
      record.hierarchy_status = 'section_page_candidate';
    } else if (parents.unresolvedContainerKeys.length) {
      record.hierarchy_status = 'parent_container_without_page_id';
    } else if (parents.excludedAncestorIds.length) {
      record.page_level = parents.ancestorIds.length;
      record.hierarchy_status = 'inferred_with_excluded_parent_stub';
    } else {
      record.page_level = parents.ancestorIds.length;
      record.hierarchy_status = 'inferred_from_vault_path';
    }
    records.push(record);
  }

  const statusCounts = records.reduce((counts, record) => {
    counts[record.hierarchy_status] = (counts[record.hierarchy_status] ?? 0) + 1;
    return counts;
  }, {});
  const excludedParentStubs = [...new Set(records.flatMap(record => record.excluded_parent_ids))]
    .sort()
    .map(onenoteId => ({ onenote_id: onenoteId, content_status: 'excluded_from_snapshot' }));

  const manifest = {
    schema_version: 1,
    source_system: 'OneNote',
    snapshot_page_count: records.length,
    matched_to_vault_count: records.filter(record => record.section_key).length,
    excluded_parent_stub_count: excludedParentStubs.length,
    relationship_source: 'inferred_from_local_vault_markdown_paths',
    section_key_note: 'Opaque key derived from the first Vault path segment; not a native OneNote section ID or title.',
    section_id_note: 'Native OneNote section IDs remain null unless explicitly reconciled.',
    page_order_note: 'Page order remains null because filesystem order is not authoritative OneNote order.',
    status_counts: Object.fromEntries(Object.entries(statusCounts).sort()),
    excluded_parent_stubs: excludedParentStubs,
    pages: records.sort((left, right) => left.onenote_id.localeCompare(right.onenote_id)),
  };

  const manifestPageIds = new Set(manifest.pages.map(record => record.onenote_id));
  const excludedStubIds = new Set(manifest.excluded_parent_stubs.map(record => record.onenote_id));
  if (manifestPageIds.size !== manifest.snapshot_page_count) {
    throw new Error('Hierarchy manifest contains duplicate or missing page IDs');
  }
  for (const record of manifest.pages) {
    if (record.parent_onenote_id
      && !manifestPageIds.has(record.parent_onenote_id)
      && !excludedStubIds.has(record.parent_onenote_id)) {
      throw new Error(`Parent ID is not present in the included snapshot: ${record.onenote_id}`);
    }
    if (record.ancestor_onenote_ids.some(id => !manifestPageIds.has(id) && !excludedStubIds.has(id))) {
      throw new Error(`Ancestor ID is not present in the included snapshot: ${record.onenote_id}`);
    }
  }
  return manifest;
}

function parseArguments(args) {
  const parsed = {};
  for (let index = 0; index < args.length; index += 2) {
    parsed[args[index].replace(/^--/, '')] = args[index + 1];
  }
  return parsed;
}

const args = parseArguments(process.argv.slice(2));
if (!args['vault-root'] || !args['snapshot-root'] || !args.output) {
  throw new Error('Usage: node build_onenote_hierarchy.mjs --vault-root PATH --snapshot-root PATH --output PATH');
}

const vaultRoot = path.resolve(args['vault-root']);
const snapshotRoot = path.resolve(args['snapshot-root']);
const outputPath = path.resolve(args.output);
const manifest = await buildManifest(vaultRoot, snapshotRoot);
await writeFile(outputPath, `${JSON.stringify(manifest, null, 2)}\n`, 'utf8');
console.log(JSON.stringify({
  snapshot_page_count: manifest.snapshot_page_count,
  matched_to_vault_count: manifest.matched_to_vault_count,
  excluded_parent_stub_count: manifest.excluded_parent_stub_count,
  status_counts: manifest.status_counts,
  output: outputPath,
}, null, 2));