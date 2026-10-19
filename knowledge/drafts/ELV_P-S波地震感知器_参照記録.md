---
schema_version: 1
record_id: "catalog-elv-p-s-wave-earthquake-sensors"
record_version: 3
title: "P波・S波地震感知器資料の参照記録"
category: "技術メモ【ELV】１"
record_type: "catalog"
product: "エレベーター"
model_type: ["MRL"]
document_number: ""
revision: ""
effective_date: ""
review_status: "in_review"
publication_status: "not_published"
classification: "unknown"
cloud_approval: "not_reviewed"
keywords: ["P波", "S波", "地震感知器", "地震管制"]
source_path: "技術メモ【ELV】１/ELV-付加仕様①/地震管制運転/P+S波地震感知器（地震計）.md"
source_filename: "P+S波地震感知器（地震計）.md"
onenote_id: "edcf3957-8d5e-4821-aee9-faf15253e61c:1"
related_ids: []
attachment_paths: []
reference_links: []
document_references:
  - document_number: "C-6-R50.40-J"
    title: "P+S波地震感知器資料"
    locator: "原資料記載の文書参照。未閲覧"
    source_path: ""
  - document_number: "C-6-R50.41-J"
    title: "P波地震感知器資料"
    locator: "原資料記載の文書参照。未閲覧"
    source_path: ""
evidence_sources:
  - source_id: "evidence-elv-earthquake-sensor-001"
    source_type: "vault_original"
    title: "P+S波地震感知器（地震計）"
    source_path: "技術メモ【ELV】１/ELV-付加仕様①/地震管制運転/P+S波地震感知器（地震計）.md"
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-08"
    supports: ["地震感知器の外形・表示・操作・試験機能に関する画像/参照が掲載されていること"]
  - source_id: "evidence-list-elv-earthquake-sensor-construction-supply-390"
    source_type: "user_provided_extract"
    title: "協力会社展開用Excel: 工事使用号機でS波感知器が動作しない報告（ID390）"
    source_path: ""
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-13"
    supports:
      - "MR機種の工事使用号機でS波感知器が動作しなかった報告と、号機間の電源供給構成に関する出典説明"
  - source_id: "evidence-list-elv-precision-s-wave-operation-check-138"
    source_type: "vault_original"
    title: "首都工・不具合情報共有リスト: MRL機種における精密級S波地震感知器の動作点検（ID138）"
    source_path: "首都工・不具合情報共有リスト.xlsx"
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-14"
    supports:
      - "MRL向け精密級S波地震感知器の動作点検に関する項目が存在すること"
      - "点検条件・手順・設定/動作点の現行適用性は確認しておらず、内容を手順化していないこと"
structured_data:
  source_notes:
    - "原資料には地震感知器の外形/表示/操作/試験関連の画像があるが、画像内容と参照PDF・共有先は未確認。"
    - "設定変更、試験、動作点、設置条件は転記していない。MRLの表記は原資料の記載に基づく。"
    - "協力会社展開用Excel ID390は、MR機種の工事使用号機でS波感知器が動作しなかった個別報告として追記。電源供給構成の説明は出典上の推定であり、図面・号機構成・現行設計との照合は未実施。端子・コネクタ・号機間結線や据付変更の指示は転載しない。"
    - "原リスト中の規制改正・検査要件に関する説明は適用時期・対象・現行法令との整合を確認していない。"
    - "一次リストID138の動作点検項目を確認したが、設定/動作点・試験条件・操作手順は転記していない。C-6-R50.40-J等の参照文書本文、版、現行適用、法令/検査要件は未確認。"
---

# P波・S波地震感知器資料の参照記録

## 概要

原資料はP波・S波地震感知器を扱い、機器外形、状態表示、操作部、試験機能に関する画像と文書参照を含む。図版・参照文書を確認できていないため、機能値や操作条件の説明は作成していない。

## 工事使用号機でのS波感知器不動作報告

協力会社展開用Excel ID390は、MR機種で工事使用号機を設定した際にS波感知器が動作しなかった事例を報告する。原リストは号機間の電源供給構成を理由として説明しているが、個別図面・号機構成・設定状態と照合しておらず、確定原因とは扱わない。端子・コネクタ・号機間結線、接続変更、P波感知器の据付変更指示は本記録に含めない。

原リストに記載された規制改正・検査要件についても現行法令との適用関係は確認していない。地震管制設備の設計・設置・試験判断には、承認済みの現行図書と所管技術者の確認を要する。

一次リストID138は、MRL機種の精密級S波地震感知器の動作点検に関する項目を掲げる。設定/動作点、試験条件、操作手順は本記録へ転載していない。参照資料の本文・版、現行設計、機種適用、法令/検査要件を確認するまで、地震感知器の点検・調整・試験の手順や判定基準として使用しない。

## 未確認事項

図版とPDFの実体/内容/改訂、対象制御方式、機種適用性、共有リストの内容、法令・設計基準との整合は未確認。設置、感度設定、試験、復帰の判断に使用しない。

## 出典・確認履歴

- 原資料: `技術メモ【ELV】１/ELV-付加仕様①/地震管制運転/P+S波地震感知器（地震計）.md`
- OneNote ID: `edcf3957-8d5e-4821-aee9-faf15253e61c:1`
- 確認日: 2026-10-08
