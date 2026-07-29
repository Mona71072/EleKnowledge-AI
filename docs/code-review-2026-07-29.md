# EleKnowledge-AI コード全体レビュー レポート

**対象:** ブランチ `mona` (HEAD: `2261f49`)
**実施日:** 2026-07-29
**対象範囲:** Lambda (Python, 4,288行) / フロントエンド (Next.js + TS, 5,860行) / IaC (SAM/CDK, 2,766行) / テスト

---

## 0. サマリ

| 重大度 | 件数 | 主な内容 |
|--------|------|----------|
| CRITICAL | 3 | 認証APIの平文パスワードログ出力、チャットAPIのIDOR、RAG APIのuserId偽装 |
| HIGH | 5 | エラー詳細漏洩、署名付きURLの期限超過、zip成果物のドリフト、セッション一覧の欠落、失敗テストの混入 |
| MEDIUM | 11 | CI不在、CORSワイルドカード、競合更新、入力検証漏れ、性能問題ほか |
| LOW | 10 | 死んだコード、重複実装、設定不整合ほか |

**総合評価:** アーキテクチャの骨格（Cognito Authorizer + WAF IP制限 + PITR + TTL/S3アーカイブ）は妥当に設計されています。一方で **「認証」は実装されているが「認可」がほぼ実装されていない** という構造的な欠陥があり、これが最大のリスクです。加えて CI が存在せず、既にテストが1件失敗した状態でコミットされています。

---

## 1. CRITICAL

### C-1. 認証APIで平文パスワードが CloudWatch Logs に記録されている

**該当:** `infrastructure/sam/phase1-template.yaml:606`

```yaml
MethodSettings:
  - ResourcePath: "/*"
    HttpMethod: "*"
    LoggingLevel: INFO
    DataTraceEnabled: true      # ← これ
```

API Gateway の `DataTraceEnabled: true` は **リクエスト/レスポンスのボディ全文** を実行ログに書き出します。この API には以下が載っています。

- `POST /auth/login` — ボディは `{"email": ..., "password": ...}`
- `POST /auth/signup` — 同上
- `POST /auth/confirm-password-reset` — 新パスワードと確認コード

つまり **全ユーザーのパスワードが平文で CloudWatch Logs に蓄積されています。** AWS 自身も本番でのこの設定を明示的に非推奨としています。

同じ設定が他の3箇所にもあり、こちらは RAG の質問文・AI回答全文・署名付きURLがログに残ります（機密文書の内容がログに流出）。

- `phase2-template.yaml:395` (RAG API)
- `phase2-template.yaml:436` (Chat API)
- `announcements-monitoring-template.yaml:372`

**対処:**
1. 4箇所すべてを `DataTraceEnabled: false` に変更し再デプロイ（最優先）。
2. 既存のログストリームの内容を確認し、該当ロググループを削除またはパージ。
3. **ログに載った期間のパスワードは漏洩したものとして扱い、全ユーザーのパスワードリセットを検討。**

---

### C-2. チャット管理APIに所有者チェックが一切ない（IDOR）

**該当:** `lambda/chat/chat-management/app.py`

API Gateway の Cognito Authorizer は「誰かがログイン済みであること」しか保証しません。**どのユーザーであるか** はハンドラ側で検証する必要がありますが、4つのエンドポイントすべてで欠落しています。

| ルート | 問題 | 該当行 |
|--------|------|--------|
| `GET /chat/sessions` | `userId` を**クエリ文字列**から取得。他人のIDを渡せば他人のセッション一覧が読める | `app.py:234` |
| `GET /chat/sessions/{sessionId}/messages` | 所有者チェックなし。sessionId を知れば誰でも会話全文を読める | `app.py:256` |
| `DELETE /chat/sessions/{sessionId}` | 所有者チェックなし。**任意ユーザーが他人の会話を削除できる** | `app.py:277` |
| `PUT /chat/messages/{messageId}/feedback` | 所有者チェックなし | `app.py:293` |

```python
# app.py:233-234 — userId が検証済みクレームではなくクエリ文字列由来
if http_method == 'GET' and path == '/chat/sessions':
    user_id = query_parameters.get('userId')
```

**攻撃例:** 正規ユーザーが自分のトークンで
`GET /chat/sessions?userId=<他人のsub>` を叩くだけで、他人のチャット履歴一覧（タイトル＝質問文の先頭50字）が取得できます。

**正しい実装は同一リポジトリ内に既にあります** — `lambda/troubleshooting/history/app.py:41,52`:

```python
user_id = authorizer.get("userId") or authorizer.get("claims", {}).get("sub") or ""
if not user_id:
    return _response(401, {"error": "認証情報が不正です"})
...
if not item or item.get("userId") != user_id:      # ← 所有者チェック
    return _response(404, {"error": "セッションが見つかりません"})
```

