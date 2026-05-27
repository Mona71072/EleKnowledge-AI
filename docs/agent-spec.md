# トラブルシューティング エージェント詳細仕様書

## ドキュメント情報

| 項目 | 内容 |
|------|------|
| **バージョン** | **1.1** |
| **ステータス** | 実装仕様 |
| **対象** | Phase 3 トラブルシューティング機能 |
| **最終更新** | 2026-05-26 |

---

## バージョン履歴

| Ver | 日付 | 変更概要 |
|-----|------|----------|
| 1.0.0 | 2026-01-23 | 初版（PoC設計） |
| 1.0.1 | 2026-01-26 | PoC実装ガイド追記 |
| **1.1** | **2026-05-26** | **条件分岐フロー・機種優先順位・source_action タグ・UIバッジ対応を追加（詳細は §9 参照）** |

---

## 1. 概要

### 1.1 目的

現場で発生したトラブルに対して、過去の事例と技術資料から原因分析と対処方法を提案する Bedrock Agent。

### 1.2 主要要件

- 工事番号がある場合のみサイト情報を取得（条件付き実行）
- 一時的に `control-system=VFGLF` 固定、任意のエラーコードによる検索フィルタリング
- 各アクションの引用元をUIで判別可能にする（source_action タグ）
- 観点別（トラブル事例・マニュアル・C資料）に整理した回答を生成
- 平均応答時間 < 60秒

---

## 2. エージェント全体アーキテクチャ

### 2.1 システム構成

```
フロントエンド入力（工事番号・機種・不具合内容・エラーコード）
  ↓
API Gateway + Lambda Authorizer（Cognito JWT 検証）
  ↓
Orchestrator Lambda
  ├→ 入力検証・正規化
  ├→ DynamoDB セッション初期化
  └→ Bedrock Agent 起動（ReAct ループ）
       │
       ├→ [Action 1] GetSiteInfo (DynamoDB)        ← 工事番号ありの場合のみ
       ├→ [Action 2] searchTroubleCases (KB)       ← control-system=VFGLF・エラーコードでフィルター
       ├→ [Action 3] searchTroubleshootManuals (KB) ← control-system=VFGLF・エラーコードでフィルター
       ├→ [Action 4] searchCMaterialDocs (KB)      ← ②③結果からキーワード抽出して検索
       └→ Claude Haiku 統合分析・観点別回答生成
  ↓
Orchestrator 後処理
  ├→ EventStream パース
  ├→ DynamoDB から source_action タグ付き引用取得
  ├→ S3 presigned URL 生成（30日有効）
  └→ sourceDocuments（source_action 付き）を返却
```

### 2.2 主要コンポーネント

| コンポーネント | 技術 | 責務 |
|---|---|---|
| Orchestrator Lambda | Python 3.11 | 入力検証、エージェント制御、引用統合、presigned URL生成 |
| Action 1: DB Search | Python 3.11 + boto3 | 工事番号で DynamoDB sites テーブルから現場情報取得 |
| Action 2: KB Search1 | Python 3.11 | トラブル事例・報告書の KB 検索（control-system=VFGLF・エラーコードフィルター） |
| Action 3: KB Search2 | Python 3.11 | トラブルシュートマニュアルの KB 検索（control-system=VFGLF・エラーコードフィルター） |
| Action 4: KB Search3 | Python 3.11 | C資料の KB 検索（control-system=VFGLF フィルター・②③結果から生成したキーワード） |
| Claude Haiku | Bedrock | 観点別統合分析・推奨アクション生成 |

---

## 3. 入出力仕様

### 3.1 入力（Request）

```typescript
interface TroubleshootingRequest {
  constructionNumber?: string;  // 任意: 工事番号（半角英数8文字）
  model?: string;               // 任意: KE-LG / KM-LD / CM-MA / ME-CH
  troubleDescription: string;   // 必須: 不具合内容（5〜2000文字）
  errorCode?: string;           // 任意: エラーコード（半角英数字3文字）
  // constructionNumber か model のいずれかは必須
}
```

### 3.2 出力（Response）

