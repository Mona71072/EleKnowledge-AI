import assert from 'node:assert/strict';
import test from 'node:test';
import {
  EDITOR_HEADING_KEYWORDS, breakBeforeNoticeMarks, isEditorHeading, splitKnowhowCardBody,
} from '../src/lib/knowhow-card-view.mjs';

// 実カード（knowledge/cards）の見出しと節構成を、短く切り詰めて写したもの。
const CHIME_399 = `# 乗場チャイム — AECH/AIL 同時適用で意図しない DN 音

## 使う場面・対象条件

**乗場電子音チャイム（AECH）** と **即時予報（AIL）** **同時適用** で、標準チャイムが鳴らない（Lists 399）。

## 症状・現象

- 到着予報後 **意図しないダウン音** 等（Lists 稲電見解）。

## ソース要約

### Lists（399）

- **机理**: かご待機階で上呼び → ①到着予報 → ②アップ音試行。

### OneNote

- なし。

## 統合した回答・ノウハウ

硬配線故障ではなく **ST S/W 更新処理** 論点（Lists）。

## 調査・確認手順

1. AECH + AIL 同時適用か。
2. かご待機階・上呼び再現。

## 関連事例と条件の違い

| list | 内容 |
| --- | --- |
| **399** | チャイム **信号合成** |

## KB確認に基づく追記

（該当なし）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | §399 |

## 未確認事項

- 修正 S/W の機種展開 — Lists のみ。
`;

const M1_397 = `# M1 カード — AC 低下 312 と急停止

## 使う場面・対象条件

**VFGLF** 工事使用中 **DOWN 急停止**（Lists 397）。

## 症状・現象

- 5 階付近等で急停止（Lists 例）。

## ソース要約

### Lists（397）

- 客先電源・仮設容量除外後 **M1 交換** → 改善。

## 統合した回答・ノウハウ

**101** とは **別経路**。

## 調査・確認手順

1. アラーム履歴 **312**。

## 正式資料

| 種別 | 参照 |
| --- | --- |
| Lists | §397 |

## 未確認事項

- なし。
`;

const CAR_LOCK_256 = `# かご固定装置 — 固定腕が穴に結合しない（Lists 索引）

## 使う場面・対象条件

Lists **256** — **対応中**。

## 症状・現象

- 固定腕が **穴に結合しない**（Lists タイトル）。

## ソース要約

### Lists（256）

- **cause / progress / Notes**: **未記載**。

## 統合した回答・ノウハウ

Lists 更新待ち。

## 調査・確認手順

1. Lists §256 の **追記** を確認。

## 関連事例と条件の違い

| カード | 備考 |
| --- | --- |
| **256** | **未確定** |

## KB確認に基づく追記

（なし）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | §256 |

## 未確認事項

- **全項目** — Lists 対応中。
`;

const BRACKET_115 = `# ブラケットスパン — 溶接検査時の位置変更

## 使う場面・対象条件

**溶接検査** でブラケット位置変更が必要なとき（Lists 115）。

## 症状・現象

- 位置変更の **明確基準が無い**（Lists）。

## ソース要約

### Lists（115）

- **3 条件**（満たせば変更可）。

## 統合した回答・ノウハウ

**最大許容値** と **設計最大値** を混同しない。

## 調査・確認手順

1. レール立図の元位置・設計スパン。

## 関連事例と条件の違い

| list | 内容 |
| --- | --- |
| **115** | ブラケット間隔 |

## KB確認に基づく追記

（SUE2-02.1 未索引）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | §115 |

## 未確認事項

- 添付①②は Lists 添付。
`;

const PIT_TRAP_394 = `# ピットタラップ取付位置と800mm基準の整理

## 使う場面・対象条件

- ピットタラップを **戸袋側へ移設**

## 症状・現象（入口キーワード）

- 社検: 三方枠から **815 mm**

## ソース要約

### Lists（list_item_id: 394）

**Notes（運用・判断）**

- 800 mm 超は **支店品証へ一報**

### OneNote（\`eb22f1b8-1002-4541-8190-5a019dc09673:1\`）

- **S-EL-323.1.pdf**

## 統合した回答・ノウハウ

据付 SUE-3-17 と社内検査 800 mm は **別レイヤの基準**。

## 調査・確認手順

1. 三方枠からタラップまでの距離

## 関連事例と条件の違い

| 基準 | 用途 |
| --- | --- |
| [据付・試験・調整ハブ](./KH-ALL-INSTALL-TEST-ADJUST-HUB.md) | 横断 |

## KB確認に基づく追記

## 正式資料・元情報（参照元）

| 種別 | 参照 |
| --- | --- |
| Lists | §394 |

## 未確認事項

- 現場確認
`;

const headings = (sections) => sections.map((section) => section.heading);

