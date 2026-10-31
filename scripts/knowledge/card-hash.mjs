import { createHash } from 'node:crypto';

export function cardDigest(markdown) {
  const canonicalMarkdown = markdown.replace(/\r\n?/g, '\n');
  return createHash('sha256').update(canonicalMarkdown).digest('hex');
}