```typescript
interface SourceDocument {
  documentName: string;     // S3 オブジェクトキーのファイル名
  title: string | null;     // KB メタデータの title フィールド
  sourceUri: string;        // S3 presigned URL（有効期限 30 日）
  documentType: string;     // KB メタデータの document フィールド
  model: string;            // KB メタデータの model フィールド
  relevance: number;        // 検索スコア（0.0〜1.0）
  source_action: string;    // ★ Ver 1.1 追加: 取得元アクション識別子
                            //   "trouble_cases" | "manual" | "c_material"
}

interface TroubleshootingResult {
  sessionId: string;                 // セッション ID（UUID）
  result: string;                    // Agent 生成テキスト（Markdown 形式・観点別構成）
  sourceDocuments: SourceDocument[]; // 参照文書リスト（source_action 付き）
}
```

**`result` の観点別構成（Ver 1.1）:**

```
【サイト情報】        ← ①取得時のみ表示
  現場名・機種・制御システム・担当者

【トラブル事例】      ← ②の検索結果をもとに
  類似事例・過去の対処内容

【マニュアル】        ← ③の検索結果をもとに
  推奨手順・注意事項

【C資料】            ← ④の検索結果をもとに
  技術詳細・部品情報

【推奨アクション】    ← ①〜④を総合した具体的対処手順
```

---

## 4. Action Group 仕様

### 4.1 Action 1: GetSiteInfo（DB 検索）

**目的:** 工事番号で現場情報・設備仕様を取得する

**実行条件（Ver 1.1）:** ユーザ入力に `constructionNumber` が含まれる場合のみ実行。含まれない場合はスキップ。

**呼び出し形式:** `apiSchema (POST /site-info)`

**入力パラメータ:**

| パラメータ | 型 | 必須 | 説明 |
|---|---|---|---|
| `constructionNumber` | string | ✓ | 工事番号（例: `EIK54801`） |

**出力（構造化テキスト）:**

```
工事番号: EIK54801
現場名: ○○川崎
現場番号: 12345
機種: KE-LG          ← エージェントはこの値を機種確定に使用する
制御システム: VFGLF
担当者: 山田太郎
```

**DynamoDB:** `sites` テーブル（PK: `constructionNumber`）

---

### 4.2 Action 2: searchTroubleCases（トラブル事例検索）

**目的:** `control-system=VFGLF` 固定と任意のエラーコードで絞り込んだトラブル事例・報告書を検索する

**呼び出し形式:** `functionSchema`

**実行条件:** 常に実行（暫定的に `controlSystem=VFGLF` を渡し、エラーコードがあれば併用する）

**入力パラメータ（Ver 1.1）:**

| パラメータ | 型 | 必須 | 説明 |
|---|---|---|---|
| `query` | string | ✓ | 不具合内容（ユーザ入力） |
| `controlSystem` | string | — | 暫定固定値 `VFGLF`。未指定でも Lambda 側で `VFGLF` を使用 |
| `errorCode` | string | — | ★ Ver 1.1 追加。半角英数字3文字のエラーコード。なければ省略 |

**KB メタデータフィルター:**

```python
andAll([
    equals("document", "Trouble-Cases"),   # または Trouble-Reports
    equals("model", model),                # model が確定している場合のみ
    equals("error-code", errorCode),       # errorCode がある場合のみ（Ver 1.1）
])
```

**DynamoDB 書き込み:** `write_citations(session_id, results, source_action="trouble_cases")`  ★ `source_action` タグ追加（Ver 1.1）

**上位5件を返却**

---

### 4.3 Action 3: searchTroubleshootManuals（マニュアル検索）

**目的:** `control-system=VFGLF` 固定と任意のエラーコードで絞り込んだトラブルシュートマニュアルを検索する

**呼び出し形式:** `functionSchema`

**実行条件:** 常に実行（②と同タイミング）

**入力パラメータ（Ver 1.1）:**

| パラメータ | 型 | 必須 | 説明 |
|---|---|---|---|
| `query` | string | ✓ | 不具合内容（ユーザ入力） |
| `controlSystem` | string | — | 暫定固定値 `VFGLF`。未指定でも Lambda 側で `VFGLF` を使用 |
| `errorCode` | string | — | ★ Ver 1.1 追加。半角英数字3文字のエラーコード。なければ省略 |

**KB メタデータフィルター（Ver 1.1 変更）:**

```python
# Ver 1.0: フィルターなし（全文検索）
# Ver 1.1 temporary: control-system=VFGLF / errorCode でフィルター
andAll([
    equals("model", model),         # model が確定している場合のみ
    equals("error-code", errorCode),# errorCode がある場合のみ
])
```

**DynamoDB 書き込み（★ Ver 1.1 新規追加）:** `write_citations(session_id, results, source_action="manual")`

**上位3件を返却**

---

