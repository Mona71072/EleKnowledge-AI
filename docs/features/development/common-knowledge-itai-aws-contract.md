---
status: development
last-verified: 2026-10-22
related-code:
  - lambda/knowledge/common-knowledge/
  - infrastructure/sam/common-knowledge-itai-template.yaml
  - tests/integration/test_common_knowledge_aws_adapters.py
  - frontend/src/lib/common-knowledge.mjs
---

# 共通知識: itai専用AWS基盤の実装契約

> 最終検証: 2026-10-22 — 実装前にAWS読取（認証主体・既存itai/共有devスタック・WAF・Amplify itai）、#195/#200のhead・コメント、設計§17の保存hashを照合。実装・配備の結果は末尾の記録へ追記する。

[I1実装契約](common-knowledge-i1-contract.md)の業務ルールは変えず、保存・配布・Git・API配線をAWSで動く形へ移す。方針の正本は設計worktreeのノウハウ設計§17。[引継ぎ](common-knowledge-itai-aws-handoff.md)の許可範囲（itai専用・非破壊・合成データのみ）を超える操作は本契約に含めない。

## 配置と既存資源との関係

| 判断 | 内容 | 理由 |
| --- | --- | --- |
| 分離スタック | 新規 `EleKnowledge-itai-common-knowledge`。既存 `EleKnowledge-itai-phase2`（T2のRAG/チャット/調査）は更新しない | 既存itaiはT2生成テンプレートで、更新するとRAG側へ差分が波及する。役割（候補台帳・Git承認・公開）が異なる |
| 共有物 | Cognito User Pool ARNはExport参照、Regional WAFは既存ACLへの関連付けのみ、IP制限はAPI ResourcePolicy。WAF本体・IPSet・Cognito・共有devは変更しない | T2と同じ参照方式。共有devへの書込IAMを持たない |
| 名前 | 物理名はCloudFormation自動生成。stage `dev`。タグは `gyoumu012Project=ele-knowledge` / `gyoumu012Component=rag` / `gyoumu012Usage=development` / `Purpose=itai-common-knowledge-validation` | 既存区分値を流用し、新しい区分値は台帳の判断として作らない |
| 機能フラグ | `CommonKnowledgeEnabled=false`（既定・今回の配備値）。`GitMode` は `unconfigured` のみ許可 | 実ロール・保持・会社Gitが未決。Git必須操作は503 `GitNotConfigured` |

APIのフロント接続先（Amplify itai）は切り替えない。itaiブランチは自動配信ONで、API URLはアプリ共通値＝共有devを使っているため、接続切替はブランチ環境変数の追加という別操作になる。

## 保存の移植

Service内の直接SQLを廃し、台帳を「作業単位（unit）」と「一覧Query」のドメイン操作に分ける。SQLiteとDynamoDBの両アダプターが同じ契約を満たす。

- **unit**: `get` / `put` / `delete`、操作の `operation_by_key` / `operation` / `target_pending` / `accept_operation` / `finish_operation`。SQLiteは `BEGIN IMMEDIATE`。DynamoDBは強整合GetItemで読んだ版番号 `v` を記録し、書込を `TransactWriteItems` 1回へまとめる。読んだ項目は版一致、未存在で読んだ項目と新規項目は `attribute_not_exists` を条件にし、書かずに読んだ項目もConditionCheckで再検証する。条件不成立・競合は `Contention` とし、操作を拒否確定にせず503で同じ操作IDの再試行へ戻す。
- **冪等・ロック**: 操作本体、`actor+key` の一意項目、同一対象の未完了ロック項目を受付時に同じtransactionで作成。完了／拒否でロックを外す。完了後のjournalはI1と同じく要求本文を残さない。
- **一覧**: 候補は `StateIndex`（状態）と `SubmitterIndex`（本人＋状態）、未完了操作は `PendingIndex`（本人）。GSIは `KEYS_ONLY` で本文を投影しない。1回のQueryで得たキーを基底表から強整合で読み直し、状態・本人・期限・共有範囲を再検証する。無効項目はページから除き、短いページとcursorで続行する。cursorは最後の並び順キーをHMAC付きで返し、offsetは使わない。
- **期限**: APIが期限切れを返さない。保持年限は未決のため、業務データにTTL物理削除を設定しない。TTL属性は合成受入の名前空間だけが設定する。
- **配布**: 台帳と別のprivate S3。artifactは `If-None-Match: *` で不変、既存と同一内容なら成功・異なれば拒否。manifestは `If-Match` ETagでCAS。公開・停止の受付票を操作IDごとに保存し、次のCAS実行者は置き換える前に現行manifestの受付票を必ず作る。これにより、manifest成功後に応答や受付票の保存が失われても、停止後に古い公開の再試行が復活しない。412/409は再読込のうえ有限回で判定する。
- **Git**: `GitMode=unconfigured` では書込・読取・tree照合をすべて503で拒否する。GitHub互換REST（blob/tree/commit/非forceのref更新）のアダプターを実装候補として持つが、配備では選択できない。会社Gitの製品・ホスト・repo・path・資格情報が決まったら、ホスト許可・path許可・操作マーカーcommitの照合・ref競合時の有限再基底を受入してから有効化する。Lambdaの `/tmp` やローカルGitを正本にしない。

