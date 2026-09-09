---
status: reference
last-verified: 2026-08-26
related-code: lambda/rag/rag-function/app.py, frontend/src/data/kbModelTypes.ts, scripts/generate_kb_metadata_catalog.py
---

# RAG 絞り込みマッピング整理（取扱機種・UI項目・スコープ実測 2026-08-26）

> **位置づけ:** PR #37 の `HANDLED_MODEL_TYPES` / `UI_MODEL_FILTERS` 定義を、S3 実測メタデータ 3,745 件
> （[kb-metadata-catalog-2026-08-26.md](./kb-metadata-catalog-2026-08-26.md)）に当てた **2026-08-26 確認時点のスナップショット**。
> 本書の件数・分布・挙動は同時点の実測であり、将来の S3/KB 状態や AWS の仕様を恒久保証するものではない。
> 検証手法・環境事実は [verification-2026-08-26-kb-vqv-metadata.md](./verification-2026-08-26-kb-vqv-metadata.md) を正とする。
> **PR #37 マージ後の自動生成への引き継ぎは条件付き:** #37 同梱の `scripts/generate_model_filter_mapping.py` は
> 旧 `docs/kb-metadata-catalog.tsv`（3,492 件）を入力とする実装のため、そのまま引き継ぐと本書の実測前の状態へ戻る。
> **同ジェネレータを 8/26 実測データ形式（S3 `.metadata.json` 直読、3,745 件）へ更新・検証した後に引き継ぐこと。**

---

## 1. UI 機種絞り込み項目 → 対象機種 → 実測件数

UI に出す 6 項目。選択時は「対象機種のいずれかを含む資料 ＋ 全機種共通資料」が検索対象になる
（改修後は `orAll [listContains(各機種), listContains "*", listContains "general"]`）。

| UI 項目 | 展開される model_type | 完全一致件数 | +共通(常時) |
|---|---|---:|---:|
| AXIEZ | AXIEZ / AXIEZ(KE-WF・KE-HF) / 駅舎エレ | 1,137 | 819 |
| AXIEZ-LINKs | AXIEZ-LINKs | 913 | 819 |
| NEXCUBE | NEXCUBE / NEXCUBE Limited / 特注機械室レスエレベーター | 485 | 819 |
| メルシティ | メルシティ | 292 | 819 |
| メルワイド | メルワイド | 291 | 819 |
| エスカレーター | エスカレーター | 83 | 819 |

旧 stringContains の部分一致誤マッチは AXIEZ 項目のみ 752 件（listContains 化で検索前に消える）。

## 2. 取扱機種スコープ `HANDLED_MODEL_TYPES`（27 値）と実測件数

機種未指定でも適用されるスコープ。**共通資料（`*` / `general`）は常に対象**。
全 27 値が実データに存在する（0 件の空振りなし）。

| model_type | 件数 | | model_type | 件数 |
|---|---:|---|---|---:|
| NEXCUBE | 483 | | 標準小中形荷物用 | 6 |
| AXIEZ | 1116 | | 標準形荷物用 | 7 |
| AXIEZ-LINKs | 913 | | 特大形荷物用 | 6 |
| AXIEZ(KE-WF・KE-HF) | 146 | | 特注形荷物用 | 7 |
| 機械室レス荷物用(中抵製) | 329 | | 規格形荷物用 | 7 |
| メルシティ | 292 | | 中小形荷物用(中抵製) | 11 |
| メルワイド | 291 | | J* | 2 |
| NEXCUBE Limited | 71 | | LINKs上部作業床 | 1 |
| エスカレーター | 83 | | その他上部作業床 | 3 |
| 特注機械室レスエレベーター | 21 | | ボルトナット・アンカーボルト | 3 |
| 斜行エレベーター | 5 | | 治工具 | 5 |
| 大容量荷物用 | 6 | | レールブラケット | 42 |
| 大形荷物用 | 6 | | 駅舎エレ | 29 |
| 小形荷物用 | 6 | |  |  |

## 3. カテゴリ絞り込みとスコープの交差（実測）

UI カテゴリチップ（安定キー）→ 実 category → スコープ適用後の内訳。

| 安定キー | 実 category | 総数 | 共通(対象) | 取扱該当(対象) | 対象外 | UI掲載 |
|---|---|---:|---:|---:|---:|---|
| `drawing` | 据付場用図 | 2,027 | 0 | 1,675 | 352 | 掲載 |
| `spec` | C資料 | 729 | 302 | 317 | 110 | 掲載 |
| `tech_info` | テクニカルインフォメーション | 308 | 25 | 283 | 0 | 掲載 |
| `incident` | 災害事例集 | 294 | 294 | 0 | 0 | 掲載 |
| `qsheet` | Qシート | 156 | 51 | 105 | 0 | 掲載 |
| `std` | 据付基準 | 121 | 76 | 45 | 0 | 掲載 |
| `note` | 据付ノート | 67 | 33 | 34 | 0 | 掲載 |
| `site_agent` | 現場代理人業務マニュアル | 30 | 30 | 0 | 0 | **非掲載(要判断: 実在30件)** |
| `quality_mgmt` | 品質管理業務マニュアル | 7 | 7 | 0 | 0 | **非掲載(要判断: 実在7件)** |
| `w_doc` | W資料 | 5 | 0 | 0 | 5 | 掲載 |
| `—` | TEST | 1 | 1 | 0 | 0 | 非掲載(PR-4で遮断) |
| | **計** | **3,745** | **819** | **2,459** | **467** | |

> **⚠ W資料問題（業務判断待ち）:** W資料 5 件は全件スコープ対象外（機種が NEXIEZ-MRL Version 2）。
> スコープフィルタ併用時、`w_doc` チップを選んでも 0 件になる。対応候補 = W資料機種を
> `HANDLED_MODEL_TYPES` に追加 or W資料カテゴリをスコープ例外化。

## 4. スコープ判定ルール（改修後実装が採る仕様）

1. 共通資料: `model_type` の全要素が `*` / `general`（空欄は実データ 0 件）→ **常に検索対象**。
   判定は要素ベース `not els or all(e in {'', '*', 'general'} for e in els)`（`["*"]` 等の list 型対応。旧判定は 495 件を誤除外）。
2. 機種固有資料: 要素のいずれかが `HANDLED_MODEL_TYPES` に含まれれば対象。
3. どちらでもない資料: 対象外（下記 §5 の 467 件）。
4. 共通値と具体機種の混在リストは実データ 0 件（判定の曖昧さなし）。

> **注:** `listContains` の型混在（list / string）に対する挙動（カンマ連結 string は完全一致で拾えない等）は
> 2026-08-26 の VQV81CNYU4 実機確認に基づく実測事実であり、AWS の公式・恒久仕様として確定したものではない。
> AWS 側の挙動変更やフィルタ実装変更の際は実機で再確認すること。

## 5. スコープ対象外の全資料リスト（467 件・実測）

取扱機種スコープ導入（PR #37 系）後に **検索対象から外れる資料の全数**。モダニ/保守系機種が主。
スコープ見直し（機種追加）の際はこのリストと突き合わせること。

### 据付場用図（352 件）

