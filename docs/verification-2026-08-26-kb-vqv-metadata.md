---
status: reference
last-verified: 2026-08-27
related-code: lambda/rag/rag-function/app.py, infrastructure/sam/phase2-template.yaml, tests/unit/test_rag_kb_filter.py
---

# 実環境検証記録: 使用KB・メタデータ実態・フィルタ挙動（2026-08-26）

> **この文書の位置づけ:** 2026-08-26 に AWS 実環境（profile `datautl-bple-mebs` / ap-northeast-1）で実測した結果の記録（**2026-08-26 確認時点の実環境スナップショット**）。PR #52 の共同確認（§7 A〜D）への回答であり、PR #37 系のフィルタ再設計・環境正本是正の根拠。2026-08-26 時点の検証結果は本検証記録を正とする。ただし KB / Data Source / Sync 状態 / S3資料 / metadata / デプロイ設定等の実環境が変更された場合は、影響する項目を再確認すること。
>
> 関連: PR #52 / PR #37 / issue #53（KB所有側への修正依頼） / [verify-checklist-2026-07-29-kb-filter.md](./verify-checklist-2026-07-29-kb-filter.md)

---

## 1. 結論サマリ

1. **実稼働KBは `VQV81CNYU4`**（jpinstd）。IaC既定値・Runbookの `DF9XUCSPDM` 記載は古い（PR #52 の分類で Case C）。
2. **`model_type` は list型2599件 / string型1146件の混在**（Case D）。空文字・キー欠落は0件。
3. **`listContains` は実機で期待どおり動作**し、string型もスカラー=単要素リストとして一致した（**実環境で確認した挙動**。AWS公式仕様上 `listContains` は STRING_LIST 向け演算子であり、型混在での動作が仕様として保証されているわけではない → §4 の注意）。機種絞り込みは検索前の完全一致（listContains）に移行できる（Case A の技術条件成立）。
4. TSVカタログ（3,492件）は実バケット（3,745件）と**253件乖離**しており正本にできない。
5. 索引欠落20件・TEST文書1件・カンマ連結メタデータ60件は**KB所有側依頼**（issue #53）。
6. DF9XUCSPDM は MULTIMODAL パースで図表ページがIMAGEチャンク化しており、アプリ改修（画像添付ロジック）とセットでなければ運用に耐えない。**当面 VQV81CNYU4 で運用**。

---

## 2. 環境の実値（2026-08-26 実測）

| 項目 | 実値 |
|---|---|
| `rag-dev` Lambda `KNOWLEDGE_BASE_ID` | `VQV81CNYU4` |
| `rag-dev` Lambda `KB_SOURCE_BUCKET` | `ragknowledgebasestackinst-datasourcebucket9fa93e04-ybbhm1efhyzb` |
| `rag-dev` Lambda `KB_SOURCE_PREFIX` | `docs/` |
| CFn `EleKnowledge-dev-phase2` パラメータ `KnowledgeBaseId` | `VQV81CNYU4`（テンプレ既定値 `DF9XUCSPDM` をデプロイ時上書き） |
| SSM `/eleknowledge/dev/knowledge-base-id` | **存在しない**（ParameterNotFound。runbook の「SSMにも書き込む」記載は実態と不一致） |
| ベクトルストア | 両KBとも OpenSearch Serverless（VQV: collection `xb9mgxrrbotww727d7eb`） |

### 2.1 VQV81CNYU4（generative-ai-use-cases-jpinstd）のデータソース

| Data Source ID | 名称 | 参照先 | 備考 |
|---|---|---|---|
| `KHPV3CNKOU` | s3-data-source | `s3://ragknowledgebasestackinst-datasourcebucket9fa93e04-ybbhm1efhyzb/docs/` | **本命**。標準TEXT抽出。最終Sync 2026-07-24 04:26 UTC（3,745件スキャン / メタデータ2,566件更新反映 / 失敗あり→§6） |
| `A0XLFVSX3P` | knowledge-base-quick-start-7duyg-data-source | `s3://rag-data-source-inst-fmp-730972069979-ap-northeast-1`（バケット全体） | category等のメタデータなし。`KB_SOURCE_BUCKET` 外のため引用presign不能 |
| `7NJIOJDD0Z` | web-crawler-data-source | Webクローラー | GenUドキュメント混入源 |

