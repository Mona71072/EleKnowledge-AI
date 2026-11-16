import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import test from 'node:test';
import {
  REWRITE_LIMITS,
  REWRITE_TARGET_HEADINGS,
  applySectionRewrites,
  buildAcceptedRewrites,
  buildConflictOpenItem,
  buildRewriteEvidence,
  buildRewriteRequest,
  buildRewriteRetryRequest,
  buildRewriteHistory,
  composeCardEdits,
  describeRewriteWarning,
  findRewriteBodyProblem,
  isRewriteEnabled,
  normalizeRewriteResponse,
  selectRewriteSections,
  summarizeRewriteDecisions,
} from '../src/lib/knowhow-rewrite.mjs';
import { buildCheckProposal } from '../src/lib/knowhow-card-proposal.mjs';

const contract = JSON.parse(readFileSync(new URL('../../tests/fixtures/knowhow-rewrite/contract.json', import.meta.url), 'utf8'));
const OPEN = '未確認事項';
const MAIN = '統合した回答・ノウハウ';
const STEPS = '調査・確認手順';

const CARD = [
  '# 題名',
  '',
  '## 使う場面・対象条件',
  '',
  '- ピットタラップを戸袋側へ移設したが社内検査で指摘されたとき',
  '',
  `## ${MAIN}`,
  '',
  '据付 SUE-3-17（600 mm 近接）と社内検査 800 mm は別の基準として共存しうる。',
  '',
  '## KB確認に基づく追記',
  '',
  '（未実施）',
  '',
  `## ${OPEN}`,
  '',
  '- SUE-3-17 本文（600 mm 規定の現行文言）',
  '',
].join('\n');

const answerFor = (mode, overrides = {}) => ({
  mode,
  query: 'q',
  content: '据付基準では三方枠からタラップ中心までの水平距離を 600 mm 以下に近づけることとしています。',
  responseType: 'pages',
  sessionId: 's',
  messageId: 'm',
  receivedAt: '2026-11-14T12:00:00.000Z',
  sourceDocuments: mode === 'law'
    ? [{ documentName: '建築基準法施行令', lawCitation: { lawId: '325CO0000000338', lawTitle: '建築基準法施行令', lawNumber: '昭和二十五年政令第三百三十八号', effectiveDate: '2025-12-01', provisionType: 'Article', provisionReference: '第百二十九条の七', sourceUrl: 'https://laws.e-gov.go.jp/law/325CO0000000338' } }]
    : [{ documentName: 'SUE-3-17_ピット点検タラップ.pdf', pageNumber: 4, sourceUri: 's3://technical-kb/SUE-3-17.pdf' }],
  pageCandidates: [],
  clarifyQuestions: [],
  ...overrides,
});
const notFound = (mode) => answerFor(mode, { responseType: 'not_found', content: '該当なし', sourceDocuments: [] });
const QUESTION_TEXT = contract.request.evidence[0].question;
const question = (id = 'q1', targets = ['normal'], text = QUESTION_TEXT) => ({ id, text, targets });
const task = (questionId, mode, result) => ({ id: `${questionId}-${mode}`, questionId, mode, query: 'q', status: 'done', result });
const confirmAll = (...ids) => Object.fromEntries(ids.map((id) => [id, 'confirm']));

test('表示条件は環境変数が文字列 true のときだけ', () => {
  assert.equal(isRewriteEnabled('true'), true);
  for (const value of [undefined, '', 'false', 'TRUE', '1', 'yes', true]) assert.equal(isRewriteEnabled(value), false);
});

test('再実行指示は trim 後 1〜1,000 字で検証し、前回案を対象節と版に結び付ける', async () => {
  const plan = buildRewriteRequest({ frontmatter: { knowledge_id: 'KH-A', card_version: 3 }, body: CARD, evidence: buildRewriteEvidence({ questions: [contractQuestion], tasks: contractTasks, decisions: confirmAll('q1') }) });
  const proposal = { knowledgeId: 'KH-A', cardVersion: 3, bases: plan.request.targets, sections: plan.request.targets.map(({ heading, body }) => ({ heading, body: `改訂: ${body}`, status: 'changed' })) };
  const retry = await buildRewriteRetryRequest({ request: plan.request, proposal, instruction: '  手順を簡潔にする  ' });
  assert.equal(retry.instruction, '手順を簡潔にする');
  assert.deepEqual(retry.previousProposal, {
    knowledgeId: 'KH-A', cardVersion: 3,
    bodyHash: await digest(JSON.stringify(plan.request.targets)),
    sections: proposal.sections.map(({ heading, body }) => ({ heading, body })),
  });
  assert.deepEqual(retry.targets, plan.request.targets);
  assert.deepEqual(retry.evidence, plan.request.evidence);
  for (const instruction of ['', '   ', 'あ'.repeat(1001), 'a\u0000b']) {
    await assert.rejects(buildRewriteRetryRequest({ request: plan.request, proposal, instruction }), TypeError);
  }
  assert.equal((await buildRewriteRetryRequest({ request: plan.request, proposal, instruction: '😀'.repeat(1000) })).instruction, '😀'.repeat(1000));
  await assert.rejects(buildRewriteRetryRequest({ request: { ...plan.request, evidence: [{ ...plan.request.evidence[0], lane: 'field' }] }, proposal, instruction: '変更' }), /field/u);
  await assert.rejects(buildRewriteRetryRequest({ request: { ...plan.request, targets: [{ heading: MAIN, body: 'あ'.repeat(2001) }] }, proposal, instruction: '変更' }), /対象の節/u);
  await assert.rejects(buildRewriteRetryRequest({ request: plan.request, proposal: { ...proposal, bases: [] }, instruction: '変更' }), /直前案/u);
});

