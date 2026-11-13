import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { createRequire } from 'node:module';
import test, { afterEach } from 'node:test';
import { createElement } from 'react';
import { renderToStaticMarkup } from 'react-dom/server';
import ts from 'typescript';

const require = createRequire(import.meta.url);
const FLAG = 'NEXT_PUBLIC_ENABLE_KNOWHOW_REWRITE';

function loadComponent(name) {
  const file = new URL(`../src/components/knowledge/${name}.tsx`, import.meta.url);
  const { outputText } = ts.transpileModule(readFileSync(file, 'utf8'), {
    compilerOptions: { module: ts.ModuleKind.CommonJS, jsx: ts.JsxEmit.ReactJSX, esModuleInterop: true },
    fileName: file.pathname,
  });
  const compiledModule = { exports: {} };
  const localRequire = (id) => {
    if (id === '@/components/ui/Button') return { Button: ({ variant: _variant, size: _size, ...props }) => createElement('button', props) };
    if (id.startsWith('@/lib/')) return require(`../src/lib/${id.slice(6)}`);
    if (id.startsWith('../../lib/')) return require(`../src/lib/${id.slice(10)}`);
    if (id.startsWith('./')) return loadComponent(id.slice(2));
    return require(id);
  };
  new Function('require', 'module', 'exports', outputText)(localRequire, compiledModule, compiledModule.exports);
  return compiledModule.exports;
}

afterEach(() => { delete process.env[FLAG]; });

const MAIN = '統合した回答・ノウハウ';
const OPEN = '未確認事項';
const STEPS = '調査・確認手順';
const noop = () => {};
const plan = {
  request: { knowledgeId: 'KH-A', cardVersion: 1, targets: [{ heading: MAIN, body: 'a' }, { heading: STEPS, body: 'b' }, { heading: OPEN, body: 'c' }], context: [], evidence: [{}, {}] },
  evidenceRefs: [{ number: 1, questionId: 'q1', question: '質問その1' }, { number: 2, questionId: 'q 2', question: '質問その2' }],
  evidenceOmitted: 0,
  excluded: [],
  blocker: '',
};
const proposal = {
  knowledgeId: 'KH-A',
  cardVersion: 1,
  bases: [{ heading: MAIN, body: '旧の主張' }, { heading: STEPS, body: '1. 旧' }, { heading: OPEN, body: '- 旧未確認' }],
  sections: [
    { heading: MAIN, status: 'changed', body: '新しい主張です', baseBody: '旧の主張', reason: '根拠 1 で確認できたため', evidence: [1], warnings: [{ code: 'unverified_number', values: ['12'] }] },
    { heading: STEPS, status: 'unchanged', evidence: [], warnings: [] },
    { heading: OPEN, status: 'rejected', evidence: [], warnings: [{ code: 'unsupported_value', values: ['SUE-9'] }] },
  ],
  conflicts: [{ description: 'カードは 800 mm、根拠は 600 mm', evidence: [2] }],
};
const ready = { phase: 'ready', proposal, evidenceRefs: plan.evidenceRefs };
const base = {
  hasKnowledgeId: true, plan, view: { phase: 'idle' }, decisions: {}, conflictDecisions: {}, note: '',
  checking: false, busy: false, onRun: noop, onCancel: noop, onDecide: noop, onDecideConflict: noop,
};
function render(props = {}, flag = 'true') {
  if (flag === null) delete process.env[FLAG]; else process.env[FLAG] = flag;
  const { KnowhowRewritePanel } = loadComponent('KnowhowRewritePanel');
  return renderToStaticMarkup(createElement(KnowhowRewritePanel, { ...base, ...props }));
}

test('フラグが true でなければ何も描画しない。knowledge_id が無いカードにも出さない', () => {
  for (const flag of [null, '', 'false', '1']) assert.equal(render({}, flag), '');
  assert.equal(render({ hasKnowledgeId: false }), '');
  assert.notEqual(render({}), '');
});