test('実カードを使う場面・症状・回答・手順・未確認は利用者向け、出どころの節は編集者向けに分ける', () => {
  const view = splitKnowhowCardBody(CHIME_399);
  assert.equal(view.title, '乗場チャイム — AECH/AIL 同時適用で意図しない DN 音');
  assert.deepEqual(headings(view.readerSections), ['使う場面・対象条件', '症状・現象', '統合した回答・ノウハウ', '調査・確認手順', '未確認事項']);
  // 「（該当なし）」だけの KB確認に基づく追記は両方から除かれる。
  assert.deepEqual(headings(view.editorSections), ['ソース要約', '関連事例と条件の違い', '正式資料・元情報']);
  assert.match(view.readerSections[0].markdown, /^## 使う場面・対象条件\n\n\*\*乗場電子音チャイム/u);
  assert.match(view.editorSections[0].markdown, /### OneNote/u);
});

test('見出しの揺れ（正式資料 / 参照元 / 入口キーワード / （なし）/ 空の節）を実カードどおりに扱う', () => {
  const m1 = splitKnowhowCardBody(M1_397);
  assert.deepEqual(headings(m1.editorSections), ['ソース要約', '正式資料']);
  assert.equal(headings(m1.readerSections).at(-1), '調査・確認手順', '「- なし。」だけの未確認事項は出さない');

  assert.deepEqual(headings(splitKnowhowCardBody(CAR_LOCK_256).editorSections), ['ソース要約', '関連事例と条件の違い', '正式資料・元情報']);

  const bracket = splitKnowhowCardBody(BRACKET_115);
  assert.ok(headings(bracket.editorSections).includes('KB確認に基づく追記'), '中身がある追記は残す');

  const pit = splitKnowhowCardBody(PIT_TRAP_394);
  assert.ok(headings(pit.readerSections).includes('症状・現象（入口キーワード）'));
  assert.deepEqual(headings(pit.editorSections), ['ソース要約', '関連事例と条件の違い', '正式資料・元情報（参照元）']);
  assert.ok(!headings(pit.editorSections).includes('KB確認に基づく追記'), '本文が無い節は出さない');
});

test('なし・該当なし・Lists のみ・ハイフンだけの節は両方から除く', () => {
  const body = ['# T', '', '## 手順', '', '1. 確認', '', '## 未確認事項', '', '- なし。', '', '## 補足', '', '（Lists のみ）', '',
    '## 別の節（該当なし）', '', '-', '', '## 見出しだけ', '', '### 小見出し', '', '- なし', ''].join('\n');
  const view = splitKnowhowCardBody(body);
  assert.deepEqual(headings(view.readerSections), ['手順']);
  assert.deepEqual(view.editorSections, []);
});

test('分類できない未知の節は利用者向けに残し、順序は元のまま', () => {
  const view = splitKnowhowCardBody('# T\n\n## 手順\n\n1. a\n\n## エレベーター — 制御方式別\n\n本文\n\n## 正式資料\n\n表\n\n## エレコール / SCU（comm）\n\n本文2\n');
  assert.deepEqual(headings(view.readerSections), ['手順', 'エレベーター — 制御方式別', 'エレコール / SCU（comm）']);
  assert.deepEqual(headings(view.editorSections), ['正式資料']);
});

test('## 見出しが無い本文は全体を1つの利用者向け節にする', () => {
  const view = splitKnowhowCardBody('# 題名\n\n本文だけ。\n\n- 箇条書き\n');
  assert.equal(view.title, '題名');
  assert.equal(view.readerSections.length, 1);
  assert.equal(view.readerSections[0].heading, '');
  assert.equal(view.readerSections[0].markdown, '本文だけ。\n\n- 箇条書き');
  assert.deepEqual(view.editorSections, []);
});

test('題名なしの本文、空文字、文字列以外でも落ちない', () => {
  assert.equal(splitKnowhowCardBody('## 手順\n\n1. a').title, '');
  assert.deepEqual(splitKnowhowCardBody(''), { title: '', readerSections: [], editorSections: [] });
  assert.deepEqual(splitKnowhowCardBody(undefined), { title: '', readerSections: [], editorSections: [] });
});

test('コードフェンス内の ## は見出しとして扱わない', () => {
  const body = '# T\n\n## 手順\n\n```\n## ソース要約\n中身\n```\n\n~~~\n## 正式資料\n~~~\n\n続き\n';
  const view = splitKnowhowCardBody(body);
  assert.deepEqual(headings(view.readerSections), ['手順']);
  assert.deepEqual(view.editorSections, []);
  assert.match(view.readerSections[0].markdown, /## ソース要約\n中身/u);
});

test('CRLF の本文も同じに分ける', () => {
  const view = splitKnowhowCardBody('# T\r\n\r\n## 手順\r\n\r\n1. a\r\n\r\n## ソース要約\r\n\r\n- x\r\n');
  assert.deepEqual(headings(view.readerSections), ['手順']);
  assert.deepEqual(headings(view.editorSections), ['ソース要約']);
  assert.ok(!view.readerSections[0].markdown.includes('\r'));
});

test('編集者向けの判定はキーワード表で行う', () => {
  assert.ok(EDITOR_HEADING_KEYWORDS.length > 0);
  assert.equal(isEditorHeading('正式資料・元情報（参照元）'), true);
  assert.equal(isEditorHeading('統合した回答・ノウハウ'), false);
  assert.equal(isEditorHeading('調査・確認手順'), false);
  assert.equal(isEditorHeading('未確認事項'), false);
});

test('行頭の※が単一改行で続くとき、別の段落になるよう空行を入れる', () => {
  assert.equal(breakBeforeNoticeMarks('※一つ目\n※二つ目\n本文'), '※一つ目\n\n※二つ目\n本文');
  assert.equal(breakBeforeNoticeMarks('本文\n※注意'), '本文\n\n※注意');
  assert.equal(breakBeforeNoticeMarks('※a\n\n※b'), '※a\n\n※b');
  assert.equal(breakBeforeNoticeMarks('※a\r\n※b'), '※a\n\n※b');
  assert.equal(breakBeforeNoticeMarks('文中の※は触らない\nつづき'), '文中の※は触らない\nつづき');
  assert.equal(breakBeforeNoticeMarks('```\n※a\n※b\n```'), '```\n※a\n※b\n```');
  assert.equal(breakBeforeNoticeMarks(undefined), '');
});