test('直前案本文は初回案上限の4,000字まで許可し、全対象見出しを要求する', async () => {
  const plan = buildRewriteRequest({ frontmatter: { knowledge_id: 'KH-A', card_version: 3 }, body: CARD, evidence: buildRewriteEvidence({ questions: [contractQuestion], tasks: contractTasks, decisions: confirmAll('q1') }) });
  const proposal = { knowledgeId: 'KH-A', cardVersion: 3, bases: plan.request.targets, sections: plan.request.targets.map(({ heading }, index) => ({ heading, body: 'x'.repeat(index === 0 ? 4000 : 0), status: 'changed' })) };
  const retry = await buildRewriteRetryRequest({ request: plan.request, proposal, instruction: '要点を短く' });
  assert.equal(retry.previousProposal.sections[0].body.length, 4000);
  assert.equal(REWRITE_LIMITS.previousProposalBodyChars, REWRITE_LIMITS.responseBodyChars);
  await assert.rejects(buildRewriteRetryRequest({ request: plan.request, proposal: { ...proposal, sections: proposal.sections.map((section, index) => index === 0 ? { ...section, body: `${section.body}x` } : section) }, instruction: '整える' }), /直前案/u);
  for (const sections of [proposal.sections.slice(1), [...proposal.sections, { heading: '余分', body: '' }]]) {
    await assert.rejects(buildRewriteRetryRequest({ request: plan.request, proposal: { ...proposal, sections }, instruction: '整える' }), /直前案/u);
  }
});

test('案履歴は初回と指示ごとの再案を順番とラベルで区別する', () => {
  const history = buildRewriteHistory([
    { instruction: null, proposal: { id: 'one' } },
    { instruction: '手順を短く', proposal: { id: 'two' } },
  ]);
  assert.deepEqual(history.map(({ label, instruction, proposal }) => ({ label, instruction, proposal })), [
    { label: '第1案', instruction: '', proposal: { id: 'one' } },
    { label: '指示1 → 第2案', instruction: '手順を短く', proposal: { id: 'two' } },
  ]);
});

async function digest(value) {
  const bytes = await globalThis.crypto.subtle.digest('SHA-256', new TextEncoder().encode(value));
  return [...new Uint8Array(bytes)].map((byte) => byte.toString(16).padStart(2, '0')).join('');
}

test('対象の節は契約の3つで、上限は契約と同じ', () => {
  assert.deepEqual([...REWRITE_TARGET_HEADINGS], contract.targetHeadings);
  const { limits } = contract;
  assert.equal(REWRITE_LIMITS.targetBodyChars, limits.targets.bodyChars);
  assert.equal(REWRITE_LIMITS.targetTotalChars, limits.targets.totalChars);
  assert.equal(REWRITE_LIMITS.contextMax, limits.context.max);
  assert.equal(REWRITE_LIMITS.contextBodyChars, limits.context.bodyChars);
  assert.equal(REWRITE_LIMITS.contextTotalChars, limits.context.totalChars);
  assert.equal(REWRITE_LIMITS.evidenceMax, limits.evidence.max);
  assert.equal(REWRITE_LIMITS.answerChars, limits.evidence.answerChars);
  assert.equal(REWRITE_LIMITS.sourcesMax, limits.sources.max);
  assert.equal(REWRITE_LIMITS.responseBodyChars, limits.response.bodyChars);
  assert.equal(REWRITE_LIMITS.previousProposalBodyChars, limits.response.bodyChars);
  assert.equal(REWRITE_LIMITS.reasonChars, limits.response.reasonChars);
  assert.equal(REWRITE_LIMITS.knowledgeIdPattern.source, limits.knowledgeIdPattern);
});

test('節の選別: 対象はカードにある3節だけ、それ以外は context。無い節は出さない', () => {
  const { targets, context, excluded } = selectRewriteSections(CARD);
  assert.deepEqual(targets.map((s) => s.heading), [MAIN, OPEN]);
  assert.equal(targets[0].body, '据付 SUE-3-17（600 mm 近接）と社内検査 800 mm は別の基準として共存しうる。');
  assert.deepEqual(context.map((s) => s.heading), ['使う場面・対象条件', 'KB確認に基づく追記']);
  assert.deepEqual(excluded, []);
});