### 4.4 Action 4: searchCMaterialDocs（C資料検索）

**目的:** ②③の検索結果から抽出したキーワードで C資料を検索する

**呼び出し形式:** `functionSchema`

**実行条件:** ②③の完了後に実行

**入力パラメータ（Ver 1.1）:**

| パラメータ | 型 | 必須 | 説明 |
|---|---|---|---|
| `query` | string | ✓ | ★ Ver 1.1 変更: ②③の結果テキストから Agent が抽出したキーワード（不具合内容そのものではない） |
| `model` | string | — | 確定済み機種。なければ省略 |

**KB メタデータフィルター:**

```python
andAll([
    equals("document", "C資料"),
    equals("model", model),  # model が確定している場合のみ
])
```

**DynamoDB 書き込み:** `write_citations(session_id, results, source_action="c_material")`  ★ `source_action` タグ付き（Ver 1.1 明示）

**上位5件を返却**

---

## 5. 機種（model）の優先順位

Ver 1.1 で明確化。エージェントは以下の優先順で機種を確定し、②③④のフィルターに使用する。

```
① GetSiteInfo の取得値（constructionNumber で DB から取得した model）
      ↓ なければ
ユーザ入力の model フィールド
      ↓ なければ
フィルターなし（全機種を対象に検索）
```

---

## 6. プロンプト設計

### 6.1 System Prompt（Bedrock Agent オーケストレーション指示）

```
あなたは昇降機のトラブルシューティング専門エージェントです。
以下のルールに従って、入力された情報をもとに順次アクションを実行し、観点別に整理した回答を生成してください。

【アクション実行ルール】

① GetSiteInfo（現場情報取得）:
- 入力に工事番号（constructionNumber）が含まれる場合のみ実行する。
- 含まれない場合はこのアクションをスキップする。
- 実行した場合、取得した「機種（model）」を以降のすべての検索アクションで使用する。

機種の確定:
- GetSiteInfo で取得できた場合 → その値を使用
- GetSiteInfo を実行しなかった、または機種が取得できなかった場合 → ユーザ入力の機種を使用
- どちらもない場合 → 機種フィルターなしで検索する

② searchTroubleCases（トラブル事例検索）:
- 「不具合内容」をクエリとして検索する。
- 暫定的に `controlSystem=VFGLF` をフィルター条件として渡し、エラーコードがあれば併用する。

③ searchTroubleshootManuals（マニュアル検索）:
- 「不具合内容」をクエリとして検索する。
- 暫定的に `controlSystem=VFGLF` をフィルター条件として渡し、エラーコードがあれば併用する。

④ searchCMaterialDocs（C資料検索）:
- ②③で取得した検索結果のテキストを分析し、C資料検索に最適なキーワードを抽出して検索クエリとする。
- 確定した機種をフィルター条件として渡す。

【回答形式】

以下の観点別に情報を整理して回答すること。

【サイト情報】
（GetSiteInfo を実行した場合のみ記載。現場名・機種・制御システム・担当者を整理する）

【トラブル事例】
（②の結果をもとに。類似事例・過去の対処内容を提示する）

【マニュアル】
（③の結果をもとに。推奨手順・注意事項を提示する）

【C資料】
（④の結果をもとに。技術詳細・部品情報を提示する）

【推奨アクション】
（①〜④を総合した具体的な対処手順を段階的に提示する）

【原則】
- 安全性を最優先とする
- 取得できた情報のみに基づいて回答する（推測を避ける）
- 根拠となった情報源を明示する
- 情報が不足している観点は「情報なし」と明記する
```

### 6.2 Orchestrator 入力プロンプトフォーマット

```python
def format_agent_input(body: dict) -> str:
    lines = [
        "以下のトラブル情報を分析してください。",
        "",
    ]
    if body.get("constructionNumber"):
        lines.append(f"工事番号: {body['constructionNumber']}")
    else:
        lines.append("工事番号: （未入力）")
    if body.get("model"):
        lines.append(f"機種: {body['model']}")
    else:
        lines.append("機種: （未入力）")
    lines.append(f"不具合内容: {body['troubleDescription']}")
    if body.get("errorCode"):
        lines.append(f"エラーコード: {body['errorCode']}")
    else:
        lines.append("エラーコード: （未入力）")
    return "\n".join(lines)
```

---

## 7. AWS リソース

