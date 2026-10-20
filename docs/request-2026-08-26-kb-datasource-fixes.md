---
status: development
last-verified: 2026-08-26
related-code: infrastructure/sam/phase2-template.yaml, lambda/rag/rag-function/
---

# 依頼: Knowledge Base データソース資料の修正・再同期（KB所有部門宛）

> **Issue:** https://github.com/yukiworkspace/EleKnowledge-AI/issues/53（本文書の正本。以後の経過は issue 側で追跡）

- **依頼元:** EleKnowledge-AI 開発チーム
- **宛先:** RagKnowledgeBaseStackINSTD / Knowledge Base 共同管理部門
- **日付:** 2026-08-26
- **対象 Knowledge Base:** `VQV81CNYU4`（generative-ai-use-cases-jpinstd）
- **対象データソース:** `KHPV3CNKOU`（s3-data-source）
- **対象 S3:** `s3://ragknowledgebasestackinst-datasourcebucket9fa93e04-ybbhm1efhyzb/docs/documents/`

## 背景

EleKnowledge-AI（据付ナレッジ検索）は、上記 Knowledge Base を読み取り専用で利用しています。2026-08-26 に S3 上の全資料 3,745 件と Knowledge Base 索引（3,725 件）を突き合わせた結果、**20 件が索引に取り込まれておらず検索不能**であることが判明しました。原因は各ファイル側にあり、当方（読み取り専用利用者）では修正できないため、以下を依頼します。

なお、当依頼は `VQV81CNYU4` のみが対象です。`DF9XUCSPDM`（jp-inst-fmp）の再同期は今回の依頼に含みません。

## 依頼 1: 索引欠落 20 件の修正（優先度: 高）

修正完了後、データソース `KHPV3CNKOU` の再同期（Sync）実行までお願いします。

### 1-A. 暗号化 PDF の差し替え（12 件・Qシート）

パスワード/権限保護（`/Encrypt`）付きのため取り込みに失敗しています。**復号（保護解除）した同一内容の PDF への差し替え**をお願いします。

対象: `docs/documents/Qシート/` 配下の
`Q-3663.pdf` `Q-3665.pdf` `Q-3667.pdf` `Q-3670.pdf` `Q-3671.pdf` `Q-3672.pdf` `Q-3675.pdf` `Q-3678.pdf` `Q-3683.pdf` `Q-3687.pdf` `Q-3689B.pdf` `Q-3699.pdf`

※ Qシートは全 156 件中 12 件（約 8%）が検索不能の状態です。

### 1-B. 50MB 超ファイルの分割（6 件）

Amazon Bedrock Knowledge Bases の 1 ファイル 50MB 上限を超えており取り込めません。**50MB 未満への分割**をお願いします（分割ツールは当方リポジトリの pdf-splitter を提供可能です）。

| ファイル | サイズ |
|---|---:|
| `W資料/WIG-27--D.pdf` | 135.3MB |
| `据付ノート/IN-EL-08-94/追加分/IN-EL-08-94-01-2.pdf` | 56.8MB |
| `据付ノート/IN-EL-12-104/IN-EL-12-104-01-1.pdf` | 72.5MB |
| `据付ノート/IN-EL-12-104/IN-EL-12-104-01-2.pdf` | 74.7MB |
| `据付ノート/IN-EL-12-104/IN-EL-12-104-01-3.pdf` | 62.7MB |
| `据付ノート/IN-EL-12-105/IN-EL-12-105-01.pdf` | 77.3MB |

### 1-C. テキスト層のないスキャン PDF の差し替え（2 件）

テキスト情報が存在しない（`/Font` なし）ためテキスト抽出に失敗しています。**OCR 済み版への差し替え**をお願いします。

対象: `現場代理人業務マニュアル/GM-01-03-A.pdf`、`現場代理人業務マニュアル/GM-01-29-A.pdf`

## 依頼 2: テスト用資料の削除（優先度: 中）

