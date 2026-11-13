import assert from 'node:assert/strict';
import test from 'node:test';
import { buildCheckQuestions } from '../src/lib/knowhow-card-check.mjs';
import { extractValueTokens, stripMarkdown } from '../src/lib/knowhow-card-check-text.mjs';
import {
  applyCheckProposals,
  buildCheckProposal,
  classifyProposalEvidence,
} from '../src/lib/knowhow-card-proposal.mjs';

const LIMIT_MS = 1_000;
const cardWith = (line) => `# 題名\n\n## 統合した回答\n${line}\n\n## 未確認事項\n- ${line}\n\n## 症状\n${line}\n`;
const timed = (run) => {
  const start = performance.now();
  run();
  return performance.now() - start;
};

for (const [name, line] of [
  ['閉じの無い [ が 6 万個', '['.repeat(60_000)],
  ['[a]( が 3 万回', '[a]('.repeat(30_000)],
  ['数字が 6 万桁（条の手前）', '1'.repeat(60_000)],
  ['開き括弧が 6 万個', '（'.repeat(60_000)],
]) {
  test(`一括照合の質問づくりは病的な行でも固まらない: ${name}`, () => {
    const elapsed = timed(() => buildCheckQuestions({ frontmatter: { title: '戸開閉' }, body: cardWith(line) }));
    assert.ok(elapsed < LIMIT_MS, `${Math.round(elapsed)}ms`);
  });
}

test('stripMarkdown と extractValueTokens は長い入力でも制限時間内で、通常のリンクは文字だけにする', () => {
  assert.equal(stripMarkdown('[資料](https://example.com/a) と ![図](x.png)'), '資料 と 図');
  assert.ok(timed(() => stripMarkdown('['.repeat(60_000))) < LIMIT_MS);
  assert.ok(timed(() => extractValueTokens('1'.repeat(60_000))) < LIMIT_MS);
  assert.deepEqual(extractValueTokens('29 条と 800 mm'), ['29 条', '800 mm']);
});

const answer = (mode, overrides = {}) => ({
  mode, query: 'q', content: '回答の本文です。', responseType: 'pages', sessionId: 's', messageId: 'm',
  receivedAt: '2026-11-13T01:00:00.000Z',
  sourceDocuments: [{ documentName: 'SUE-3-17.pdf', pageNumber: 4, sourceUri: 's3://technical-kb/SUE-3-17.pdf' }],
  pageCandidates: [], clarifyQuestions: [], ...overrides,
});
const notFound = (mode) => answer(mode, { responseType: 'not_found', sourceDocuments: [] });
const clarify = (mode) => answer(mode, { responseType: 'clarify', sourceDocuments: [] });
const noSource = (mode) => answer(mode, { sourceDocuments: [] });

test('「KB に該当資料なし」は照合した全レーンが not_found のときだけ。聞き返し・出典なしは別の書き方', () => {
  assert.equal(classifyProposalEvidence({ technical: answer('normal') }), 'sourced');
  assert.equal(classifyProposalEvidence({ technical: notFound('normal') }), 'not_found');
  assert.equal(classifyProposalEvidence({ technical: notFound('normal'), law: notFound('law') }), 'not_found');
  assert.equal(classifyProposalEvidence({ technical: notFound('normal'), law: clarify('law') }), 'no_source');
  assert.equal(classifyProposalEvidence({ technical: clarify('normal') }), 'no_source');
  assert.equal(classifyProposalEvidence({ law: noSource('law') }), 'no_source');
  assert.equal(classifyProposalEvidence({ technical: answer('normal'), law: notFound('law') }), 'sourced');
  const build = (input) => buildCheckProposal({ question: '質問', checkedOn: '2026-11-13', ...input });
  assert.match(build({ technical: notFound('normal'), law: notFound('law') }), /- 確認: KB に該当資料なし（2026-11-13）/u);
  const mixed = build({ technical: notFound('normal'), law: clarify('law') });
  assert.doesNotMatch(mixed, /確認: KB に該当資料なし/u);
  assert.match(mixed, /- 確認: 根拠になる出典が見つからなかった（聞き返し・出典なしの回答を含む）（2026-11-13）/u);
  assert.match(build({ technical: noSource('normal') }), /- 確認: 根拠になる出典が見つからなかった/u);
  assert.doesNotMatch(build({ technical: noSource('normal') }), /確認: KB に該当資料なし/u);
});