| リソース | 値 |
|---|---|
| Bedrock Agent ID | `D6FAGLJPPO` |
| Agent Alias | `TSTALIASID`（DRAFT）|
| Foundation Model | `us.anthropic.claude-haiku-4-5-20251001-v1:0` |
| Knowledge Base ID | `OCLVRJDMAH` |
| DynamoDB: sessions | `troubleshooting-sessions`（TTL: 30日） |
| DynamoDB: sites | `sites`（PK: constructionNumber） |
| API Gateway | `troubleshooting-api`（専用 Gateway） |
| リージョン | `us-east-1` |

---

## 8. Lambda 構成

| Lambda 関数名 | 役割 | 呼び出し形式 |
|---|---|---|
| `troubleshooting-orchestrator` | エントリーポイント・セッション管理・後処理 | API Gateway → 直接 |
| `troubleshooting-db-search` | DynamoDB から現場情報取得 | apiSchema (POST /site-info) |
| `troubleshooting-kb-search1` | トラブル事例・報告書 KB 検索 | functionSchema (`searchTroubleCases`) |
| `troubleshooting-kb-search2` | マニュアル KB 検索 | functionSchema (`searchTroubleshootManuals`) |
| `troubleshooting-kb-search3` | C資料 KB 検索 | functionSchema (`searchCMaterialDocs`) |
| `troubleshooting-history` | 履歴一覧・詳細取得 | API Gateway → 直接 |
| `troubleshooting-authorizer` | Cognito JWT 検証・userId 抽出 | Lambda Authorizer |

---

## 9. Ver 1.1 変更内容と実装手順

### 9.1 変更サマリ

| 変更対象 | Ver 1.0 の挙動 | Ver 1.1 の挙動 |
|---|---|---|
| ① GetSiteInfo 実行条件 | 常に実行 | 工事番号あり時のみ実行 |
| 機種の決定方法 | ユーザ入力のみ | ①取得値 → ユーザ入力値 の優先順 |
| ② KB Search1 フィルター | model + controlSystem | control-system=VFGLF + errorCode |
| ③ KB Search2 フィルター | なし（全文検索） | control-system=VFGLF + errorCode |
| ③ KB Search2 引用保存 | 保存しない | DynamoDB に write_citations() で保存 |
| ④ KB Search3 クエリ | 不具合内容（ユーザ入力） | ②③結果から Agent が抽出したキーワード |
| sourceDocuments 構造 | source_action なし | source_action フィールドを追加 |
| Agent 回答形式 | 自由形式 | 観点別セクション（サイト情報・事例・マニュアル・C資料・推奨アクション） |
| UI 引用表示 | 区別なし | ②③④バッジで取得元を表示 |

### 9.2 Bedrock Agent システムプロンプト変更

**変更箇所:** AWS マネジメントコンソール → Bedrock → Agents → `D6FAGLJPPO` → Edit → Instructions

上記 §6.1 の System Prompt に全文置き換える。

---

### 9.3 kb-search1 Lambda 変更（source_action タグ追加）

**ファイル:** `lambda/troubleshooting/kb-search1/app.py`

**変更点:** `write_citations()` に `source_action` パラメータを追加

```python
# Before（Ver 1.0）
def write_citations(session_id: str, results: list) -> None:
    citations = []
    for r in results:
        ...
        citations.append({
            "uri": ..., "title": ..., "document": ...,
            "model": ..., "score": ...,
        })

# After（Ver 1.1）
def write_citations(session_id: str, results: list) -> None:
    citations = []
    for r in results:
        ...
        citations.append({
            "uri": ..., "title": ..., "document": ...,
            "model": ..., "score": ...,
            "source_action": "trouble_cases",  # ← 追加
        })
```

---

### 9.4 kb-search2 Lambda 変更（フィルター追加 + write_citations 新規実装）

**ファイル:** `lambda/troubleshooting/kb-search2/app.py`

**変更点 1:** `model` / `errorCode` パラメータによるメタデータフィルターを追加

```python
# Before（Ver 1.0）: フィルターなし
response = bedrock_client.retrieve(
    knowledgeBaseId=KB_ID,
    retrievalConfiguration={"vectorSearchConfiguration": {"numberOfResults": 3}},
    retrievalQuery={"text": query},
)

# After（Ver 1.1 temporary）: control-system=VFGLF / errorCode フィルターを追加
def build_metadata_filter(model: str | None, error_code: str | None) -> dict | None:
    conditions = []
    if model:
        conditions.append({"equals": {"key": "model", "value": model}})
    if error_code:
        conditions.append({"equals": {"key": "error-code", "value": error_code}})
    if not conditions:
        return None
    return {"andAll": conditions} if len(conditions) > 1 else conditions[0]

metadata_filter = build_metadata_filter(model, error_code)
config = {"vectorSearchConfiguration": {"numberOfResults": 3}}
if metadata_filter:
    config["vectorSearchConfiguration"]["filter"] = metadata_filter

response = bedrock_client.retrieve(
    knowledgeBaseId=KB_ID,
    retrievalConfiguration=config,
    retrievalQuery={"text": query},
)
```

