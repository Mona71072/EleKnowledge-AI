import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';

const chat = readFileSync(new URL('../src/app/chat/page.tsx', import.meta.url), 'utf8');

test('normal technical KB not_found exposes the existing admin handoff only after a completed successful lookup', () => {
  const notFound = chat.slice(chat.indexOf("{message.responseType === 'not_found' && ("), chat.indexOf('<div className="chat-markdown', chat.indexOf("{message.responseType === 'not_found' && (")));
  assert.match(notFound, /canOpenOfficialKbGap/);
  assert.match(notFound, /!isLawMode/);
  assert.match(notFound, /answerMode === 'normal'/);
  assert.ok(notFound.includes('!loading'));
  assert.ok(notFound.includes('!error'));
  assert.match(notFound, /openOfficialKbGap/);
  assert.match(notFound, /ノウハウカードの候補にする/);
  const handoff = chat.slice(chat.indexOf('const openOfficialKbGap ='), chat.indexOf('const handleNewSession ='));
  assert.match(handoff, /storeKnowledgeGapRequest\(\{ kind: 'official_kb' \}\)/u);
  assert.doesNotMatch(handoff, /userId|query|content|messageId|question/iu);
});

test('research handoff never puts a question in the URL and research mode ignores legacy q parameters', () => {
  const senpaiTurn = readFileSync(new URL('../src/components/knowledge/SenpaiChatTurn.tsx', import.meta.url), 'utf8');
  assert.match(senpaiTurn, /function researchHref\(\)\s*\{\s*return ['"]\/chat\?research=1['"]/u);
  assert.match(senpaiTurn, /storeResearchQuery\(turn\.query\)/u);
  const initialQuery = chat.slice(chat.indexOf("const researchLink = params.get('research')"), chat.indexOf('if (sessionId)', chat.indexOf("const researchLink = params.get('research')")));
  assert.match(initialQuery, /researchLink \? consumeResearchQuery\(\) : params\.get\('q'\)/u);
  assert.match(initialQuery, /consumeResearchQuery/u);
  assert.match(initialQuery, /let dirty = researchLink/u);
  const urlCleanup = chat.slice(chat.indexOf('if (dirty)', chat.indexOf("const researchLink = params.get('research')")), chat.indexOf('const handleSuggestedQuestion'));
  assert.match(urlCleanup, /window\.history\.replaceState/u);
});

test('field material AI consent names every value sent to the suggestion endpoint', () => {
  const panel = readFileSync(new URL('../src/components/knowledge/KnowledgeFieldMaterialPanel.tsx', import.meta.url), 'utf8');
  assert.match(panel, /選んだ抜粋・確認テーマ・資料名・確認日（本日）をAIへ送ってよいことを確認した/u);
  assert.match(panel, /確認日/);
});
