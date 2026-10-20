import assert from 'node:assert/strict';
import test from 'node:test';
import { formatElapsed, linkResearchRefs, researchRefAnchor } from '../src/lib/knowledge-senpai-research-view.mjs';
import { modelFitNotice, modelWithFacts } from '../src/lib/knowledge-senpai-model-fit.mjs';

test('linkResearchRefs turns known refs into in-page links and leaves everything else alone', () => {
  const known = new Set(['T1', 'L2', 'K1']);
  const text = linkResearchRefs('結論 [T1] と [L2][K1]。未知 [T9]、注 [T1](https://x.test)、定義 [K1]: x', known, 'turn-3');
  assert.equal(text.includes('[\\[T1\\]](#turn-3-ref-T1) と [\\[L2\\]](#turn-3-ref-L2)[\\[K1\\]](#turn-3-ref-K1)'), true);
  assert.equal(text.includes('[T9]'), true);
  assert.equal(text.includes('[T1](https://x.test)'), true);
  assert.equal(text.includes('[K1]: x'), true);
  assert.equal(researchRefAnchor('turn-3', 'T1'), 'turn-3-ref-T1');
});

test('linkResearchRefs does not touch code spans or fenced code, and tolerates odd input', () => {
  const known = new Set(['T1']);
  const text = linkResearchRefs('`[T1]` と\n```\n[T1]\n```\nと [T1]', known, 'p');
  assert.equal(text.match(/\(#p-ref-T1\)/gu).length, 1);
  assert.equal(linkResearchRefs('', known, 'p'), '');
  assert.equal(linkResearchRefs('[T1]', new Set(), 'p'), '[T1]');
  assert.equal(linkResearchRefs(undefined, known, 'p'), '');
});

test('formatElapsed renders seconds and minutes for people', () => {
  assert.equal(formatElapsed(0), '0秒');
  assert.equal(formatElapsed(999), '0秒');
  assert.equal(formatElapsed(12_400), '12秒');
  assert.equal(formatElapsed(65_000), '1分05秒');
  assert.equal(formatElapsed(-5), '0秒');
  assert.equal(formatElapsed(Number.NaN), '0秒');
});

test('model fit notice is shared with the Senpai chat wording', () => {
  assert.equal(modelWithFacts('AXIEZ'), 'AXIEZ（VFGLB・巻上機下部）');
  assert.equal(modelWithFacts('NEXCUBE'), 'NEXCUBE');
  assert.equal(modelFitNotice({ modelFit: 'other_product', modelFitProducts: ['AXIEZ-LINKs'] }, 'AXIEZ'),
    'AXIEZ-LINKs（VFGLF・巻上機上部）の事例です。選択中の AXIEZ（VFGLB・巻上機下部）でも当てはまるかは要確認です。');
  assert.equal(modelFitNotice({ modelFit: 'other_product' }, 'メルシティ'), '別の機種区分の事例です。選択中の メルシティでも当てはまるかは要確認です。');
  assert.equal(modelFitNotice({ modelFit: 'matched' }, 'AXIEZ'), null);
  assert.equal(modelFitNotice({ modelFit: 'other_product' }, undefined), null);
});

import {
  EXAMPLE_QUESTIONS, buildCopyText, clarifyAsksModel, composeClarifyQuestion, copyText, modelMismatch,
  splitAnswerSections, stepRowLabel,
} from '../src/lib/knowledge-senpai-research-view.mjs';

test('finished steps use past-tense labels; running keeps the server label', () => {
  const row = (step, status, labelJa) => ({ step, status, labelJa });
  assert.equal(stepRowLabel(row('understand', 'running', '質問を整理中')), '質問を整理中');
  const done = {
    understand: '質問を整理しました', knowhow: 'ノウハウを確認しました', tech_search: '技術資料を検索しました',
    law_search: '法令を確認しました', sufficiency: '不足を確認しました', retry_search: '言い換えて再検索しました',
    doc_page: '資料のページを確認しました', clarify: '確認点を整理しました', synthesize: '回答をまとめました', verify: '根拠を照合しました',
  };
  for (const [step, label] of Object.entries(done)) {
    assert.equal(stepRowLabel(row(step, 'done', 'x中')), label, step);
    assert.match(stepRowLabel(row(step, 'failed', 'x中')), /できませんでした|られませんでした/u, step);
  }
  assert.equal(stepRowLabel(row('law_search', 'skipped', '法令を確認中')), '法令を確認（省略）');
  assert.equal(stepRowLabel(row('mystery', 'done', '何かを実行中')), '何かを実行中');
});

test('splitAnswerSections recognises the known headings and falls back to null without them', () => {
  const md = '前置き\n\n## 結論の候補\n調整です [T1]\n\n## 技術資料から\n手順\n\n## 食い違い・不足\n- 階数不明\n\n## 次に確認すること\n- 音のタイミング\n';
  const sections = splitAnswerSections(md);
  assert.deepEqual(sections.map((section) => section.kind), ['normal', 'conclusion', 'normal', 'caution', 'todo']);
  assert.equal(sections[0].heading, undefined);
  assert.equal(sections[1].heading, '結論の候補');
  assert.equal(sections[1].body, '調整です [T1]');
  assert.equal(splitAnswerSections('ただの文章です\n## 別の見出し\n本文'), null);
  assert.equal(splitAnswerSections(''), null);
  assert.equal(splitAnswerSections(undefined), null);
});

test('a clarify reply is composed with the original question within 2000 characters', () => {
  assert.equal(composeClarifyQuestion('ドアの異音', 'AXIEZです'), 'ドアの異音\n補足: AXIEZです');
  const long = composeClarifyQuestion('あ'.repeat(1990), 'い'.repeat(100));
  assert.equal(Array.from(long).length, 2000);
  assert.ok(long.endsWith('い'.repeat(100)));
  assert.match(long, /\n補足: /u);
  const huge = composeClarifyQuestion('元', 'い'.repeat(3000));
  assert.equal(Array.from(huge).length, 2000);
  assert.ok(huge.startsWith('元\n補足: '));
});

test('model chips are offered only when the clarify mentions the model', () => {
  assert.equal(clarifyAsksModel({ clarifyQuestions: ['機種は何ですか'], answerMarkdown: '' }), true);
  assert.equal(clarifyAsksModel({ clarifyQuestions: ['異音はいつ出ますか'], answerMarkdown: '' }), false);
  assert.equal(clarifyAsksModel({ clarifyQuestions: [], answerMarkdown: '型式を教えてください' }), true);
});

test('modelMismatch compares the understood model with the selected one', () => {
  const known = new Set(['AXIEZ', 'NEXCUBE']);
  const result = (modelType) => ({ understanding: { modelType } });
  assert.deepEqual(modelMismatch(result('NEXCUBE'), 'AXIEZ', known), { detected: 'NEXCUBE', selected: 'AXIEZ' });
  assert.equal(modelMismatch(result('AXIEZ'), 'AXIEZ', known), null);
  assert.equal(modelMismatch(result(null), 'AXIEZ', known), null);
  assert.equal(modelMismatch(result('NEXCUBE'), undefined, known), null);
  assert.equal(modelMismatch(result('不明な機種'), 'AXIEZ', known), null);
  assert.equal(modelMismatch({}, 'AXIEZ', known), null);
});

test('buildCopyText gives the answer followed by numbered plain-text sources', () => {
  const text = buildCopyText({
    answerMarkdown: '## 結論の候補\n調整です [T1]',
    sources: {
      tech: [{ ref: 'T1', title: '手順書', pageNumber: 3 }],
      law: [{ ref: 'L1', lawTitle: '建築基準法', provision: '第三十五条', effectiveDate: '2025-04-01' }],
      knowhow: { used: [{ ref: 'K1', title: '勘所', cardVersion: 2, status: 'draft' }], candidates: [{ knowledgeId: 'KH-9', cardVersion: 1, title: '使わず' }] },
    },
  });
  assert.match(text, /^## 結論の候補\n調整です \[T1\]\n\n出典\n/u);
  assert.match(text, /\[T1\] 手順書 3ページ/u);
  assert.match(text, /\[L1\] 建築基準法 第三十五条（施行日 2025-04-01）/u);
  assert.match(text, /\[K1\] 勘所 v2（未承認・参考）/u);
  assert.doesNotMatch(text, /使わず/u);
  assert.equal(buildCopyText({ answerMarkdown: '本文', sources: { tech: [], law: [], knowhow: { used: [], candidates: [] } } }), '本文');
});

test('copyText reports success, and failure without throwing', async () => {
  const written = [];
  assert.equal(await copyText('本文', { writeText: async (value) => { written.push(value); } }), true);
  assert.deepEqual(written, ['本文']);
  assert.equal(await copyText('本文', { writeText: async () => { throw new Error('denied'); } }), false);
  assert.equal(await copyText('本文', undefined), false);
});

test('three example questions are offered for the empty state', () => {
  assert.equal(EXAMPLE_QUESTIONS.length, 3);
  assert.ok(EXAMPLE_QUESTIONS.every((text) => text.length > 10 && text.length <= 2000));
});
