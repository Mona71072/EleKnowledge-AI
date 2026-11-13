import assert from 'node:assert/strict';
import test from 'node:test';
import {
  MAX_COMMENT_ADDITION_CHARS,
  MAX_REVIEW_COMMENT_CHARS,
  buildCommentAddition,
  buildCommentResearchQuery,
  buildConfirmedCommentBody,
  findCommentSection,
  listCommentSections,
} from '../src/lib/knowledge-comment-review.mjs';

const CHECKED_ON = '2026-11-14';
const answer = (overrides = {}) => ({
  mode: 'normal',
  query: 'query',
  content: '条件を確認し、固定状態を記録する。',
  responseType: 'pages',
  sessionId: 's1',
  messageId: 'm1',
  receivedAt: '2026-11-13T00:00:00.000Z',
  sourceDocuments: [{ documentName: '施工要領.pdf', pageNumber: 12, sourceUri: 's3://technical-kb/docs/install.pdf' }],
  pageCandidates: [],
  clarifyQuestions: [],
  ...overrides,
});

test('lists H2 sections outside fenced blocks with stable unique IDs and one-based lines', () => {
  const body = '# Card\n\n## 確認\n本文\n```md\n## fake\n```\n## 確認\n続き\n';
  const sections = listCommentSections(body);
  assert.deepEqual(sections.map(({ label, line }) => ({ label, line })), [
    { label: '確認', line: 3 },
    { label: '確認', line: 8 },
  ]);
  assert.notEqual(sections[0].id, sections[1].id);
  assert.deepEqual(listCommentSections(body), sections);
});

test('uses a body fallback for H1-only cards', () => {
  assert.deepEqual(listCommentSections('# Title\n\n本文'), [{ id: 'body', label: '本文全体', line: 1 }]);
});

test('refuses ambiguous duplicate headings even when their generated IDs differ', () => {
  const body = '# Title\n\n## 確認\nFirst\n\n## 確認\nSecond';
  const sections = listCommentSections(body);
  assert.notEqual(sections[0].id, sections[1].id);
  assert.equal(findCommentSection(body, sections[0].id), undefined);
  assert.equal(findCommentSection(body, sections[0].id, '確認'), undefined);
  assert.throws(() => buildCommentAddition(body, sections[0].id, answer()), /複数/u);
});

test('builds a bounded research prompt using only title, section, and comment', () => {
  const query = buildCommentResearchQuery({
    title: 'カード題名', sectionLabel: '確認手順', comment: '適用条件が不足',
    body: 'THIS MUST NEVER BE INCLUDED',
  });
  assert.match(query, /資料だけを確認/u);
  assert.match(query, /技術KBと法令KB/u);
  assert.doesNotMatch(query, /OneNote|Lists/u);
  assert.match(query, /条件/u);
  assert.match(query, /不足/u);
  assert.doesNotMatch(query, /THIS MUST NEVER BE INCLUDED/u);
  assert.ok(query.length <= 2_000);
  assert.equal(MAX_REVIEW_COMMENT_CHARS, 900);
  const bounded = buildCommentResearchQuery({ title: 't', sectionLabel: 's', comment: 'c'.repeat(1_000) });
  assert.equal(bounded.split('確認コメント: ')[1], 'c'.repeat(MAX_REVIEW_COMMENT_CHARS));
  assert.ok(buildCommentResearchQuery({ title: 't'.repeat(3000), sectionLabel: 's', comment: 'c' }).length <= 2_000);
});

