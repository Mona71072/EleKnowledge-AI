---
schema_version: 1
record_id: "u-hss-handrail-slip-detector"
record_version: 1
title: "u形エスカレーター HSS（手摺スリップ検出装置）"
category: "エスカ（u形）"
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
  - "手摺スリップ"
  - "速度検出"
source_path: "エスカ（u形）/エス安全スイッチの機能/HSS（手摺スリップ検出装置）.md"
source_filename: "HSS（手摺スリップ検出装置）.md"
onenote_id: "06535fb9-1e04-44ce-81e8-794ca50b3d11:80"
related_ids: []
attachment_paths:
  - "エスカ（u形）/エス安全スイッチの機能/OneNote/HSS（手摺スリップ検出装置） image.png"
  - "エスカ（u形）/エス安全スイッチの機能/OneNote/HSS（手摺スリップ検出装置） image 1.png"
reference_links: []
document_references: []
evidence_sources:
  - source_id: "evidence-u-hss-original"
    source_type: "vault_original"
    title: "HSS（手摺スリップ検出装置）（原文）"
    source_path: "エスカ（u形）/エス安全スイッチの機能/HSS（手摺スリップ検出装置）.md"
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-01"
    supports:
      - "手摺速度の検出と機種別マスク記述"
structured_data:
  specifications:
    - name: "検出方法"
      value: "移動手摺の動きに伴うローラーの回転数から速度を検出"
      unit: ""
      condition: "原文記載"
    - name: "異常時の動作"
      value: "手摺速度が遅れた場合、エスカレーターを停止"
      unit: ""
      condition: "原文記載"
  source_notes:
    - "原文の「4回はちょっと動くが5回目からは動かない」の意味が不明確。"
    - "u形のスロー運転時はマスク、他機種は自動・スローとも停止すると原文にある。回路・条件・現行性は要確認。"
    - "ローラーをドライバーで持ち上げる旨の原文記述は作業指示に転記していない。"
---

# u形エスカレーター HSS（手摺スリップ検出装置）

## 機能

- 原文では、異常により移動手摺の速度が遅れた場合にエスカレーターを停止させると説明している。
- 手摺の動きに伴って回転するローラーの回転数から速度を検出すると記載されている。
- 原文はu形についてスロー運転時にマスクされる仕様、他機種は自動・スローの両方で停止すると記す。

## 原文確認が必要な記述

「4回はちょっと動くが5回目からは動かない」という記述は、回数の対象や動作条件が明確でないため解釈していない。ローラーをドライバーで持ち上げる旨の記載も、安全な作業方法として転記していない。

![[エスカ（u形）/エス安全スイッチの機能/OneNote/HSS（手摺スリップ検出装置） image.png]]
![[エスカ（u形）/エス安全スイッチの機能/OneNote/HSS（手摺スリップ検出装置） image 1.png]]

## 出典・確認履歴

- 原文ノート: [[エスカ（u形）/エス安全スイッチの機能/HSS（手摺スリップ検出装置）]]
- 添付画像2点はVault内で実在確認済み。技術担当者による作動条件・マスク条件の確認が必要。
- 安全装置の技術レビュー前のドラフト。試験・調整・運転判断には使用しない。