## API・Lambda・IAM（責任別）

| Lambda | ルート | 台帳 | 配布S3 | その他 |
| --- | --- | --- | --- | --- |
| intake | `POST/GET /knowledge/contributions`、`GET/PATCH .../{id}`、`GET /knowledge/operations`、`GET .../operations/{id}` | 読取・Query・transaction内の書込 | なし | cursor秘密のGetSecretValue |
| editorial | `GET /cards/{id}`、`PUT .../draft`、`POST .../review-requests`・`/decisions` | 同上 | なし | Git（未設定のため権限なし） |
| publication | `POST .../publish`・`/withdraw` | 同上 | artifact/manifest/受付票のGet・Put | Git読取（同上） |
| reader | `GET /knowledge/published/{id}` | なし | artifact/manifestのGetのみ | なし |
| recovery | `POST /knowledge/operations/{id}/retry` | 同上 | publicationと同じ | 保存済み要求を元の操作として再認可する。新規操作は受けない |

全関数は認可表（別DynamoDB表）を `GetItem` だけで読む。認可表が空なら全操作403、共有許可も無いので投函も403。書込は `dynamodb:EnclosingOperation=TransactWriteItems` の条件付きで、単独の Put/Delete を許さない。Scanは許可しない。各Lambdaは自分の責任外のルートを404にする（API Gatewayの配線誤りへの二重防御）。

APIはCognito Authorizer必須、OPTIONSのみ認証なし。CORSは指定したHTTPS originだけ。stageのスロットリングを設定し、アクセスログはphase2と同じ本文・トークンなしの形式。応答は `no-store`。タイムアウト10秒・メモリ256MBはDynamoDB/S3の単発I/Oだけを前提にした暫定値で、Git連携方式を決めた時点で根拠を取り直す。

フロントは `NEXT_PUBLIC_COMMON_KNOWLEDGE_API_URL` にHTTPSのstage付きURL（例 `https://<api>/dev`）を受け付ける。合成モードは従来どおりループバックだけ。実データの投函・保存は引き続き「受入待ち」で止める。

## 受入条件

ローカル: 既存I1の合成テストがSQLite台帳で全て通る。同じシナリオがDynamoDB／S3の挙動を模したアダプターでも通る（3入口の公開・停止、Git成功後の投影失敗の再開、承認時刻の固定、artifactのみ成功、manifest成功後の停止競走、期限、manifest不能、ページング、未完了操作の復旧、同時更新は拒否確定にしない）。Git未設定・設定欠落・責任外ルートは拒否。Lint・型検査・SAM変換/lint・`git diff --check`。

AWS: 新規stackのCREATE changesetが全Addで、共有・既存itaiスタックの変更なし。完了後、暗号化・TLS強制・公開ブロック・バージョニング・PITR、IAMが上表どおり、Lambdaの配備コードが対象コミットと一致、フラグoff・Git未設定であることを確認する。未認証401、フラグoffの403、責任外ルート404を配備版で確認する。台帳とS3アダプターは配備した表・バケットに対し、合成の名前空間（自動失効付き）で上記シナリオを通す。このときGit区間はローカル合成Gitであり、会社Git連携の受入ではない。

未受入として分けて記録するもの: 会社Git連携と知識の一往復、実Cognito主体での画面操作・業務ロール割当、実データ・保持方針、IP外からの拒否の実査、Amplify itaiの接続切替、RAG／開発エージェントの実接続と有料品質検証。

## 費用・停止・rollback（反映前の見積り）

- 固定費: Secrets Manager 1件（約0.40 USD/月）。DynamoDB 2表・S3・Lambda・API Gatewayは従量で、合成受入の量ではほぼ0。PITRとS3バージョンは保存量比例。既存WAFへの関連付けで追加の固定料金はなく、通過リクエスト分のみ。
- 停止: `CommonKnowledgeEnabled=false` が既定。API stageのスロットリングで上限を固定。
- rollback: 本スタックは他スタックからExport参照されない。changeset作成で失敗した場合は実行しない。作成後の撤去が必要になった場合は、Retain指定の台帳表・認可表・配布バケットが残ることを確認したうえで、スタック削除とRetain資源の扱いを別途確認する（今回は削除しない）。
