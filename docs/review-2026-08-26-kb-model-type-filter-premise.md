---
status: joint-review-required
date: 2026-08-26
owner: mona
reviewer: yukiworkspace
related:
  - PR #37
  - lambda/rag/rag-function/app.py
  - tests/unit/test_rag_kb_filter.py
  - infrastructure/sam/phase2-template.yaml
  - docs/api/rag.md
  - docs/verify-checklist-2026-07-29-kb-filter.md
---

# KB `model_type` 実体・使用KB・フィルタ方式の再確認（PR #37 前提再検証）

## 0. この文書の目的

PR #37「機種絞り込みの完全一致化と取扱機種スコープ導入」は、現状 `stringContains` で広めに取得し、Lambda 側で `model_type_matches` / `in_service_scope` により後段除外する設計になっている。

しかし 2026-08-26 の AWS Console / S3 実物確認で、これまでの検討時に参照していた `docs/kb-metadata-catalog.tsv` のカンマ区切り表記と、S3 の実メタデータ形式が一致しない可能性が判明した。

特に、S3 の実 `.metadata.json` では `model_type` が **配列**で保持されている実例が確認できた。Amazon Bedrock Knowledge Bases は `STRING_LIST` に対する `listContains` を公式サポートしているため、実稼働KBでも配列として索引化されているなら、#37 の「`stringContains` が必須」という前提を再確認する必要がある。

本書は **実装変更を決める文書ではない**。まず実稼働環境の事実を itai と共同確認し、確認結果に応じて #37 の実装・ドキュメントを正すためのレビュー記録である。

---

## 1. 現時点の結論

### 確認できていること

1. EleKnowledge Phase 2 のコード/IaC上の既定値は、Knowledge Base ID `DF9XUCSPDM` を使用する構成である。
2. `phase2-template.yaml` では `DF9XUCSPDM = generative-ai-use-cases-jp-inst-fmp` と明記され、`rag-dev` の環境変数 `KNOWLEDGE_BASE_ID` に渡される。
3. 同テンプレートでは再利用KBのS3として `ragknowledgebasestackinst-datasourcebucket9fa93e04-ybbhm1efhyzb`、prefix `docs/` が既定値になっている。
4. S3実物確認で、少なくとも1件の `.metadata.json` が `model_type: ["*"]` という配列形式だった。
5. AWS公式仕様では、メタデータが文字列リストの場合、`listContains` で **リスト要素の完全一致**を検索前フィルタとして実行できる。
6. #37 の現行単体テストは、`model_type: "*"` や `"AXIEZ,NEXCUBE"` といった文字列表現を主に模擬しており、実S3で確認した `model_type: ["*"]` をテストしていない。

### まだ確定していないこと

1. **現在デプロイ済みの `rag-dev` が本当に `DF9XUCSPDM` を向いているか。**  
   SAM既定値はデプロイ時に上書き可能なので、Lambda実環境変数で確認が必要。
2. **`DF9XUCSPDM` のベクトルインデックス内で `model_type` が現在も配列として保持されているか。**  
   現在のS3オブジェクトが配列でも、KBがその変更後にSyncされていなければ索引側は古い可能性がある。
3. **カタログ上の `model_type` 空欄440件が、S3/KB内で何に変換されているか。**  
   `[]` / `["*"]` / `[""]` / キー欠落などでフィルタ設計が変わる。
4. **`listContains` が当該KBの実ベクトルストアで期待どおり動作するか。**

したがって、現時点で「#37は不要」「#37の現方式が正しい」のどちらも断定しない。

---

## 2. これまでの検討で混ざっていた2種類の情報

### 2.1 管理用カタログ

`docs/kb-metadata-catalog.tsv` / `docs/kb-metadata-catalog-2026-07-29.md` では、`model_type` は例えば以下のように表現される。

```text
AXIEZ,NEXCUBE
メルワイド,メルシティ
```

この表記は検索・集計用に複数機種をカンマで表現した **管理カタログ上の表現**であり、S3の生メタデータ形式そのものとは限らない。

#37 の `app.py` は配列/文字列の両方を処理できるよう `_model_type_elements()` を持つが、Bedrockへ送る粗フィルタでは「多値なので `equals` では一致せず `stringContains` が必須」とコメントしている。

### 2.2 S3実メタデータ