test('節の選別: コードフェンス内の見出し・CRLF・見出しの空白・frontmatter を正しく扱う', () => {
  const card = ['---', 'knowledge_id: KH-A', '---', '# t', '', `##   ${MAIN}  ##`, '', '```', `## ${OPEN}`, '```', '本文', '', `## ${OPEN}`, '- 未確認'].join('\r\n');
  const { targets } = selectRewriteSections(card);
  assert.deepEqual(targets.map((s) => s.heading), [MAIN, OPEN]);
  assert.equal(targets[0].body, `\`\`\`\n## ${OPEN}\n\`\`\`\n本文`);
  assert.equal(targets[1].body, '- 未確認');
});

test('節の選別: 上限超過・空・重複は対象から外し、理由を返す。切り詰めない', () => {
  const long = 'あ'.repeat(REWRITE_LIMITS.targetBodyChars + 1);
  const card = `# t\n\n## ${MAIN}\n\n${long}\n\n## ${STEPS}\n\n1. 手順\n\n## ${OPEN}\n\n`;
  const result = selectRewriteSections(card);
  assert.deepEqual(result.targets.map((s) => s.heading), [STEPS]);
  assert.deepEqual(result.excluded, [{ heading: MAIN, reason: 'too_long' }, { heading: OPEN, reason: 'empty' }]);
  const dup = selectRewriteSections(`# t\n\n## ${MAIN}\n\nA\n\n## ${MAIN}\n\nB\n`);
  assert.deepEqual(dup.targets, []);
  assert.deepEqual(dup.excluded, [{ heading: MAIN, reason: 'duplicate' }]);
  const half = 'い'.repeat(1500);
  const total = selectRewriteSections(`# t\n\n## ${MAIN}\n\n${half}\n\n## ${STEPS}\n\n${half}\n\n## ${OPEN}\n\n${half}\n`);
  assert.deepEqual(total.targets.map((s) => s.heading), [MAIN, STEPS]);
  assert.deepEqual(total.excluded, [{ heading: OPEN, reason: 'total_too_long' }]);
});

test('節の選別: context は件数・文字数の上限内で、利用者向けの節を先に入れる', () => {
  const sections = Array.from({ length: 12 }, (_, i) => `## 参考${i}\n\n内容${i}`).join('\n\n');
  const { context } = selectRewriteSections(`# t\n\n## ソース要約\n\n要約\n\n${sections}\n\n## ${MAIN}\n\n本文\n`);
  assert.equal(context.length, REWRITE_LIMITS.contextMax);
  assert.equal(context[0].heading, '参考0');
  assert.ok(!context.some((s) => s.heading === 'ソース要約'), '上限を超えた分は編集者向けの節から外れる');
  const big = selectRewriteSections(`# t\n\n## 巨大\n\n${'あ'.repeat(REWRITE_LIMITS.contextBodyChars + 1)}\n\n## ${MAIN}\n\n本文\n`);
  assert.deepEqual(big.context, []);
});

const contractQuestion = question('q1', ['normal']);
const contractTasks = [task('q1', 'normal', answerFor('normal'))];

test('根拠の絞り込み: 確認して追記する・出典つきの照合先だけが入る', () => {
  const items = buildRewriteEvidence({ questions: [contractQuestion], tasks: contractTasks, decisions: confirmAll('q1') });
  assert.equal(items.length, 1);
  assert.equal(items[0].lane, 'technical');
  assert.equal(items[0].questionId, 'q1');
  for (const decisions of [{}, { q1: 'skip' }]) {
    assert.deepEqual(buildRewriteEvidence({ questions: [contractQuestion], tasks: contractTasks, decisions }), []);
  }
  const both = [question('q2', ['normal', 'law'])];
  const tasks = [task('q2', 'normal', answerFor('normal')), task('q2', 'law', notFound('law'))];
  const lanes = buildRewriteEvidence({ questions: both, tasks, decisions: confirmAll('q2') }).map((i) => i.lane);
  assert.deepEqual(lanes, ['technical'], '該当なしの法令KBは入らない');
  const noSource = [task('q1', 'normal', answerFor('normal', { sourceDocuments: [] }))];
  assert.deepEqual(buildRewriteEvidence({ questions: [contractQuestion], tasks: noSource, decisions: confirmAll('q1') }), []);
  const unfinished = [question('q3', ['normal', 'law'])];
  assert.deepEqual(buildRewriteEvidence({ questions: unfinished, tasks: [task('q3', 'normal', answerFor('normal'))], decisions: confirmAll('q3') }), []);
});

