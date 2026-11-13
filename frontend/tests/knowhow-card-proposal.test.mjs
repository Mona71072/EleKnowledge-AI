import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import test from 'node:test';
import { parseKnowledgeMarkdown } from '../src/lib/knowledge-workbench.mjs';
import { splitKnowhowCardBody } from '../src/lib/knowhow-card-view.mjs';
import {
  PROPOSAL_ANSWER_HEAD_CHARS,
  applyCheckProposals,
  buildCheckProposal,
  classifyCheckAnswer,
  classifyProposalEvidence,
  summarizeCheckDecisions,
  formatCheckDate,
} from '../src/lib/knowhow-card-proposal.mjs';

const answer = (mode, overrides = {}) => ({
  mode,
  query: 'ピットタラップの基準は？',
  content: 'ピット点検タラップは三方枠から 600 mm 以下に近づけて取り付けます。',
  responseType: 'pages',
  sessionId: 's-1',
  messageId: 'm-1',
  receivedAt: '2026-11-13T01:00:00.000Z',
  sourceDocuments: mode === 'law'
    ? [{ documentName: '建築基準法施行令', lawCitation: { lawId: '325CO0000000338', lawTitle: '建築基準法施行令', lawNumber: '昭和二十五年政令第三百三十八号', effectiveDate: '2025-12-01', provisionType: 'Article', provisionReference: '第百二十九条の七', sourceUrl: 'https://laws.e-gov.go.jp/law/325CO0000000338' } }]
    : [{ documentName: 'SUE-3-17.pdf', title: 'ピット点検タラップ', pageNumber: 4, sourceUri: 's3://technical-kb/SUE-3-17.pdf' }, { documentName: 'SUE-3-17.pdf', pageNumber: 5, sourceUri: 's3://technical-kb/SUE-3-17.pdf' }],
  pageCandidates: [],
  clarifyQuestions: [],
  ...overrides,
});
const notFound = (mode) => answer(mode, { responseType: 'not_found', content: '該当する情報が見つかりませんでした。', sourceDocuments: [] });
const proposal = (question = 'ピットタラップの基準は？', checkedOn = '2026-11-13') => ({
  question,
  checkedOn,
  markdown: buildCheckProposal({ question, technical: answer('normal'), law: notFound('law'), checkedOn }),
});
const CARD = [
  '# 題名',
  '',
  '## 統合した回答・ノウハウ',
  '',
  '本文の主張。',
  '',
  '## KB確認に基づく追記',
  '',
  '（該当なし）',
  '',
  '## 正式資料・元情報',
  '',
  '| 種別 | 参照 |',
  '',
  '## 未確認事項',
  '',
  '- なし。',
  '',
].join('\n');

test('「見つからない」は応答の responseType で判定し、無ければ出典0件で判定する', () => {
  assert.equal(classifyCheckAnswer(answer('normal')), 'found');
  assert.equal(classifyCheckAnswer(notFound('normal')), 'not_found');
  assert.equal(classifyCheckAnswer(answer('normal', { responseType: 'clarify', clarifyQuestions: ['機種は？'] })), 'clarify');
  assert.equal(classifyCheckAnswer(answer('normal', { sourceDocuments: [] })), 'no_source');
  assert.equal(classifyCheckAnswer(answer('normal', { content: '   ' })), 'no_source');
  assert.equal(classifyCheckAnswer(answer('normal', { sourceDocuments: [{ documentName: 'URL未検証.pdf', sourceUri: 'https://attacker.example/doc.pdf' }] })), 'no_source');
  assert.equal(classifyCheckAnswer(answer('law', { sourceDocuments: [{ documentName: 'URL未検証', lawCitation: { ...answer('law').sourceDocuments[0].lawCitation, sourceUrl: 'https://attacker.example/law' } }] })), 'no_source');
  assert.equal(classifyCheckAnswer(null), 'not_found');
});