**対処:** chat-management でも `userId` を `event['requestContext']['authorizer']['claims']['sub']` から取得し、`sessionId` 系の操作前に該当アイテムの `userId` と突合する。`userId` クエリパラメータは廃止する。

---

### C-3. RAG API が body の `userId` を無検証で信頼している

**該当:** `lambda/rag/rag-function/app.py:677, 698`

```python
user_id = body.get('userId')          # ← クライアント申告値をそのまま採用
...
chat_history = get_chat_history(session_id, limit=5)   # ← 所有者チェックなし
```

2つの影響があります。

1. **なりすまし書き込み** — メッセージが攻撃者の指定した `userId` で DynamoDB に保存され、`userId-timestamp-index` GSI を汚染します。集計 (`metrics/aggregator`) の activeUsers も汚染されます。
2. **他人の会話内容の間接的漏洩** — 他人の `sessionId` を指定すると、その履歴が `messages` に積まれて Claude に渡され、回答の文脈として反映されます。C-2 と組み合わせると sessionId の入手も容易です。

**対処:** C-2 と同様、`userId` は Cognito クレームから取得。`sessionId` 指定時は、そのセッションが呼び出し元のものか検証する。

---

## 2. HIGH

### H-1. エラーレスポンスが AWS 内部情報を露出

`login/app.py:150`, `signup/app.py:132`, `rag-function/app.py:799` などで、未分類の `ClientError` に対して Cognito/AWS の生メッセージをそのまま返しています。

```python
return {
    'statusCode': 500,
    'body': json.dumps({'error': error_code, 'message': error_message})  # ← 生の AWS メッセージ
}
```

内部リソース名・設定不備・IAM 情報が攻撃者に渡ります。`announcements/write/app.py:244` は正しく汎用メッセージに丸めているので、そちらに揃えるべきです。

### H-2. 署名付きURLの有効期限が SigV4 の上限を超えている（リンクが機能しない）

`lambda/troubleshooting/orchestrator/app.py:201`

```python
ExpiresIn=2592000,   # 30日。SigV4 の上限は 604800 秒 (7日)
```

S3 は `X-Amz-Expires > 604800` の署名付きURLを拒否します。**トラブルシューティング結果の参考資料リンクは全件エラーになっているはず** です。

RAG 側 (`rag-function/app.py:569`) は 604800 で上限内ですが、Lambda 実行ロールの一時認証情報で署名するため実効期限は最長12時間です（この点はコードコメントに記載済み＝既知だが未対処）。長期リンクが必要なら、S3 署名専用ロールの `AssumeRole`（`DurationSeconds` 拡張）か、都度発行するAPI経由に切り替える設計が必要です。

### H-3. コミット済み zip が現行ソースと乖離している

11個の `.zip` がリポジトリに含まれ、内容が古いままです。

```
lambda/troubleshooting/orchestrator.zip 内の app.py  ←→  現行ソース   差分 693行
```

さらに `orchestrator.zip` は `orchestrator/app.py`(1/26) と ルート直下の `app.py`(1/30) の**2つの異なるバージョン**を同梱しています。また同じ zip が2箇所（`lambda/troubleshooting/*.zip` と `lambda/troubleshooting/*/*.zip`）に重複しています。

`scripts/deploy_lambdas.py:48-52` は一時ディレクトリで zip を作り直すため、これらは**デプロイに使われていません**。誤って古いコードを手動デプロイする事故のもとです。

**対処:** 全 zip を `git rm` し、`.gitignore` に `*.zip` を追加。

### H-4. セッション一覧が静かに欠落する

`lambda/chat/chat-management/app.py:69-78`

```python
response = chatlogs_table.query(
    IndexName='userId-timestamp-index',
    FilterExpression='attribute_not_exists(#del) OR #del = :false',
    Limit=limit * 10
)
```

DynamoDB は **`Limit` を `FilterExpression` より先に適用** します。論理削除済みメッセージが蓄積すると、500件読んだうち大半がフィルタで落ち、ユーザーには一覧が欠けて見えます。`LastEvaluatedKey` によるページネーションもないため回復もしません。

**対処:** `LastEvaluatedKey` ループを実装し、必要件数が揃うまで読み進める。根本的には「セッション」を独立エンティティとして持ち、メッセージから毎回導出するのをやめる設計が望ましいです。

### H-5. 失敗するテストがコミットされている

```
$ pytest tests/unit -q
1 failed, 50 passed
FAILED tests/unit/test_orchestrator.py::test_extract_user_id_empty_string
  assert 'anonymous' == ''
```

`orchestrator/app.py:94` は認証情報が空のとき `"anonymous"` を返しますが、テストは `""` を期待しています。これは単なるテスト不整合ではなく実害があります。