test('根拠: 法令の出典は条名つきの題名、回答の抜粋は先頭だけ', () => {
  const questions = [question('q2', ['law'])];
  const [item] = buildRewriteEvidence({ questions, tasks: [task('q2', 'law', answerFor('law', { content: 'あ。'.repeat(500) }))], decisions: confirmAll('q2') });
  assert.equal(item.lane, 'law');
  assert.deepEqual(item.sources, [{ title: '建築基準法施行令 第百二十九条の七' }]);
  assert.ok(Array.from(item.answer).length <= REWRITE_LIMITS.answerChars);
  assert.ok(Array.from(item.answer).length < 500 * 2);
});

function planFor(body = CARD, overrides = {}) {
  const evidence = buildRewriteEvidence({ questions: [contractQuestion], tasks: contractTasks, decisions: confirmAll('q1') });
  return buildRewriteRequest({ frontmatter: { knowledge_id: 'KH-PIT-TRAP-POSITION-394', card_version: 1 }, body, evidence, ...overrides });
}

test('要求は契約の request 例と同じ形になり、内部のIDは含まない', () => {
  const { request, blocker, excluded } = planFor();
  assert.equal(blocker, '');
  assert.deepEqual(excluded, []);
  assert.deepEqual(request.targets, contract.request.targets);
  assert.deepEqual(request.context.slice(0, 1), contract.request.context);
  assert.deepEqual(request.evidence, contract.request.evidence);
  assert.deepEqual(Object.keys(request).sort(), ['cardVersion', 'context', 'evidence', 'knowledgeId', 'targets']);
  assert.equal(request.knowledgeId, contract.request.knowledgeId);
  assert.equal(request.cardVersion, contract.request.cardVersion);
  assert.ok(!JSON.stringify(request).includes('questionId'));
});

test('要求は契約の上限内で、frontmatter・カード全文・題名を含まない', () => {
  const card = `---\nknowledge_id: KH-PIT-TRAP-POSITION-394\ncard_version: 1\nsource_refs: [秘密の参照]\n---\n${CARD}`;
  const { request } = planFor(card);
  const text = JSON.stringify(request);
  for (const leaked of ['source_refs', '秘密の参照', 'knowledge_id', '# 題名']) assert.ok(!text.includes(leaked), leaked);
  const { limits } = contract;
  assert.ok(new TextEncoder().encode(text).length < limits.bodyBytes);
  assert.match(request.knowledgeId, new RegExp(limits.knowledgeIdPattern, 'u'));
  assert.ok(request.targets.length >= limits.targets.min && request.targets.length <= limits.targets.max);
  assert.ok(request.context.length <= limits.context.max);
  assert.ok(request.evidence.length >= limits.evidence.min && request.evidence.length <= limits.evidence.max);
  for (const item of request.evidence) {
    assert.ok(Array.from(item.question).length <= limits.evidence.questionChars);
    assert.ok(item.sources.length <= limits.sources.max);
  }
});

test('要求を作れない理由: 根拠なし・ID不正・版不正・対象の節なし', () => {
  assert.match(planFor(CARD, { evidence: [] }).blocker, /出典つきの確認済みが無い/u);
  assert.equal(planFor(CARD, { evidence: [] }).request, null);
  assert.match(planFor(CARD, { frontmatter: { knowledge_id: 'bad', card_version: 1 } }).blocker, /knowledge_id/u);
  assert.match(planFor(CARD, { frontmatter: { knowledge_id: 'KH-A', card_version: 0 } }).blocker, /card_version/u);
  assert.match(planFor('# t\n\n## 他の節\n\n本文\n').blocker, /対象の節/u);
  assert.equal(planFor(CARD, { frontmatter: { knowledge_id: 'KH-A', card_version: '12' } }).request.cardVersion, 12);
});

test('根拠が12件を超えたら先頭12件だけを送り、省いた件数を返す', () => {
  const one = buildRewriteEvidence({ questions: [contractQuestion], tasks: contractTasks, decisions: confirmAll('q1') })[0];
  const plan = planFor(CARD, { evidence: Array.from({ length: 14 }, (_, i) => ({ ...one, questionId: `q${i}` })) });
  assert.equal(plan.request.evidence.length, 12);
  assert.equal(plan.evidenceOmitted, 2);
  assert.equal(plan.evidenceRefs.length, 12);
  assert.deepEqual(plan.evidenceRefs[0], { number: 1, questionId: 'q0', question: one.question });
});

test('応答の再検証: 契約の response 例を受理する', () => {
  const { request } = planFor();
  const result = normalizeRewriteResponse(contract.response, request);
  assert.deepEqual(result.sections.map((s) => [s.heading, s.status]), [[MAIN, 'unchanged'], [OPEN, 'changed']]);
  const changed = result.sections[1];
  assert.equal(changed.body, contract.response.sections[1].body);
  assert.equal(changed.baseBody, '- SUE-3-17 本文（600 mm 規定の現行文言）');
  assert.deepEqual(changed.evidence, [1]);
  assert.deepEqual(changed.warnings, []);
  assert.deepEqual(result.conflicts, []);
});

