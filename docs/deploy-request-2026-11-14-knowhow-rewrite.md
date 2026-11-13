# ノウハウカード本文の書き換え案 デプロイ依頼書（dev・既定オフ）

@yuki-mebs（itai） cc: デプロイ担当

**依頼日:** 2026-11-14
**ブランチ:** `mona` 系 → `develop` へ PR マージ後に作業（マージの扱いは `AGENTS.md` の「マージ担当」に従う）
**緊急度:** 低（既定オフ。有効化しなければ何も変わらない）
**対象:** dev 環境のみ。prod には作られない（Condition で dev 限定）
**対象スタック:** phase2（`infrastructure/sam/phase2-template.yaml` のスタック）

---

## 0. 3行サマリ

1. 管理者が確認済みの根拠を材料に、AI がカード本文の書き換え案を返す Lambda と API を追加した（`POST /rag/knowhow/rewrite-proposal`）
2. **既定オフ**。SAM パラメータ `KnowhowRewriteEnabled=true` を渡したときだけ、dev に関数・ロール・経路ができる
3. 何も保存しない。IAM は Bedrock の `InvokeModel` だけ

## 1. 何を足したか

| 内容 | 場所 |
| --- | --- |
| Lambda（`knowhow-rewrite-${Environment}`） | `lambda/rag/knowhow-rewrite/` |
| SAM: パラメータ `KnowhowRewriteEnabled`、Condition `KnowhowRewriteDevEnabled`、ロール `KnowhowRewriteLambdaRole`、関数 `KnowhowRewriteFunction`、RagApi への経路、Output `KnowhowRewriteFunctionArn` | `infrastructure/sam/phase2-template.yaml` |
| API 契約・検証規則・限界 | `docs/features/development/knowhow-rewrite-proposal-contract.md` |

既存リソースの変更・削除は無い。フロントの画面は別 PR（Amplify 側の変数で表示を切り替える）。

## 2. 有効化の手順（dev）

1. phase2 スタックを、パラメータ `KnowhowRewriteEnabled=true` を付けてデプロイする。他のパラメータは現状のままにする
   * 例: 既存のデプロイ手順に `--parameter-overrides ... KnowhowRewriteEnabled=true` を足す（プロファイル・スタック名は現行の運用どおり。ここでは固定しない）
2. Amplify の dev 用ブランチに環境変数 `NEXT_PUBLIC_ENABLE_KNOWHOW_REWRITE=true` を設定して再ビルドする
3. 共有の dev でフロントを出したくないときは、手順 2 を行わない（API だけ有効にして動作確認ができる）

SAM をマージしても AWS には自動では入らない（`AGENTS.md` のとおり。「SAM は itai」）。

## 3. IAM の追加

* 新しいロール `KnowhowRewriteLambdaRole` を作る（`AWSLambdaBasicExecutionRole` と `bedrock:InvokeModel` のみ）
* `bedrock:InvokeModel` の対象は `BedrockModelId` の推論プロファイルと基盤モデル。`SenpaiSynthesisLambdaRole` と同じ組み立て
* DynamoDB・S3・`bedrock:Retrieve` は付けていない。既存ロールの変更は無い

## 4. 費用の目安の考え方

* 1 回の呼び出しで Bedrock を 1 回だけ呼ぶ（再試行なし）。入力は数千字、出力は書き換えた節の本文と理由（上限 `max_tokens` 4,096）
* 費用は「呼び出し回数 × （入力・出力トークン数 × `BedrockModelId` の単価）」。管理者が手で押したときだけ呼ばれるため、回数は管理者の操作に比例する
* **実測はしていない**。トークン数は CloudWatch ログの `inputTokens` / `outputTokens`（本文は出ない）で、配備後に見積もれる

## 5. 配備後の確認

1. 管理者のユーザーで `POST /rag/knowhow/rewrite-proposal` を呼び、200 で `sections` が返ること（リクエスト例は `tests/fixtures/knowhow-rewrite/contract.json` の `request`）
2. 管理者以外のユーザーで 403（`FeatureUnavailable`）になること
3. CloudWatch Logs（`/aws/lambda/knowhow-rewrite-<環境名>`）に、`event: knowhow_rewrite` の件数・トークン数・`status` だけが出ていて、本文・質問・回答・ID が出ていないこと
4. 呼び出し後、DynamoDB・S3 に新しい書き込みが無いこと（権限が無いので書けない）

**未確認:** Bedrock の実出力での挙動（JSON を守るか、`rejected` の頻度、読み取り 24 秒で足りるか）、Lambda のメモリ使用量、dev の API Gateway 経由の実機。単体テストとテンプレートの静的検査（cfn-lint）までを確認した。

## 6. 戻し方

* SAM パラメータ `KnowhowRewriteEnabled=false` で再デプロイする。関数・ロール・経路が dev から消える（保存データが無いので後始末は不要）
* Amplify の `NEXT_PUBLIC_ENABLE_KNOWHOW_REWRITE` も外す（または `false`）
