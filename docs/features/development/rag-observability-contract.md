---
status: development
last-verified: 2026-09-24
related-code:
  - lambda/rag/rag-function/app.py
  - lambda/rag/rag-function/telemetry.py
  - infrastructure/sam/phase2-template.yaml
related-issues:
  - 86
  - 129
  - 130
  - 132
---

# RAG 運用ログ契約

> 最終検証: 2026-09-24 — 実装 PR #111、開発 API Gateway アクセスログ、既存 retrievalTrace 設計を照合

## 目的と境界

> 最終検証: 2026-09-25 — API Gateway アクセスログを契約対象に含める旨を追記

この文書は、CloudWatch の構造化運用ログで何を取得・非取得とするかを定義する。目的は、1 リクエストを `requestId` で追跡し、検索・生成・保存のどこで失敗又は品質低下が起きたかを、利用者本文を保存せずに切り分けることである。 API Gateway のアクセスログも本契約の対象とし、送信元 IP・User-Agent・Cognito `sub` は記録しない。

`retrievalTrace` は assistant 行とアーカイブに保存する詳細トレースの別設計であり、本契約の CloudWatch ログと混同しない。利用者本文、プロンプト、回答本文、引用本文を CloudWatch に出さない。

## イベント契約

> 最終検証: 2026-10-14 — 共通項目の版指定をSAMパラメータから渡す仕様を追加。デプロイごとに検証済みソースのGit SHAを指定し、実環境の反映は別途確認する。

`ragLogicVersion`はphase2の`RagLogicVersion`から環境変数`RAG_LOGIC_VERSION`へ渡す。デプロイ時に検証済みソースのGit SHA（7〜40桁の小文字16進）を指定する。SAMには既定値を置かず、版不明のまま新しい配信を進めない。アプリの`unknown`は旧配信や環境変数未設定時の互換フォールバックとして残す。

すべての RAG ログ行は JSON とし、`schemaVersion` と `event` を持つ。イベントは `rag_request`、`rag_error`、`document_open`、`reformulation` の 4 種とする。

| 分類 | 取得する項目 | 意図 |
|---|---|---|
| 共通 | `schemaVersion`、`event`、`requestId`、`route`、`statusCode`、`latencyMs`、`ragLogicVersion` | API Gateway と Lambda、版変更前後の比較 |
| 検索 | `filterKinds`、`retrievedCount`、`selectedCount`、`excludedByModelScope`、`scoreBand`、`retrieveLatencyMs`、`priorityExpanded` | 絞り込み・候補不足・低スコアを生成不良と区別 |
| 生成 | `modelId`、`generationLatencyMs`、`inputTokens`、`outputTokens`、`stopReason`、`retryCount` | モデル、コスト、遅延、停止を比較 |
| 結果 | `responseType`、`pageCandidateCount`、`sourceDocumentCount`、`documentOpened`、`feedback`、`reformulated` | 到達と暗黙の失敗を集計 |
| エラー | `stage`、`errorCode`、`exceptionClass`、`errorFingerprint` | 失敗経路と同一原因の集約。本文を使わない |

`scoreBand` は個別スコアではなく `none`、`low`、`medium`、`high` とする。閾値と意味は検索選択ロジックと同じ版で管理する。

## 非取得項目

| 非取得項目 | 理由 | 代替 |
|---|---|---|
| 質問文、回答文、プロンプト | 個人情報・業務情報を含み得る | responseType、候補数、スコア帯、評価 |
| 引用本文、KB チャンク本文 | ナレッジ引用全文を CloudWatch に出さない | 運用者が必要時にアクセス制御済み retrievalTrace／アーカイブを参照 |
| JWT、Cognito `sub`、生 IP、User-Agent | 利用者又は端末を追跡可能にする | requestId、集約メトリクス |
| 生 `errorMessage`、スタックトレース | 入力・内部 URL・AWS 資源情報を含み得る | errorCode、exceptionClass、stage、errorFingerprint（SHA-256 先頭 16 桁） |
| `sessionId`、`messageId` | CloudWatch では利用者行動の連結を避ける | 認可済みの DynamoDB／アーカイブでのみ参照 |

## エラー指紋

> 最終検証: 2026-10-10 — telemetry.py の `error_fingerprint` と単体テスト（同一原因の一致・文面の不混入）に照合。鍵は使わない実装

`errorFingerprint` は、`stage`・`exceptionClass`・`errorCode` を `|` で連結した文字列の SHA-256 の先頭 16 桁とする。鍵は使わず、Secrets Manager や環境変数の設定も要らない。入力は運用上の固定値だけで、利用者のデータ・例外の文面・ID を含まないため、本番でも常に値が入る。

同じ段階・例外の型・エラーコードなら、エラーメッセージの文面が違っても同じ値になる。メッセージは入力に含めないので、指紋から本文は復元できない。指紋は同一原因の集約キーであり、秘匿の手段ではない（入力の候補は既知の固定値の組に限られるため、秘匿性は求めない）。

## 判断経緯と追跡

- issue #86 と `docs/design-2026-09-10-retrieval-trace.md` は、検索トレース、トークン、候補・除外を品質改善に使う必要を定義した。
- PR #111 は API Gateway 相関、RAG 500 の一般化、資料クリック、言い換えを追加した。
- 2026-09-23 の開発環境検証で API Gateway の 401 は `errorMessage=Unauthorized`、Auth Lambda の 500 は `errorMessage=-` だった。ただし任意例外文字列を記録する RAG Lambda は安全性を保証できないため、生本文を契約から除外した。
- issue #129 はトークン単位 WAF とアカウント単位レート制限の分離、issue #130 は日次 GSI による Scan 廃止、issue #132 は通知・初動・記録の運用完成を追跡する。

重要な仕様判断はこの文書を正本とし、実装 PR には本ファイルと関連 issue をリンクする。運用上の手順は `docs/ops-runbook.md`、詳細検索トレースは `docs/design-2026-09-10-retrieval-trace.md` を参照する。

## 実装と検証

1. `telemetry.py` にイベント契約を実装し、生 `errorMessage` を廃止する。
2. `app.py` で検索・生成の計測値を収集して telemetry に渡す。例外をテレメトリで発生させない。
3. `errorFingerprint` は鍵を使わない（上記）。HMAC 鍵・Secrets Manager の配線は不要。
4. 単体テストで、イベント必須項目、本文・JWT・`sub`・IP・例外本文が出力されないこと、同一エラーの指紋一致を検証する。
5. 開発環境で `requestId` により API Gateway と Lambda を照合し、検索失敗・生成失敗・保存失敗をそれぞれ安全に確認する。