const withSection = (section) => ({ ...contract.response, sections: [section] });
const changedSection = (overrides = {}) => ({ heading: OPEN, status: 'changed', body: '- 新しい本文 12', reason: '理由', evidence: [1], warnings: [], ...overrides });
const normalizeOne = (section) => normalizeRewriteResponse(withSection(section), planFor().request).sections[0];

test('応答の再検証: 対象外の見出し・範囲外の根拠・見出し入り本文・型違いは不採用', () => {
  assert.equal(normalizeOne(changedSection()).status, 'changed');
  const cases = [
    [changedSection({ heading: '正式資料・元情報' }), 'invalid_heading'],
    [changedSection({ heading: STEPS }), 'invalid_heading'],
    [changedSection({ evidence: [2] }), 'invalid_evidence'],
    [changedSection({ evidence: [0] }), 'invalid_evidence'],
    [changedSection({ evidence: [1.5] }), 'invalid_evidence'],
    [changedSection({ evidence: [] }), 'invalid_evidence'],
    [changedSection({ evidence: '1' }), 'invalid_evidence'],
    [changedSection({ body: '本文\n## 別の節\nx' }), 'heading_in_body'],
    [changedSection({ body: '---\nfrontmatter のふり' }), 'heading_in_body'],
    [changedSection({ body: '```\n開いたまま' }), 'unclosed_fence'],
    [changedSection({ body: 'x'.repeat(REWRITE_LIMITS.responseBodyChars + 1) }), 'too_long'],
    [changedSection({ body: 123 }), 'invalid_body'],
    [changedSection({ body: '   ' }), 'invalid_body'],
    [changedSection({ reason: 5 }), 'invalid_reason'],
    [changedSection({ status: 'weird' }), 'invalid_status'],
    [changedSection({ warnings: [{ code: 'unsupported_value', values: ['SUE-9'] }] }), 'unsupported_value'],
  ];
  for (const [section, code] of cases) {
    const got = normalizeOne(section);
    assert.equal(got.status, 'rejected', code);
    assert.equal(got.body, undefined, 'rejected は本文を持たない');
    assert.ok(got.warnings.some((w) => w.code === code), `${code}: ${JSON.stringify(got.warnings)}`);
  }
});

test('応答の再検証: 元の本文に無いリンク・HTML・見えない文字・制御文字は不採用', () => {
  const rejectedWith = (body) => normalizeOne(changedSection({ body })).warnings.map((w) => w.code);
  for (const body of ['詳細は https://evil.example を参照', '詳細は http://evil.example', 'www.evil.example を見る', '[x](#local)', '[x](javascript:alert(1))', '![img](x.png)', '<b>強調</b>', '本文</div>', '<!-- 隠し -->', '<img src=x>']) {
    assert.deepEqual(rejectedWith(body), ['link_or_html'], body);
  }
  for (const body of ['ゼロ幅\u200bスペース', '右から左\u202e', '制御\u0000文字', 'エスケープ\u001b[0m', 'BOM\ufeff', '削除\u007f']) {
    assert.deepEqual(rejectedWith(body), ['suspicious_text'], JSON.stringify(body));
  }
  for (const body of ['1 < 2 かつ 3 > 2', '1<2', '改行\nとタブ\tは許す', '800 mm を超えるとき']) {
    assert.equal(normalizeOne(changedSection({ body })).status, 'changed', body);
  }
});

test('元の本文に同じリンクや HTML がある場合だけ通す', () => {
  const original = '参照 https://example.com/a と [資料](./doc.md) と <br>';
  assert.equal(findRewriteBodyProblem(`${original} 追記 12`, original), null);
  assert.equal(findRewriteBodyProblem('参照 https://example.com/a 追記', original), null);
  assert.equal(findRewriteBodyProblem('参照 https://example.com/b', original), 'link_or_html');
  assert.equal(findRewriteBodyProblem('[資料](./other.md)', original), 'link_or_html');
  assert.equal(findRewriteBodyProblem('<script>', original), 'link_or_html');
  assert.equal(findRewriteBodyProblem('https://example.com/a'), 'link_or_html', '元が無ければ通さない');
  const card = `# t\n\n## ${MAIN}\n\n参照 https://example.com/a\n`;
  const { request } = planFor(card);
  const data = { ...contract.response, sections: [{ heading: MAIN, status: 'changed', body: '参照 https://example.com/a 追記 12', reason: '理由', evidence: [1], warnings: [] }] };
  assert.equal(normalizeRewriteResponse(data, request).sections[0].status, 'changed');
});

test('変更理由と食い違いの要約に URL・HTML・見えない文字があれば表示しない', () => {
  for (const reason of ['https://evil.example で確認', '<b>x</b>', 'www.evil.example', '[a](b)', '見えない\u200b文字']) {
    const got = normalizeOne(changedSection({ reason }));
    assert.equal(got.status, 'changed', reason);
    assert.equal(got.reason, '', reason);
  }
  assert.equal(normalizeOne(changedSection({ reason: '普通の理由' })).reason, '普通の理由');
  const { request } = planFor();
  const conflicts = normalizeRewriteResponse({ ...contract.response, conflicts: [
    { heading: null, summary: 'https://evil.example', evidence: [1] },
    { heading: null, summary: '<i>x</i>', evidence: [1] },
    { heading: null, summary: '普通の食い違い', evidence: [1] },
  ] }, request).conflicts;
  assert.deepEqual(conflicts.map((c) => c.description), ['普通の食い違い']);
});

