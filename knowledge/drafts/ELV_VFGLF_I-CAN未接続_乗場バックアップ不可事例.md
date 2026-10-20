---
schema_version: 1
record_id: "case-elv-vfglf-i-can-disconnected-hall-backup-unavailable-id417"
list_item_id: "417"
record_version: 1
title: "VFGLFで乗場バックアップができない"
category: "不具合対応(ELV)"
record_type: "troubleshooting_case"
product: "エレベーター"
model_type:
  - "VFGLF"
document_number: ""
revision: ""
effective_date: ""
review_status: "in_review"
publication_status: "not_published"
classification: "unknown"
cloud_approval: "not_reviewed"
keywords:
  - "I-CAN"
  - "乗場バックアップ"
  - "E30"
related_ids: []
source_path: ""
source_filename: ""
onenote_id: ""
attachment_paths: []
reference_links: []
document_references: []
evidence_sources:
  - source_id: "evidence-list-vfglf-i-can-hall-backup-id417"
    source_type: "lists_csv_snapshot"
    title: "首都工・不具合情報共有リスト: I-CAN未接続により乗場バックアップできない"
    source_path: ""
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-19"
    supports:
      - "リスト上のタイトル、機種、エラー表示欄の記載、現象分類、対応済みステータス（症状・原因・Notes はスナップショット上保留）"
structured_data:
  equipment: "VFGLF"
  symptom: "スナップショット上、症状の自由記述は情報管理確認まで保留。タイトルは I-CAN 未接続により乗場バックアップできない旨。"
  error_codes:
    - "MON1/0→E/0 表示と【E30】（2桁エラー。据付完了後のため2桁のみ、とリスト記載）"
  cause: "リスト上は原因・対策欄が情報管理確認まで保留。I-CAN 未接続とタイトルが示唆するが、因果は未確認。"
  verified_actions: []
  outcome: "リスト上は対応済み。具体的な対応内容はスナップショットに無い。"
---

# VFGLFで乗場バックアップができない

首都工・不具合情報共有共有リスト上の記録 は、VFGLF において I-CAN 未接続により乗場バックアップができない事象を報告する。スナップショットでは症状・原因・Notes の自由記述は情報管理確認まで保留のため、ここではリスト見出しとメタデータのみを整理する。

## リスト上の記録（2026-02-16 共有）

- 現象分類: 電気的
- エラー表示欄: MON1/0→E/0、【E30】（据付完了後のため2桁エラーのみ、と記載）
- ステータス: 対応済み
- 重要度: 高

## 未確認事項

- 症状・原因・対策の原文（スナップショットでは伏せ字）
- I-CAN 未接続の確認方法、復旧手順、再発条件
- E30 と MON 表示の現行定義・資料上の該当箇所

本記録は事例索引用であり、運転・診断・復旧手順ではない。