### 2.2 DF9XUCSPDM（generative-ai-use-cases-jp-inst-fmp）のデータソース

| Data Source ID | 名称 | 参照先 | 備考 |
|---|---|---|---|
| `WQ4ED5IFOP` | knowledge-base-quick-start-ol83s-data-source | **同じ** `s3://ragknowledgebasestackinst-...ybbhm1efhyzb/docs/` | `parsingStrategy: BEDROCK_FOUNDATION_MODEL`（Claude Sonnet 4.6 / **MULTIMODAL**）→ 図表ページがIMAGEチャンク化。最終Sync **2026-06-03**（7/24のメタデータ一括更新は**未反映**） |

**含意:** 両KBの据付資料は同一バケット・同一prefix。違いはパース方式・同期鮮度・追加データソースの有無のみ。KBを替えても読む資料は変わらない。

### 2.3 DF9XUCSPDM を当面使わない理由（2026-08-26 判断）

- 実クエリで上位10件中7件がIMAGEチャンク（本文テキストなし）になる事例を確認。アプリの画像添付は `MAX_IMAGE_BLOCKS = 3`（全体上限）のため、肝心の文書の画像が添付されず「記載がありません」と誤回答する。
- Sync してもこれは直らない（差分取り込みでありPDF本体は変わっていない上、パース設定が原因のため再取り込みしても同じ）。パース設定は作成後変更不可＝データソース作り直しになり、TEXT抽出に寄せるなら VQV81CNYU4 と同じものを作るだけ。
- DF9XUCSPDM 対応の本命はアプリ改修（画像添付の文書単位選抜など）。将来の仕切り直しPRの論点。
- DF9XUCSPDM の再Sync は共同管理部門に未確認のため**実施しない**（そもそも共有KBのSyncは所有側の作業）。

---

## 3. メタデータ実態（S3 `*.metadata.json` 3,745件の全数調査）

### 3.1 スキーマ

キー構成は2パターンのみ。キー欠落・想定外キーなし。

- 6キー（1,635件）: `file_path` / `filename` / `category` / `model_type` / `upload_date` / `folder_depth`
- 8キー（2,110件）: 上記 + `tags` / `tags_string`（据付場用図・災害事例集・据付ノート。サブフォルダ名由来。`tags` と `tags_string` の不整合0件）

`folder_depth` は `"2"`(1,635) / `"3"`(2,078) / `"4"`(32) の3値。

### 3.2 category 実測件数（TSVカタログとの差分）

| category | 実測 | TSVカタログ | 差 |
|---|---:|---:|---:|
| 据付場用図 | 2,027 | 1,752 | +275 |
| C資料 | 729 | 816 | −87 |
| テクニカルインフォメーション | 308 | 308 | 0 |
| 災害事例集 | 294 | 294 | 0 |
| Qシート | 156 | 156 | 0 |
| 据付基準 | 121 | 121 | 0 |
| 据付ノート | 67 | 40 | +27 |
| 現場代理人業務マニュアル | 30 | 0 | +30 |
| 品質管理業務マニュアル | 7 | 0 | +7 |
| W資料 | 5 | 5 | 0 |
| TEST | 1 | — | +1 |
| **計** | **3,745** | **3,492** | **+253** |

→ **TSVカタログは正本にできない**。カタログ再生成は実測メタデータから行う（PR-5）。

### 3.3 model_type の型と値

