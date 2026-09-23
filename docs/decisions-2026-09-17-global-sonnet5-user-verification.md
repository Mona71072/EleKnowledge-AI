---
status: draft
last-verified: 2026-09-17
related-code:
  - infrastructure/sam/phase2-template.yaml
  - lambda/rag/rag-function/app.py
  - scripts/ops/provision_users.py
  - scripts/ops/confirm_unconfirmed_users.py
---

# 決定: Global Sonnet 5 の採用と利用者アカウント照合運用

> **決定日:** 2026-09-17  
> **決定根拠:** 社内のGlobal標準利用方針、およびプロジェクト管理者の指示（Sonnet 5 のコストパフォーマンスを採用理由とする）  
> **関連PR:** #90 / #84 / #97 / #98 / #101 / #116  
> **状態:** Global利用と本人照合運用は確認済み。Sonnet 5採用の妥当性のみ共同確認する。実装・デプロイは別PRで扱う。

## 1. Global利用に関する社内方針

社内OneNoteに記録された輸管方針に従い、Global標準のように海外リージョンで処理される可能性がある
AIモデルの利用は、輸管対象に当たらないものとして扱う。根拠は、本社輸管部から共有されたCISTECの
見解であり、生成AIへのプロンプト提供もストレージサービスと同様に扱うという認識である。

したがって、Global inference profileを使用する可否は本PRの共同確認事項ではない。ただしGlobal
Cross-Region Inferenceではリクエストが世界中の対応AWS商用リージョンで処理され得るため、東京
リージョンからの呼出しだけを国内処理の保証として扱わない。

## 2. Sonnet 5採用の決定

RAG本文生成および、同じモデル設定を継承する履歴見出し生成で、Amazon Bedrock の
`global.anthropic.claude-sonnet-5` を採用候補とする。採用理由はコストパフォーマンスであり、
本PRで共同確認するのは、このモデルを受入れ条件・見直し条件の下で採用してよいかである。

採用の最低条件は次のとおり。

1. 組織で必要とするBedrockのデータ利用・保持に関するオプトアウト設定が有効であること
2. モデル呼出しログに質問本文、回答本文、ナレッジ引用全文、トークンその他の認証情報を出力しないこと
3. IAMは必要な `InvokeModel` と対象推論プロファイルに限定し、追加の広範な権限を導入しないこと
4. 初回デプロイ時および設定変更時に、実際のモデルID・推論プロファイル・設定値・検証日時を社内運用記録へ残すこと
5. CloudTrailの `additionalEventData.inferenceRegion` 等の本文を含まない監査情報で、Global経路を使用した事実を確認できること

オプトアウトの状態そのものはリポジトリやPR本文に値・証跡を載せない。確認者、確認日時、確認方法、
結果だけを社内記録に残す。

## 3. 受入れ条件と見直し

### 受入れ条件

- #90 はSonnet 5に適したリクエスト形式（sampling指定なし、対応するthinking設定）で本文生成できる。
- #84 は同じ互換処理を見出し生成にも使い、見出し生成の遅延または失敗で既に生成済みの回答を失わない。
- 通常回答、聞き返し、該当なし、継続会話、見出し生成の回帰テストが通る。
- 実環境で、社内画面から回答・資料閲覧まで確認し、応答時間と失敗時の利用者向け応答を記録する。
- 本文を含むBedrock invocation loggingは無効のまま、またはAGENTS.mdのログ秘匿要件に適合する匿名化済み構成である。

### 見直し条件

次のいずれかが起きたとき、Global profileの継続利用を再評価する。

- 組織のデータ所在・保持方針がGlobal処理を許容しなくなった
- オプトアウトまたは保持設定を確認できない
- レイテンシ、エラー率、費用が採用根拠を満たさない
- AWSまたはモデル提供者の保持・推論プロファイル仕様が変わった

## 4. 利用者アカウントの本人照合

mona提案にプロジェクト管理者が賛同し、次の運用を共同確認済みとする。

`provision_users.py` による事前発行と、`confirm_unconfirmed_users.py confirm` による
メール確認済み化は、**正式な社内情報で対象メールアドレスと本人を照合済みの場合だけ**実行する。

自己申告、メールドメインだけ、または「登録したか」の口頭確認だけを根拠にしてはならない。
社員ID、本人確認資料、初期パスワード、対象者CSVはGitHub・リポジトリ・CloudWatch Logsへ保存しない。

### 実行前の必須記録

社内のアクセス制御された運用記録に、対象ごとまたは同一照合単位ごとに次を残す。

| 項目 | 記録内容 |
|---|---|
| 確認担当 | 正式な社内情報を照合した担当者 |
| 確認日時 | JSTの日時 |
| 対象 | 最小限の識別子。必要に応じて社内台帳上の参照IDのみ |
| 根拠 | 社内台帳・人事名簿等の参照先ID。証憑本文は添付しない |
| 照合結果 | 一致 / 不一致 / 保留 |
| 実行結果 | dry-run、本実行、対象件数、成功・復旧・失敗件数、再実行要否 |

`confirm` 実行時は `--verified-by` と `--evidence-ref` を必須とし、値は上記社内記録の
担当者・参照IDに対応させる。事前発行CSVの投入前にも同じ記録を確認する。

### 実行手順

1. 正式な社内情報との照合と社内記録を完了する。
2. リポジトリ外の入力CSVを使い `--dry-run` を実行し、対象と想定結果を確認する。
3. 初期パスワード出力先がリポジトリ外の**新規ファイル**であることを確認する。
4. 本実行後、結果CSVと終了コードを確認する。失敗があれば終了コード1として扱い、原因を解消して同じ入力で安全に再実行する。
5. 配布後、初期パスワードCSVは社内の定めた保管・廃棄手順に従う。

## 5. PRへの反映順

- #116 を #101 のheadへ取り込み、途中失敗からの復旧・既存出力の上書き防止・終了コードを反映する。
- #101 に本節の本人照合・社内記録の運用を反映して再レビューする。
- #90 に本決定への参照を追加し、#84を#90の互換処理へ整合させる。
- #97 / #98 は「国内限定」と読める記述を本決定に合わせて訂正する。
- #104以降の設計・実装PRは、上記の決定済み前提を参照する。

## 6. 一次情報

- [AWS: Global cross-Region inference](https://docs.aws.amazon.com/bedrock/latest/userguide/global-cross-region-inference.html)
- [AWS: Claude Sonnet 5 model card](https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-anthropic-claude-sonnet-5.html)
- [AWS: Data retention](https://docs.aws.amazon.com/bedrock/latest/userguide/data-retention.html)
- [AWS: Model invocation logging](https://docs.aws.amazon.com/bedrock/latest/userguide/model-invocation-logging.html)
