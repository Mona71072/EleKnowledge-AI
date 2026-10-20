---
fixture: synthetic
schema_version: 1
record_id: "SYNTH-TECHREF-001"
record_version: 1
title: "架空表示機能の参照情報"
category: "synthetic-fixture"
record_type: "technical_reference"
product: "SYNTHETIC"
model_type: ["SYNTH-B"]
document_number: ""
revision: ""
effective_date: ""
review_status: "unreviewed"
publication_status: "not_published"
classification: "unknown"
cloud_approval: "not_reviewed"
keywords: ["synthetic", "display"]
source_path: ""
source_filename: "synthetic-source"
onenote_id: "SYNTH-ONENOTE-002"
related_ids: []
attachment_paths: []
reference_links: []
document_references: []
evidence_sources:
  - source_id: "SYNTH-EVIDENCE-002"
    source_type: "user_provided_extract"
    title: "合成テスト入力"
    source_path: ""
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-19"
    supports: ["架空表示機能の状態名"]
structured_data:
  specifications:
    - name: "架空表示状態"
      value: "MODE-A"
      unit: ""
      condition: "合成テスト専用。実機仕様・設定値・判定値ではない。"
  source_notes:
    - "このファイルの全ての型式・値・条件は架空であり、実機に適用しない。"
---

# 架空表示機能の参照情報

状態名`MODE-A`を含む合成レコード。検索表示で出典と「実機仕様ではない」という条件が一緒に扱われることを確認する。