| filename | model_type |
|---|---|
| `YA012B029_Z.pdf` | NEXIEZ-MRL Version 2 |
| `YA014B846_Y.pdf` | NEXIEZ-MRL Version 2 |
| `YA031A537_D.pdf` | NEXIEZ-MRL Version 2 |
| `YA031A538_D.pdf` | NEXIEZ-MRL Version 2 |
| `YA034A217_J.pdf` | NEXIEZ-MRL Version 2 |
| `YA034A218_I.pdf` | NEXIEZ-MRL Version 2 |
| `YA047A129_M.pdf` | NEXIEZ-MRL Version 2 |
| `YA047A162_O.pdf` | NEXIEZ-MRL Version 2 |
| `YA059A307_X.pdf` | NEXIEZ-MRL Version 2 |
| `YA062A984_B.pdf` | NEXIEZ-MRL Version 2 |
| `YA062A985_B.pdf` | NEXIEZ-MRL Version 2 |
| `YA063A585_B.pdf` | NEXIEZ-MRL Version 2 |
| `YA064A377_B.pdf` | NEXIEZ-MRL Version 2 |
| `YA065A653_I.pdf` | NEXIEZ-MRL Version 2 |
| `YA065A654_I.pdf` | NEXIEZ-MRL Version 2 |
| `YA066A220_G.pdf` | NEXIEZ-MRL Version 2 |
| `YA066A221_F.pdf` | NEXIEZ-MRL Version 2 |
| `YA070C053_F.pdf` | NEXIEZ-MRL Version 2 |
| `YA071A130_G.pdf` | NEXIEZ-MRL Version 2 |
| `YA071A131_G.pdf` | NEXIEZ-MRL Version 2 |
| `YA071A132_H.pdf` | NEXIEZ-MRL Version 2 |
| `YA073A271_C.pdf` | NEXIEZ-MRL Version 2 |
| `YA081A364_W.pdf` | NEXIEZ-MRL Version 2 |
| `YA081A366_U.pdf` | NEXIEZ-MRL Version 2 |
| `YA081A367_T.pdf` | NEXIEZ-MRL Version 2 |
| `YA091A112_B.pdf` | NEXIEZ-MRL Version 2 |
| `YA091A168_D.pdf` | NEXIEZ-MRL Version 2 |
| `YA092A009_F.pdf` | NEXIEZ-MRL Version 2 |
| `YA092A167_D.pdf` | NEXIEZ-MRL Version 2 |
| `YA095A488_A.pdf` | NEXIEZ-MRL Version 2 |
| `YA096A775_F.pdf` | NEXIEZ-MRL Version 2 |
| `YA099D541_J.pdf` | NEXIEZ-MRL Version 2 |
| `YA107A077_H.pdf` | NEXIEZ-MRL Version 2 |
| `YA107A172_I.pdf` | NEXIEZ-MRL Version 2 |
| `YA114A407_D.pdf` | NEXIEZ-MRL Version 2 |
| `YA114A408_E.pdf` | NEXIEZ-MRL Version 2 |
| `YA114A409_E.pdf` | NEXIEZ-MRL Version 2 |
| `YA114A410_E.pdf` | NEXIEZ-MRL Version 2 |
| `YA118A451_J.pdf` | NEXIEZ-MRL Version 2 |
| `YA118A570_B.pdf` | NEXIEZ-MRL Version 2 |
| `YA118A671_P.pdf` | NEXIEZ-MRL Version 2 |
| `YA118B177_H.pdf` | NEXIEZ-MRL Version 2 |
| `YA124C719_Q.pdf` | NEXIEZ-MRL Version 2 |
| `YA128A485_G.pdf` | NEXIEZ-MRL Version 2 |
| `YA128A490_M.pdf` | NEXIEZ-MRL Version 2 |
| `YA128A498_F.pdf` | NEXIEZ-MRL Version 2 |
| `YA128A539_B.pdf` | NEXIEZ-MRL Version 2 |
| `YA131A285_0.pdf` | NEXIEZ-MRL Version 2 |
| `YA131A471_I.pdf` | NEXIEZ-MRL Version 2 |
| `YA131A987_F.pdf` | NEXIEZ-MRL Version 2 |
| `YA132A731_A.pdf` | NEXIEZ-MRL Version 2 |
| `YA132A732_A.pdf` | NEXIEZ-MRL Version 2 |
| `YA133A697_A.pdf` | NEXIEZ-MRL Version 2 |
| `YA133A698_A.pdf` | NEXIEZ-MRL Version 2 |
| `YA136B736_I.pdf` | NEXIEZ-MRL Version 2 |
| `YA139A107_S.pdf` | NEXIEZ-MRL Version 2 |
| `YA139A339_0.pdf` | NEXIEZ-MRL Version 2 |
| `YA140C195_E.pdf` | NEXIEZ-MRL Version 2 |
| `YA141B237_O.pdf` | NEXIEZ-MRL Version 2 |
| `YA141D987_C.pdf` | NEXIEZ-MRL Version 2 |
| `YA144A423_J.pdf` | NEXIEZ-MRL Version 2 |
| `YA144A443_E.pdf` | NEXIEZ-MRL Version 2 |
| `YA144A467_G.pdf` | NEXIEZ-MRL Version 2 |
| `YA144A486_F.pdf` | NEXIEZ-MRL Version 2 |
| `YA144A489_C.pdf` | NEXIEZ-MRL Version 2 |
| `YA145C946_D.pdf` | NEXIEZ-MRL Version 2 |
| `YA150A520_D.pdf` | NEXIEZ-MRL Version 2 |
| `YA150A777_C.pdf` | NEXIEZ-MRL Version 2 |
| `YA150A778_H.pdf` | NEXIEZ-MRL Version 2 |
| `YA151A034_F.pdf` | NEXIEZ-MRL Version 2 |
| `YA151A160_A.pdf` | NEXIEZ-MRL Version 2 |
| `YA151A197_B.pdf` | NEXIEZ-MRL Version 2 |
| `YA155C203_K.pdf` | NEXIEZ-MRL Version 2 |
| `YA159A433_G.pdf` | NEXIEZ-MRL Version 2 |
| `YA159A434_G.pdf` | NEXIEZ-MRL Version 2 |
| `YA159A444_D.pdf` | NEXIEZ-MRL Version 2 |
| `YA159A445_D.pdf` | NEXIEZ-MRL Version 2 |
| `YA159A446_D.pdf` | NEXIEZ-MRL Version 2 |
| `YA162A932_I.pdf` | NEXIEZ-MRL Version 2 |
| `YA162A946_H.pdf` | NEXIEZ-MRL Version 2 |
| `YA163A290_G.pdf` | NEXIEZ-MRL Version 2 |
| `YA163A309_D.pdf` | NEXIEZ-MRL Version 2 |
| `YA163A340_H.pdf` | NEXIEZ-MRL Version 2 |
| `YA163A371_C.pdf` | NEXIEZ-MRL Version 2 |
| `YA163A381_D.pdf` | NEXIEZ-MRL Version 2 |
| `YA163A394_C.pdf` | NEXIEZ-MRL Version 2 |
| `YA164B851_G.pdf` | NEXIEZ-MRL Version 2 |
| `YA167B435_G.pdf` | NEXIEZ-MRL Version 2 |
| `YA170C222_O.pdf` | NEXIEZ-MRL Version 2 |
| `YA171B989_K.pdf` | NEXIEZ-MRL Version 2 |
| `YA173C234_C.pdf` | NEXIEZ-MRL Version 2 |
| `YA176A932_D.pdf` | NEXIEZ-MRL Version 2 |
| `YA177A044_C.pdf` | NEXIEZ-MRL Version 2 |
| `YA177A045_C.pdf` | NEXIEZ-MRL Version 2 |
| `YA177A052_D.pdf` | NEXIEZ-MRL Version 2 |
| `YA177A061_C.pdf` | NEXIEZ-MRL Version 2 |
| `YA177A062_A.pdf` | NEXIEZ-MRL Version 2 |
| `YA177A073_A.pdf` | NEXIEZ-MRL Version 2 |
| `YA177A076_B.pdf` | NEXIEZ-MRL Version 2 |
| `YA177A096_F.pdf` | NEXIEZ-MRL Version 2 |
| `YA179B253_L.pdf` | NEXIEZ-MRL Version 2 |
| `YA182A276_D.pdf` | NEXIEZ-MRL Version 2 |
| `YA182A282_K.pdf` | NEXIEZ-MRL Version 2 |
| `YA182A457_D.pdf` | NEXIEZ-MRL Version 2 |
| `YA182A458_0.pdf` | NEXIEZ-MRL Version 2 |
| `YA182A459_0.pdf` | NEXIEZ-MRL Version 2 |
| `YA182A464_0.pdf` | NEXIEZ-MRL Version 2 |
| `YA182A468_E.pdf` | NEXIEZ-MRL Version 2 |
| `YA182A483_B.pdf` | NEXIEZ-MRL Version 2 |
| `YA182A516_0.pdf` | NEXIEZ-MRL Version 2 |
| `YA182A584_B.pdf` | NEXIEZ-MRL Version 2 |
| `YA188A931_A.pdf` | NEXIEZ-MRL Version 2 |
| `YA188A979_A.pdf` | NEXIEZ-MRL Version 2 |
| `YA189A207_A.pdf` | NEXIEZ-MRL Version 2 |
| `YA189A247_B.pdf` | NEXIEZ-MRL Version 2 |
| `YA189A389_B.pdf` | NEXIEZ-MRL Version 2 |
| `YA189A596_0.pdf` | NEXIEZ-MRL Version 2 |
| `YA189C286_0.pdf` | NEXIEZ-MRL Version 2 |
| `YA190A304_C.pdf` | NEXIEZ-MRL Version 2 |
| `YA190A324_A.pdf` | NEXIEZ-MRL Version 2 |
| `YA190A325_A.pdf` | NEXIEZ-MRL Version 2 |
| `YA190A333_F.pdf` | NEXIEZ-MRL Version 2 |
| `YA190A335_F.pdf` | NEXIEZ-MRL Version 2 |
| `YA190A338_A.pdf` | NEXIEZ-MRL Version 2 |
| `YA190A339_A.pdf` | NEXIEZ-MRL Version 2 |
| `YA190A340_A.pdf` | NEXIEZ-MRL Version 2 |
| `YA190A341_A.pdf` | NEXIEZ-MRL Version 2 |
| `YA190A346_C.pdf` | NEXIEZ-MRL Version 2 |
| `YA192A625_0.pdf` | NEXIEZ-MRL Version 2 |
| `YA192A627_0.pdf` | NEXIEZ-MRL Version 2 |
| `YA192A837_0.pdf` | NEXIEZ-MRL Version 2 |
| `YA206D238_A.pdf` | NEXIEZ-MRL Version 2 |
| `YA210D598_0.pdf` | NEXIEZ-MRL Version 2 |
| `YA212B759_F.pdf` | NEXIEZ-MRL Version 2 |
| `YA212D190_0.pdf` | NEXIEZ-MRL Version 2 |
| `YA215C502_B.pdf` | NEXIEZ-MRL Version 2 |
| `YA215C503_0.pdf` | NEXIEZ-MRL Version 2 |
| `YA218C882_C.pdf` | NEXIEZ-MRL Version 2 |
| `YA239B531_B.pdf` | NEXIEZ-MRL Version 2 |
| `YA239B546_B.pdf` | NEXIEZ-MRL Version 2 |
| `YA239B630_0.pdf` | NEXIEZ-MRL Version 2 |
| `YA254B257_D.pdf` | NEXIEZ-MRL Version 2 |
| `YA266B783_D.pdf` | NEXIEZ-MRL Version 2 |
| `YA266B797_D.pdf` | NEXIEZ-MRL Version 2 |
| `YA266B953_0.pdf` | NEXIEZ-MRL Version 2 |
| `YA267B040_A.pdf` | NEXIEZ-MRL Version 2 |
| `YA267B044_B.pdf` | NEXIEZ-MRL Version 2 |
| `YA271B965_C.pdf` | NEXIEZ-MRL Version 2 |
| `YA282B715_0.pdf` | NEXIEZ-MRL Version 2 |
| `YA282B749_E.pdf` | NEXIEZ-MRL Version 2 |
| `YA283B019_A.pdf` | NEXIEZ-MRL Version 2 |
| `YA291C921_C.pdf` | NEXIEZ-MRL Version 2 |
| `YA292B484_E.pdf` | NEXIEZ-MRL Version 2 |
| `YA302B722_B.pdf` | NEXIEZ-MRL Version 2 |
| `YA302B817_D.pdf` | NEXIEZ-MRL Version 2 |
| `YA302B821_D.pdf` | NEXIEZ-MRL Version 2 |
| `YA302B822_F.pdf` | NEXIEZ-MRL Version 2 |
| `YA302B856_E.pdf` | NEXIEZ-MRL Version 2 |
| `YA303B155_C.pdf` | NEXIEZ-MRL Version 2 |
| `YA303B350_0.pdf` | NEXIEZ-MRL Version 2 |
| `YA303B413_A.pdf` | NEXIEZ-MRL Version 2 |
| `YA303B425_C.pdf` | NEXIEZ-MRL Version 2 |
| `YA304C875_H.pdf` | NEXIEZ-MRL Version 2 |
| `YA307B024_C.pdf` | NEXIEZ-MRL Version 2 |
| `YA307B090_0.pdf` | NEXIEZ-MRL Version 2 |
| `YA307B282_0.pdf` | NEXIEZ-MRL Version 2 |
| `YA314C459_C.pdf` | NEXIEZ-MRL Version 2 |
| `YA314C565_B.pdf` | NEXIEZ-MRL Version 2 |
| `YA323B401_A.pdf` | NEXIEZ-MRL Version 2 |
| `YA323B402_A.pdf` | NEXIEZ-MRL Version 2 |
| `YA323B600_0.pdf` | NEXIEZ-MRL Version 2 |
| `YA323B669_A.pdf` | NEXIEZ-MRL Version 2 |
| `YA323B738_B.pdf` | NEXIEZ-MRL Version 2 |
| `YA323B780_B.pdf` | NEXIEZ-MRL Version 2 |
| `YA323B812_C.pdf` | NEXIEZ-MRL Version 2 |
| `YA323B815_A.pdf` | NEXIEZ-MRL Version 2 |
| `YA325C995_D.pdf` | NEXIEZ-MRL Version 2 |
| `YA332C939_B.pdf` | NEXIEZ-MRL Version 2 |
| `YA335B415_E.pdf` | NEXIEZ-MRL Version 2 |
| `YA339C533_A.pdf` | NEXIEZ-MRL Version 2 |
| `YA339C551_A.pdf` | NEXIEZ-MRL Version 2 |
| `YA339C552_A.pdf` | NEXIEZ-MRL Version 2 |
| `YA339C605_B.pdf` | NEXIEZ-MRL Version 2 |
| `YA342C574_A.pdf` | NEXIEZ-MRL Version 2 |
| `YA342C575_A.pdf` | NEXIEZ-MRL Version 2 |
| `YA342C576_A.pdf` | NEXIEZ-MRL Version 2 |
| `YA342C853_0.pdf` | NEXIEZ-MRL Version 2 |
| `YA346B014_K.pdf` | NEXIEZ-MRL Version 2 |
| `YA346B026_G.pdf` | NEXIEZ-MRL Version 2 |
| `YA346B068_0.pdf` | NEXIEZ-MRL Version 2 |
| `YA346B089_0.pdf` | NEXIEZ-MRL Version 2 |
| `YA346B090_A.pdf` | NEXIEZ-MRL Version 2 |
| `YA346B092_0.pdf` | NEXIEZ-MRL Version 2 |
| `YA346B169_A.pdf` | NEXIEZ-MRL Version 2 |
| `YA346B179_0.pdf` | NEXIEZ-MRL Version 2 |
| `YA347B043_0.pdf` | NEXIEZ-MRL Version 2 |
| `YA347B047_A.pdf` | NEXIEZ-MRL Version 2 |
| `YA347B051_0.pdf` | NEXIEZ-MRL Version 2 |
| `YA347B052_C.pdf` | NEXIEZ-MRL Version 2 |
| `YA347B071_B.pdf` | NEXIEZ-MRL Version 2 |
| `YA347B092_0.pdf` | NEXIEZ-MRL Version 2 |
| `YA361C715_F.pdf` | NEXIEZ-MRL Version 2 |
| `YA363B807_C.pdf` | NEXIEZ-MRL Version 2 |
| `YA363B862_A.pdf` | NEXIEZ-MRL Version 2 |
| `YA363B870_0.pdf` | NEXIEZ-MRL Version 2 |
| `YA363B871_C.pdf` | NEXIEZ-MRL Version 2 |
| `YA363B947_E.pdf` | NEXIEZ-MRL Version 2 |
| `YA363B948_E.pdf` | NEXIEZ-MRL Version 2 |
| `YA364B032_F.pdf` | NEXIEZ-MRL Version 2 |
| `YA364B080_B.pdf` | NEXIEZ-MRL Version 2 |
| `YA365B414_0.pdf` | NEXIEZ-MRL Version 2 |
| `YA367C299_0.pdf` | NEXIEZ-MRL Version 2 |
| `YA367C300_0.pdf` | NEXIEZ-MRL Version 2 |
| `YA367C301_0.pdf` | NEXIEZ-MRL Version 2 |
| `YA367C381_B.pdf` | NEXIEZ-MRL Version 2 |
| `YA367C383_0.pdf` | NEXIEZ-MRL Version 2 |
| `YA368B612_A.pdf` | NEXIEZ-MRL Version 2 |
| `YA368B661_0.pdf` | NEXIEZ-MRL Version 2 |
| `YA374B177_0.pdf` | NEXIEZ-MRL Version 2 |
| `YA374B195_0.pdf` | NEXIEZ-MRL Version 2 |
| `YA378C871_A.pdf` | NEXIEZ-MRL Version 2 |
| `YA381C929_0.pdf` | NEXIEZ-MRL Version 2 |
| `YA383C105_0.pdf` | NEXIEZ-MRL Version 2 |
| `YE205C253_B.pdf` | NEXIEZ-MRL Version 2 |
| `YE207C004_A.pdf` | NEXIEZ-MRL Version 2 |
| `YE207C114_A.pdf` | NEXIEZ-MRL Version 2 |
| `YE316C668_0.pdf` | NEXIEZ-MRL Version 2 |
| `YE316C670_C.pdf` | NEXIEZ-MRL Version 2 |
| `YE317C100_AM.pdf` | NEXIEZ-MRL Version 2 |
| `YE317C300_W.pdf` | NEXIEZ-MRL Version 2 |
| `YE317C401_Q.pdf` | NEXIEZ-MRL Version 2 |
| `YE400B232_C.pdf` | NEXIEZ-MRL Version 2 |
| `YE400C057_D.pdf` | NEXIEZ-MRL Version 2 |
| `YE401A202_F.pdf` | NEXIEZ-MRL Version 2 |
| `YE401A214_0.pdf` | NEXIEZ-MRL Version 2 |
| `YE401A215_A.pdf` | NEXIEZ-MRL Version 2 |
| `YE401A216_0.pdf` | NEXIEZ-MRL Version 2 |
| `YE401A218_0.pdf` | NEXIEZ-MRL Version 2 |
| `YE401B196_G.pdf` | NEXIEZ-MRL Version 2 |
| `YE401B744_B.pdf` | NEXIEZ-MRL Version 2 |
| `YE401B745_B.pdf` | NEXIEZ-MRL Version 2 |
| `YE401B779_0.pdf` | NEXIEZ-MRL Version 2 |
| `YE402B114_0.pdf` | NEXIEZ-MRL Version 2 |
| `YE402B201_0.pdf` | NEXIEZ-MRL Version 2 |
| `YE402B202_C.pdf` | NEXIEZ-MRL Version 2 |
| `YE402B205_0.pdf` | NEXIEZ-MRL Version 2 |
| `YE402B208_0.pdf` | NEXIEZ-MRL Version 2 |
| `YE402B214_C.pdf` | NEXIEZ-MRL Version 2 |
| `YE402B215_C.pdf` | NEXIEZ-MRL Version 2 |
| `YE402B216_C.pdf` | NEXIEZ-MRL Version 2 |
| `YE402B217_0.pdf` | NEXIEZ-MRL Version 2 |
| `YE402B218_0.pdf` | NEXIEZ-MRL Version 2 |
| `YE402B235_0.pdf` | NEXIEZ-MRL Version 2 |
| `YE402B240_0.pdf` | NEXIEZ-MRL Version 2 |
| `YE606B372_0.pdf` | NEXIEZ-MRL Version 2 |
| `YX204C238_A.pdf` | NEXIEZ-MRL Version 2 |
| `YX204C249_C.pdf` | NEXIEZ-MRL Version 2 |
| `YX204C250_A.pdf` | NEXIEZ-MRL Version 2 |
| `YX301C812_G.pdf` | NEXIEZ-MRL Version 2 |
| `YX304C224_0.pdf` | NEXIEZ-MRL Version 2 |
| `YX304C687_A.pdf` | NEXIEZ-MRL Version 2 |
| `YX401B959_C.pdf` | NEXIEZ-MRL Version 2 |
| `YX401D266_F.pdf` | NEXIEZ-MRL Version 2 |
| `YA012B029_Z.pdf` | NEXIEZ-MRL Version 2 |
| `YA047A129_M.pdf` | NEXIEZ-MRL Version 2 |
| `YA047A162_O.pdf` | NEXIEZ-MRL Version 2 |
| `YA059A307_X.pdf` | NEXIEZ-MRL Version 2 |
| `YA070C053_F.pdf` | NEXIEZ-MRL Version 2 |
| `YA081A364_W.pdf` | NEXIEZ-MRL Version 2 |
| `YA081A366_U.pdf` | NEXIEZ-MRL Version 2 |
| `YA081A367_T.pdf` | NEXIEZ-MRL Version 2 |
| `YA118A451_J.pdf` | NEXIEZ-MRL Version 2 |
| `YA118B177_H.pdf` | NEXIEZ-MRL Version 2 |
| `YA124C719_Q.pdf` | NEXIEZ-MRL Version 2 |
| `YA131A987_F.pdf` | NEXIEZ-MRL Version 2 |
| `YA136B736_I.pdf` | NEXIEZ-MRL Version 2 |
| `YA144A423_J.pdf` | NEXIEZ-MRL Version 2 |
| `YA144A489_C.pdf` | NEXIEZ-MRL Version 2 |
| `YA164B851_G.pdf` | NEXIEZ-MRL Version 2 |
| `YA173C234_C.pdf` | NEXIEZ-MRL Version 2 |
| `YA179B253_L.pdf` | NEXIEZ-MRL Version 2 |
| `YA182A276_D.pdf` | NEXIEZ-MRL Version 2 |
| `YA182A282_K.pdf` | NEXIEZ-MRL Version 2 |
| `YA190A304_C.pdf` | NEXIEZ-MRL Version 2 |
| `YA190A346_C.pdf` | NEXIEZ-MRL Version 2 |
| `YA302B722_B.pdf` | NEXIEZ-MRL Version 2 |
| `YA346B014_K.pdf` | NEXIEZ-MRL Version 2 |
| `YA346B026_G.pdf` | NEXIEZ-MRL Version 2 |
| `YA361C715_F.pdf` | NEXIEZ-MRL Version 2 |
| `YA368B612_A.pdf` | NEXIEZ-MRL Version 2 |
| `YE207C004_A.pdf` | NEXIEZ-MRL Version 2 |
| `YE316C668_0.pdf` | NEXIEZ-MRL Version 2 |
| `YE316C670_C.pdf` | NEXIEZ-MRL Version 2 |
| `YE317C100_AM.pdf` | NEXIEZ-MRL Version 2 |
| `YE317C300_W.pdf` | NEXIEZ-MRL Version 2 |
| `YE317C401_Q.pdf` | NEXIEZ-MRL Version 2 |
| `YE400B232_C.pdf` | NEXIEZ-MRL Version 2 |
| `YE400C057_D.pdf` | NEXIEZ-MRL Version 2 |
| `YE401B196_G.pdf` | NEXIEZ-MRL Version 2 |
| `YE402B201_0.pdf` | NEXIEZ-MRL Version 2 |
| `YE402B202_C.pdf` | NEXIEZ-MRL Version 2 |
| `YE402B205_0.pdf` | NEXIEZ-MRL Version 2 |
| `YE402B208_0.pdf` | NEXIEZ-MRL Version 2 |
| `YX204C238_A.pdf` | NEXIEZ-MRL Version 2 |
| `YX301C812_G.pdf` | NEXIEZ-MRL Version 2 |
| `YX304C687_A.pdf` | NEXIEZ-MRL Version 2 |
| `YX401B959_C.pdf` | NEXIEZ-MRL Version 2 |
| `YA012B029_Z.pdf` | NEXIEZ-MRL Version 2 |
| `YA014B846_Y.pdf` | NEXIEZ-MRL Version 2 |
| `YA031A537_D.pdf` | NEXIEZ-MRL Version 2 |
| `YA031A538_D.pdf` | NEXIEZ-MRL Version 2 |
| `YA047A129_M.pdf` | NEXIEZ-MRL Version 2 |
| `YA047A162_O.pdf` | NEXIEZ-MRL Version 2 |
| `YA070C053_F.pdf` | NEXIEZ-MRL Version 2 |
| `YA081A364_W.pdf` | NEXIEZ-MRL Version 2 |
| `YA081A366_U.pdf` | NEXIEZ-MRL Version 2 |
| `YA081A367_T.pdf` | NEXIEZ-MRL Version 2 |
| `YA118B177_H.pdf` | NEXIEZ-MRL Version 2 |
| `YA124C719_Q.pdf` | NEXIEZ-MRL Version 2 |
| `YA131A471_I.pdf` | NEXIEZ-MRL Version 2 |
| `YA139A107_S.pdf` | NEXIEZ-MRL Version 2 |
| `YA144A489_C.pdf` | NEXIEZ-MRL Version 2 |
| `YA155C203_K.pdf` | NEXIEZ-MRL Version 2 |
| `YA170C222_O.pdf` | NEXIEZ-MRL Version 2 |
| `YA171B989_K.pdf` | NEXIEZ-MRL Version 2 |
| `YA173C234_C.pdf` | NEXIEZ-MRL Version 2 |
| `YA179B253_L.pdf` | NEXIEZ-MRL Version 2 |
| `YA182A282_K.pdf` | NEXIEZ-MRL Version 2 |
| `YA302B722_B.pdf` | NEXIEZ-MRL Version 2 |
| `YA363B947_E.pdf` | NEXIEZ-MRL Version 2 |
| `YA363B948_E.pdf` | NEXIEZ-MRL Version 2 |
| `YA364B032_F.pdf` | NEXIEZ-MRL Version 2 |
| `YA364B080_B.pdf` | NEXIEZ-MRL Version 2 |
| `YE400B232_C.pdf` | NEXIEZ-MRL Version 2 |
| `YE606B372_0.pdf` | NEXIEZ-MRL Version 2 |
| `YX301C812_G.pdf` | NEXIEZ-MRL Version 2 |
| `YA012B029_Z.pdf` | NEXIEZ-MRL Version 2 |
| `YA014B846_Y.pdf` | NEXIEZ-MRL Version 2 |
| `YA096A775_F.pdf` | NEXIEZ-MRL Version 2 |
| `YA107A172_I.pdf` | NEXIEZ-MRL Version 2 |
| `YA131A471_I.pdf` | NEXIEZ-MRL Version 2 |
| `YA190A304_C.pdf` | NEXIEZ-MRL Version 2 |
| `YA014B846_Y.pdf` | NEXIEZ-MRL Version 2 |
| `YA107A172_I.pdf` | NEXIEZ-MRL Version 2 |
| `YA131A471_I.pdf` | NEXIEZ-MRL Version 2 |
| `YA139A107_S.pdf` | NEXIEZ-MRL Version 2 |
| `YA171B989_K.pdf` | NEXIEZ-MRL Version 2 |
| `YA363B947_E.pdf` | NEXIEZ-MRL Version 2 |
| `YA363B948_E.pdf` | NEXIEZ-MRL Version 2 |
| `YA364B032_F.pdf` | NEXIEZ-MRL Version 2 |
| `YA364B080_B.pdf` | NEXIEZ-MRL Version 2 |
| `YE606B372_0.pdf` | NEXIEZ-MRL Version 2 |