2026-08-26 に AWS Console で確認した実例：

```json
{
  "metadataAttributes": {
    "file_path": "documents/C資料/C-16-A1.20-J-_-01.pdf",
    "filename": "C-16-A1.20-J-_-01.pdf",
    "category": "C資料",
    "model_type": [
      "*"
    ],
    "upload_date": "2026-07-24T04:06:27.422810+00:00",
    "folder_depth": "2"
  }
}
```

このオブジェクトでは `model_type` は文字列ではなく配列である。

**注意:** この1件だけで全オブジェクト、または現在のKBインデックス内の型まで断定してはいけない。

---

## 3. AWS公式仕様との照合

Amazon Bedrock `RetrievalFilter` の公式仕様では、次の演算子が定義されている。

### `stringContains`

文字列の部分一致、または文字列リストの各要素に対する部分一致。

例：

```json
{
  "stringContains": {
    "key": "model_type",
    "value": "AXIEZ"
  }
}
```

この場合、リスト要素が以下ならいずれも拾う可能性がある。

```text
AXIEZ
AXIEZ-LINKs
モダニゼーションAXIEZ
MAXIEZ ...（文字列中に AXIEZ を含む場合）
```

### `listContains`

メタデータ属性が文字列リストの場合、指定値を **リストの1メンバーとして含むか** を判定する。

```json
{
  "listContains": {
    "key": "model_type",
    "value": "AXIEZ"
  }
}
```

期待する判定：

```text
["AXIEZ"]                    -> match
["AXIEZ", "NEXCUBE"]         -> match
["AXIEZ-LINKs"]              -> no match
["モダニゼーションAXIEZ"]     -> no match
```

AWS公式:
- https://docs.aws.amazon.com/bedrock/latest/APIReference/API_RetrievalFilter.html
- https://docs.aws.amazon.com/bedrock/latest/userguide/kb-test-config.html
- https://docs.aws.amazon.com/bedrock/latest/userguide/kb-metadata.html

したがって、**実稼働KBの `model_type` が STRING_LIST として索引化されているなら、選択機種の完全一致は `listContains` で検索前に実施できる可能性が高い。**

---

## 4. #37 への影響が大きい理由

### 4.1 現方式は「10件取った後に落とす」ため取りこぼしが発生し得る

#37 の `query_knowledge_base()` は `numberOfResults=10` が既定で、Bedrockから返った後に `in_service_scope` と `model_type_matches` を適用する。

例：

```text
Bedrock TOP10
  正しいAXIEZ 4件
  部分一致ノイズ 6件
        ↓ post-filter
最終4件
```

11位以下に有効なAXIEZ資料があっても取得されない。

もし検索前に `listContains` で候補集合を正しく限定できれば、

```text
AXIEZを含む資料だけ
        ↓
意味的に近いTOP10
```

にでき、post-filterによるrecall低下を避けられる。

### 4.2 さらに重大: `model_type: ["*"]` を現行コードが共通資料と判定できない可能性

#37 の `_is_common_model_type()` は現在、概念的に次の判定をしている。

```python
if raw is None:
    return True
if isinstance(raw, (list, tuple)):
    return len([e for e in raw if str(e).strip()]) == 0
return str(raw).strip() in ('', '*', 'general')
```

このロジックでは、

```python
raw = ["*"]
```

は「空のリストではない」ため `False` となる。

続く `in_service_scope()` では `"*"` は `HANDLED_MODEL_TYPES` に含まれないため、**Retrieve結果が本当に `["*"]` で返るなら、全機種共通資料を除外する可能性がある。**

また、機種選択時のBedrock粗フィルタは現在、共通資料に対して

```json
{"equals": {"key": "model_type", "value": "*"}}
```

を送っている。実メタデータが `["*"]` の場合、scalar `"*"` の `equals` でリスト値を拾えるかは未確認であり、`listContains("*")` を使う方がAWS仕様には素直である。

これは「性能最適化」だけではなく、**共通資料を残すという#37の仕様自体が実データ型と合っているか**の確認事項である。

### 4.3 単体テストが実データ型を再現していない

現行 `tests/unit/test_rag_kb_filter.py` は、例えば以下をテストしている。

```python
{"model_type": "*"}
{"model_type": "AXIEZ,NEXCUBE"}
```

一方、今回確認したS3実物は、