**変更点 2:** `write_citations()` を新規実装（kb-search1/3 と同パターン）

```python
def write_citations(session_id: str, results: list) -> None:
    table = dynamodb.Table(SESSIONS_TABLE)
    citations = []
    for r in results:
        loc = r.get("location", {}).get("s3Location", {})
        meta = r.get("metadata", {})
        uri = loc.get("uri", "")
        if not uri or uri.endswith(".md"):
            continue
        citations.append({
            "uri": uri,
            "title": meta.get("title", ""),
            "document": meta.get("document", ""),
            "model": meta.get("model", ""),
            "score": Decimal(str(r.get("score", 0))),
            "source_action": "manual",  # ← manual タグ
        })
    if citations:
        table.update_item(
            Key={"session_id": session_id},
            UpdateExpression="SET citations = list_append(if_not_exists(citations, :empty), :c)",
            ExpressionAttributeValues={":c": citations, ":empty": []},
        )
```

---

### 9.5 kb-search3 Lambda 変更（source_action タグ追加）

**ファイル:** `lambda/troubleshooting/kb-search3/app.py`

kb-search1 と同様に `write_citations()` に `"source_action": "c_material"` を追加。

---

### 9.6 Orchestrator Lambda 変更（source_action フィールドを保持）

**ファイル:** `lambda/troubleshooting/orchestrator/app.py`

**変更点:** `build_source_documents()` で DynamoDB から取得した citations の `source_action` フィールドを `sourceDocuments` に引き継ぐ

```python
# Before（Ver 1.0）
def _citation_to_source_doc(citation: dict, presigned_url: str) -> dict:
    return {
        "documentName": ...,
        "title": citation.get("title"),
        "sourceUri": presigned_url,
        "documentType": citation.get("document", ""),
        "model": citation.get("model", ""),
        "relevance": float(citation.get("score", 0)),
    }

# After（Ver 1.1）
def _citation_to_source_doc(citation: dict, presigned_url: str) -> dict:
    return {
        "documentName": ...,
        "title": citation.get("title"),
        "sourceUri": presigned_url,
        "documentType": citation.get("document", ""),
        "model": citation.get("model", ""),
        "relevance": float(citation.get("score", 0)),
        "source_action": citation.get("source_action", ""),  # ← 追加
    }
```

---

### 9.7 Frontend 変更（②③④バッジ表示）

**ファイル:** `frontend/src/app/troubleshooting/page.tsx`

`sourceDocuments` の `source_action` フィールドをもとにバッジを表示する。

| source_action | 表示バッジ | 色（例） |
|---|---|---|
| `trouble_cases` | ② トラブル事例 | 青 |
| `manual` | ③ マニュアル | 緑 |
| `c_material` | ④ C資料 | 橙 |

```tsx
const SOURCE_ACTION_LABELS: Record<string, string> = {
  trouble_cases: "② トラブル事例",
  manual: "③ マニュアル",
  c_material: "④ C資料",
};

// SourceDocument カード内
<span className="badge">
  {SOURCE_ACTION_LABELS[doc.source_action] ?? doc.source_action}
</span>
```

---

### 9.8 実装チェックリスト

- [ ] Bedrock Agent システムプロンプトを §6.1 に更新
- [ ] kb-search1: `write_citations()` に `"source_action": "trouble_cases"` を追加
- [ ] kb-search2: `build_metadata_filter()` を実装・適用
- [ ] kb-search2: `write_citations()` を新規実装（`"source_action": "manual"`）
- [ ] kb-search3: `write_citations()` に `"source_action": "c_material"` を追加
- [ ] orchestrator: `_citation_to_source_doc()` に `source_action` フィールドを追加
- [ ] frontend: `SOURCE_ACTION_LABELS` マップを追加・バッジ表示を実装
- [ ] E2E テスト: 工事番号あり/なし 両パターンで sourceDocuments の source_action を確認
