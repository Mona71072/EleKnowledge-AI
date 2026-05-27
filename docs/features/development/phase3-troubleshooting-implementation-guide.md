---
status: development
phase: 3
last-verified: 2026-05-26
related-code: lambda/troubleshooting/, frontend/src/app/troubleshooting/
---

# トラブルシューティング エージェント 実装ガイド — Ver 1.1

## ドキュメント情報

| 項目 | 内容 |
|------|------|
| **バージョン** | **1.1** |
| **ステータス** | 実装ガイド |
| **対象** | Phase 3 本実装フェーズ |
| **最終更新** | 2026-05-26 |

本ドキュメントは [agent-spec.md](../../agent-spec.md) Ver 1.1 の仕様に基づいた実装ガイドです。  
機能仕様は [phase3-troubleshooting-spec.md](phase3-troubleshooting-spec.md) も参照してください。

---

## バージョン履歴

| Ver | 日付 | 変更概要 |
|-----|------|----------|
| 1.0.0 | 2026-01-26 | PoC 実装ガイド（初版） |
| **1.1** | **2026-05-26** | **Ver 1.1 仕様に対応。条件分岐・フィルター変更・source_action・UIバッジの実装手順を追加** |

---

## 1. Ver 1.1 変更概要

### 1.1 変更一覧

| # | 変更対象 | 変更内容 | 難易度 |
|---|---|---|---|
| A | Bedrock Agent システムプロンプト | 条件分岐ロジック・観点別出力形式を追加 | 低（コンソール操作のみ） |
| B | kb-search1 Lambda | `write_citations()` に `source_action` タグを追加 | 低 |
| C | kb-search2 Lambda | メタデータフィルター追加 + `write_citations()` 新規実装 | 中 |
| D | kb-search3 Lambda | `write_citations()` に `source_action` タグを追加 | 低 |
| E | orchestrator Lambda | `source_action` フィールドを `sourceDocuments` に引き継ぐ | 低 |
| F | Frontend | ②③④ バッジを実装 | 中 |

### 1.2 実装順序（推奨）

```
A（Agent プロンプト）→ B, D（KB タグ追加）→ C（KB2 フィルター＋引用保存）
→ E（Orchestrator）→ F（Frontend）→ E2E テスト
```

A〜E は互いに影響が少なく並列作業も可能。F は E の完了後に開始する。

---

## 2. 変更 A: Bedrock Agent システムプロンプト

### 2.1 変更箇所

AWS マネジメントコンソール → Bedrock → Agents → `D6FAGLJPPO` → **Edit** → **Instructions**

### 2.2 更新後プロンプト

[agent-spec.md §6.1](../../agent-spec.md) の System Prompt に全文置き換える。

### 2.3 確認方法

コンソールの **Test** タブで以下の2パターンを実行し、各観点セクションが出力されることを確認する。

```
# パターン1: 工事番号あり
工事番号: EIK54801
機種: （未入力）
不具合内容: エレベーターが途中で停止する
エラーコード: E34

→ 【サイト情報】が表示され、機種がサイト情報から取得されること
→ ②③に control-system=VFGLF・エラーコードフィルターが渡されること

# パターン2: 工事番号なし・機種あり
工事番号: （未入力）
機種: KE-LG
不具合内容: 扉が開かない
エラーコード: （未入力）

→ 【サイト情報】が表示されないこと
→ ②③に機種フィルターのみ渡されること
```

---

## 3. 変更 B: kb-search1 Lambda（source_action タグ追加）

**ファイル:** `lambda/troubleshooting/kb-search1/app.py`

### 3.1 変更箇所

`write_citations()` 内の citations リスト構築部に `"source_action": "trouble_cases"` を追加する。

```python
# lambda/troubleshooting/kb-search1/app.py

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
            "source_action": "trouble_cases",           # ← この行を追加
        })
    if citations:
        table.update_item(
            Key={"session_id": session_id},
            UpdateExpression="SET citations = list_append(if_not_exists(citations, :empty), :c)",
            ExpressionAttributeValues={":c": citations, ":empty": []},
        )
```

### 3.2 確認方法

DynamoDB コンソール → `troubleshooting-sessions` テーブルで対象セッションの `citations` リストに `"source_action": "trouble_cases"` が含まれることを確認する。

---

## 4. 変更 C: kb-search2 Lambda（フィルター追加 + write_citations 新規実装）

**ファイル:** `lambda/troubleshooting/kb-search2/app.py`

これが Ver 1.1 で最も変更量が多い。

### 4.1 パラメータ追加

