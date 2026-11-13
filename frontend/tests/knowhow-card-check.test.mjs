import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import test from 'node:test';
import { parseKnowledgeMarkdown } from '../src/lib/knowledge-workbench.mjs';
import {
  CHECK_TARGETS_BY_KIND,
  MAX_CHECK_QUESTIONS,
  buildCheckQuestions,
  countCheckCalls,
  createManualQuestion,
} from '../src/lib/knowhow-card-check.mjs';
import { extractValueTokens, findLawTerms, stripManagementTerms } from '../src/lib/knowhow-card-check-text.mjs';

const CARD_PATHS = {
  'KH-ALL-HALL-CHIME-SIGNAL-399': '../../knowledge/cards/case-summaries/KH-ALL-HALL-CHIME-SIGNAL-399.md',
  'KH-VFGLF-M1-AC-SAG-397': '../../knowledge/cards/case-summaries/KH-VFGLF-M1-AC-SAG-397.md',
  'KH-ALL-WHISPER-U-BOLT-SIZE-369': '../../knowledge/cards/case-summaries/KH-ALL-WHISPER-U-BOLT-SIZE-369.md',
  'KH-PIT-TRAP-POSITION-394': '../../knowledge/cards/practice-guides/KH-PIT-TRAP-POSITION-394.md',
  'KH-MR-SFLEX-ROPE-SOCKET-278': '../../knowledge/cards/practice-guides/KH-MR-SFLEX-ROPE-SOCKET-278.md',
  'KH-ALL-CABIN-ILLUMINANCE-62LX-282': '../../knowledge/cards/practice-guides/KH-ALL-CABIN-ILLUMINANCE-62LX-282.md',
};
const loadCard = (id) => parseKnowledgeMarkdown(
  readFileSync(new URL(CARD_PATHS[id], import.meta.url), 'utf8'),
);
const questionsOf = (id, options = {}) => {
  const card = loadCard(id);
  return buildCheckQuestions({ frontmatter: card.frontmatter, body: card.body, ...options });
};
const card = (body, frontmatter = {}) => ({
  frontmatter: { title: '戸開閉の調整', ...frontmatter },
  body: `# 戸開閉の調整\n\n${body}`,
});
// 質問文に入れてはいけない、カード内の管理用の呼び名。
const MANAGEMENT_WORDS = /Lists|OneNote|§\s*\d|KH-[A-Z]|list_item_id|情報管理/u;
const FIXTURE_IDS = [
  'KH-ALL-HALL-CHIME-SIGNAL-399',
  'KH-VFGLF-M1-AC-SAG-397',
  'KH-ALL-WHISPER-U-BOLT-SIZE-369',
  'KH-PIT-TRAP-POSITION-394',
  'KH-MR-SFLEX-ROPE-SOCKET-278',
  'KH-ALL-CABIN-ILLUMINANCE-62LX-282',
];

test('照合先の既定は、法令は法令のみ・数値と未確認は両方・根拠は技術のみ', () => {
  assert.deepEqual(CHECK_TARGETS_BY_KIND.law, ['law']);
  assert.deepEqual(CHECK_TARGETS_BY_KIND.value_check, ['normal', 'law']);
  assert.deepEqual(CHECK_TARGETS_BY_KIND.open_item, ['normal', 'law']);
  assert.deepEqual(CHECK_TARGETS_BY_KIND.basis, ['normal']);
  assert.equal(MAX_CHECK_QUESTIONS, 6);
});

test('材料が乏しいカードでも、題名から根拠の質問を1問は作る', () => {
  const questions = buildCheckQuestions(card('## 未確認事項\n\n- なし。\n'));
  assert.equal(questions.length, 1);
  assert.equal(questions[0].kind, 'basis');
  assert.match(questions[0].text, /戸開閉の調整/u);
  assert.match(questions[0].text, /根拠になる正式資料/u);
  assert.deepEqual(questions[0].targets, ['normal']);
  assert.equal(questions[0].selected, true);
});

test('「なし」「該当なし」だけの未確認事項からは質問を作らない', () => {
  for (const item of ['- なし。', '- 該当なし', '- （該当なし）', '- なし（Lists 原因明記）。']) {
    const questions = buildCheckQuestions(card(`## 未確認事項\n\n${item}\n`));
    assert.deepEqual(questions.map((question) => question.kind), ['basis'], item);
  }
});

test('管理用のKB取り込み名は照合質問にしない', () => {
  const questions = buildCheckQuestions(card('## 未確認事項\n\n- KB 上の取り込み名を確認する\n'));
  assert.deepEqual(questions.map((question) => question.kind), ['basis']);
});

test('未確認事項は1件ずつ質問になり、元の節と行を持つ', () => {
  const questions = buildCheckQuestions(card('## 未確認事項\n\n- 戸閉力の現行の規定値\n- 高速戸での調整手順の違い\n'));
  const open = questions.filter((question) => question.kind === 'open_item');
  assert.equal(open.length, 2);
  assert.equal(open[0].sourceSection, '未確認事項');
  assert.equal(open[0].sourceText, '戸閉力の現行の規定値');
  assert.match(open[0].text, /戸閉力の現行の規定値/u);
  assert.match(open[0].text, /戸開閉の調整/u);
  assert.deepEqual(open[0].targets, ['normal', 'law']);
});