test('appends escaped, source-linked research with an administrator-confirmation line at selected section end and retains other sections and CRLF', () => {
  const body = '# Card\r\n\r\n## First\r\nKeep first\r\n\r\n## Second\r\nKeep second\r\n\r\n## Third\r\nKeep third\r\n';
  const sections = listCommentSections(body);
  const result = buildCommentAddition(body, sections[1].id, answer(), '### injection\n<script>alert(1)</script>', CHECKED_ON);
  assert.match(result, /Keep second\r\n\r\n\\#\\#\\# injection/u);
  assert.doesNotMatch(result, /原資料未確認|AI追記案|反映してください/u);
  assert.match(result, /\r\n確認: 管理者が出典を確認（2026-11-14）\r\n\r\n## Third/u);
  assert.match(result, /\\#\\#\\# injection\r\n&lt;script&gt;alert\\\(1\\\)&lt;\/script&gt;/u);
  assert.match(result, /施工要領\\\.pdf.*p\.12/u);
  assert.match(result, /\]\(<\/doc\?uri=/u);
  assert.match(result, /## Third\r\nKeep third/u);
  assert.doesNotMatch(result, /(?<!\r)\n/u);
});

test('preserves paragraph breaks in a multiline draft and separates an immediately following heading', () => {
  const body = '# Card\n\n## Section\nOriginal text\n## Next\nNext content';
  const [section] = listCommentSections(body);
  const result = buildCommentAddition(body, section.id, answer(), '第1段落\n\n## 追加見出しではない\n第2段落', CHECKED_ON);
  assert.match(result, /第1段落\n\n\\#\\# 追加見出しではない\n第2段落/u);
  assert.match(result, /## Next\nNext content/u);
  assert.ok(result.indexOf('第2段落') < result.indexOf('## Next'));
});

test('adds a verified law effective date and safely wraps its official source link', () => {
  const body = '# Card\n\n## Law';
  const [section] = listCommentSections(body);
  const lawCitation = {
    lawId: '347M50002000032', lawTitle: '労働安全衛生規則', lawNumber: '昭和四十七年労働省令第三十二号',
    effectiveDate: '2025-04-01', provisionType: 'main', provisionReference: '第518条',
    sourceUrl: 'https://laws.e-gov.go.jp/law/347M50002000032',
  };
  const lawAnswer = answer({
    mode: 'law',
    sourceDocuments: [{ documentName: lawCitation.lawTitle, lawCitation, sourceUri: lawCitation.sourceUrl }],
  });
  const result = buildCommentAddition(body, section.id, lawAnswer, undefined, CHECKED_ON);
  assert.match(result, /労働安全衛生規則.*施行日 2025-04-01/u);
  assert.match(result, /\]\(<https:\/\/laws\.e-gov\.go\.jp\/law\/347M50002000032>\)/u);
});

test('caps proposal text by Unicode code points and limits listed sources', () => {
  assert.equal(MAX_COMMENT_ADDITION_CHARS, 6_000);
  const body = '# Card\n\n## Section';
  const [section] = listCommentSections(body);
  assert.throws(() => buildCommentAddition(body, section.id, answer(), '😀'.repeat(6_001), CHECKED_ON), /6,000/u);
  const manySources = Array.from({ length: 12 }, (_, index) => ({
    documentName: `source-${index}.pdf`, sourceUri: `s3://technical-kb/docs/${index}.pdf`, pageNumber: index + 1,
  }));
  const result = buildCommentAddition(body, section.id, answer({ sourceDocuments: manySources }), undefined, CHECKED_ON);
  assert.match(result, /source-7\\\.pdf/u);
  assert.doesNotMatch(result, /source-8\\\.pdf/u);
});

test('rejects missing sections, non-pages answers, missing answer text, and answers without safe sources', () => {
  const body = '# Card\n\n## Section\nBody';
  const section = listCommentSections(body)[0];
  assert.throws(() => buildCommentAddition(body, 'missing', answer()), /節/u);
  assert.throws(() => buildCommentAddition(body, section.id, answer({ responseType: 'clarify' })), /回答/u);
  assert.throws(() => buildCommentAddition(body, section.id, answer({ content: '  ' })), /回答/u);
  assert.throws(() => buildCommentAddition(body, section.id, answer({ sourceDocuments: [] })), /出典/u);
  assert.throws(() => buildCommentAddition(body, section.id, answer({
    sourceDocuments: [{ documentName: 'bad', sourceUri: 'javascript:alert(1)' }],
  })), /出典/u);
});

test('rejects a target section inside an unclosed code fence', () => {
  const body = '# Card\n\n## Target\n```md\ncontents';
  const section = listCommentSections(body)[0];
  assert.throws(() => buildCommentAddition(body, section.id, answer(), undefined, CHECKED_ON), /フェンス/u);
});

test('確認日は実在する YYYY-MM-DD でなければ追記を作らず、出典付きの強制は維持する', () => {
  const body = '# Card\n\n## Section\nBody';
  const [section] = listCommentSections(body);
  for (const bad of [undefined, '', '2026-13-01', '2026-02-30', '令和8年', '2026/11/14']) {
    assert.throws(() => buildCommentAddition(body, section.id, answer(), undefined, bad), /確認日/u);
  }
  const result = buildCommentAddition(body, section.id, answer(), undefined, CHECKED_ON);
  assert.match(result, /根拠資料:\n- \[施工要領/u);
  assert.match(result, /\n確認: 管理者が出典を確認（2026-11-14）$/u);
  assert.throws(() => buildCommentAddition(body, section.id, answer({ sourceDocuments: [] }), undefined, CHECKED_ON), /出典/u);
});

test('管理者が「確認して追記する」を選んだ追記案だけが本文に入る。未確認・追記しないは入らない', () => {
  const body = '# Card\n\n## Section\nBody\n';
  const [section] = listCommentSections(body);
  const technical = answer({ content: '技術KBの内容。' });
  const law = answer({ mode: 'law', content: '法令KBの内容。', receivedAt: '2026-11-15T03:00:00.000Z',
    sourceDocuments: [{ documentName: '労働安全衛生規則', lawCitation: { lawId: '347M50002000032', lawTitle: '労働安全衛生規則', lawNumber: '昭和四十七年労働省令第三十二号', effectiveDate: '2025-04-01', provisionType: 'main', provisionReference: '第518条', sourceUrl: 'https://laws.e-gov.go.jp/law/347M50002000032' }, sourceUri: 'https://laws.e-gov.go.jp/law/347M50002000032' }] });
  const entry = (source, decision, text = source.content) => ({ answer: source, text, decision });
  assert.deepEqual(buildConfirmedCommentBody(body, section.id, [entry(technical, undefined), entry(law, undefined)]), { body, applied: 0 });
  assert.deepEqual(buildConfirmedCommentBody(body, section.id, [entry(technical, 'skip'), entry(law, 'skip')]), { body, applied: 0 });
  const only = buildConfirmedCommentBody(body, section.id, [entry(technical, 'confirm', '編集した技術案。'), entry(law, 'skip')]);
  assert.equal(only.applied, 1);
  assert.match(only.body, /編集した技術案/u);
  assert.doesNotMatch(only.body, /法令KBの内容/u);
  assert.match(only.body, /確認: 管理者が出典を確認（2026-11-13）/u);
  const both = buildConfirmedCommentBody(body, section.id, [entry(technical, 'confirm'), entry(law, 'confirm')]);
  assert.equal(both.applied, 2);
  assert.ok(both.body.indexOf('技術KBの内容') < both.body.indexOf('法令KBの内容'));
  assert.doesNotMatch(both.body, /原資料未確認|AI追記案/u);
});