エージェントから `model` / `errorCode` を受け取れるよう `_extract_params()` を更新する。

```python
def _extract_params(event: dict) -> tuple[str, str | None, str | None]:
    """
    Returns: (query, model, error_code)
    エージェントの functionSchema 形式と直接呼び出し形式の両方に対応。
    """
    # functionSchema 形式（Bedrock Agent からの呼び出し）
    if "function" in event:
        params = {p["name"]: p["value"]
                  for p in event.get("parameters", [])}
        return (
            params.get("query", ""),
            params.get("model"),
            params.get("errorCode"),
        )
    # 直接呼び出し形式（テスト用）
    body = event.get("body", {})
    if isinstance(body, str):
        body = json.loads(body)
    return (
        body.get("query", ""),
        body.get("model"),
        body.get("errorCode"),
    )
```

### 4.2 メタデータフィルター実装

```python
def build_metadata_filter(model: str | None, error_code: str | None) -> dict | None:
    conditions = []
    if model:
        conditions.append({"equals": {"key": "model", "value": model}})
    if error_code:
        conditions.append({"equals": {"key": "error-code", "value": error_code}})
    if not conditions:
        return None
    if len(conditions) == 1:
        return conditions[0]
    return {"andAll": conditions}
```

### 4.3 KB 検索呼び出しの変更

```python
def search_knowledge_base(query: str, model: str | None, error_code: str | None) -> list:
    config = {
        "vectorSearchConfiguration": {
            "numberOfResults": 3,
            "overrideSearchType": "SEMANTIC",
        }
    }
    metadata_filter = build_metadata_filter(model, error_code)
    if metadata_filter:
        config["vectorSearchConfiguration"]["filter"] = metadata_filter

    response = bedrock_client.retrieve(
        knowledgeBaseId=KB_ID,
        retrievalConfiguration=config,
        retrievalQuery={"text": query},
    )
    return response.get("retrievalResults", [])
```

### 4.4 write_citations 新規実装

```python
import boto3
from decimal import Decimal

dynamodb = boto3.resource("dynamodb", region_name=os.environ.get("BEDROCK_REGION", "us-east-1"))
SESSIONS_TABLE = os.environ["SESSIONS_TABLE"]

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
            "source_action": "manual",
        })
    if citations:
        table.update_item(
            Key={"session_id": session_id},
            UpdateExpression="SET citations = list_append(if_not_exists(citations, :empty), :c)",
            ExpressionAttributeValues={":c": citations, ":empty": []},
        )
```

### 4.5 lambda_handler 更新

```python
def lambda_handler(event, context):
    try:
        query, model, error_code = _extract_params(event)
        session_id = (event.get("sessionAttributes") or {}).get("session_id")

        results = search_knowledge_base(query, model, error_code)

        # 引用を DynamoDB に保存（session_id がある場合のみ）
        if session_id and results:
            write_citations(session_id, results)

        formatted = format_results(results)
        return _make_response(event, formatted)

    except Exception as e:
        logger.error(f"kb-search2 error: {e}")
        return _make_response(event, "マニュアル検索中にエラーが発生しました")
```

### 4.6 環境変数追加

`SESSIONS_TABLE` 環境変数が kb-search2 に未設定の場合は CDK スタックで追加する。

```python
# infrastructure/cdk/stacks/troubleshooting_stack.py

kb_search2_fn.add_environment("SESSIONS_TABLE", sessions_table.table_name)
sessions_table.grant_read_write_data(kb_search2_fn)  # DynamoDB 権限も付与
```

### 4.7 確認方法

- DynamoDB セッションに `source_action = "manual"` の引用が保存されることを確認
- `model` / `errorCode` を渡したリクエストで KB 検索スコアが改善していることを確認

---

## 5. 変更 D: kb-search3 Lambda（source_action タグ追加）

**ファイル:** `lambda/troubleshooting/kb-search3/app.py`

変更 B と同様。`write_citations()` に `"source_action": "c_material"` を追加する。

```python
citations.append({
    "uri": uri,
    "title": meta.get("title", ""),
    "document": meta.get("document", ""),
    "model": meta.get("model", ""),
    "score": Decimal(str(r.get("score", 0))),
    "source_action": "c_material",   # ← この行を追加
})
```

---

## 6. 変更 E: Orchestrator Lambda（source_action フィールドを保持）

**ファイル:** `lambda/troubleshooting/orchestrator/app.py`

### 6.1 `_citation_to_source_doc()` の変更