test('追記案は、質問・確認日・技術KBの要点と出典・法令KBの要点と出典を定型で並べる', () => {
  const markdown = buildCheckProposal({ question: 'ピットタラップの基準は？', technical: answer('normal'), law: answer('law'), checkedOn: '2026-11-13' });
  assert.match(markdown, /^### KB照合（確認日 2026-11-13）\n\n- 質問: ピットタラップの基準は？\n- 確認: 管理者が出典を確認（2026-11-13）\n/u);
  assert.doesNotMatch(markdown, /未承認|原資料未確認/u);
  assert.match(markdown, /#### 技術KBの要点\n\n```text\nピット点検タラップは三方枠から 600 mm 以下に近づけて取り付けます。\n```/u);
  assert.match(markdown, /#### 技術KBの出典\n\n- `SUE-3-17\.pdf` p\.4\n- `SUE-3-17\.pdf` p\.5/u);
  assert.match(markdown, /#### 法令KBの出典\n\n- 建築基準法施行令（昭和二十五年政令第三百三十八号） 第百二十九条の七 — \[公式法令\]\(https:\/\/laws\.e-gov\.go\.jp\/law\/325CO0000000338\)/u);
  assert.ok(!markdown.endsWith('\n'));
});

test('見つからなかった側は、その旨を確認した記録として書き、出典の節は作らない', () => {
  const markdown = proposal().markdown;
  assert.match(markdown, /#### 法令KBの要点\n\n法令KBに該当資料なし（確認日時点）。未確認事項の解消ではなく、確認した記録です。/u);
  assert.doesNotMatch(markdown, /法令KBの出典/u);
  const clarify = buildCheckProposal({ question: 'q', technical: answer('normal', { responseType: 'clarify', clarifyQuestions: ['機種は？'], sourceDocuments: [] }), checkedOn: '2026-11-13' });
  assert.match(clarify, /技術KBは条件の聞き返しを返し、回答は得られませんでした。/u);
  assert.match(clarify, /#### 法令KBの要点\n\nこの質問では照合していません。/u);
  const noSource = buildCheckProposal({ question: 'q', technical: answer('normal', { sourceDocuments: [] }), checkedOn: '2026-11-13' });
  assert.match(noSource, /技術KBは回答を返しましたが、出典がありません。根拠としては扱えません。/u);
});

test('要点は回答の先頭だけを使い、AI に要約させない。長い回答は文の切れ目で切る', () => {
  const sentence = 'これは回答の一文です。';
  const long = sentence.repeat(80);
  const markdown = buildCheckProposal({ question: 'q', technical: answer('normal', { content: long }), checkedOn: '2026-11-13' });
  const head = /```text\n([\s\S]*?)\n```/u.exec(markdown)[1];
  assert.ok(head.startsWith(sentence));
  assert.ok(Array.from(head).length <= PROPOSAL_ANSWER_HEAD_CHARS + 10);
  assert.ok(head.endsWith('。\n…（以下略）'));
  assert.ok(long.startsWith(head.replace('\n…（以下略）', '')));
});

test('回答や質問に Markdown の記号や改行があっても、追記案の構造を壊さない', () => {
  const markdown = buildCheckProposal({
    question: '質問の1行目\n## 2行目',
    technical: answer('normal', { content: '```\n## 見出しのふり\n```\n続き', sourceDocuments: [{ documentName: 'a`b.pdf', sourceUri: 's3://technical-kb/a.pdf' }] }),
    checkedOn: '2026-11-13',
  });
  assert.match(markdown, /- 質問: 質問の1行目 \\#\\# 2行目\n/u);
  assert.match(markdown, /````text\n```\n## 見出しのふり\n```\n続き\n````/u);
  assert.match(markdown, /- `` a`b\.pdf ``/u);
  const applied = applyCheckProposals(CARD, [{ question: '質問の1行目\n## 2行目', checkedOn: '2026-11-13', markdown }]).markdown;
  const headings = applied.split('\n').filter((line) => /^## /u.test(line));
  assert.deepEqual(splitKnowhowCardBody(applied).editorSections.map((section) => section.heading), ['KB確認に基づく追記', '正式資料・元情報']);
  assert.ok(headings.includes('## 見出しのふり'), 'フェンス内の行は残るが節としては数えない');
});

test('法令出典と質問のMarkdown記号をエスケープし、同じ質問・日付の二重防止を保つ', () => {
  const question = '戸開 *基準* [確認](javascript:alert(1))';
  const law = answer('law', { sourceDocuments: [{
    documentName: '法令出典',
    lawCitation: {
      ...answer('law').sourceDocuments[0].lawCitation,
      lawTitle: '[危険](javascript:alert(1)) *法令*',
      lawNumber: '第1号 [参照](javascript:x)',
      provisionReference: '第1条 *本文*',
    },
  }] });
  const markdown = buildCheckProposal({ question, technical: answer('normal'), law, checkedOn: '2026-11-13' });
  assert.ok(markdown.includes('- 質問: 戸開 \\*基準\\* \\[確認\\]\\(javascript:alert\\(1\\)\\)'));
  assert.ok(markdown.includes('\\[危険\\]\\(javascript:alert\\(1\\)\\) \\*法令\\*（第1号 \\[参照\\]\\(javascript:x\\)） 第1条 \\*本文\\* — [公式法令](https://laws.e-gov.go.jp/law/325CO0000000338)'));
  const first = applyCheckProposals(CARD, [{ question, checkedOn: '2026-11-13', markdown }]);
  const repeated = applyCheckProposals(first.markdown, [{ question, checkedOn: '2026-11-13', markdown }]);
  assert.deepEqual([first.applied, repeated.applied, repeated.skipped], [1, 0, 1]);
});

test('未閉鎖コードフェンス内へ追記しない', () => {
  const unclosed = `${CARD.replace('## 正式資料・元情報', '## 正式資料・元情報').replace('本文の主張。', '本文の主張。\n\n```text\n閉じていないコード')}`;
  assert.throws(() => applyCheckProposals(unclosed, [proposal()]), /閉じていないコードフェンス/u);
});

test('入力が不正なら作らない', () => {
  assert.throws(() => buildCheckProposal({ question: ' ', technical: answer('normal'), checkedOn: '2026-11-13' }), TypeError);
  assert.throws(() => buildCheckProposal({ question: 'q', technical: answer('normal'), checkedOn: '2026/11/13' }), TypeError);
  assert.throws(() => buildCheckProposal({ question: 'q', checkedOn: '2026-11-13' }), TypeError);
  assert.throws(() => buildCheckProposal({ question: 'q', technical: answer('law'), checkedOn: '2026-11-13' }), TypeError);
  assert.throws(() => buildCheckProposal({ question: 'q', technical: answer('normal'), checkedOn: '2026-13-40' }), TypeError);
});

test('確認日は手元の日付で YYYY-MM-DD', () => {
  assert.equal(formatCheckDate(new Date(2026, 10, 3, 23, 59)), '2026-11-03');
});

test('確認件数は、追記・追記しない・未確認（未選択）に分けて数える', () => {
  assert.deepEqual(
    summarizeCheckDecisions(['a', 'b', 'c', 'd', 'e'], { a: 'confirm', b: 'confirm', c: 'skip', z: 'confirm' }),
    { total: 5, confirmed: 2, skipped: 1, pending: 2 },
  );
  assert.deepEqual(summarizeCheckDecisions(['a'], {}), { total: 1, confirmed: 0, skipped: 0, pending: 1 });
});

const KB = '## KB確認に基づく追記';
const kbBody = (markdown) => splitKnowhowCardBody(markdown).editorSections.find((section) => section.heading.startsWith('KB確認に基づく追記'))?.body;

test('出典つきなら「出典を確認」、照合した全レーンが「該当なし」なら「該当資料なし」の確認記録にする（聞き返し・出典なしは別の記録）', () => {
  assert.equal(classifyProposalEvidence({ technical: answer('normal'), law: notFound('law') }), 'sourced');
  assert.equal(classifyProposalEvidence({ technical: notFound('normal') }), 'not_found');
  assert.equal(classifyProposalEvidence({ technical: answer('normal', { responseType: 'clarify', sourceDocuments: [] }) }), 'no_source');
  assert.equal(classifyProposalEvidence({ technical: answer('normal', { sourceDocuments: [] }) }), 'no_source');
  const record = buildCheckProposal({ question: 'q', technical: notFound('normal'), checkedOn: '2026-11-13' });
  assert.match(record, /- 確認: KB に該当資料なし（2026-11-13）。管理者が確認した記録で、未確認事項の解消ではありません\n/u);
  assert.doesNotMatch(record, /出典を確認/u);
});

test('追記案の採用が無ければ何も入らない（未確認・追記しないはカードに入れない）', () => {
  assert.deepEqual(applyCheckProposals(CARD, []), { markdown: CARD, applied: 0, skipped: 0 });
  assert.doesNotMatch(applyCheckProposals(CARD, [proposal()]).markdown, /KB照合メモ（原資料未確認）/u);
});

test('「（該当なし）」だけの節は置き換え、確認した追記を入れる', () => {
  const result = applyCheckProposals(CARD, [proposal()]);
  assert.equal(result.applied, 1);
  assert.match(result.markdown, /## KB確認に基づく追記\n\n### KB照合（確認日 2026-11-13）\n/u);
  assert.doesNotMatch(result.markdown, /（該当なし）/u);
  assert.doesNotMatch(result.markdown, /KB照合メモ/u);
  assert.match(result.markdown, /確認した記録です。\n\n## 正式資料・元情報\n/u);
  assert.ok(result.markdown.startsWith('# 題名\n\n## 統合した回答・ノウハウ\n\n本文の主張。\n\n## KB確認に基づく追記\n'));
  assert.ok(result.markdown.endsWith('## 未確認事項\n\n- なし。\n'));
});

test('情報の無い書き置きは置き換え、見出しの注記も外す', () => {
  for (const placeholder of ['（Lists のみ）', '（なし）', '(該当なし)', '（該当なし — Lists のみ）', '（該当 KB なし）', '（未実施）', '（なし。）']) {
    const result = applyCheckProposals(CARD.replace('（該当なし）', placeholder), [proposal()]);
    assert.ok(!result.markdown.includes(placeholder), placeholder);
    assert.match(result.markdown, /## KB確認に基づく追記\n\n### KB照合/u, placeholder);
  }
  const suffixed = CARD.replace('## KB確認に基づく追記\n\n（該当なし）', '## KB確認に基づく追記（該当なし）\n');
  const result = applyCheckProposals(suffixed, [proposal()]);
  assert.match(result.markdown, /\n## KB確認に基づく追記\n\n### KB照合/u);
  assert.doesNotMatch(result.markdown, /追記（該当なし）/u);
  const keptSuffix = applyCheckProposals(CARD.replace(KB, '## KB確認に基づく追記（SUE-3-17 参照）'), [proposal()]);
  assert.match(keptSuffix.markdown, /## KB確認に基づく追記（SUE-3-17 参照）\n/u);
});

test('情報のある書き置き（未実施・pending）は消さず、その後ろに足す', () => {
  const note = '（未実施 — SUE-3-17 本文、S-EL-323 系の KB 文件名確定後。）';
  const result = applyCheckProposals(CARD.replace('（該当なし）', note), [proposal()]);
  assert.match(result.markdown, new RegExp(`## KB確認に基づく追記\\n\\n${note}\\n\\n### KB照合（確認日 2026-11-13）`, 'u'));
  const multi = applyCheckProposals(CARD.replace('（該当なし）', '（なし）\n（SUE-3-17 pending）'), [proposal()]);
  assert.match(multi.markdown, /（SUE-3-17 pending）\n\n### KB照合/u);
});

test('既に追記がある場合は末尾に足し、既存の追記を消さない', () => {
  const first = applyCheckProposals(CARD, [proposal('1つ目の質問')]).markdown;
  const second = applyCheckProposals(first, [proposal('2つ目の質問')]);
  assert.equal(second.applied, 1);
  const kb = kbBody(second.markdown);
  assert.ok(kb.indexOf('- 質問: 1つ目の質問') < kb.indexOf('- 質問: 2つ目の質問'));
  assert.equal(kb.match(/### KB照合/gu).length, 2);
  assert.match(second.markdown, /確認した記録です。\n\n## 正式資料・元情報\n/u);
  const manual = CARD.replace('（該当なし）', '- 原資料で確認済みの既存メモ');
  assert.match(applyCheckProposals(manual, [proposal()]).markdown, /- 原資料で確認済みの既存メモ\n\n### KB照合/u);
});

test('同じ質問・同じ確認日の追記は二重に入れない（別の日なら入れる）', () => {
  const once = applyCheckProposals(CARD, [proposal(), proposal()]);
  assert.deepEqual([once.applied, once.skipped], [1, 1]);
  const again = applyCheckProposals(once.markdown, [proposal()]);
  assert.deepEqual([again.applied, again.skipped], [0, 1]);
  assert.equal(again.markdown, once.markdown);
  const nextDay = applyCheckProposals(once.markdown, [proposal(undefined, '2026-11-14')]);
  assert.equal(nextDay.applied, 1);
});

test('旧版の未確認メモ節にある同じ追記は、確認節へ重複して入れない', () => {
  const legacy = CARD.replace('## 正式資料・元情報', `## KB照合メモ（原資料未確認）\n\n${proposal().markdown}\n\n## 正式資料・元情報`);
  const result = applyCheckProposals(legacy, [proposal()]);
  assert.deepEqual([result.applied, result.skipped, result.markdown], [0, 1, legacy]);
  const older = CARD.replace('（該当なし）', `${proposal().markdown}\n`);
  assert.equal(applyCheckProposals(older, [proposal()]).applied, 0);
});

test('節が無ければ「正式資料」（見出しの揺れ含む）の前に作り、それも無ければ末尾に作る', () => {
  const withoutKb = CARD.replace('## KB確認に基づく追記\n\n（該当なし）\n\n', '');
  const before = applyCheckProposals(withoutKb, [proposal()]).markdown;
  assert.match(before, /本文の主張。\n\n## KB確認に基づく追記\n\n### KB照合[\s\S]*確認した記録です。\n\n## 正式資料・元情報\n/u);
  const variant = applyCheckProposals(withoutKb.replace('## 正式資料・元情報', '## 正式資料・元情報（参照元）'), [proposal()]).markdown;
  assert.match(variant, /確認した記録です。\n\n## 正式資料・元情報（参照元）\n/u);
  const atEnd = applyCheckProposals('# 題名\n\n## 未確認事項\n\n- 回答資料 PDF\n', [proposal()]).markdown;
  assert.match(atEnd, /- 回答資料 PDF\n\n## KB確認に基づく追記\n\n### KB照合[\s\S]*確認した記録です。\n$/u);
  const noNewline = applyCheckProposals('# 題名', [proposal()]).markdown;
  assert.match(noNewline, /^# 題名\n\n## KB確認に基づく追記\n\n### KB照合[\s\S]*記録です。$/u);
});

test('CRLF のカードは CRLF のまま返す', () => {
  const crlf = CARD.replaceAll('\n', '\r\n');
  const result = applyCheckProposals(crlf, [proposal()]);
  assert.ok(!/(?<!\r)\n/u.test(result.markdown), 'LF だけの改行が混ざらない');
  assert.equal(result.markdown.replaceAll('\r\n', '\n'), applyCheckProposals(CARD, [proposal()]).markdown);
});

test('コードフェンス内の見出しを節と誤認しない', () => {
  const fenced = CARD.replace('本文の主張。', '```md\n## KB確認に基づく追記\n\n（該当なし）\n\n## 正式資料・元情報\n```\n\n~~~\n## KB確認に基づく追記\n~~~');
  const result = applyCheckProposals(fenced, [proposal()]);
  assert.ok(result.markdown.includes('```md\n## KB確認に基づく追記\n\n（該当なし）\n\n## 正式資料・元情報\n```'));
  assert.equal(result.markdown.match(/### KB照合/gu).length, 1);
  assert.ok(result.markdown.indexOf('### KB照合') > result.markdown.indexOf('~~~\n## KB確認に基づく追記\n~~~'));
});

test('frontmatter 付きでも frontmatter を1文字も変えず、card_version・review_status を上げない', () => {
  const frontmatter = '---\nknowledge_id: KH-X-1\ncard_version: 3\nreview_status: in_review\ntitle: "## KB確認に基づく追記"\nnote: |\n  ## KB確認に基づく追記\n  （該当なし）\n---\n';
  const result = applyCheckProposals(`${frontmatter}\n${CARD}`, [proposal()]);
  assert.ok(result.markdown.startsWith(`${frontmatter}\n# 題名\n`));
  assert.equal(result.markdown.match(/### KB照合/gu).length, 1);
  assert.equal(parseKnowledgeMarkdown(result.markdown).version, 3);
});

test('本文の主張の節は書き換えず、不正な入力は拒否する', () => {
  const result = applyCheckProposals(CARD, [proposal()]);
  const section = (markdown, heading) => splitKnowhowCardBody(markdown).readerSections.find((item) => item.heading === heading)?.body;
  assert.equal(section(result.markdown, '統合した回答・ノウハウ'), '本文の主張。');
  assert.throws(() => applyCheckProposals(null, [proposal()]), TypeError);
});

test('閉じていないコードフェンスには追記しない', () => {
  const unclosed = CARD.replace('本文の主張。', '本文の主張。\n\n```text\n閉じていない');
  assert.throws(() => applyCheckProposals(unclosed, [proposal()]), /閉じていないコードフェンス/u);
});

test('実カード: 節なし（397）・書き置きあり（394）・該当なし（399）に差し込める', () => {
  const load = (path) => parseKnowledgeMarkdown(readFileSync(new URL(path, import.meta.url), 'utf8')).body;
  const hall = applyCheckProposals(load('../../knowledge/cards/case-summaries/KH-ALL-HALL-CHIME-SIGNAL-399.md'), [proposal()]).markdown;
  assert.match(hall, /## KB確認に基づく追記\n\n### KB照合[\s\S]*記録です。\n\n## 正式資料・元情報\n/u);
  assert.doesNotMatch(hall, /KB確認に基づく追記\n\n（該当なし）/u);
  const sag = applyCheckProposals(load('../../knowledge/cards/case-summaries/KH-VFGLF-M1-AC-SAG-397.md'), [proposal()]).markdown;
  assert.match(sag, /4\. 不発 FB。\n\n## KB確認に基づく追記\n\n### KB照合[\s\S]*記録です。\n\n## 正式資料\n/u);
  const pit = applyCheckProposals(load('../../knowledge/cards/practice-guides/KH-PIT-TRAP-POSITION-394.md'), [proposal()]).markdown;
  assert.match(pit, /## KB確認に基づく追記[\s\S]*### KB照合[\s\S]*記録です。\n\n## 正式資料・元情報（参照元）\n/u);
});