test('実行前に、送る根拠の件数・節の数・利用料を表示し、ボタンが押せる', () => {
  const html = render();
  assert.match(html, /確認済みの根拠 2 件と、カードの3つの節を AI に送ります。AI の利用料がかかります。/);
  assert.match(html, /AI に本文の書き換え案を作らせる/);
  const button = /<button[^>]*>AI に本文の書き換え案を作らせる<\/button>/u.exec(html)[0];
  assert.doesNotMatch(button, /disabled/);
});

test('作れない理由を短く表示し、ボタンを押せなくする', () => {
  const html = render({ plan: { ...plan, request: null, blocker: '出典つきの確認済みが無いため作れません。' } });
  assert.match(html, /出典つきの確認済みが無いため作れません。/);
  assert.match(/<button[^>]*>AI に本文の書き換え案を作らせる<\/button>/u.exec(html)[0], /disabled/);
  assert.doesNotMatch(html, /AI に送ります/);
  const waiting = render({ checking: true });
  assert.match(/<button[^>]*>AI に本文の書き換え案を作らせる<\/button>/u.exec(waiting)[0], /disabled/);
});

test('対象から外した節と、省いた根拠の件数を理由つきで表示する', () => {
  const html = render({ plan: { ...plan, evidenceOmitted: 3, excluded: [{ heading: STEPS, reason: 'too_long' }, { heading: OPEN, reason: 'duplicate' }] } });
  assert.match(html, /「調査・確認手順」は本文が2,000字を超えるため対象から外しました/);
  assert.match(html, /「未確認事項」は同じ見出しが複数あるため対象から外しました/);
  assert.match(html, /根拠が多いため、先頭の 12 件だけを送ります。ほか 3 件は使いません。/);
});

test('作成中は中止できる。二重に押せない。失敗は固定文言で出す', () => {
  const loading = render({ view: { phase: 'loading' } });
  assert.match(loading, /案を作成しています/);
  assert.match(/<button[^>]*>AI に本文の書き換え案を作らせる<\/button>/u.exec(loading)[0], /disabled/);
  assert.match(loading, /<button[^>]*>中止<\/button>/);
  const failed = render({ view: { phase: 'error', message: '混み合っています。少し待ってからやり直してください。' } });
  assert.match(failed, /role="alert"[^>]*>混み合っています。少し待ってからやり直してください。/);
});

test('結果: 変更前後の差分・理由・根拠・警告・注記を表示し、既定はどの節も未確認', () => {
  const html = render({ view: ready });
  assert.match(html, /AI が確認済みの根拠から作った案です。差分と根拠を確認してから反映してください。/);
  assert.match(html, /<mark[^>]*bg-red-300[^>]*>旧の<\/mark>/, '削除側の変わった部分だけを濃い赤で強調する');
  assert.match(html, /<mark[^>]*bg-green-300[^>]*>新しい<\/mark>/, '追加側の変わった部分だけを濃い緑で強調する');
  assert.match(html, /根拠 1 で確認できたため/);
  assert.match(html, /href="#check-question-q1"/);
  assert.match(html, /質問その1/);
  assert.match(html, /根拠に見当たらない数字: 12/);
  assert.match(html, /border-amber-400/);
  assert.match(html, /1節中 0節を反映・0節を反映しない・1節が未確認/);
  assert.match(html, /未確認/);
  assert.doesNotMatch(html, /確認済み: /);
  assert.doesNotMatch(html, /aria-pressed="true"/);
  assert.doesNotMatch(html, /本文の主張を変えました/);
});

test('変更なしは「変更なし」、不採用は理由つきで本文なしに表示する', () => {
  const html = render({ view: ready });
  assert.match(html, /調査・確認手順[\s\S]*変更なし/);
  assert.match(html, /検査で不採用（根拠に見当たらない資料番号・数値: SUE-9）/);
  assert.doesNotMatch(html, /本文に取り込めません/);
  assert.equal((html.match(/確認して反映する/g) ?? []).length, 1, '反映を選べるのは変更ありの節だけ');
});