category `TEST` の資料が 1 件残っています（パスは付録 A）。検索結果への混入防止は当方アプリ側でも暫定対処しますが、恒久対応として削除をお願いします。

## 依頼 3: `model_type` メタデータの正規化（優先度: 中）

`.metadata.json` の `model_type` に、配列ではなくカンマ連結文字列（例: `"機械室レス荷物用(中抵製),機械室レス荷物用(モダニ)"`）で複数機種が入っている資料が 60 件あります（一覧は付録 B）。完全一致フィルタ（`listContains`）で拾えない形式のため、**配列形式（例: `["機械室レス荷物用(中抵製)", "機械室レス荷物用(モダニ)"]`）への統一**をお願いします。当方アプリ側で暫定救済は入れますが、正規化完了後に撤去します。

## 依頼 4（協議）: 追加データソースの扱い

`VQV81CNYU4` には s3-data-source 以外に以下の 2 データソースが接続されており、据付業務と無関係な文書が検索結果に混入し得ます。当方アプリ側でフィルタ遮断しますが、KB としても不要であれば削除をご検討ください。

- `7NJIOJDD0Z` web-crawler-data-source（GenU ドキュメントを取り込むクローラー）
- `A0XLFVSX3P` knowledge-base-quick-start-7duyg-data-source（`s3://rag-data-source-inst-fmp-<DEV_ACCOUNT_ID>-ap-northeast-1` 全体）

## 確認したい運用事項

1. データソース `KHPV3CNKOU` の Sync 実行の担当・手順・依頼窓口（今後、資料更新時の再同期を依頼する際のルート）
2. 依頼 1〜3 の対応可否と目安時期

## 付録 A: TEST 資料のパス

- `docs/documents/TEST/test-document_2024.docx`（1 件。PDF ではなく docx）

## 付録 B: カンマ連結 `model_type` の 60 件一覧

全 60 件が「据付場用図」カテゴリで、`model_type` の値はすべて同一の
`"機械室レス荷物用(中抵製),機械室レス荷物用(モダニ)"` です。
→ `["機械室レス荷物用(中抵製)", "機械室レス荷物用(モダニ)"]` への置換をお願いします。

### `docs/documents/据付場用図/KF-ETC_MTC/`（41 件）

`YA289B251_A` `YA289B394_0` `YA289B438_C` `YA289B447_D` `YA293B226_B` `YA294B380_A` `YA305C627_B` `YA312B803_0` `YA317C987_0` `YA348C005_0` `YA348C095_0` `YD000G218_B` `YD100F331_C` `YD301F171_B` `YD301F172_B` `YD301F181_0` `YD301F182_0` `YD301F183_0` `YD301F184_0` `YD301F187_0` `YD301F188_0` `YD301F212_A` `YD301G220_J` `YD302G200_G` `YD302G240_D` `YE307C167_B` `YE307C197_0` `YE313C850_L` `YE313C870_F` `YE320B777_0` `YE320B790_A` `YE322B569_A` `YE322B570_A` `YE322B571_A` `YE322B572_A` `YE322B573_A` `YE400B446_0` `YE400C947_0` `YE401A102_E` `YE401C001_0` `YE401C415_0`（各 `.pdf` / `.pdf.metadata.json`）

### `docs/documents/据付場用図/KM-LD/`（19 件）

`YA096A783_L` `YA100A664_A` `YA100A666_0` `YA139A299_I` `YA139A300_I` `YA139A301_H` `YA139A302_H` `YA139A304_H` `YA139A307_F` `YA139A308_F` `YA139A309_E` `YA139A367_I` `YA139A387_B` `YA144A152_H` `YA144A187_A` `YA160B637_L` `YA289B394_0` `YA289B438_C` `YA289B447_D`（各 `.pdf` / `.pdf.metadata.json`）

※ `YA289B394` / `YA289B438` / `YA289B447` は KF-ETC_MTC と KM-LD の両フォルダに存在します（同名別パス）。