test('優先順は 未確認事項 → 数値・基準 → 根拠 → 法令 で、上限は6問', () => {
  const body = [
    '## 統合した回答・ノウハウ',
    '',
    '戸閉力は 150 N 以下とする。隙間は 6 mm 以内（SUE-3-17）。',
    '',
    '## 調査・確認手順',
    '',
    '1. 建築基準法の定期検査の対象か確認する。',
    '',
    '## 未確認事項',
    '',
    ...['a', 'b', 'c', 'd', 'e'].map((key) => `- 確認したい別々の内容その${key}の現行の扱い`),
  ].join('\n');
  const questions = buildCheckQuestions(card(body));
  assert.equal(questions.length, MAX_CHECK_QUESTIONS);
  const kinds = questions.map((question) => question.kind);
  assert.deepEqual([...new Set(kinds)], ['open_item', 'value_check', 'basis']);
  assert.equal(kinds.filter((kind) => kind === 'basis').length, 1, '根拠の質問は必ず残す');
});

test('上限を変えると、優先度の低い種類から落ちる', () => {
  const body = '## 統合した回答・ノウハウ\n\n隙間は 6 mm 以内。消防法の対象。\n\n## 未確認事項\n\n- 隙間の現行の規定値と測定位置\n';
  assert.deepEqual(buildCheckQuestions(card(body)).map((question) => question.kind), ['open_item', 'value_check', 'basis', 'law']);
  assert.deepEqual(buildCheckQuestions({ ...card(body), limit: 2 }).map((question) => question.kind), ['open_item', 'basis']);
});

test('質問数の上限は1〜既定上限の整数だけを受け付ける', () => {
  for (const limit of [0, -1, 1.5, 7, Number.NaN]) {
    assert.throws(() => buildCheckQuestions({ ...card('## 未確認事項\n\n- 現行の要件を確認する'), limit }), /上限/u);
  }
});

test('数値・基準・資料番号を含む文から数値確認の質問を作り、値はそのまま入れる', () => {
  const questions = buildCheckQuestions(card('## 統合した回答・ノウハウ\n\n据付 SUE-3-17 では **800 mm** 以内とする。交換は現場判断でよい。\n'));
  const value = questions.filter((question) => question.kind === 'value_check');
  assert.equal(value.length, 1);
  assert.match(value[0].text, /SUE-3-17/u);
  assert.match(value[0].text, /800 mm/u);
  assert.equal(value[0].sourceSection, '統合した回答・ノウハウ');
  assert.match(value[0].sourceText, /800 mm/u);
  assert.deepEqual(value[0].targets, ['normal', 'law']);
});

test('同じ数値・資料番号だけの文は重ねて質問にしない', () => {
  const body = '## 統合した回答・ノウハウ\n\n隙間は 6 mm 以内。\n\n## 調査・確認手順\n\n1. 隙間が 6 mm 以内か測る。\n2. 6 mm を超える場合は調整する。\n';
  const value = buildCheckQuestions(card(body)).filter((question) => question.kind === 'value_check');
  assert.equal(value.length, 1);
});

test('法令・安全に関わる語があると法令の質問を1問作り、法令KBだけに投げる', () => {
  const questions = buildCheckQuestions(card('## 使う場面・対象条件\n\n建築基準法の完了検査で指摘されたとき。\n'));
  const law = questions.filter((question) => question.kind === 'law');
  assert.equal(law.length, 1);
  assert.deepEqual(law[0].targets, ['law']);
  assert.match(law[0].text, /建築基準法/u);
  assert.match(law[0].text, /法令/u);
  assert.equal(law[0].sourceSection, '使う場面・対象条件');
});

test('機種は model_scope から入れ、「全エレ機種」のような総称は入れない', () => {
  const scoped = buildCheckQuestions(card('', { model_scope: { control_methods: ['VFGLF'], machine_room: ['MRL'], lists_model_label: ['VFGLF'] } }));
  assert.match(scoped[0].text, /VFGLF/u);
  assert.match(scoped[0].text, /MRL/u);
  assert.equal(scoped[0].text.match(/VFGLF/gu).length, 1, '同じ機種名は1回だけ');
  const generic = buildCheckQuestions(card('', { model_scope: { lists_model_label: ['全エレ機種'] } }));
  assert.doesNotMatch(generic[0].text, /全エレ機種|機種:/u);
});