test('応答の再検証: コードフェンス内の ## は見出しとして数えない。未知のキーは無視し、型違いの全体は null', () => {
  const fenced = normalizeOne(changedSection({ body: '```\n## 例\n```\n本文 12', extra: 'x' }));
  assert.equal(fenced.status, 'changed');
  assert.equal(Object.hasOwn(fenced, 'extra'), false);
  const { request } = planFor();
  for (const data of [null, 'x', [], { ...contract.response, knowledgeId: 'KH-OTHER' }, { ...contract.response, cardVersion: 2 }, { ...contract.response, sections: 'x' }]) {
    assert.equal(normalizeRewriteResponse(data, request), null);
  }
  const duplicated = normalizeRewriteResponse({ ...contract.response, sections: [changedSection(), changedSection()] }, request).sections;
  assert.deepEqual(duplicated.map((s) => s.status), ['changed', 'rejected']);
});

test('応答の再検証: 本文が元と同じなら変更なし、変更なし・不採用は本文を持たない', () => {
  const same = normalizeOne(changedSection({ body: '- SUE-3-17 本文（600 mm 規定の現行文言）\n' }));
  assert.equal(same.status, 'unchanged');
  const body = normalizeOne({ heading: OPEN, status: 'unchanged', body: '返してはいけない' });
  assert.equal(body.body, undefined);
  const rejected = normalizeOne({ heading: OPEN, status: 'rejected', body: 'x', warnings: [{ code: 'unsupported_value', values: ['SUE-9'] }] });
  assert.equal(rejected.status, 'rejected');
  assert.equal(rejected.body, undefined);
  assert.deepEqual(rejected.warnings, [{ code: 'unsupported_value', values: ['SUE-9'] }]);
});

test('警告: 文字列でも {code, values} でも受け、数字は日本語で説明する', () => {
  const got = normalizeOne(changedSection({ warnings: ['unverified_number', { code: 'unverified_number', tokens: ['12', '345'] }, { code: 'novel' }, 5] }));
  assert.equal(got.status, 'changed');
  assert.deepEqual(got.warnings.map((w) => w.code), ['unverified_number', 'unverified_number', 'unknown']);
  assert.deepEqual(got.warnings[1].values, ['12', '345']);
  const empty = normalizeOne({ heading: OPEN, status: 'rejected', warnings: [{ code: 'empty_body' }, { code: 'brand_new' }] });
  assert.deepEqual(empty.warnings.map((w) => w.code), ['empty_body', 'unknown']);
  for (const code of ['empty_body', 'suspicious_text', 'link_or_html', 'unclosed_fence']) {
    assert.equal(normalizeOne(changedSection({ warnings: [{ code }] })).status, 'rejected', code);
  }
  assert.equal(describeRewriteWarning({ code: 'unverified_number', values: ['12', '34'] }), '根拠に見当たらない数字: 12、34');
  assert.match(describeRewriteWarning({ code: 'unverified_number', values: [] }), /根拠に見当たらない数字/u);
  assert.match(describeRewriteWarning({ code: 'unsupported_value', values: ['SUE-9'] }), /SUE-9/u);
  assert.equal(describeRewriteWarning({ code: 'suspicious_text' }), '見えない文字や制御文字が含まれている');
  assert.equal(describeRewriteWarning({ code: 'link_or_html' }), '元の本文に無いリンクや HTML が含まれている');
  assert.equal(describeRewriteWarning({ code: 'unclosed_fence' }), 'コードの囲みが閉じていない');
  assert.equal(describeRewriteWarning({ code: 'empty_body' }), '本文が空');
  for (const code of [...contract.warningCodes, 'suspicious_text', 'link_or_html', 'unclosed_fence', 'empty_body', 'invalid_heading', 'invalid_evidence', 'invalid_status', 'invalid_body', 'invalid_reason', 'unknown']) {
    assert.ok(describeRewriteWarning({ code, values: [] }).length > 0, code);
  }
});

test('食い違い: 検証して残し、定型の1行にする', () => {
  const { request } = planFor();
  const data = { ...contract.response, conflicts: [
    { heading: null, summary: 'カードは 800 mm、根拠は 600 mm。\n## 注入', evidence: [1] },
    { heading: MAIN, summary: '', evidence: [1] },
    { heading: MAIN, summary: '範囲外', evidence: [9] },
    'x',
  ] };
  const { conflicts } = normalizeRewriteResponse(data, request);
  assert.equal(conflicts.length, 1);
  assert.deepEqual(conflicts[0].evidence, [1]);
  assert.equal(conflicts[0].heading, null);
  const line = buildConflictOpenItem(conflicts[0]);
  assert.equal(line, '- 要確認（確認済みの根拠との食い違い）: カードは 800 mm、根拠は 600 mm。 ## 注入');
  assert.ok(!line.includes('\n'));
  assert.equal(findRewriteBodyProblem(line), null);
});