- **型混在:** list型 2,599件 / string型 1,146件。string型は据付場用図822・災害事例集294・現場代理人30。
- **空欄は存在しない:** 空文字・空配列・キー欠落 0件。TSVカタログの空欄440件は取り込み時に `"general"` へ変換済み（実測487件。うち災害事例集294件は全件 string の `"general"`）。
- **共通資料表現:** `["*"]` 302件 / `"*"` 30件 / `general` 487件（list 193 + string 294）。
- **共通値と具体機種の混在リスト（例 `["*", "AXIEZ"]`）は0件。**
- **カンマ連結文字列60件:** 全件が据付場用図で値も同一 `"機械室レス荷物用(中抵製),機械室レス荷物用(モダニ)"`（KF-ETC_MTC 41件 / KM-LD 19件）。listContains で拾えない唯一の形式 → 正規化を issue #53 依頼3で所有側へ依頼済み。
- **異なり値は生値175種／要素正規化後174種**（カンマ連結を分解すると1種減る。出現3回以下のロングテール52種。`MELWIDE`/`メルワイド` の英日重複、`E*` `J*`、Home Elevator系など）。**値の業務的正しさ・表記ゆれ統合は未検証**（取扱機種スコープの確定には業務側の棚卸しが必要）。

### 3.4 メタデータの信頼性の線引き

- **信用してよい:** 構造・型・分布・索引への反映（全数検証済み。§4のとおり索引はS3の7/24版を反映しており「S3で見た値=フィルタが評価する値」）。
- **信用してはいけない:** 値の業務的正しさ（model_type が資料内容と合っているか）、TSVカタログ、175種の語彙統制。

---

## 4. Bedrock フィルタ演算子の実機挙動（VQV81CNYU4 に対する retrieve 実測）

| 演算子 | 実測結果 |
|---|---|
| `listContains(model_type, "AXIEZ")` | AXIEZ 要素を持つ資料のみ。AXIEZ-LINKs 単独・MAXIEZ は混入しない。**string型 `"AXIEZ"` も一致**（スカラー=単要素リスト扱い）→ 型混在でも取りこぼさない |
| `listContains / equals (model_type, "*")` | どちらも `"*"` と `["*"]` の**両方**に一致 |
| `listContains / equals (model_type, "general")` | 動作OK |
| `stringContains(model_type, "AXIEZ")` | `["AXIEZ-LINKs"]` 単独資料が混入（部分一致ノイズ実在 = PR #33 Major 4） |

**注意（AWS仕様との関係）:** AWS 公式仕様上 `listContains` は STRING_LIST 型向けの演算子。上表の「string型も一致（スカラー=単要素リスト扱い）」は **VQV81CNYU4 実環境（2026-08-26）で確認した挙動**であり、型混在での動作が AWS 仕様として保証されているわけではない。型の正規化（issue #53 依頼）が完了するまでは、この実測挙動に依存していることを前提として扱うこと。

Retrieve が返す `metadata.model_type` は **S3の型のまま**（str / list 混在）。よって post-filter は両型対応が必須。

**確定バグ（PR #52 §4.2）:** #37 の `_is_common_model_type()` は `["*"]` / `["general"]`（list型）を共通と判定できず、`in_service_scope` が共通資料を除外する。実データで495件が該当（§5.2）。

CLI 注意: 日本語を含むフィルタは `AWS_CLI_FILE_ENCODING=UTF-8` + `--cli-input-json`、出力は `--query` で metadata に絞る（本文の特殊文字で cp932 エンコードエラーになるため）。

---

## 5. 取扱機種スコープのシミュレーション（メタデータ正・全3,745件）

前提: PR #37 の `HANDLED_MODEL_TYPES`（27値）と `UI_MODEL_FILTERS`（6項目）。

### 5.1 スコープ適用後の検索対象

| 判定 | 件数 | 割合 |
|---|---:|---:|
| 検索対象（共通 `*`/`general`） | 819 | 21.9% |
| 検索対象（取扱機種を1つ以上含む） | 2,459 | 65.7% |
| **検索対象 計** | **3,278** | **87.5%** |
| 対象外 | 467 | 12.5% |

対象外467件 = 据付場用図352 + C資料110 + **W資料5（全件）**。機種は NEXIEZ-MRL Version 2（392）ほかモダニ/保守系。

> **W資料問題（将来対応・業務判断待ち）:** W資料はスコープフィルタ併用時に UI の `w_doc` チップを選んでも0件になる。対応候補 = W資料機種（GPM等）を `HANDLED_MODEL_TYPES` へ追加 or W資料カテゴリをスコープ例外化。