const CARD = '# 題名\n\n## 統合した回答\n本文。\n\n## 正式資料・元情報\n参照。\n';
const proposalFor = (question) => ({
  question, checkedOn: '2026-11-13',
  markdown: buildCheckProposal({ question, technical: answer('normal'), checkedOn: '2026-11-13' }),
});
const countHeadings = (markdown) => markdown.split('\n').filter((line) => /^ {0,3}## KB確認に基づく追記/u.test(line)).length;

test('行頭に空白のある「 ## KB確認に基づく追記」でも節を重複させず、同じ追記は入れない', () => {
  const first = applyCheckProposals(CARD, [proposalFor('質問A')]).markdown;
  const indented = first.replace('## KB確認に基づく追記', '  ## KB確認に基づく追記');
  assert.match(indented, /^ {2}## KB確認に基づく追記/mu);
  assert.equal(applyCheckProposals(indented, [proposalFor('質問A')]).applied, 0);
  const added = applyCheckProposals(indented, [proposalFor('質問B')]);
  assert.equal(added.applied, 1);
  assert.equal(countHeadings(added.markdown), 1);
  assert.match(added.markdown, /質問A[\s\S]*質問B/u);
  const spaced = applyCheckProposals('# 題名\n\n   ## 正式資料・元情報\n参照。\n', [proposalFor('質問C')]).markdown;
  assert.ok(spaced.indexOf('## KB確認に基づく追記') < spaced.indexOf('## 正式資料・元情報'));
});

test('先頭の --- が妥当な frontmatter でないときは、その区切りまでを frontmatter とみなさない', () => {
  const markdown = '---\n\n## 正式資料・元情報\n参照。\n\n---\n\n本文。\n';
  const result = applyCheckProposals(markdown, [proposalFor('質問D')]).markdown;
  assert.ok(result.indexOf('## KB確認に基づく追記') < result.indexOf('## 正式資料・元情報'));
  const real = '---\nknowledge_id: KH-T\ntitle: T\n---\n\n# 題名\n\n## 正式資料・元情報\n参照。\n';
  const realResult = applyCheckProposals(real, [proposalFor('質問E')]).markdown;
  assert.ok(realResult.startsWith('---\nknowledge_id: KH-T\ntitle: T\n---\n'));
  assert.ok(realResult.indexOf('## KB確認に基づく追記') < realResult.indexOf('## 正式資料・元情報'));
  const fakeHeadingInYaml = '---\ntitle: T\nnote: |\n  ## KB確認に基づく追記\n---\n\n# 題名\n\n## 正式資料・元情報\n参照。\n';
  const yamlResult = applyCheckProposals(fakeHeadingInYaml, [proposalFor('質問F')]).markdown;
  assert.equal(yamlResult.split('\n').filter((line) => line === '## KB確認に基づく追記').length, 1);
});

test('見出し行の判定は、末尾の空白や # が長く続く行でも固まらない', async () => {
  const { listCommentSections } = await import('../src/lib/knowledge-comment-review.mjs');
  const { splitKnowhowCardBody } = await import('../src/lib/knowhow-card-view.mjs');
  const spaced = `## 確認${' '.repeat(20_000)}x`;
  const hashes = `## 確認 ${'#'.repeat(20_000)}x`;
  const suffix = `## KB確認に基づく追記${' '.repeat(20_000)}x`;
  for (const line of [spaced, hashes, suffix]) {
    const body = `# 題名\n\n${line}\n本文\n`;
    assert.ok(timed(() => listCommentSections(body)) < LIMIT_MS);
    assert.ok(timed(() => splitKnowhowCardBody(body)) < LIMIT_MS);
    assert.ok(timed(() => applyCheckProposals(body, [proposalFor('質問G')])) < LIMIT_MS);
  }
  assert.deepEqual(listCommentSections('# T\n\n## 見出し ##\n').map((s) => s.label), ['見出し']);
  assert.deepEqual(listCommentSections('# T\n\n   ## 見出し\n').map((s) => s.label), ['見出し']);
});

test('本文を編集しても一括照合は作り直さない。作り直すのは別のカードを読み込んだときだけ', async () => {
  const { readFileSync } = await import('node:fs');
  const workbench = readFileSync(new URL('../src/components/knowledge/KnowledgeWorkbench.tsx', import.meta.url), 'utf8');
  const element = /<KnowhowCardCheck[\s\S]*?\/>\s*<\/div>/u.exec(workbench)?.[0] ?? '';
  const key = /key=\{([^}]*)\}/u.exec(element)?.[1] ?? '';
  assert.equal(key, 'documentSession');
  const component = readFileSync(new URL('../src/components/knowledge/KnowhowCardCheck.tsx', import.meta.url), 'utf8');
  assert.match(component, /本文が変わりました。追記の差し込みは最新の本文に対して行います/u);
});

test('照合を始めた後に本文が編集されても、追記は最新の本文に足され、編集は消えない', () => {
  const started = CARD;
  const edited = started.replace('本文。', '本文。\n\n照合の後で足した一文。');
  const result = applyCheckProposals(edited, [proposalFor('質問H')]);
  assert.equal(result.applied, 1);
  assert.match(result.markdown, /照合の後で足した一文。/u);
  assert.ok(result.markdown.indexOf('照合の後で足した一文') < result.markdown.indexOf('## KB確認に基づく追記'));
  assert.ok(result.markdown.indexOf('## KB確認に基づく追記') < result.markdown.indexOf('## 正式資料・元情報'));
});