test('管理用の呼び名は質問文に入れない', () => {
  const body = [
    '## 統合した回答・ノウハウ',
    '',
    '硬配線ではなく更新処理の論点（Lists 399）。隙間は §12 のとおり 6 mm（OneNote）。',
    '',
    '## 未確認事項',
    '',
    '- 修正 S/W の機種展開 — Lists のみ。',
    '- Lists 保留の「原因・対策」フィールド',
    '- `record_id` の対応づけ（KH-ALL-HALL-CHIME-SIGNAL-399）',
  ].join('\n');
  const questions = buildCheckQuestions(card(body, { title: '乗場チャイム（Lists 399）' }));
  for (const question of questions) assert.doesNotMatch(question.text, MANAGEMENT_WORDS, question.text);
  const open = questions.filter((question) => question.kind === 'open_item');
  assert.deepEqual(open.map((question) => question.sourceText), ['修正 S/W の機種展開 — Lists のみ。']);
  assert.match(open[0].text, /修正 S\/W の機種展開/u);
});

test('ほぼ同じ文の質問は除く', () => {
  const body = '## 未確認事項\n\n- 戸閉力の現行の規定値\n- 戸閉力の現行の規定値。\n- **戸閉力**の現行の規定値\n';
  const open = buildCheckQuestions(card(body)).filter((question) => question.kind === 'open_item');
  assert.equal(open.length, 1);
});

test('コードフェンスの中の見出しや箇条書きは材料にしない', () => {
  const body = '## 統合した回答・ノウハウ\n\n```\n## 未確認事項\n- フェンスの中の行は拾わない内容\n```\n';
  assert.deepEqual(buildCheckQuestions(card(body)).map((question) => question.kind), ['basis']);
});

test('題名が無い・本文が文字列でないときも落ちない', () => {
  assert.deepEqual(buildCheckQuestions({ frontmatter: {}, body: '' }), []);
  assert.deepEqual(buildCheckQuestions({ frontmatter: null, body: null }), []);
  const fromHeading = buildCheckQuestions({ frontmatter: {}, body: '# 本文の題名\n' });
  assert.match(fromHeading[0].text, /本文の題名/u);
});

test('文字の切り出し: 数値・資料番号・法令語・管理用の呼び名', () => {
  assert.deepEqual(extractValueTokens('SUE-3-17 は 600 mm、S-EL・323 と S-EL-323.1。P-6-S900.01-B と 62.5 lx、500msec。'),
    ['SUE-3-17', '600 mm', 'S-EL・323', 'S-EL-323.1', 'P-6-S900.01-B', '62.5 lx', '500msec']);
  assert.deepEqual(extractValueTokens('KH-ALL-HALL-CHIME-SIGNAL-399 と AXIEZ-LINKS、5 階、M10。'), []);
  assert.deepEqual(extractValueTokens('告示 1455 と JIS3525、構造規格 29 条。'), ['告示 1455', 'JIS3525', '29 条']);
  assert.deepEqual(findLawTerms('建築基準法 OK でも労基目線。官検あり。'), ['建築基準法', '労基', '官検']);
  assert.equal(stripManagementTerms('標準チャイムが鳴らない（Lists 399）。OneNote の §91 と KH-ALL-X-1 参照'), '標準チャイムが鳴らない。の と 参照');
});

test('実行前の回数は、選んだ質問の照合先ごとに数える', () => {
  const questions = [
    { id: 'a', selected: true, targets: ['normal', 'law'], text: 'x' },
    { id: 'b', selected: true, targets: ['law'], text: 'y' },
    { id: 'c', selected: false, targets: ['normal'], text: 'z' },
    { id: 'd', selected: true, targets: ['normal'], text: '   ' },
  ];
  assert.deepEqual(countCheckCalls(questions), { questions: 2, normal: 1, law: 2, total: 3 });
});

test('手で足す質問は、技術・法令の両方が既定で、ID が重ならない', () => {
  const existing = [{ id: 'manual-1' }, { id: 'basis-1' }];
  const manual = createManualQuestion(existing, '  手で足した質問  ');
  assert.equal(manual.id, 'manual-2');
  assert.equal(manual.kind, 'manual');
  assert.equal(manual.text, '手で足した質問');
  assert.deepEqual(manual.targets, ['normal', 'law']);
  assert.equal(manual.selected, true);
});

test('実カード6枚: どれからも質問が出て、管理用の呼び名を含まず、上限以内', () => {
  for (const id of FIXTURE_IDS) {
    const questions = questionsOf(id);
    assert.ok(questions.length >= 1 && questions.length <= MAX_CHECK_QUESTIONS, id);
    assert.equal(questions.filter((question) => question.kind === 'basis').length, 1, id);
    assert.equal(new Set(questions.map((question) => question.id)).size, questions.length, id);
    assert.equal(new Set(questions.map((question) => question.text)).size, questions.length, id);
    for (const question of questions) {
      assert.doesNotMatch(question.text, MANAGEMENT_WORDS, `${id}: ${question.text}`);
      assert.doesNotMatch(question.text, /\*\*|`|\]\(/u, `${id}: ${question.text}`);
      assert.ok(question.text.endsWith('。'), `${id}: ${question.text}`);
      assert.ok(!question.text.includes('\n'), id);
    }
  }
});