- orchestrator は `"anonymous"` でセッションを保存する
- 一方 `history/app.py:41` は同条件で `""` を返し **401** を出す

結果、`anonymous` で保存されたセッションは**永久に誰からも参照できない**孤児データになります。両者の挙動を統一し、認証情報が取れない場合は `401` で弾くのが正解です。

（補足: ローカルの Python が 3.9 のみのため、`test_announcements_monitoring.py` は `str | None` 構文で収集エラーになります。Lambda ランタイムは 3.13 なのでコード側の問題ではありませんが、開発環境の要求 Python バージョンがどこにも明記されていない点は課題です。）

---

## 3. MEDIUM

### M-1. CI が存在しない
`.github/` なし。lint / 型チェック / テストのゲートが一切なく、H-5 のような失敗テストがそのまま main 系ブランチに入ります。リポジトリ自身のルールが掲げる「カバレッジ80%」に対し、**最大かつ最も機密性の高い2モジュール（`rag-function` 813行、`chat-management` 359行）のテストは0件**、フロントエンドも0件です。

### M-2. CORS が全 API・全 Lambda でワイルドカード
`Access-Control-Allow-Origin: '*'` が Lambda 15箇所と SAM テンプレート全4本に散在。WAF の IP 制限があるため実リスクは限定的ですが、社内ネットワーク内の任意サイトから API を叩けます。Amplify のオリジンに固定すべきです。

### M-3. お知らせ更新に競合制御がない
`announcements/write/app.py:157-184` は get_item → マージ → put_item のリードモディファイライトで、`ConditionExpression` がありません。管理者2名の同時編集で片方の変更が消えます。

### M-4. 部分更新時のバリデーション漏れ
`announcements/write/app.py:110` — メンテナンス時間帯の `start < end` チェックは `body` に `type` が含まれるときのみ実行されます。既存のメンテナンス告知に対し `startAt` だけを PATCH すると検証を素通りし、`startAt > endAt` の不正な状態を作れます。

### M-5. 管理画面のお知らせ一覧が全件スキャン
`announcements/write/app.py:192-204` の `list_all()` は毎回テーブル全スキャン。件数増加に比例してコストとレイテンシが伸びます。

### M-6. 日付パラメータが未検証
`metrics/read/app.py:79` — `datetime.fromisoformat(qs['from'])` にユーザー入力を直接渡しており、不正値で `ValueError` → 500 になります。400 を返すべきです。

### M-7. ブラウザコンソールへのトークン出力
`frontend/src/app/chat/page.tsx:346, 469` — エラー時に axios の `err.config` をそのまま `console.error` しています。`config.headers` には `Authorization: Bearer <IDトークン>` が含まれます。同 330行には `console.log('Token available:', !!token)` などデバッグ出力も残存。本番ビルドから除去すべきです。

### M-8. セッション削除が N+1 書き込み
`chat-management/app.py:157-168` — メッセージ1件ごとに `update_item` を逐次実行。件数分のラウンドトリップが発生し、途中で失敗すると**半分だけ削除された**状態になります。`BatchWriteItem` かトランザクションを検討。

### M-9. 正規表現ベースの HTML サニタイズ
`announcements/write/app.py:43-83` の `sanitize_markdown` は正規表現による除去で、原理的にバイパス可能です（属性内改行、エンコード、ネスト等）。現状は react-markdown を `rehype-raw` なしで使っているため実害はありませんが、「セキュリティ対策」として置かれている以上、誰かが `rehype-raw` を足した瞬間に破綻します。コメントに「防御の第2層」と明記されている点は良いので、フロント側の制約もそこに追記すべきです。

### M-10. `rag-function/app.py` が 800行の上限超過
813行。検索・プロンプト構築・引用生成・永続化・HTTP 処理が1ファイルに同居しています。リポジトリ自身のルール（800行上限）に抵触。`retrieval.py` / `prompt.py` / `citations.py` / `handler.py` への分割が妥当です。

### M-11. 設定値の重複と情報露出
- `waf-rules.json` に AWS アカウントID `423623870147` と IPSet ARN がハードコード
- `security-waf-template.yaml:14` と `phase2-template.yaml:158` に**社内出口IP 10件が Default 値として二重に**記載
- `security-waf-template.yaml:17-26` に API Gateway ID 4件がハードコード

資格情報ではありませんが偵察に有用で、かつ3箇所に散らばっているため変更時の同期漏れリスクがあります。SSM Parameter Store への集約を推奨。

---

## 4. LOW

