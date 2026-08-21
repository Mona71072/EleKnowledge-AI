# 【緊急】セキュリティ修正 デプロイ依頼書

@yukiworkspace（itai） cc: デプロイ担当

**依頼日:** 2026-07-29
**ブランチ:** `mona` → **`develop` へ PR マージ後に作業**
**緊急度:** 最高（本番で平文パスワードが CloudWatch Logs に記録され続けています）
**対象アカウント／リージョン:** `730972069979` / `ap-northeast-1`
**必要プロファイル:** `datautl-bple-mebs`

---

## 0. itai 向け：何が自動で、何が手動か

| 対象 | 反映方法 | あなた（itai）の作業 |
|---|---|---|
| **Amplify（フロント）** | `develop` にマージされると **自動** ビルド・デプロイ | **不要**（PR マージを待つだけ） |
| **Lambda / API Gateway（バックエンド）** | **git push では反映されない** | **必須** — 下記 SAM 3 本 + ログ削除 |

**お願い:**

1. **PR の内容を確認**してください（認可ロジック・テンプレート変更・破壊的変更の有無）。
2. **`develop` マージ後**、本書の **§2 SAM デプロイ** と **§3 ログ削除** を実行してください。
3. Amplify 以外（Lambda・API Gateway・CloudWatch ログ）は **リポジトリに push しただけでは AWS に届きません**。必ず `sam deploy` が必要です。
4. 問題があれば PR にコメントするか、マージ前に差し戻してください。

---

## 0.1. 3行サマリ

1. **SAM スタックを 3 本デプロイ**してください（phase1 / phase2 / announcements-monitoring）。
2. デプロイ後、**CloudWatch のロググループを 4 本削除**してください（コードでは消えません）。
3. **phase3 は今回の対象外**。**Amplify（フロント）は `develop` マージで自動** — 追加作業不要。

---

## 1. 何を直したか

| ID | 内容 | 変更ファイル |
|----|------|------------|
| C-1 | API Gateway の `DataTraceEnabled` を `false` に。有効時はリクエストボディ全文がログに出るため、`/auth/login` 等の**平文パスワード**がログに残っていた | `phase1-template.yaml`<br>`phase2-template.yaml`<br>`announcements-monitoring-template.yaml` |
| C-2 | チャット管理 API に所有者チェックを追加。従来は `userId` をクエリ文字列から受け取っており、**任意の認証済ユーザーが他人の会話を閲覧・削除できた** | `lambda/chat/chat-management/app.py` |
| C-3 | RAG API の `userId` をボディではなく Cognito クレームから取得。既存セッション指定時の所有者検証を追加 | `lambda/rag/rag-function/app.py` |
| （付随） | フロントから不要な `?userId=` を削除。エラーログに ID トークンが出ていた箇所を修正 | `frontend/src/app/chat/page.tsx` |

差分規模: 6 ファイル / +154 −40 行。

---

## 2. デプロイ手順

### 事前確認（重要）

`rag-dev` は 2026-07-27 に `aws lambda update-function-code` で直接更新されており、CloudFormation とドリフトしています（[task-history.md](task-history.md) 参照）。

**そのため phase2 の changeset には、今回の修正以外の差分も表示されます。これは想定内です**（ドリフトの解消）。ただし念のため、現在稼働中のコードが本ブランチのソースと一致しているか、デプロイ前に確認してください。

```bash
aws lambda get-function --function-name rag-dev --region ap-northeast-1 --profile datautl-bple-mebs --query 'Configuration.[CodeSha256,LastModified]'
```

### ① phase1（最優先 — パスワードのログ出力を止める）

```bash
cd infrastructure/sam && sam build --template phase1-template.yaml && sam deploy --config-file samconfig.toml --stack-name EleKnowledge-dev-phase1 --profile datautl-bple-mebs
```

### ② phase2（RAG / Chat の認可修正）

```bash
cd infrastructure/sam && sam build --template phase2-template.yaml && sam deploy --config-file samconfig.toml --stack-name EleKnowledge-dev-phase2 --profile datautl-bple-mebs
```

### ③ announcements-monitoring

```bash
cd infrastructure/sam && sam build --template announcements-monitoring-template.yaml && sam deploy --config-file samconfig-announcements-monitoring.toml --profile datautl-bple-mebs
```

> スタック名が上記と異なる場合は、実環境の名前に読み替えてください。
> `docs/DEPLOYMENT_GUIDE.md` と `docs/deployment-guide.md` は**東京移行前の内容（us-east-1・旧スタック名）のままで古い**ため参照しないでください。手順書の更新は別途必要です。