### C資料（110 件）

| filename | model_type |
|---|---|
| `C-1-C110.1-E-H.pdf` | ELENESSA / ELENESSA-AP / ELENESSA-IP / MAXIEZ LZ / NEXIEZ-MRL / NEXIEZ-MRL Version 2 / NEXIEZ-Fit |
| `C-1-C125-E-A.pdf` | NEXIEZ-MRL |
| `C-1-C130.1-E-E.pdf` | ELENESSA / ELENESSA-AP / ELENESSA-IP / MAXIEZ LZ / NEXIEZ-MRL / NEXIEZ-MRL Version 2 / NEXIEZ-Fit |
| `C-1-C300-E-N.pdf` | DIAMOND TRAC / DIAMOND HS / Diamond Trac2 / ELENESSA / ELENESSA-AP / ELENESSA-IP / MAXIEZ-B / MAXIEZ CZ / MAXIEZ LZ / NEXIEZ / NEXIEZ-MRL / NEXIEZ-MRL Version 2 / NEXIEZ-Fit / NexWay / NexWay-S |
| `C-1-C400.1-E-B.pdf` | NEXIEZ-MRL |
| `C-1-C400.1-J-B.pdf` | NEXIEZ-MRL |
| `C-10-B5.11-E-B.pdf` | NEXIEZ-MRL Version 2 / NEXIEZ-Fit |
| `C-10-C10.23-E-B.pdf` | NEXIEZ-MRL Version 2 / NEXIEZ-Fit |
| `C-18-A26.1-B-A.pdf` | Diamond Trac2 / ELENESSA / MAXIEZ CZ / MAXIEZ LZ / NEXIEZ / NEXIEZ-MRL / NEXIEZ-MRL Version 2 / NexWay / NexWay-S |
| `C-18-A9-491.1-E-C.pdf` | DIAMOND TRAC / DIAMOND HS / Diamond Trac2 / NEXIEZ / NEXIEZ-MRL Version 2 / NEXIEZ-Fit / NexWay / NexWay-S |
| `C-18-A9.314-E-A.pdf` | DIAMOND TRAC / DIAMOND HS / Diamond Trac2 / ELENESSA / GPM-3U / MAXIEZ-B / MAXIEZ CZ / MAXIEZ LZ / NEXIEZ / NEXIEZ-MRL / NEXIEZ-MRL Version 2 / NEXIEZ-GPX / NEXIEZ-GPX-MRL / NEXIEZ-LITE / NEXIEZ-LITE MRL / NEXIEZ-Fit / NexWay / NexWay MODERNIZATION / NexWay-S / NexWay-S MODERNIZATION / COMPACT4 / MELWIDE / MELCITY / NEXIEZ-S |
| `C-18-C14.1-E-D.pdf` | DIAMOND TRAC / DIAMOND HS / Diamond Trac2 / DeLITE / ELENESSA / ELENESSA-AP / ELENESSA-IP / ELEMOTION-IH / ELEMOTION-LS / ELEMOTION-HS / ELEMOTION-IM / ELEMOTION-TY / ELEMOTION-TZ / ELEMOTION-IZ / ELEMOTION-AZ / GPM-3U / MAXIEZ-B / MAXIEZ CZ / MAXIEZ LZ / MAXIEZ-M / MAXIEZ-H / NEXIEZ / NEXIEZ-MRL / NEXIEZ-MRL Version 2 / NEXIEZ-MRL MP / NEXIEZ-GPX / NEXIEZ-GPX-MRL / NEXIEZ-LITE / NEXIEZ-LITE MRL / NEXIEZ-Fit / NexWay / NexWay MODERNIZATION / NexWay-S / NexWay-S MODERNIZATION / COMPACT4 / MELWIDE / MELCITY / NEXIEZ-S |
| `C-18-D59.1-E-B.pdf` | NEXIEZ-MRL Version 2 |
| `C-18-D60-K1.1-E-A.pdf` | DIAMOND TRAC / Diamond Trac2 / NEXIEZ-MRL Version 2 |
| `C-18-D61-K1.1-E-_.pdf` | MAXIEZ-B / MAXIEZ CZ / MAXIEZ LZ / NEXIEZ / NEXIEZ-MRL / NEXIEZ-MRL Version 2 / NEXIEZ-GPX / NEXIEZ-GPX-MRL / NEXIEZ-LITE / NEXIEZ-LITE MRL / NexWay-S |
| `C-19-A81.1-E-_.pdf` | NEXIEZ-MRL |
| `C-19-G3.1-E-C.pdf` | DIAMOND TRAC / Diamond Trac2 / NEXIEZ-MRL |
| `C-19-G5.1-E-B.pdf` | ELENESSA / MAXIEZ LZ / NEXIEZ-MRL |
| `C-19-S2.1-E-D.pdf` | Diamond Trac2 / ELENESSA / ELENESSA-AP / ELENESSA-IP / MAXIEZ-B / MAXIEZ LZ / NEXIEZ-MRL |
| `C-20-D5.1-E-A.pdf` | Diamond Trac2 / NEXIEZ-MRL |
| `C-23-B10.1-B-C.pdf` | DIAMOND TRAC / NEXIEZ-MRL / NEXIEZ-GPX-MRL / NEXIEZ-LITE / NEXIEZ-S |
| `C-23-B11.2-B-_.pdf` | NEXIEZ-MRL |
| `C-23-B6.2-B-_.pdf` | ELENESSA / MAXIEZ-B / MAXIEZ CZ / MAXIEZ LZ / NEXIEZ / NEXIEZ-MRL / NexWay / NexWay-S / E* |
| `C-3-F53-E-A.pdf` | NEXIEZ-MRL |
| `C-3-F54-E-B.pdf` | Diamond Trac2 / NEXIEZ-MRL / NEXIEZ-MRL Version 2 |
| `C-3-F57-E-_.pdf` | NEXIEZ-MRL Version 2 |
| `C-30-A26.1-E-A.pdf` | NEXIEZ-MRL Version 2 / NEXIEZ-Fit |
| `C-30-E6.106-E-_.pdf` | NEXIEZ-MRL |
| `C-30-E6.108-E-_.pdf` | NEXIEZ-MRL |
| `C-30-H2.1-E-_.pdf` | NEXIEZ-MRL Version 2 |
| `C-32-A21.1-E-_.pdf` | NEXIEZ-MRL / NEXIEZ-GPX / NEXIEZ-GPX-MRL |
| `C-32-A22.1-E-_.pdf` | NEXIEZ-MRL |
| `C-32-A23.1-E-A.pdf` | NEXIEZ-MRL |
| `C-32-A261.1-E-A.pdf` | GPM-III / GPS-III |
| `C-32-A295.1-E-_.pdf` | ELENESSA / ELEMOTION-TZ / ELEMOTION-IZ / ELEMOTION-AZ / MAXIEZ CZ / MAXIEZ LZ / NEXIEZ / NEXIEZ-MRL / NEXIEZ-GPX / NEXIEZ-GPX-MRL / NexWay / NexWay-S |
| `C-32-A902.1-E-_.pdf` | NEXIEZ-MRL |
| `C-32-B100.1-E-D.pdf` | ELENESSA / ELEMOTION-IM / ELEMOTION-TZ / ELEMOTION-IZ / ELEMOTION-AZ / GPM-III / MAXIEZ-B / MAXIEZ CZ / NEXIEZ / NEXIEZ-MRL / NexWay / NexWay-S |
| `C-32-B110.1-E-A.pdf` | ELENESSA / ELEMOTION-IM / ELEMOTION-TZ / ELEMOTION-IZ / ELEMOTION-AZ / NEXIEZ / NEXIEZ-MRL / NexWay / NexWay-S |
| `C-32-B120.1-E-D.pdf` | ELENESSA / MAXIEZ-H / MAXIEZ-M / MAXIEZ CZ / MAXIEZ LZ / NEXIEZ / NEXIEZ-MRL / NexWay / NexWay-S |
| `C-32-B121.2-E-_.pdf` | ELENESSA / ELEMOTION-IH / ELEMOTION-IM / ELEMOTION-TZ / ELEMOTION-IZ / ELEMOTION-AZ / NEXIEZ / NEXIEZ-MRL / NexWay / NexWay-S |
| `C-32-B122.1-E-B.pdf` | DIAMOND TRAC / DIAMOND HS / Diamond Trac2 / ELENESSA / ELEMOTION-IH / ELEMOTION-LS / ELEMOTION-HS / ELEMOTION-IM / ELEMOTION-TZ / ELEMOTION-IZ / ELEMOTION-AZ / GPM-3U / MAXIEZ CZ / MAXIEZ LZ / NEXIEZ / NEXIEZ-MRL / NexWay / NexWay-S |
| `C-32-B125.1-E-C.pdf` | DIAMOND TRAC / DIAMOND HS / Diamond Trac2 / ELENESSA / ELEMOTION-IH / ELEMOTION-LS / ELEMOTION-HS / ELEMOTION-IM / ELEMOTION-TZ / ELEMOTION-IZ / ELEMOTION-AZ / GPM-3U / MAXIEZ CZ / MAXIEZ LZ / NEXIEZ / NEXIEZ-MRL / NexWay / NexWay-S |
| `C-32-B126.1-E-A.pdf` | DIAMOND TRAC / DIAMOND HS / Diamond Trac2 / ELENESSA / ELEMOTION-IH / ELEMOTION-LS / ELEMOTION-HS / ELEMOTION-IM / ELEMOTION-TZ / ELEMOTION-IZ / NEXIEZ-MRL / NexWay / NexWay-S |
| `C-32-B130.1-E-B.pdf` | DIAMOND TRAC / DIAMOND HS / Diamond Trac2 / ELENESSA / ELEMOTION-LS / MAXIEZ CZ / MAXIEZ LZ / NEXIEZ / NEXIEZ-MRL / NexWay / NexWay-S |
| `C-32-B140.1-B-_.pdf` | ELEMOTION-AZ / NEXIEZ / NEXIEZ-MRL Version 2 / AT-MOD |
| `C-32-B160.1-E-_.pdf` | NEXIEZ-MRL |
| `C-32-B190.1-E-_.pdf` | NEXIEZ-MRL |
| `C-32-B28.45-E-A.pdf` | ELENESSA / ELEMOTION-IM / ELEMOTION-TZ / ELEMOTION-IZ / ELEMOTION-AZ / NEXIEZ / NEXIEZ-MRL / NexWay / NexWay-S |
| `C-32-B32.11-E-C.pdf` | ELENESSA / ELEMOTION-IM / ELEMOTION-TZ / ELEMOTION-IZ / ELEMOTION-AZ / NEXIEZ / NEXIEZ-MRL / NexWay / NexWay-S |
| `C-32-B32.4-E-_.pdf` | NEXIEZ-MRL |
| `C-32-B32.50-E-D.pdf` | ELENESSA / ELEMOTION-IM / ELEMOTION-TY / ELEMOTION-TZ / ELEMOTION-IZ / ELEMOTION-AZ / NEXIEZ / NEXIEZ-MRL / NEXIEZ-GPX / NEXIEZ-GPX-MRL / NEXIEZ-LITE / NEXIEZ-LITE MRL / NexWay / NexWay-S |
| `C-32-B34.1-E-B.pdf` | ELENESSA / ELEMOTION-IM / ELEMOTION-TZ / ELEMOTION-IZ / ELEMOTION-AZ / NEXIEZ / NEXIEZ-MRL / NEXIEZ-LITE / NEXIEZ-LITE MRL / NexWay / NexWay-S |
| `C-32-B35.1-E-A.pdf` | NEXIEZ-MRL |
| `C-32-B41.1-E-D.pdf` | ELENESSA / ELEMOTION-IM / ELEMOTION-TZ / ELEMOTION-IZ / ELEMOTION-AZ / NEXIEZ / NEXIEZ-MRL / NEXIEZ-MRL Version 2 / NEXIEZ-GPX / NEXIEZ-GPX-MRL / NexWay / NexWay-S |
| `C-32-B61.1-E-A.pdf` | ELENESSA / ELENESSA-IP / ELEMOTION-IM / ELEMOTION-TZ / ELEMOTION-IZ / ELEMOTION-AZ / MAXIEZ CZ / MAXIEZ LZ / NEXIEZ / NEXIEZ-MRL / NexWay / NexWay-S |
| `C-32-B61.5-E-B.pdf` | ELENESSA / ELEMOTION-IM / ELEMOTION-TZ / ELEMOTION-IZ / ELEMOTION-AZ / NEXIEZ / NEXIEZ-MRL / NexWay / NexWay-S |
| `C-32-B90.1-E-C.pdf` | ELENESSA / GPM-III / NEXIEZ / NEXIEZ-MRL / NexWay / NexWay-S |
| `C-32-C8.91-E-A.pdf` | ELENESSA / NEXIEZ / NEXIEZ-MRL / NexWay / NexWay-S |
| `C-32-C8.92-E-A.pdf` | NEXIEZ-MRL |
| `C-32-C81.1-E-A.pdf` | NEXIEZ / NEXIEZ-MRL / NEXIEZ-MRL Version 2 / NexWay / NexWay-S / MELWIDE / MELCITY |
| `C-32-D-B15.3-E-_.pdf` | ELEMOTION-AZ / NEXIEZ / NEXIEZ-MRL Version 2 / AT-MOD |
| `C-35-L1.1-J-_.pdf` | ELENESSA / MAXIEZ CZ / MAXIEZ LZ / NEXIEZ / NEXIEZ-MRL / NexWay / NexWay-S |
| `C-41-B184.2-B-_-01.pdf` | モダニゼーション |
| `C-41-C148.30-E-C.pdf` | NEXIEZ-MRL Version 2 |
| `C-41-C148.31-E-_.pdf` | NEXIEZ-MRL |
| `C-41-C148.60-E-_.pdf` | NEXIEZ-MRL Version 2 |
| `C-41-C148.61-E-_.pdf` | NEXIEZ-MRL Version 2 |
| `C-41-D-C300.1-J-A.pdf` | Elemotion+ / Elemotion+ [ZERO] / ELEMOTION E系制御改修(巻上機取替) / ELEMOTION E系制御改修(巻上機流用) / ELEMOTION M系制御改修(巻上機取替) / ELEMOTION M系制御改修(巻上機流用) / ELEMOTION一括改修(ウォーム巻上機) |
| `C-41-F711.01-E-B.pdf` | NEXIEZ-MRL Version 2 |
| `C-41-J10.1-E-D.pdf` | NEXIEZ / NEXIEZ-MRL / NEXIEZ-MRL Version 2 / NEXIEZ-Fit / NexWay-S / NEXIEZ-S |
| `C-6-R111.1-E-A.pdf` | ELENESSA / MAXIEZ CZ / MAXIEZ LZ / NEXIEZ / NEXIEZ-MRL / NexWay / NexWay-S / NEXIEZ-S |
| `C-6-R111.1-J-A.pdf` | ELENESSA / MAXIEZ-H / MAXIEZ-M / MAXIEZ-B / MAXIEZ CZ / MAXIEZ LZ / NEXIEZ / NEXIEZ-MRL / NexWay / NexWay-S / NEXIEZ-S |
| `C-6-R50.40-E-_.pdf` | NEXIEZ-MRL |
| `C-6-S1300-E-I.pdf` | NEXIEZ / NEXIEZ-MRL / NEXIEZ-GPX / NEXIEZ-LITE / NexWay / NexWay-S / NEXIEZ-S |
| `C-6-S1311-E-B.pdf` | ELEMOTION-IM / ELEMOTION-TY / ELEMOTION-TZ / ELEMOTION-IZ / NEXIEZ / NEXIEZ-MRL / NEXIEZ-GPX / NexWay-S / NEXIEZ-S |
| `C-6-S197.1-E-A.pdf` | NEXIEZ-MRL / NEXIEZ-MRL Version 2 |
| `C-6-S466.1-J-_.pdf` | アクセルVF / アクセルAI |
| `C-6-S470.1-J-_.pdf` | アクセルVF / アクセルAI |
| `C-7-A23.1-B-A.pdf` | エレペットアドバンス |
| `C-7-C2900-K.1-J-_-01.pdf` | ニューグランディ |
| `C-7-C3300.1700-J-F.pdf` | エレコールシステムセキュリティシステム |
| `C-7-C3330-K2-E-_.pdf` | DIAMOND TRAC / DIAMOND HS / Diamond Trac2 / ELENESSA / MAXIEZ-B / MAXIEZ CZ / MAXIEZ LZ / MAXIEZ-M / MAXIEZ-H / NEXIEZ / NEXIEZ-MRL / NexWay / NexWay-S |
| `C-7-C3330.1-E-G.pdf` | DIAMOND TRAC / Diamond Trac2 / ELENESSA / MAXIEZ-B / MAXIEZ CZ / MAXIEZ LZ / NEXIEZ / NEXIEZ-MRL / NexWay / NexWay-S |
| `C-7-C3331.1-E-D.pdf` | DIAMOND TRAC / Diamond Trac2 / ELENESSA / MAXIEZ-B / MAXIEZ CZ / MAXIEZ LZ / NEXIEZ / NEXIEZ-MRL / NexWay / NexWay-S |
| `C-7-C3333.1-E-C.pdf` | DIAMOND TRAC / DIAMOND HS / Diamond Trac2 / ELENESSA / MAXIEZ-B / MAXIEZ CZ / MAXIEZ LZ / NEXIEZ / NEXIEZ-MRL / NexWay / NexWay-S |
| `C-7-C3334.1-E-C.pdf` | ELEMOTION / DIAMOND TRAC / DIAMOND HS / Diamond Trac2 / ELENESSA / ELENESSA-AP / ELENESSA-IP / ELEMOTION-IH / ELEMOTION-LS / ELEMOTION-HS / ELEMOTION-IM / ELEMOTION-TY / ELEMOTION-TZ / ELEMOTION-IZ / ELEMOTION-AZ / GPM-3U / GPM-III / GPM-IIIMZ / GPQ / GPS-III / GPS-IIIMZ / GPS-IIIW / GPX / MAXIEZ-B / MAXIEZ CZ / MAXIEZ LZ / MAXIEZ-M / MAXIEZ-H / NEXIEZ / NEXIEZ-MRL / NexWay / NexWay MODERNIZATION / NexWay-S |
| `C-7-C3335.1-E-A.pdf` | ELEMOTION / DIAMOND TRAC / DIAMOND HS / Diamond Trac2 / ELENESSA / ELENESSA-AP / ELENESSA-IP / ELEMOTION-IH / ELEMOTION-LS / ELEMOTION-HS / ELEMOTION-IM / ELEMOTION-TY / ELEMOTION-TZ / ELEMOTION-IZ / ELEMOTION-AZ / GPM-3U / GPM-III / GPM-IIIMZ / GPQ / GPS-III / GPS-IIIMZ / GPS-IIIW / GPX / MAXIEZ-B / MAXIEZ CZ / MAXIEZ LZ / MAXIEZ-M / MAXIEZ-H / NEXIEZ / NEXIEZ-MRL / NexWay / NexWay MODERNIZATION / NexWay-S |
| `C-7-C3336.1-E-_.pdf` | ELEMOTION / DIAMOND TRAC / DIAMOND HS / Diamond Trac2 / ELENESSA / ELENESSA-AP / ELENESSA-IP / ELEMOTION-IH / ELEMOTION-LS / ELEMOTION-HS / ELEMOTION-IM / ELEMOTION-TY / ELEMOTION-TZ / ELEMOTION-IZ / ELEMOTION-AZ / GPM-3U / GPM-III / GPM-IIIMZ / GPQ / GPS-III / GPS-IIIMZ / GPS-IIIW / GPX / MAXIEZ-B / MAXIEZ CZ / MAXIEZ LZ / MAXIEZ-M / MAXIEZ-H / NEXIEZ / NEXIEZ-MRL / NexWay / NexWay MODERNIZATION / NexWay-S |
| `C-7-C3337.1-E-_.pdf` | ELEMOTION / DIAMOND TRAC / DIAMOND HS / Diamond Trac2 / ELENESSA / ELENESSA-AP / ELENESSA-IP / ELEMOTION-IH / ELEMOTION-LS / ELEMOTION-HS / ELEMOTION-IM / ELEMOTION-TY / ELEMOTION-TZ / ELEMOTION-IZ / ELEMOTION-AZ / GPM-3U / GPM-III / GPM-IIIMZ / GPQ / GPS-IIIW / NEXIEZ / NEXIEZ-MRL / NEXIEZ-MRL Version 2 / NEXIEZ-MRL MP / NexWay / NexWay MODERNIZATION / NexWay-S / NexWay-S MODERNIZATION |
| `C-7-C3339.1-E-_.pdf` | ELEMOTION / DIAMOND TRAC / DIAMOND HS / Diamond Trac2 / ELENESSA / ELENESSA-AP / ELENESSA-IP / ELEMOTION-IH / ELEMOTION-LS / ELEMOTION-HS / ELEMOTION-IM / ELEMOTION-TY / ELEMOTION-TZ / ELEMOTION-IZ / ELEMOTION-AZ / GPM-3U / GPM-III / GPM-IIIMZ / GPQ / GPS-IIIW / NEXIEZ / NEXIEZ-MRL / NEXIEZ-MRL Version 2 / NEXIEZ-MRL MP / NexWay / NexWay MODERNIZATION / NexWay-S / NexWay-S MODERNIZATION |
| `C-7-C3343.1-J-E.pdf` | エレコールシステムセキュリティシステム |
| `C-7-C3344.1-J-A.pdf` | エレコールシステムセキュリティシステム |
| `C-7-C3345.1-J-A.pdf` | エレコールシステムセキュリティシステム |
| `C-7-C3350-K4-E-_.pdf` | DIAMOND TRAC / DIAMOND HS / Diamond Trac2 / DeLITE / ELENESSA / ELENESSA-AP / ELENESSA-IP / ELEMOTION-TZ / ELEMOTION-IZ / ELEMOTION-AZ / GPS-II / GPS-III / GPS-IIIW / GPX / MAXIEZ-B / MAXIEZ CZ / MAXIEZ LZ / MAXIEZ-M / MAXIEZ-H / NEXIEZ / NEXIEZ-MRL / NEXIEZ-MRL Version 2 / NEXIEZ-MRL MP / NEXIEZ-GPX / NEXIEZ-GPX-MRL / NEXIEZ-LITE / NEXIEZ-LITE MRL / NEXIEZ-Fit / NexWay / NexWay MODERNIZATION / NexWay-S / NexWay-S MODERNIZATION / NEXIEZ-S / AT-MOD |
| `C-7-C3381.1-E-A.pdf` | DIAMOND TRAC / DIAMOND HS / Diamond Trac2 / ELENESSA / MAXIEZ CZ / MAXIEZ LZ / NEXIEZ / NEXIEZ-MRL / NexWay / NexWay-S |
| `C-7-C3382.1-E-C.pdf` | DIAMOND TRAC / DIAMOND HS / Diamond Trac2 / ELENESSA / MAXIEZ CZ / MAXIEZ LZ / NEXIEZ / NEXIEZ-MRL / NexWay / NexWay-S |
| `C-7-C3421.1-E-A.pdf` | DIAMOND TRAC / DIAMOND HS / Diamond Trac2 / ELENESSA / MAXIEZ-B / MAXIEZ CZ / MAXIEZ LZ / NEXIEZ / NEXIEZ-MRL / NexWay / NexWay-S |
| `C-7-C3425.1-E-_.pdf` | DIAMOND TRAC / Diamond Trac2 / ELENESSA / MAXIEZ-B / MAXIEZ CZ / MAXIEZ LZ / NEXIEZ / NEXIEZ-MRL / NexWay / NexWay-S |
| `C-7-C3950-E-D.pdf` | NEXIEZ-MRL Version 2 / NEXIEZ-Fit |
| `C-7-C3950-K1-E-_.pdf` | NEXIEZ-MRL Version 2 / NEXIEZ-Fit |
| `C-8-S38.0-J-_.pdf` | エレペットアドバンス |
| `C-8-S436.1-E-AE.pdf` | DIAMOND TRAC / DIAMOND HS / Diamond Trac2 / ELENESSA-IP / ELEMOTION-LS / ELEMOTION-HS / MAXIEZ-B / MAXIEZ CZ / MAXIEZ LZ / NEXIEZ / NEXIEZ-MRL / NEXIEZ-GPX / NEXIEZ-LITE / NexWay / NexWay-S / NEXIEZ-S |
| `C-8-S438.1-E-P.pdf` | DIAMOND TRAC / DIAMOND HS / Diamond Trac2 / ELENESSA-IP / ELEMOTION-LS / ELEMOTION-HS / MAXIEZ-B / MAXIEZ CZ / MAXIEZ LZ / NEXIEZ / NEXIEZ-MRL / NEXIEZ-GPX / NEXIEZ-GPX-MRL / NEXIEZ-LITE / NexWay / NexWay-S / NEXIEZ-S |
| `C-8-S450-E-N.pdf` | DIAMOND TRAC / DIAMOND HS / Diamond Trac2 / ELENESSA-IP / ELEMOTION-LS / ELEMOTION-HS / MAXIEZ-B / MAXIEZ CZ / MAXIEZ LZ / NEXIEZ / NEXIEZ-MRL / NEXIEZ-MRL Version 2 / NEXIEZ-GPX / NEXIEZ-GPX-MRL / NEXIEZ-LITE / NEXIEZ-LITE MRL / NEXIEZ-Fit / NexWay / NexWay-S / NEXIEZ-S / AT-MOD |
| `C-8-S451-E-U.pdf` | DIAMOND TRAC / DIAMOND HS / Diamond Trac2 / ELENESSA-IP / ELEMOTION-LS / ELEMOTION-HS / MAXIEZ-B / MAXIEZ CZ / MAXIEZ LZ / NEXIEZ / NEXIEZ-MRL / NEXIEZ-MRL Version 2 / NEXIEZ-GPX / NEXIEZ-GPX-MRL / NEXIEZ-LITE / NEXIEZ-LITE MRL / NEXIEZ-Fit / NexWay / NexWay-S / NEXIEZ-S / AT-MOD |
| `C-8-S452-E-_.pdf` | NEXIEZ-MRL |
| `C-8-S519.1-E-C.pdf` | ELENESSA / MAXIEZ-B / MAXIEZ CZ / MAXIEZ LZ / NEXIEZ / NEXIEZ-MRL / NexWay / NexWay-S |
| `C-8-S524-B-_.pdf` | ELEMOTION / DIAMOND TRAC / DIAMOND HS / Diamond Trac2 / ELENESSA / ELEMOTION-IH / ELEMOTION-LS / ELEMOTION-IM / ELEMOTION-TY / ELEMOTION-IZ / GPM-III / GPQ / MAXIEZ CZ / MAXIEZ LZ / MAXIEZ-M / MAXIEZ-H / NEXIEZ / NEXIEZ-MRL / NEXIEZ-MRL Version 2 / NEXIEZ-GPX / NEXIEZ-GPX-MRL / NEXIEZ-LITE / NEXIEZ-LITE MRL / NexWay / NexWay MODERNIZATION / NexWay-S / NexWay-S MODERNIZATION / AT-MOD |
| `C-8-S525-B-_.pdf` | DIAMOND TRAC / DIAMOND HS / Diamond Trac2 / ELENESSA / ELENESSA-IP / ELEMOTION-IH / ELEMOTION-LS / ELEMOTION-HS / ELEMOTION-IM / ELEMOTION-TY / ELEMOTION-IZ / GPM / GPM-3U / GPM-III / GPQ / GPS / GPS-III / GPX / MAXIEZ-B / MAXIEZ CZ / MAXIEZ LZ / MAXIEZ-M / MAXIEZ-H / NEXIEZ / NEXIEZ-MRL / NEXIEZ-MRL Version 2 / NEXIEZ-GPX / NEXIEZ-GPX-MRL / NEXIEZ-LITE / NEXIEZ-LITE MRL / NexWay / NexWay MODERNIZATION / NexWay-S / NexWay-S MODERNIZATION / AT-MOD |
| `C-904-C130.1-E-G.pdf` | DIAMOND TRAC / Diamond Trac2 / グローバル遠隔監視装置 GRM-3XXXシリーズ / ELEMOTION-TY / ELEMOTION-TZ / ELEMOTION-AZ / NEXIEZ / NEXIEZ-MRL / NEXIEZ-LITE |

