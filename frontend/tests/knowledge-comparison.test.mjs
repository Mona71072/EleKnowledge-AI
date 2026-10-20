import assert from 'node:assert/strict';
import test from 'node:test';

import { buildComparisonNote } from '../src/lib/knowledge-comparison.mjs';

const QUERY = '作業床の端部に必要な措置';

function technical(overrides = {}) {
  return {
    mode: 'normal',
    query: QUERY,
    content: '手すりの設置条件を確認する。',
    responseType: 'pages',
    sessionId: 'session_technical_1',
    messageId: 'message_technical_1',
    receivedAt: '2026-10-20T01:00:00.000Z',
    responseTimestamp: '2026-10-20T00:59:58.000Z',
    sourceDocuments: [{ documentName: '据付要領.pdf', sourceUri: 's3://technical-kb/docs/install.pdf', pageNumber: 12 }],
    pageCandidates: [],
    clarifyQuestions: [],
    ...overrides,
  };
}

function law(overrides = {}) {
  const sourceUrl = 'https://laws.e-gov.go.jp/law/347M50002000032/20240401_506M60000002012#Mp-At_518';
  return {
    mode: 'law',
    query: QUERY,
    content: '事業者は作業床の端に墜落防止措置を講じる。',
    responseType: 'pages',
    sessionId: 'session_law_1',
    messageId: 'message_law_1',
    receivedAt: '2026-10-20T01:00:01.000Z',
    sourceDocuments: [{
      documentName: '労働安全衛生規則 第518条',
      sourceUri: sourceUrl,
      lawCitation: {
        lawId: '347M50002000032',
        lawTitle: '労働安全衛生規則',
        lawNumber: '昭和四十七年労働省令第三十二号',
        effectiveDate: '2025-04-01',
        provisionType: 'main',
        provisionReference: '第518条',
        sourceUrl,
      },
    }],
    pageCandidates: [],
    clarifyQuestions: [],
    ...overrides,
  };
}

function assessment(overrides = {}) {
  return {
    status: 'unresolved',
    findings: '対象条件の読み方は概ね共通している。',
    applicability: '高所で作業床端部が開放されている場合。',
    unresolvedPoints: '既設設備の具体的な構造条件を確認する。',
    ...overrides,
  };
}

