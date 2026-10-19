---
schema_version: 1
record_id: "elv-maintenance-console-pdf-display-protected-mode-hold-id258"
record_version: 1
title: "メンテコンのトラブルシュートPDF表示不具合（ID258・セキュリティレビュー保留）"
category: "不具合対応【ELV】"
record_type: "technical_reference"
product: "メンテコン資料閲覧環境"
model_type: []
document_number: ""
revision: ""
effective_date: ""
review_status: "in_review"
publication_status: "not_published"
classification: "unknown"
cloud_approval: "not_reviewed"
keywords:
  - "メンテコン"
  - "PDF表示"
  - "Acrobat Reader"
  - "保護機能"
  - "セキュリティ"
source_path: ""
source_filename: "技術情報リスト（協力会社展開用）.xlsx"
onenote_id: ""
related_ids: []
attachment_paths: []
reference_links: []
document_references: []
evidence_sources:
  - source_id: "evidence-list-elv-maintenance-console-pdf-display-258"
    source_type: "user_provided_extract"
    title: "協力会社展開用Excel: メンテコン トラブルシュートマニュアルが表示されない（ID258）"
    source_path: ""
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-13"
    supports:
      - "マニュアルの選択後にPDF内容が表示されないとの報告"
      - "原リストがPDFリーダーの保護機能設定変更を原因/対処として提案していること"
structured_data:
  symptom: "エラー項目選択後のポップアップでマニュアル内容が表示されないとの原リスト報告。"
  cause_reported: "原リストはPDFリーダー設定の問題と説明するが、環境・再現条件・原因は未検証。"
  security_note: "原リストの保護機能無効化案は記録/再掲しない。セキュリティ機能の変更を本記録は推奨・承認しない。"
  limitations:
    - "保護機能を弱める設定変更手順、端末/利用者情報、内部資料リンクは転載しない。"
    - "PDFリーダーの版、端末管理基準、管理者承認、現在の再現性は未確認。"
    - "必要な場合は社内IT管理者が承認した閲覧環境/設定を確認する。"
---

# メンテコンのトラブルシュートPDF表示不具合（ID258・セキュリティレビュー保留）

協力会社展開用リストID258は、エラー項目の選択後にトラブルシュートマニュアルの内容が表示されないと報告し、PDFリーダーの設定を原因として挙げている。環境・再現条件・原因は独立確認していない。

原リストにはPDF閲覧時の保護機能を無効化する案があるが、具体設定は記録せず、本記録もその変更を推奨・承認しない。端末管理基準に沿って社内IT管理者が承認した閲覧環境を確認すること。保護機能を弱める設定手順として使用しない。