```python
def _citation_to_source_doc(citation: dict, presigned_url: str) -> dict:
    uri = citation.get("uri", "")
    file_name = uri.split("/")[-1] if uri else ""
    return {
        "documentName": file_name,
        "title": citation.get("title"),
        "sourceUri": presigned_url,
        "documentType": citation.get("document", ""),
        "model": citation.get("model", ""),
        "relevance": float(citation.get("score", 0)),
        "source_action": citation.get("source_action", ""),  # ← この行を追加
    }
```

### 6.2 確認方法

API レスポンスの `sourceDocuments` 各要素に `source_action` フィールドが含まれていることを確認する。

```bash
# 確認コマンド例
curl -X POST https://<api-url>/analyze \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"constructionNumber":"EIK54801","troubleDescription":"昇降機が停止する","model":"KE-LG","errorCode":"E34"}' \
  | jq '.sourceDocuments[].source_action'
```

---

## 7. 変更 F: Frontend（②③④ バッジ実装）

**ファイル:** `frontend/src/app/troubleshooting/page.tsx`

### 7.1 バッジラベル定数の追加

```typescript
const SOURCE_ACTION_LABELS: Record<string, { label: string; color: string }> = {
  trouble_cases: { label: "② トラブル事例", color: "blue" },
  manual:        { label: "③ マニュアル",   color: "green" },
  c_material:    { label: "④ C資料",       color: "orange" },
};
```

### 7.2 SourceDocument 型の更新

```typescript
interface SourceDocument {
  documentName: string;
  title: string | null;
  sourceUri: string;
  documentType: string;
  model: string;
  relevance: number;
  source_action: string;  // ← 追加
}
```

### 7.3 ドキュメントカードの更新

```tsx
function SourceDocumentCard({ doc }: { doc: SourceDocument }) {
  const badge = SOURCE_ACTION_LABELS[doc.source_action];

  return (
    <div className="source-doc-card">
      {badge && (
        <span
          className="source-action-badge"
          style={{ backgroundColor: badge.color }}
        >
          {badge.label}
        </span>
      )}
      <a href={doc.sourceUri} target="_blank" rel="noopener noreferrer">
        {doc.title ?? doc.documentName}
      </a>
      <span className="relevance">関連度: {(doc.relevance * 100).toFixed(0)}%</span>
    </div>
  );
}
```

### 7.4 CSS（例）

```css
.source-action-badge {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 4px;
  color: white;
  font-size: 0.75rem;
  font-weight: bold;
  margin-right: 8px;
}
```

---

## 8. E2E テスト

### 8.1 テストケース

| TC | 工事番号 | 機種 | エラーコード | 確認内容 |
|---|---|---|---|---|
| TC-01 | あり | なし | あり | ①実行、②③に control-system=VFGLF・エラーコードフィルター適用 |
| TC-02 | なし | KE-LG | なし | ①スキップ、②③に control-system=VFGLF フィルター適用 |
| TC-03 | なし | なし | なし | ①スキップ、②③④フィルターなし |
| TC-04 | あり | KE-LG (入力) | なし | ①実行、機種は DB 取得値を優先（入力値より優先） |

### 8.2 各テストで確認するポイント

1. **DynamoDB `citations` フィールド**: `source_action` が `trouble_cases` / `manual` / `c_material` で保存されているか
2. **API レスポンス**: `sourceDocuments` に `source_action` が含まれるか
3. **回答テキスト**: `【サイト情報】【トラブル事例】【マニュアル】【C資料】【推奨アクション】` の5観点が含まれるか（TC-02/03 では【サイト情報】なし）
4. **Frontend**: 各ドキュメントに正しいバッジが表示されるか

---

## 9. 参考: Ver 1.0 との差分まとめ

```diff
 # kb-search1/app.py
 citations.append({
     "uri": uri,
     ...
+    "source_action": "trouble_cases",
 })

 # kb-search2/app.py（大幅変更）
+def build_metadata_filter(model, error_code): ...
+def write_citations(session_id, results): ...   # 新規
-# フィルターなし全文検索
+# control-system=VFGLF / errorCode フィルター付き検索

 # kb-search3/app.py
 citations.append({
     "uri": uri,
     ...
+    "source_action": "c_material",
 })

 # orchestrator/app.py
 return {
     ...
+    "source_action": citation.get("source_action", ""),
 }

 # frontend/src/app/troubleshooting/page.tsx
+const SOURCE_ACTION_LABELS = { ... }
+interface SourceDocument { ...; source_action: string }
+<span className="source-action-badge">{badge.label}</span>
```
