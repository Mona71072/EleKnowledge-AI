---
schema_version: 1
record_id: "esc-hss-inspection-values"
record_version: 1
title: "u形エスカレーター HSS総点検記述"
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
  - "HSS"
  - "手摺スリップ検出装置"
  - "センサー"
  - "ローラ"
source_path: "総点(u型エス)/上部機械室/HSS（手摺スリップ検出装置）.md"
source_filename: "HSS（手摺スリップ検出装置）.md"
onenote_id: "c3c2f392-7d60-46db-b6a4-f3973a5f37e4:78"
related_ids:
  - "u-hss-handrail-slip-detector"
attachment_paths:
  - "総点(u型エス)/上部機械室/OneNote/HSS（手摺スリップ検出装置） image.png"
  - "総点(u型エス)/上部機械室/OneNote/HSS（手摺スリップ検出装置） image 1.png"
  - "総点(u型エス)/上部機械室/OneNote/HSS（手摺スリップ検出装置） image 2.png"
reference_links: []
document_references: []
evidence_sources:
  - source_id: "evidence-esc-hss-inspection-original"
    source_type: "vault_original"
    title: "上部機械室 HSS（原文）"
    source_path: "総点(u型エス)/上部機械室/HSS（手摺スリップ検出装置）.md"
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-01"
    supports:
      - "HSS総点検値および回転確認に関する原文記述"
structured_data:
  specifications:
    - name: "ローラと手摺の状態"
      value: "ほぼ平行で接触していないこと"
      unit: ""
      condition: "原文記載"
    - name: "センサーとローラの間隙"
      value: "2~3"
      unit: "mm"
      condition: "原文記載"
  source_notes:
    - "「4回はちょっと動くが5回目からは動かない」は原文のまま保持。回数の対象や意味は要確認。"
    - "u形はスロー運転時にマスク、他機種は自動・スロー双方で停止との記述は原文主張であり、機種別仕様との照合は未実施。"
---

# u形エスカレーター HSS総点検記述

## 原文記載値・状態

- ローラと手摺は、ほぼ平行で接触していないこと。
- センサーとローラの間隙: 2~3 mm。
- 原文に「4回はちょっと動くが5回目からは動かない」とあるが、何を何回操作するかは明確でないため未解釈。

## 原文の機能・条件記述

原文は、移動手摺速度の遅れをローラ回転数から検出して停止させる機能と説明している。また、u形エスカレーターではスロー運転時にマスクされ、他機種は自動・スロー双方で停止すると記載する。機種別の承認済み仕様との照合は未実施。

## 関連・出典

- 機能説明: [[整備済み資料/技術資料/u形_HSS]]
- 原文ノート: [[総点(u型エス)/上部機械室/HSS（手摺スリップ検出装置）]]
- 添付3点はVault内で実在確認済み。画像内容・測定位置は未確認。
- 技術・安全レビュー前のドラフト。作動試験や調整の指示として使用しない。