test('件数の集計: 反映・反映しない・未確認', () => {
  assert.deepEqual(summarizeRewriteDecisions([MAIN, OPEN, STEPS], { [MAIN]: 'confirm', [OPEN]: 'skip' }), { total: 3, confirmed: 1, skipped: 1, pending: 1 });
  assert.deepEqual(summarizeRewriteDecisions([], {}), { total: 0, confirmed: 0, skipped: 0, pending: 0 });
  assert.deepEqual(summarizeRewriteDecisions([MAIN], { [OPEN]: 'confirm' }), { total: 1, confirmed: 0, skipped: 0, pending: 1 });
});

const proposalOf = (sections, conflicts = []) => normalizeRewriteResponse({ ...contract.response, sections, conflicts }, planFor().request);

test('反映する節: 既定は空。選んだ節だけを返し、食い違いは未確認事項へ足す', () => {
  const proposal = proposalOf([changedSection({ heading: MAIN, body: '新しい主張 12' }), changedSection({ body: '- 新しい未確認 34' })], [{ heading: null, summary: '食い違い', evidence: [1] }]);
  assert.deepEqual(buildAcceptedRewrites(proposal, {}, {}), []);
  assert.deepEqual(buildAcceptedRewrites(proposal, { [OPEN]: 'skip' }, {}), []);
  assert.deepEqual(buildAcceptedRewrites(proposal, { [MAIN]: 'confirm' }, {}), [{ heading: MAIN, body: '新しい主張 12' }]);
  const both = buildAcceptedRewrites(proposal, { [OPEN]: 'confirm' }, { 0: 'confirm' });
  assert.equal(both[0].body, '- 新しい未確認 34\n- 要確認（確認済みの根拠との食い違い）: 食い違い');
  const onlyConflict = buildAcceptedRewrites(proposal, {}, { 0: 'confirm' });
  assert.equal(onlyConflict[0].body, '- SUE-3-17 本文（600 mm 規定の現行文言）\n- 要確認（確認済みの根拠との食い違い）: 食い違い');
});

test('反映する節: 未確認事項が「該当なし」だけなら、その行を残さず食い違いを足す', () => {
  const card = `# t\n\n## ${MAIN}\n\n本文\n\n## ${OPEN}\n\n- （該当なし）\n`;
  const { request } = planFor(card);
  const proposal = normalizeRewriteResponse({ ...contract.response, sections: [], conflicts: [{ heading: null, summary: '食い違い', evidence: [1] }] }, request);
  assert.equal(buildAcceptedRewrites(proposal, {}, { 0: 'confirm' })[0].body, '- 要確認（確認済みの根拠との食い違い）: 食い違い');
});

const accepted = (heading, body) => [{ heading, body }];

test('置換: 選んだ節の本文だけを入れ替え、他の節と見出しは保つ', () => {
  const result = applySectionRewrites(CARD, accepted(MAIN, '新しい主張'), CARD);
  assert.equal(result.applied, 1);
  assert.deepEqual(result.stale, []);
  assert.equal(result.markdown, CARD.replace('据付 SUE-3-17（600 mm 近接）と社内検査 800 mm は別の基準として共存しうる。', '新しい主張'));
  assert.equal(applySectionRewrites(CARD, [], CARD).markdown, CARD);
});

test('置換: 複数の節・見出しの空白・最後の節・末尾改行なしを壊さない', () => {
  const card = `---\nknowledge_id: KH-A\ncard_version: 1\n---\n# t\n\n##  ${MAIN}  \n本文A\n\n## ${OPEN}\n- 未確認`;
  const result = applySectionRewrites(card, [{ heading: OPEN, body: '- 新しい未確認' }, { heading: MAIN, body: '新A\n\n- 点' }], card);
  assert.equal(result.applied, 2);
  assert.equal(result.markdown, `---\nknowledge_id: KH-A\ncard_version: 1\n---\n# t\n\n##  ${MAIN}  \n新A\n\n- 点\n\n## ${OPEN}\n- 新しい未確認`);
});

test('置換: CRLF を保つ', () => {
  const crlf = CARD.replaceAll('\n', '\r\n');
  const result = applySectionRewrites(crlf, accepted(MAIN, '1行目\n2行目'), crlf);
  assert.ok(result.markdown.includes(`## ${MAIN}\r\n\r\n1行目\r\n2行目\r\n\r\n## KB確認`));
  assert.ok(!/[^\r]\n/u.test(result.markdown), 'LF だけの改行が混ざらない');
});