### W資料（5 件）

| filename | model_type |
|---|---|
| `WIG-27--D.pdf` | NEXIEZ-MRL Version 2 |
| `WIG-28--B.pdf` | NEXIEZ-MRL Version 2 |
| `WIG-29--D.pdf` | NEXIEZ-MRL Version 2 |
| `WIG-30--_.pdf` | NEXIEZ-MRL Version 2 |
| `WIT-02--C.pdf` | NEXIEZ-MRL Version 2 |

## 6. 検索不能・問題資料の所在一覧（テキスト化の索引）

| 問題 | 件数 | リストの所在 |
|---|---:|---|
| KB 索引未取り込み（検索不能） | 20 | [カタログ](./kb-metadata-catalog-2026-08-26.md) の ⚠未索引 ／ issue #53 依頼 1 ／ [検証記録 §6](./verification-2026-08-26-kb-vqv-metadata.md) |
| 取扱機種スコープ対象外 | 467 | **本書 §5（全数）** |
| カンマ連結 model_type（listContains 不可） | 60 | カタログの † ／ issue #53 依頼 3（付録 B に全数） |
| TEST ゴミデータ | 1 | カタログ ／ issue #53 依頼 2（PR-4 のカテゴリ遮断でも除外） |
| web-crawler / quick-start 由来の混入文書 | 不定 | メタデータなしのため列挙不能。PR-4 の category `in` フィルタで遮断 ／ issue #53 依頼 4 |

※ 未索引 20 件のうち W資料 `WIG-27--D` はスコープ対象外とも重複（§5 にも掲載）。
