---
schema_version: 1
record_id: "catalog-elv-car-announcement-reference"
record_version: 3
title: "かご内アナウンスの機能区分とUPS時の号機差"
category: "技術メモ【ELV】２"
record_type: "knowhow"
product: "エレベーター"
model_type: ["AXIEZ", "NEXCUBE-Limited", "NEXCUBE"]
document_number: ""
revision: ""
effective_date: ""
review_status: "in_review"
publication_status: "not_published"
classification: "unknown"
cloud_approval: "not_reviewed"
keywords: ["かご内アナウンス", "UPS", "音声ガイダンス", "気配りアナウンス", "号機差"]
source_path: "技術メモ【ELV】２/ELV-一般/かご/かご内アナウンス.md"
source_filename: "かご内アナウンス.md"
onenote_id: "7db0d38d-96df-4e66-a15d-43749473578a:1"
related_ids: []
attachment_paths: []
reference_links: []
document_references:
  - document_number: "D-C-847.1-J"
    title: "付加動作説明書（信号表示編）"
    locator: "原資料内社内PDFリンク。未閲覧"
    source_path: ""
  - document_number: "C-8-S451-J"
    title: "LINKs各台管理パラメータ調整"
    locator: "原資料内SharePoint PDFリンク。未閲覧"
    source_path: ""
evidence_sources:
  - source_id: "evidence-elv-car-announcement-001"
    source_type: "vault_original"
    title: "かご内アナウンス"
    source_path: "技術メモ【ELV】２/ELV-一般/かご/かご内アナウンス.md"
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-08"
    supports: ["機種別案内機能とUPS時の表示分岐の説明/図版参照があること"]
structured_data:
  knowledge_items:
    - topic: "かご内アナウンスの機能振分け例"
      statement: "原文では、#F(#6,7)を音声ガイダンス（AAN-G）、#F以外を気配りアナウンス（AAN-B）としている例が示され、「このように振り分けられていることが多い」と説明している。"
      conditions: ["原文上の参考例。型式、機能設定、表示記号の定義と現行適用は未確認。"]
      exceptions: ["すべての号機/機種に共通する設定規則として扱わない。"]
      rationale: "アナウンス機能の呼称と号機条件を取り違えないよう、回答時に原文の例と個別設定を区別する。"
      verification_status: "source_recorded"
      evidence_source_ids: ["evidence-elv-car-announcement-001"]
    - topic: "UPS時のアナウンス内容は号機ごとに異なる場合がある"
      statement: "原文は、UPS時にはアナウンス内容がバンク内の号機によって分かれている場合があると注意している。UPS時の案内内容をバンク全号機で同一と前提せず、個別の承認済み仕様・設定資料で対象号機との対応を確認する観点として扱う。"
      conditions: ["原文は「分かれていることがある」としており、全設備で必ず差があるとは述べていない。"]
      exceptions: ["画像2点と関連設定資料の本文は未確認。号機別の具体的な案内内容は特定できない。"]
      rationale: "号機差の可能性を見落とし、UPS時の案内仕様を誤って一律に説明することを避ける。"
      verification_status: "source_recorded"
      evidence_source_ids: ["evidence-elv-car-announcement-001"]
  source_notes:
    - "原ノートには正式資料番号がなく、document_numberは空欄。D-C-847.1-J、C-8-S451-Jは参照先資料番号としてdocument_referencesに区別して記録。"
    - "埋め込み画像2点は2026-10-09に原文の同階層・想定OneNote保管場所・Vault共通添付画像フォルダー・Vault全体の画像名検索で実ファイルを確認できず、実在/内容とも未確認。"
    - "参照PDF/SharePoint資料は未閲覧。資料名・番号の記録は内容の裏付けを意味しない。機能設定、機種適用、現行性は未確認。"
---

# かご内アナウンスの機能区分とUPS時の号機差

## 原文に記載された機能区分

- 原文の参考例では、`#F(#6,7)` を音声ガイダンス（AAN-G）、`#F以外` を気配りアナウンス（AAN-B）としている。
- 原文は、この振分けが「多い」としており、共通仕様やすべての機種に適用される規則とはしていない。

## UPS時の号機差

原文は、UPS時のアナウンス内容がバンク内の号機で分かれている場合があると注意している。これは個別号機差の可能性を確認するための知見であり、具体的な号機割当や案内内容は原文本文・画像だけでは確認できない。

## 適用確認と制約

- 問い合わせ時は、原文の一般例と対象設備の承認済み仕様/設定資料を区別する。個別の機能振分けやUPS時の内容は対象号機・バンク単位で確認する。
- 関連資料として原文に挙がるD-C-847.1-JとC-8-S451-Jは未閲覧。文書番号の存在だけで内容を確認済みと扱わない。
- 原文の埋め込み画像2点は2026-10-09のVault検索で実ファイルを確認できず、内容未確認。現行版、機種適用、設定条件も未確認であり、本記録は設定変更や試験手順の根拠ではない。

## 出典

- 原文: [[技術メモ【ELV】２/ELV-一般/かご/かご内アナウンス]]（OneNote ID `7db0d38d-96df-4e66-a15d-43749473578a:1`）
- 参照先: D-C-847.1-J「付加動作説明書（信号表示編）」、C-8-S451-J「LINKs各台管理パラメータ調整」。いずれも本文未閲覧。
- 本文とリンク記載の確認日: 2026-10-08。添付所在の再確認日: 2026-10-09。
