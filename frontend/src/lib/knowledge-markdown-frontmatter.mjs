import { isAlias, isMap, isScalar, isSeq, parseDocument } from 'yaml';

const MAX_FRONTMATTER_DEPTH = 32;
const MAX_FRONTMATTER_NODES = 12_000;
const DANGEROUS_KEYS = new Set(['__proto__', 'prototype', 'constructor']);

function fail(message) {
  throw new TypeError(message);
}

export function parseKnowledgeFrontmatter(markdown, maxBytes) {
  if (typeof markdown !== 'string') fail('Markdown must be a string.');
  if (markdown.includes('\0')) fail('Markdown cannot contain NUL bytes.');
  if (new TextEncoder().encode(markdown).byteLength > maxBytes) {
    fail('Markdown exceeds the configured size limit.');
  }

  const firstLineEnd = markdown.indexOf('\n');
  if (firstLineEnd < 0 || !/^---\r?$/.test(markdown.slice(0, firstLineEnd))) {
    fail('Markdown must start with YAML frontmatter.');
  }

  const firstContentOffset = firstLineEnd + 1;
  let cursor = firstContentOffset;
  let closingStart = -1;
  let closingEnd = -1;
  while (cursor <= markdown.length) {
    const lineEnd = markdown.indexOf('\n', cursor);
    const end = lineEnd < 0 ? markdown.length : lineEnd;
    const line = markdown.slice(cursor, end).replace(/\r$/, '');
    if (line === '---') {
      closingStart = cursor;
      closingEnd = lineEnd < 0 ? end : lineEnd + 1;
      break;
    }
    if (lineEnd < 0) break;
    cursor = lineEnd + 1;
  }
  if (closingStart < 0) fail('YAML frontmatter closing delimiter is missing.');

  const yamlText = markdown.slice(firstContentOffset, closingStart);
  const document = parseDocument(yamlText, {
    schema: 'core',
    uniqueKeys: true,
    version: '1.2',
  });
  if (document.errors.length > 0 || document.warnings.length > 0) {
    fail('YAML frontmatter contains a parse error or warning.');
  }
  if (!document.contents || !isMap(document.contents)) fail('YAML frontmatter must be a mapping.');

  validateYamlNodes(document.contents);
  let value;
  try {
    value = document.toJS({ maxAliasCount: 0, mapAsMap: false });
  } catch {
    fail('YAML aliases or unsupported values are not allowed.');
  }
  validatePlainValue(value);

  const afterFence = markdown.slice(closingEnd);
  const body = afterFence.startsWith('\r\n')
    ? afterFence.slice(2)
    : afterFence.startsWith('\n')
      ? afterFence.slice(1)
      : afterFence;
  return { frontmatter: value, body };
}

function validateYamlNodes(node) {
  if (!node) return;
  if (isAlias(node)) fail('YAML aliases are not allowed.');
  if (node.anchor) fail('YAML anchors are not allowed.');
  if (node.tag) fail('Explicit YAML tags are not allowed.');
  if (isMap(node)) {
    for (const pair of node.items) {
      validateYamlNodes(pair.key);
      validateYamlNodes(pair.value);
    }
    return;
  }
  if (isSeq(node)) {
    for (const item of node.items) validateYamlNodes(item);
    return;
  }
  if (!isScalar(node)) fail('Unsupported YAML node type.');
}

function validatePlainValue(value) {
  let count = 0;
  const visit = (current, depth) => {
    count += 1;
    if (count > MAX_FRONTMATTER_NODES || depth > MAX_FRONTMATTER_DEPTH) {
      fail('YAML frontmatter is too deeply nested or contains too many values.');
    }
    if (current === null || ['string', 'boolean'].includes(typeof current)) return;
    if (typeof current === 'number') {
      if (!Number.isFinite(current)) fail('Non-finite YAML numbers are not allowed.');
      return;
    }
    if (Array.isArray(current)) {
      for (const item of current) visit(item, depth + 1);
      return;
    }
    const prototype = current && typeof current === 'object' ? Object.getPrototypeOf(current) : undefined;
    if (typeof current !== 'object' || (prototype !== null && prototype !== Object.prototype)) {
      fail('YAML frontmatter must contain only plain JSON-like values.');
    }
    for (const [key, child] of Object.entries(current)) {
      if (DANGEROUS_KEYS.has(key) || key === '<<') fail('Unsafe YAML mapping key.');
      visit(child, depth + 1);
    }
  };
  visit(value, 0);
}