```python
{"model_type": ["*"]}
```

である。

少なくとも確認後には、実KBのRetrieveレスポンスと同じ型をfixtureとしてテストする必要がある。

---

## 5. 使用KBについての再確認

### コード/IaC上の想定

`infrastructure/sam/phase2-template.yaml` の既定値：

```text
KnowledgeBaseId = DF9XUCSPDM
DF9XUCSPDM = generative-ai-use-cases-jp-inst-fmp
VQV81CNYU4 = generative-ai-use-cases-jpinstd
```

`rag-dev` には次が設定される設計：

```text
KNOWLEDGE_BASE_ID = !Ref KnowledgeBaseId
```

既定のS3：

```text
s3://ragknowledgebasestackinst-datasourcebucket9fa93e04-ybbhm1efhyzb/docs/
```

Runbookにも、Phase 2 は `DF9XUCSPDM` / data source `WQ4ED5IFOP` を読み取り専用で再利用すると記載されている。

### ただし「現在の実環境」は別途確認が必要

SAMのDefaultはデプロイ時に上書きできる。したがって、実稼働の正本はLambdaの環境変数で確認する。

確認対象：

```text
Lambda > rag-dev > Configuration > Environment variables
KNOWLEDGE_BASE_ID = ?
```

併せて以下も一致確認する。

```text
CloudFormation Phase2 parameter: KnowledgeBaseId
SSM: /eleknowledge/dev/knowledge-base-id
```

---

## 6. 同期日時の矛盾（重要）

2026-08-26 にAWS Consoleで確認したKnowledge Base一覧では、次の最終同期日時だった。

| Knowledge Base | 最終同期 |
|---|---|
| `installation-qa-kb-instd` | 2026-08-06 13:35 JST |
| `rag-data-source-for-mai-box-inst-markdown` | 2026-06-03 13:26 JST |
| `generative-ai-use-cases-jp-inst-fmp` | **2026-06-03 14:59 JST** |
| `generative-ai-use-cases-jpinstd` | **2026-07-24 13:43 JST** |

一方、上記S3実メタデータの `upload_date` は、

```text
2026-07-24T04:06:27Z
= 2026-07-24 13:06:27 JST
```

である。

したがって、**現在S3にある配列形式のmetadataが、6/3以降Syncされていない `generative-ai-use-cases-jp-inst-fmp` の索引へ反映済みとは限らない。**

逆に `generative-ai-use-cases-jpinstd` は同日13:43にSyncされているため、7/24時点のデータ変更との時系列が近い。

この事実だけで「実際はjpinstdを使っている」とは断定しない。必要なのは `rag-dev` の実環境変数確認である。

---

## 7. itai に実環境で確認してほしいこと（Approve条件）

以下を **Yes / No + 実値** で確認したい。

### A. 使用KB

- [ ] `rag-dev` の `KNOWLEDGE_BASE_ID` は `DF9XUCSPDM` か。
- [ ] CloudFormation Phase2 parameter / SSM `/eleknowledge/dev/knowledge-base-id` も同じ値か。
- [ ] `DF9XUCSPDM` は現在 `generative-ai-use-cases-jp-inst-fmp` を指しているか。

### B. Data Source / Vector Store

- [ ] `DF9XUCSPDM` の data source は `WQ4ED5IFOP` か。
- [ ] data source は `s3://ragknowledgebasestackinst-datasourcebucket9fa93e04-ybbhm1efhyzb/docs/` を参照しているか。
- [ ] ベクトルストアは `listContains` を利用可能な構成（想定: OpenSearch Serverless）か。

### C. 実KBでの `model_type` 型

S3の現在値ではなく、**実際のRetrieve結果の `metadata.model_type`** を確認する。

- [ ] 単一機種資料: `"AXIEZ"` か `["AXIEZ"]` か。
- [ ] 複数機種資料: `"メルワイド,メルシティ"` か `["メルワイド", "メルシティ"]` か。
- [ ] 共通資料: `"*"` か `["*"]` か。
- [ ] カタログ上空欄の資料（例 `SUE-1-01`）: 空文字 / 空配列 / `*` / キー欠落のどれか。

### D. `listContains` 実機テスト

同一KBで次を試し、フィルタがエラーなく動き、返却metadataが期待どおりか確認する。

```json
{
  "listContains": {
    "key": "model_type",
    "value": "AXIEZ"
  }
}
```