| # | 内容 | 該当 |
|---|------|------|
| L-1 | `.gitignore` に `spec.md` があるが `spec.md` はコミット済み（矛盾） | `.gitignore:6` |
| L-2 | `KNOWLEDGE_BASE_ID` が `'PLACEHOLDER'` にフォールバック。Bedrock 呼び出し時まで失敗が遅延。すぐ下の `CHATLOGS_TABLE` は正しく起動時に `RuntimeError` を投げている | `rag-function/app.py:19` vs `:25` |
| L-3 | 死んだコード: `is_weak_retrieval()` は定義のみで未使用 | `rag-function/app.py:290` |
| L-4 | 放置された PoC: `troubleshooting-small/` はテーブル名 `"sites"` ハードコード、env 参照がコメントアウト、`__main__` ブロック付き、`requirements.txt` に boto3 が2回＋pytest 混入。zip 付きでコミット済み | `lambda/troubleshooting-small/` |
| L-5 | `kb-search1/2/3` がほぼ重複（1と3は 247行中 diff 50行のみ）。共通モジュール化されていない | `lambda/troubleshooting/kb-search*/` |
| L-6 | フロントで `any` が多用（`chat/page.tsx` に約30箇所）。リポジトリの TS ルールに違反 | `frontend/src/app/**` |
| L-7 | `select_retrieval_results()` が同一データに対し1リクエストで2〜3回実行される。`boto3.client('s3')` もリクエスト毎に生成 | `rag-function/app.py:321,547,576` |
| L-8 | 署名付きURL・引用生成のロジックが rag-function と orchestrator で重複実装 | 両ファイル |
| L-9 | `split_pdf` がサイズ推定のため全ページを個別に再シリアライズ。大きな PDF でメモリ・時間を浪費 | `pdf-splitter/app.py:63-70` |
| L-10 | `boto3==1.26.137` を固定している Lambda が2つだけあり、他はランタイム同梱版に依存。python3.13 ランタイムに対し古い boto3 を持ち込むのは非推奨 | `auth/forgot-password`, `auth/confirm-password-reset` |

**参考（実害なし）:** `login/app.py:126` と `forgot-password/app.py:84` に `UserNotFoundException` → 404「アカウントが存在しません」の分岐があり、単体ではユーザー列挙になります。ただし Cognito クライアント側で `PreventUserExistenceErrors: ENABLED` (`phase1-template.yaml:206`) が設定されているため、実際にはこの例外が返らず到達不能です。設定に依存した安全性なので、コード側も汎用メッセージに揃えておくのが堅実です。

---

## 5. 評価できる点

公平を期すため、良く出来ている箇所も記録します。

- **API Gateway レベルでの Cognito Authorizer + WAF IP allowlist + リソースポリシー IP 制限** の三重防御。設計方針は妥当。
- **`troubleshooting/history/app.py` の認可実装** は正しい（所有者チェックあり）。C-2 の修正はこれを横展開すればよい。
- **管理者判定がサーバー側で実施されている** (`announcements/write/app.py:61`, `metrics/read/app.py:50`)。フロントの `admin/layout.tsx` は UI 補助と明記されており、認識が正確。
- **DynamoDB PITR が全テーブルで有効**、TTL + DynamoDB Stream → S3 アーカイブで論理削除後もデータ保全。
- **Cognito のメールドメイン allowlist** (`cognito-domain-guard`) と MFA OPTIONAL / 強パスワードポリシー。
- **コードコメントの質が高い。** 特に `rag-function` の `build_kb_filter` や `merge_retrieval_results` は「なぜ旧実装が0件だったか」「なぜ `stringContains` が必須か」といった過去の障害原因が明記されており、保守性に大きく寄与しています。
- **EMF によるフィードバックメトリクス** (`chat-management/app.py:25`) は、テーブルスキャンを避ける設計として適切。

---

## 6. 推奨対応順序

**第1段階（即時・本番影響あり）**
1. C-1: `DataTraceEnabled: false` × 4箇所 → 再デプロイ → ログ削除 → パスワードリセット要否を判断
2. C-2 / C-3: `userId` を Cognito クレーム由来に変更し、所有者チェックを追加（`history/app.py` を参考実装とする）

**第2段階（1〜2週間）**

3. H-1: エラーメッセージの汎用化
4. H-2: `ExpiresIn` を 604800 以下に修正（＋実効期限の設計見直し）
5. H-5: `extract_user_id` の挙動統一とテスト修正
6. M-1: CI 導入（pytest + ruff + tsc + `next build`）— 以降の再発防止の土台

**第3段階（継続改善）**

7. H-3: zip 削除、H-4: ページネーション修正
8. M-2 CORS 固定、M-3/M-4 バリデーションと競合制御
9. M-10: `rag-function` の分割、L-4/L-5 の重複・死蔵コード整理
10. `rag-function` / `chat-management` のテスト整備（カバレッジ目標に対する最大のギャップ）
