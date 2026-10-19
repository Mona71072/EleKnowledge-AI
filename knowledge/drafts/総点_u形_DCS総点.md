---
schema_version: 1
record_id: "esc-dcs-inspection-values"
record_version: 1
title: "u形エスカレーター DCS総点検記述"
category: "総点(u型エス)"
record_type: "technical_reference"
product: "エスカレーター"
model_type:
  - "u形"
document_number: ""
revision: ""
effective_date: ""
review_status: "in_review"
publication_status: "not_published"
classification: "unknown"
cloud_approval: "not_reviewed"
keywords:
  - "DCS"
  - "Drive Chain Switch"
  - "ドライブチェーンスイッチ"
  - "ラチェットポール"
  - "隙間G"
source_path: "総点(u型エス)/上部機械室/DCS (Drive Chain Switch).md"
source_filename: "DCS (Drive Chain Switch).md"
onenote_id: "c3c2f392-7d60-46db-b6a4-f3973a5f37e4:69"
related_ids:
  - "u-dcs-drive-chain-switch"
attachment_paths:
  - "総点(u型エス)/上部機械室/OneNote/DCS (Drive Chain Switch) image.png"
  - "総点(u型エス)/上部機械室/OneNote/DCS (Drive Chain Switch) image.jpg"
reference_links: []
document_references: []
evidence_sources:
  - source_id: "evidence-esc-dcs-inspection-original"
    source_type: "vault_original"
    title: "上部機械室 DCS（原文）"
    source_path: "総点(u型エス)/上部機械室/DCS (Drive Chain Switch).md"
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-01"
    supports:
      - "DCS総点検値とDN運転に関する原文説明"
structured_data:
  specifications:
    - name: "ラチェットポールとラチェットホイールの隙間"
      value: "45~55"
      unit: "mm"
      condition: "原文はDN運転後に確認と記載"
    - name: "スイッチローラとカムの隙間G"
      value: "1 < G <= 1.5"
      unit: "mm"
      condition: "原文は手巻DN運転後に目視確認と記載"
  source_notes:
    - "DN運転で隙間が最小になるという説明は原文記載の理由であり、独立した技術資料との照合は未実施。"
---

# u形エスカレーター DCS総点検記述

## 原文記載値

- ラチェットポールとラチェットホイールの隙間: 45~55 mm。DN運転後に確認と記載。
- 手巻DN運転後、スイッチローラとカムとの隙間Gを目視確認: 1 < G <= 1.5 mm。

## 原文の説明と保留

原文は、シューレバーがドライブチェーンの張りに伴って上下し、DN運転時にラチェットポールがラチェットホイールへ近づくため、隙間が最小になるタイミングで測定すると説明している。この理由・運転条件は原文記載の説明として保持し、承認済み作業手順との一致は確認していない。

## 関連・出典

- 機能説明: [[整備済み資料/技術資料/u形_DCS]]
- 原文ノート: [[総点(u型エス)/上部機械室/DCS (Drive Chain Switch)]]
- 添付2点はVault内で実在確認済み。測定位置を示す図版は未読解。
- 技術・安全レビュー前のドラフト。運転・測定の作業指示として使用しない。