### 5.2 `_is_common_model_type` バグの影響と修正効果

| | 検索対象 | 割合 |
|---|---:|---:|
| #37 現行コード（バグあり） | 2,783 | 74.3% |
| 修正後（要素ベース判定） | 3,278 | 87.5% |

- 修正で**495件回復・新たな除外0件**。回復内訳: C資料302 / 据付基準76 / Qシート51 / 据付ノート33 / TI25 / 品質管理7 / TEST1（TESTはカテゴリ遮断で別途除外）。
- 修正案: `_is_common_model_type(raw)` = `els = _model_type_elements(raw); return not els or all(e in {'', '*', 'general'} for e in els)`（混在リスト0件のため all 判定で曖昧さなし）。

### 5.3 UI項目別の listContains 完全一致母数

| UI項目 | 完全一致 | stringContains誤マッチ（listContains化で消える） |
|---|---:|---:|
| AXIEZ | 1,137 | **752** |
| AXIEZ-LINKs | 913 | 0 |
| NEXCUBE | 485 | 0 |
| メルシティ | 292 | 0 |
| メルワイド | 291 | 0 |
| エスカレーター | 83 | 0 |

（共通819件は常時加算。AXIEZ 以外の誤マッチ0は、部分一致しうる機種名が実データでは必ず正解機種と同一リストに併記されているため）

### 5.4 確定した実装方針（PR-3 相当）

1. 機種選択時の粗フィルタ: `stringContains` → `orAll [listContains(展開機種...), listContains "*", listContains "general"]`。`equals ""` は削除（空欄0件）。
2. `_is_common_model_type()` を要素ベース判定へ修正（§5.2）。
3. post-filter（要素完全一致・スコープ）は安全弁として残置。カンマ連結60件は機種未指定経路では post-filter の要素分解で通過するため現状実害なし。
4. テストfixtureは実データ型8種: `"AXIEZ"` / `["AXIEZ"]` / 多値list / `"*"` / `["*"]` / `"general"` / `["general"]` / カンマ連結文字列。
5. 全検索時にも `in: {key: category, value: [実カテゴリ10種（TEST除く）]}` を常時適用し、web-crawler / quick-start / TEST 文書を遮断（PR-4 相当）。

---

## 6. 索引欠落20件（検索不能・所有側依頼済み）

索引済み文書3,725件 vs S3実体3,745件の突き合わせで特定（Syncジョブ統計の「失敗14件」とは不一致。20件が実欠落）。詳細・全ファイル一覧は **issue #53**。

| 原因 | 件数 | 対処 |
|---|---:|---|
| 暗号化PDF（`/Encrypt` あり） | 12（Qシート Q-3663〜Q-3699） | 復号版に差し替え |
| 1ファイル50MB上限超過（57〜135MB） | 6（W資料 WIG-27--D、据付ノート IN-EL-08-94 / IN-EL-12-104×3 / IN-EL-12-105） | 分割して再アップロード |
| テキスト層なしスキャンPDF（`/Font` なし） | 2（GM-01-03-A / GM-01-29-A） | OCR済み版に差し替え |

Qシートは156件中12件（約8%）が検索不能。修正は S3 差し替え + `KHPV3CNKOU` 再Sync（共有KBのため所有側実施）。アプリ側では救済不能。

---

## 7. 未解決・持ち越し事項

- [ ] issue #53 の所有側対応（欠落20件 / TEST削除 / カンマ連結正規化 / 追加データソース協議 / Sync運用窓口）
- [ ] W資料のスコープ例外 or 機種追加の業務判断（§5.1）
- [ ] model_type 175種の語彙棚卸し（表記ゆれ統合・スコープ内外仕分け。#37 の取扱機種リスト確定に必要）
- [ ] IaC・Runbook の VQV81CNYU4 への是正（PR-2）と、SSM パラメータ不存在の扱い（テンプレから削除 or 再作成）
- [ ] DF9XUCSPDM 将来対応（画像添付ロジック改修とセット。再Syncは所有側と要調整）