test('置換: コードフェンス内の ## を節の区切りにしない', () => {
  const card = `# t\n\n## ${MAIN}\n\n\`\`\`\n## ${OPEN}\n\`\`\`\n旧\n\n## ${OPEN}\n\n- 旧未確認\n`;
  const result = applySectionRewrites(card, accepted(OPEN, '- 新'), card);
  assert.equal(result.markdown, `# t\n\n## ${MAIN}\n\n\`\`\`\n## ${OPEN}\n\`\`\`\n旧\n\n## ${OPEN}\n\n- 新\n`);
});

test('置換: 案を作ったあとに節が編集されていたら、その節は反映しない', () => {
  const edited = CARD.replace('別の基準として共存しうる。', '別の基準として共存しうる。人が足した一文。');
  const result = applySectionRewrites(edited, [{ heading: MAIN, body: '新しい主張' }, { heading: OPEN, body: '- 新' }], CARD);
  assert.deepEqual(result.stale, [MAIN]);
  assert.equal(result.applied, 1);
  assert.ok(result.markdown.includes('人が足した一文。'));
  assert.ok(result.markdown.includes('- 新'));
  const gone = applySectionRewrites(CARD.replace(`## ${OPEN}`, '## 別名'), accepted(OPEN, '- 新'), CARD);
  assert.deepEqual(gone.stale, [OPEN]);
  assert.equal(gone.applied, 0);
  assert.equal(gone.markdown, CARD.replace(`## ${OPEN}`, '## 別名'));
});

test('置換: 他の節（追記など）が変わっても、対象の節が同じなら反映できる', () => {
  const changedElsewhere = CARD.replace('（未実施）', '（実施済み）');
  const result = applySectionRewrites(changedElsewhere, accepted(MAIN, '新'), CARD);
  assert.equal(result.applied, 1);
  assert.ok(result.markdown.includes('（実施済み）'));
});

test('置換: 構造を壊す本文は拒否し、不正な入力は TypeError', () => {
  assert.throws(() => applySectionRewrites(CARD, accepted(MAIN, '本文\n## 別の節'), CARD), TypeError);
  assert.throws(() => applySectionRewrites(CARD, accepted(MAIN, '```\n開いたまま'), CARD), TypeError);
  assert.throws(() => applySectionRewrites(null, [], CARD), TypeError);
  assert.throws(() => applySectionRewrites(CARD, 'x', CARD), TypeError);
  assert.throws(() => applySectionRewrites(CARD, accepted(MAIN, '新'), 5), TypeError);
});

test('既存の追記と合成しても壊れず、節の書き換えと追記が1つの差分に入る', () => {
  const proposal = {
    question: '質問', checkedOn: '2026-11-14',
    markdown: buildCheckProposal({ question: '質問', technical: answerFor('normal'), checkedOn: '2026-11-14' }),
  };
  const result = composeCardEdits(CARD, { rewrites: accepted(MAIN, '新しい主張'), expectedBody: CARD, proposals: [proposal] });
  assert.deepEqual([result.rewritten, result.applied, result.skipped, result.stale], [1, 1, 0, []]);
  assert.ok(result.markdown.includes(`## ${MAIN}\n\n新しい主張\n`));
  assert.ok(result.markdown.includes('### KB照合（確認日 2026-11-14）'));
  assert.ok(result.markdown.includes('（未実施）') === false, '追記の節の書き置きは追記で置き換わる');
  assert.ok(result.markdown.includes(`## ${OPEN}\n\n- SUE-3-17 本文`));
  const onlyRewrite = composeCardEdits(CARD, { rewrites: accepted(MAIN, '新'), expectedBody: CARD, proposals: [] });
  assert.deepEqual([onlyRewrite.rewritten, onlyRewrite.applied], [1, 0]);
  const onlyAppend = composeCardEdits(CARD, { rewrites: [], expectedBody: CARD, proposals: [proposal] });
  assert.deepEqual([onlyAppend.rewritten, onlyAppend.applied], [0, 1]);
});

test('実カードの本文で、3つの節を選び別の節を変えずに置換できる', () => {
  const file = readFileSync(new URL('../../knowledge/cards/practice-guides/KH-PIT-TRAP-POSITION-394.md', import.meta.url), 'utf8');
  const { targets, context } = selectRewriteSections(file);
  assert.deepEqual(targets.map((s) => s.heading), [MAIN, STEPS, OPEN]);
  assert.ok(context.length > 0);
  const result = applySectionRewrites(file, accepted(STEPS, '1. 新手順'), file);
  assert.equal(result.applied, 1);
  const before = selectRewriteSections(file).targets;
  const after = selectRewriteSections(result.markdown).targets;
  assert.equal(after[0].body, before[0].body);
  assert.equal(after[2].body, before[2].body);
  assert.equal(after[1].body, '1. 新手順');
  assert.ok(result.markdown.startsWith(file.slice(0, file.indexOf('# ピットタラップ'))), 'frontmatter は変わらない');
});