test('食い違いは別枠に出し、未確認事項へ追加する／しないを選べる。既定は未選択', () => {
  const html = render({ view: ready });
  assert.match(html, /カードと根拠の食い違い/);
  assert.match(html, /カードは 800 mm、根拠は 600 mm/);
  assert.match(html, /href="#check-question-q%202"/);
  assert.match(html, /未確認事項に追加する/);
  assert.match(html, /追加しない/);
  const chosen = render({ view: ready, conflictDecisions: { 0: 'confirm' } });
  assert.match(chosen, /確認済み: 追加する/);
  const noOpen = render({ view: { ...ready, proposal: { ...proposal, bases: [] } } });
  assert.doesNotMatch(noOpen, /未確認事項に追加する/);
  assert.match(noOpen, /「未確認事項」の節が無い/);
});

test('選んだ節の件数と、反映するときの注意書き（card_version・台帳・技術承認ではない）', () => {
  const html = render({ view: ready, decisions: { [MAIN]: 'confirm' } });
  assert.match(html, /1節中 1節を反映・0節を反映しない・0節が未確認/);
  assert.match(html, /確認済み: 反映する/);
  assert.match(html, /本文の主張を変えました。Git に入れるときは card_version を上げ、台帳を作り直してください。この確認は技術承認ではありません。/);
  const skipped = render({ view: ready, decisions: { [MAIN]: 'skip' } });
  assert.match(skipped, /1節を反映しない/);
  assert.doesNotMatch(skipped, /本文の主張を変えました/);
});

test('案を破棄したときは、その旨を一言表示する', () => {
  const html = render({ note: '確認の選択が変わったため、作った案を破棄しました。' });
  assert.match(html, /role="status"[^>]*>確認の選択が変わったため、作った案を破棄しました。/);
});

test('結果の注記: 不正な内容があっても React が文字列として描画する（HTML を解釈しない）', () => {
  const evil = { ...proposal, sections: [{ ...proposal.sections[0], reason: '<img src=x onerror=alert(1)>', body: '<script>x</script>' }] };
  const html = render({ view: { phase: 'ready', proposal: evil, evidenceRefs: plan.evidenceRefs } });
  assert.doesNotMatch(html, /<img|<script/);
  assert.match(html, /&lt;img/);
});

test('警告コードの新しい理由と、表示できない変更理由の扱い', () => {
  const rejectedWith = (code) => render({ view: { phase: 'ready', evidenceRefs: plan.evidenceRefs, proposal: { ...proposal, sections: [{ heading: OPEN, status: 'rejected', evidence: [], warnings: [{ code, values: [] }] }], conflicts: [] } } });
  assert.match(rejectedWith('link_or_html'), /検査で不採用（元の本文に無いリンクや HTML が含まれている）/);
  assert.match(rejectedWith('suspicious_text'), /検査で不採用（見えない文字や制御文字が含まれている）/);
  assert.match(rejectedWith('unclosed_fence'), /検査で不採用（コードの囲みが閉じていない）/);
  assert.match(rejectedWith('brand_new_code'), /検査で不採用（理由は未対応の警告コード）/);
  assert.doesNotMatch(rejectedWith('brand_new_code'), /検査で不採用（検査で不採用/);
  const noReason = render({ view: { phase: 'ready', evidenceRefs: plan.evidenceRefs, proposal: { ...proposal, sections: [{ ...proposal.sections[0], reason: '' }] } } });
  assert.doesNotMatch(noReason, /変更理由/);
});

test('変更理由に URL があってもリンクにしない（テキストとして描画する）', () => {
  const html = render({ view: { phase: 'ready', evidenceRefs: plan.evidenceRefs, proposal: { ...proposal, sections: [{ ...proposal.sections[0], reason: 'https://evil.example を参照' }] } } });
  assert.doesNotMatch(html, /href="https:\/\/evil/);
});
