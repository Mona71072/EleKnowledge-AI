#!/usr/bin/env node
// Regenerates tests/fixtures/knowledge/synthetic/built-index.json from the synthetic cards in
// tests/fixtures/knowledge/synthetic/contract-root, using the real build code. The fixture is
// the contract shared by the JS builder test and the Python retrieval test.
//   npm --prefix frontend run knowledge:regen-contract-fixture
import { writeFile } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { buildKnowhowIndex, inventoryKnowhowCards } from './build-senpai-index.mjs';

const repoRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../..');
export const CONTRACT_ROOT = path.join(repoRoot, 'tests/fixtures/knowledge/synthetic/contract-root');
export const CONTRACT_INDEX = path.join(repoRoot, 'tests/fixtures/knowledge/synthetic/built-index.json');
export const CONTRACT_GENERATED_AT = '2026-10-20T00:00:00.000Z';

/** Build the contract index text (same serialization as the private index writer). */
export async function buildContractFixtureText() {
  const inventory = await inventoryKnowhowCards(CONTRACT_ROOT);
  if (inventory.errors.length > 0) throw new Error('A synthetic contract card failed validation.');
  const manifest = {
    schemaVersion: 1,
    purpose: 'senpai-admin-navigation',
    approvedBy: 'Synthetic fixture generator',
    approvedAt: CONTRACT_GENERATED_AT,
    entries: inventory.cards.map((card) => ({
      path: card.path, knowledgeId: card.knowledgeId, cardVersion: card.cardVersion, sha256: card.sha256, cloudApproved: true,
    })),
  };
  const index = await buildKnowhowIndex({ root: CONTRACT_ROOT, manifest, generatedAt: CONTRACT_GENERATED_AT });
  return `${JSON.stringify(index, null, 2)}\n`;
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  await writeFile(CONTRACT_INDEX, await buildContractFixtureText(), 'utf8');
  process.stdout.write(`Wrote ${path.relative(repoRoot, CONTRACT_INDEX)}\n`);
}