期待:

```text
AXIEZ 要素あり       -> 対象
AXIEZ-LINKsのみ      -> 対象外
MAXIEZのみ           -> 対象外
```

共通資料についても、

```json
{
  "listContains": {
    "key": "model_type",
    "value": "*"
  }
}
```

が機能するか確認する。

---

## 8. 確認結果ごとの対応方針

### Case A: `rag-dev = DF9XUCSPDM` かつ実KB `model_type = STRING_LIST`、`listContains` が正常

この場合、#37の前提を修正する。

候補：

1. 選択機種の粗い `stringContains` を `listContains` へ置換。
2. 共通資料も `listContains("*")` 等、実データ表現に合わせる。
3. UIグループ（AXIEZ -> AXIEZ / KE-WF・HF / 駅舎エレ）は `orAll(listContains(...))` で検索前に展開。
4. 取扱機種スコープも可能なら `orAll` で検索前フィルタへ移し、post-filterによるTOP10の取りこぼしを避ける。
5. `model_type_matches` / `in_service_scope` は不要部分を削除するか、安全弁として残す場合も実データ型をfixtureにしたテストへ変更。
6. `docs/api/rag.md` の「部分一致」前提を修正。
7. `docs/rag-model-filter-mapping.md` の件数を実KBのリスト要素一致基準で再検証。

### Case B: `rag-dev = DF9XUCSPDM` だが実KB索引は旧型/文字列、または `listContains` が利用不可

#37のpost-filter方式には技術的理由がある。

ただし、次を正式記録する。

- S3現行metadataとKB索引の型が異なる理由。
- 共有KBがread-onlyでSyncできない制約。
- `stringContains + post-filter` が暫定措置であること。
- post-filterによる返却件数減少/recall低下。
- 将来のKB同期・metadata正規化時に `listContains` へ移行する条件。

### Case C: 実 `rag-dev` が `VQV81CNYU4` 等、`DF9XUCSPDM` 以外

IaC/Runbookと実環境が乖離している。

#37の修正前に、

- 実使用KB
- Data Source
- S3
- metadata schema
- Vector Store

を正本へ反映し直す。`phase2-template.yaml` / Runbookのどちらを正すべきか決める。

### Case D: `model_type` が資料ごとにSTRINGとSTRING_LISTで混在

検索前の完全一致だけでは統一できない可能性がある。

- まず混在件数を実測。
- KB所有側でmetadata正規化するか、移行期間のみ双方のフィルタをORするか判断。
- 正規化完了条件を決定記録に残す。

---

## 9. 確認後に正本へ残すべき情報

itai確認後、少なくとも以下は一時的な会話やPRコメントだけで終わらせない。

1. **Phase 2が実際に使用するKnowledge Base ID / 名称 / Data Source / S3 / prefix / Vector Store**
2. **`model_type` の正規データ型と共通資料の表現**
3. **カタログのカンマ表記は生metadataなのか、表示・集計上の正規化表現なのか**
4. **機種絞り込みで使用するBedrock演算子と、その選定理由**
5. **全機種共通・空欄・キー欠落の扱い**
6. **取扱機種スコープを検索前/後のどちらで適用するか**
7. **KBが共有read-onlyであることと、Sync/metadata変更の責任者**
8. **実データ型を再現したテストfixture**

更新候補:

- `docs/api/rag.md`
- `docs/verify-checklist-2026-07-29-kb-filter.md`
- `docs/rag-model-filter-mapping.md`
- `docs/aws-migration-runbook.md`
- `infrastructure/sam/phase2-template.yaml`（実値と違う場合のみ）
- 新規 decision record（最終確認結果を固定する場合）

---

## 10. 今回の教訓

今回の検討では、次の3層を混同すると判断を誤ることが分かった。

```text
管理カタログ上の表現
        ≠
S3 .metadata.json の現在値
        ≠
最後にSyncされたKnowledge Base索引内の実値
```

今後、RAG metadata/filterの設計判断では、

1. raw S3 metadata
2. KBのSync日時
3. Retrieveが返す実metadata
4. Bedrock公式フィルタ仕様

をセットで確認してから実装方針を決める。

#37についても、**カタログ文字列を前提にした机上判定ではなく、実稼働KBのRetrieve結果を正本として再評価する。**