---

## 3. デプロイ後に必ず実施：既存ログの削除

**コード修正では既に記録されたログは消えません。** 出力先はテンプレートで定義している `/aws/apigateway/*` ではなく、API Gateway が自動生成する以下のロググループです。

| ロググループ | API | 含まれる機密情報 |
|---|---|---|
| `API-Gateway-Execution-Logs_mqsyka1v9j/dev` | 認証 | **平文パスワード**（最優先） |
| `API-Gateway-Execution-Logs_lwi9g3kzik/dev` | RAG | 質問文・AI 回答全文・署名付き URL |
| `API-Gateway-Execution-Logs_92pdw6k1o4/dev` | Chat | 会話履歴 |
| `API-Gateway-Execution-Logs_0q3vewys59/dev` | お知らせ/メトリクス | — |

### 手順

**(1) まず影響範囲を確認**（何件・いつからパスワードが記録されていたか）

```bash
aws logs filter-log-events --log-group-name "API-Gateway-Execution-Logs_mqsyka1v9j/dev" --filter-pattern "password" --max-items 5 --region ap-northeast-1 --profile datautl-bple-mebs
```

**(2) 最古のログ日時を記録**（パスワードリセット要否の判断材料になります）

```bash
aws logs describe-log-streams --log-group-name "API-Gateway-Execution-Logs_mqsyka1v9j/dev" --order-by LastEventTime --region ap-northeast-1 --profile datautl-bple-mebs --query 'logStreams[0].[logStreamName,firstEventTimestamp]'
```

**(3) 削除**（(1)(2) の結果を保全してから実行してください）

```bash
aws logs delete-log-group --log-group-name "API-Gateway-Execution-Logs_mqsyka1v9j/dev" --region ap-northeast-1 --profile datautl-bple-mebs
```

残り 3 本も同様に削除してください。

---

## 4. 動作確認

### C-1 の確認（ログにボディが出ないこと）

デプロイ後にログイン操作を 1 回行い、ロググループが再作成されないこと、または新しいログにボディが含まれないことを確認。

### C-2 / C-3 の確認（正常系）

1. ログインしてチャット画面を開く → **セッション一覧が今まで通り表示されること**
2. 過去セッションを開く → メッセージが読めること
3. 新規質問を送信 → 回答が返ること
4. セッションを削除 → 消えること
5. 👍/👎 フィードバック → エラーにならないこと

### C-2 の確認（異常系 — 他人のセッションを弾くこと）

自分のトークンで、他ユーザーの `sessionId` を指定して 404 が返ることを確認します。

```bash
curl -i -H "Authorization: Bearer <自分のIDトークン>" "https://92pdw6k1o4.execute-api.ap-northeast-1.amazonaws.com/dev/chat/sessions/<他人のsessionId>/messages"
```

**期待値: `404 NotFound`**（修正前は 200 で他人の会話全文が返っていました）

---

## 5. ロールバック

いずれも CloudFormation 管理なので、問題があれば直前のバージョンへ再デプロイで戻せます。

ただし **C-1 のロールバックは避けてください**（パスワードのログ出力が再開されます）。C-2 / C-3 に問題が出た場合は、`DataTraceEnabled: false` を維持したまま Lambda コードのみ戻す形にしてください。

---

## 6. 別途、判断が必要な事項（技術ではなく運用の判断）

ログに記録されていた期間のパスワードは**漏洩したものとして扱うのが妥当**です。第 3 節 (1)(2) で確認した記録期間をもとに、以下をセキュリティ／運用責任者に確認してください。

- 全ユーザーへのパスワードリセットを実施するか
- 該当期間のログへのアクセス履歴（CloudTrail）を確認するか
- インシデントとして報告する必要があるか

---

## 7. 参考

- 詳細な調査レポート: [docs/code-review-2026-07-29.md](code-review-2026-07-29.md)
  （今回の CRITICAL 3 件のほか、HIGH 5 件・MEDIUM 11 件・LOW 10 件を記載）
- 未対応で優先度が高いもの:
  - **H-2**: `orchestrator/app.py` の署名付き URL が期限 30 日指定（SigV4 上限 7 日超）で、トラブルシューティングの資料リンクが機能していない可能性
  - **M-1**: バックエンドに CI が無く、毎回この手作業デプロイが必要な状態。GitHub Actions の導入を推奨
