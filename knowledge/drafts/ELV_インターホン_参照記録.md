---
schema_version: 1
record_id: "catalog-elv-intercom-reference"
record_version: 3
title: "インターホン資料の参照記録"
category: "技術メモ【ELV】２"
record_type: "catalog"
product: "エレベーター"
model_type: []
document_number: ""
revision: ""
effective_date: ""
review_status: "in_review"
publication_status: "not_published"
classification: "unknown"
cloud_approval: "not_reviewed"
keywords: ["インターホン", "バッテリー", "結線"]
source_path: "技術メモ【ELV】２/ELV-付加仕様（その他）/インターホン.md"
source_filename: "インターホン.md"
onenote_id: "053f163d-7a20-4cfd-950d-005f567aaf6f:1"
related_ids: []
attachment_paths: []
reference_links: []
document_references: []
evidence_sources:
  - source_id: "evidence-elv-intercom-001"
    source_type: "vault_original"
    title: "インターホン"
    source_path: "技術メモ【ELV】２/ELV-付加仕様（その他）/インターホン.md"
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-08"
    supports: ["機種別通話/電源に関する情報共有、個別不具合と図版があること"]
  - source_id: "evidence-list-elv-intercom-reset-circuit-328"
    source_type: "user_provided_extract"
    title: "協力会社展開用Excel: CPD-K+Sの時のインターホン結線方法（ID328）"
    source_path: ""
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-13"
    supports:
      - "特定の特殊運転/インターホン構成で発生した動作不整合、リセット回路の結線が原因との説明、および変更後の改善報告"
  - source_id: "evidence-list-elv-intercom-relay-mode-239"
    source_type: "user_provided_extract"
    title: "協力会社展開用Excel: DC24V応答検出リレー付インターホン親機の動作モード説明（ID239）"
    source_path: ""
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-13"
    supports:
      - "モード設定不一致でCPD-Kが動作しなかったとの報告、および設定説明資料が必要との指摘"
structured_data:
  source_notes:
    - "原資料に結線、電源分配、バッテリー、個別不具合、部材情報がある。具体条件/手順/案件IDは転載していない。"
    - "協力会社展開用Excel ID328は、特殊運転中にインターホンの動作不整合があり、リセット回路の結線誤りが原因とされ、結線変更後に改善したと報告する。対象構成の図面が見当たらなかったとの記載もある。個別条件・原因・結果・図面状況は独立確認していない。物件/機器/階識別、端子、試行順、結線方法は転載しない。"
    - "協力会社展開用Excel ID239は、インターホンのモード設定不一致でCPD-Kが動作しなかったと報告し、設定説明資料の不足を指摘する。具体的なモード値/接点条件/資料番号は転載しない。原因、資料の承認/適用範囲、現行仕様は未確認。"
---

# インターホン資料の参照記録

原資料はインターホンの機種別電源/通話、バッテリー、結線、不具合、関連部材に関する過去情報と画像を含む。具体的な結線・電源条件、操作手順、個別案件識別子は転記していない。

協力会社展開用Excel ID328は、特殊運転中にインターホンの動作不整合があり、リセット回路の結線誤りが原因とされ、結線変更後に改善したと報告する。対象構成の図面が見当たらなかったとの記載もある。これは個別の原リスト報告であり、原因・改善結果・図面状況は独立確認していない。物件/機器/階識別、端子、試行順、結線方法は記録しない。

協力会社展開用Excel ID239は、インターホンのモード設定不一致によりCPD-Kが動作しなかったと報告し、設定説明資料の不足を指摘する。具体的なモード値・接点条件・資料番号は記録しない。原因、説明資料の承認/適用範囲、現行仕様は未確認である。

閉じ込め救出/非常通話機能に関わるため、機種別現行回路図と承認済み試験要領を確認するまで、設計・施工・点検判断に使用しない。

出典: `技術メモ【ELV】２/ELV-付加仕様（その他）/インターホン.md`（OneNote ID `053f163d-7a20-4cfd-950d-005f567aaf6f:1`）。確認日: 2026-10-08。