test('creates a deterministic unapproved comparison note with both answers, sources, and trace metadata', () => {
  const input = { technical: technical(), law: law(), assessment: assessment() };
  const before = JSON.stringify(input);
  const note = buildComparisonNote(input);

  assert.match(note, /照合まとめ.*未承認/);
  assert.match(note, /判断保留/);
  assert.match(note, /対象条件の読み方は概ね共通している/);
  assert.match(note, /高所で作業床端部が開放されている場合/);
  assert.match(note, /既設設備の具体的な構造条件を確認する/);
  assert.match(note, /手すりの設置条件を確認する/);
  assert.match(note, /事業者は作業床の端に墜落防止措置を講じる/);
  assert.match(note, /s3:\/\/technical-kb\/docs\/install\.pdf/);
  assert.match(note, /20240401_506M60000002012#Mp-At_518/);
  assert.match(note, /session\\_technical\\_1/);
  assert.match(note, /message\\_law\\_1/);
  assert.equal(note, buildComparisonNote(input));
  assert.equal(JSON.stringify(input), before);
});

test('renders each supported assessment status with its own Japanese label', () => {
  const labels = new Map([
    ['consistent', '一致している'],
    ['conditions_differ', '条件が違う'],
    ['conflict', '食い違いあり'],
    ['unresolved', '判断保留'],
  ]);
  for (const [status, label] of labels) {
    const input = {
      technical: technical(),
      law: law(),
      assessment: assessment({ status, unresolvedPoints: status === 'conflict' || status === 'unresolved' ? '確認先に問い合わせる。' : '' }),
    };
    assert.match(buildComparisonNote(input), new RegExp(label));
  }
});

test('requires valid one-per-mode pages answers for the same explicit question and evidence links', () => {
  const invalidPairs = [
    { technical: null, law: law() },
    { technical: technical(), law: null },
    { technical: technical({ mode: 'law' }), law: law() },
    { technical: technical(), law: law({ mode: 'normal' }) },
    { technical: technical(), law: law({ query: '別の質問' }) },
    { technical: technical({ responseType: 'not_found' }), law: law() },
    { technical: technical(), law: law({ responseType: 'clarify' }) },
    { technical: technical({ sourceDocuments: [] }), law: law() },
    { technical: technical({ sourceDocuments: [{ documentName: '法令だけ', lawCitation: law().sourceDocuments[0].lawCitation }] }), law: law() },
    { technical: technical(), law: law({ sourceDocuments: [{ documentName: 'S3だけ', sourceUri: 's3://technical-kb/docs/manual.pdf' }] }) },
    { technical: technical(), law: law({ sourceDocuments: [{ documentName: '不正法令', lawCitation: { ...law().sourceDocuments[0].lawCitation, sourceUrl: 'https://attacker.example/law/fake' } }] }) },
  ];
  for (const pair of invalidPairs) {
    assert.throws(() => buildComparisonNote({ ...pair, assessment: assessment() }), (error) => error.code === 'validation');
  }
});

test('validates required assessment text, status, NULs, and 4000-character limits', () => {
  for (const invalidAssessment of [
    assessment({ status: 'unknown' }),
    assessment({ findings: '' }),
    assessment({ findings: '   ' }),
    assessment({ findings: 42 }),
    assessment({ findings: 'bad\0text' }),
    assessment({ findings: 'x'.repeat(4001) }),
    assessment({ applicability: '' }),
    assessment({ applicability: 'x'.repeat(4001) }),
    assessment({ applicability: 'bad\0text' }),
    assessment({ status: 'conflict', unresolvedPoints: '' }),
    assessment({ status: 'unresolved', unresolvedPoints: '   ' }),
    assessment({ status: 'conflict', unresolvedPoints: 'x'.repeat(4001) }),
    assessment({ status: 'unresolved', unresolvedPoints: 'bad\0text' }),
    assessment({ status: 'consistent', unresolvedPoints: 42 }),
  ]) {
    assert.throws(() => buildComparisonNote({ technical: technical(), law: law(), assessment: invalidAssessment }), (error) => error.code === 'validation');
  }
  assert.doesNotThrow(() => buildComparisonNote({
    technical: technical(),
    law: law(),
    assessment: assessment({ status: 'consistent', findings: '😀'.repeat(4_000), unresolvedPoints: '' }),
  }));
  assert.throws(() => buildComparisonNote({
    technical: technical(),
    law: law(),
    assessment: assessment({ status: 'consistent', findings: '😀'.repeat(4_001), unresolvedPoints: '' }),
  }), (error) => error.code === 'validation');
});

test('preserves hostile user text and answer text inside escaped Markdown or dynamically sized code fences', () => {
  const hostile = '# 見出し\n<script>alert(1)</script>\n```\n## 偽の節';
  const input = {
    technical: technical({ content: hostile }),
    law: law({ content: hostile }),
    assessment: assessment({ findings: hostile, applicability: hostile, unresolvedPoints: hostile }),
  };
  const note = buildComparisonNote(input);
  assert.ok(note.includes(hostile));
  assert.ok(note.includes('<script>alert(1)</script>'));
  assert.ok(note.includes('````'));
  assert.ok(note.includes('````text\n' + hostile + '\n````'));
  assert.ok(note.includes('````\n' + hostile + '\n````'));
});

test('marks optional unresolved items as unfilled rather than claiming none or resolved', () => {
  const note = buildComparisonNote({
    technical: technical(),
    law: law(),
    assessment: assessment({ status: 'consistent', unresolvedPoints: '' }),
  });
  assert.match(note, /未記入/);
  assert.doesNotMatch(note, /確認事項なし|解決済み/);
});

test('rejects missing or malformed outer assessment input', () => {
  for (const input of [
    null,
    {},
    { technical: technical(), law: law() },
    { technical: technical(), law: law(), assessment: null },
  ]) {
    assert.throws(() => buildComparisonNote(input), (error) => error.code === 'validation');
  }
});
