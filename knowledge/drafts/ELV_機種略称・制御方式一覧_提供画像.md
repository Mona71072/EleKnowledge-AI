---
schema_version: 1
record_id: "elv-model-abbreviations-user-image"
record_version: 2
title: "エレベーター機種略称・制御方式一覧（提供画像）"
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
keywords:
  - "機種略称"
  - "機械室"
  - "制御方式"
  - "AXIEZ"
  - "Nexcube"
source_path: ""
source_filename: "ユーザー提供画像（エレベーター機種略称一覧）"
related_ids: []
attachment_paths: []
reference_links: []
document_references: []
evidence_sources:
  - source_id: "evidence-elv-model-list-user-image-20261009"
    source_type: "user_provided_extract"
    title: "ユーザー提供画像: エレベーター機種略称一覧"
    source_path: ""
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-09"
    supports:
      - "画像に表示された商品名、区分、機械室、機種略称、制御方式の対応"
      - "MRL/MR/CMRの略語説明"
structured_data:
  items:
    - product: "AXIEZ"
      category: "機械室レスエレベーター"
      machine_room: "MRL"
      model_abbreviations: ["KE-PF", "KE-RF", "KE-RFS", "KE-BF", "KE-WF/HF"]
      control_method_labels: ["VFGLB", "VFGLB-JB"]
    - product: "Nexcube"
      category: "低速大容量エレベーター"
      machine_room: "CMR"
      model_abbreviations: ["KM-LD"]
      control_method_labels: ["VFGLB-WB"]
    - product: "Nexcube"
      category: "省スペース型低速エレベーター"
      machine_room: "CMR"
      model_abbreviations: ["CM-LB"]
      control_method_labels: ["VFGLB-K"]
    - product: "Nexcube"
      category: "省スペース型高速エレベーター"
      machine_room: "CMR"
      model_abbreviations: ["CM-MA"]
      control_method_labels: ["VFGH"]
    - product: "Nexcube"
      category: "超高速エレベーター"
      machine_room: "MR"
      model_abbreviations: ["ME-CH"]
      control_method_labels: ["VFGH"]
    - product: "Nexcube"
      category: "高速エレベーター"
      machine_room: "MR"
      model_abbreviations: ["ME-CM"]
      control_method_labels: ["VFGH"]
    - product: "Nexcube"
      category: "低速エレベーター"
      machine_room: ""
      model_abbreviations: ["ME-BL"]
      control_method_labels: ["VFEL"]
    - product: "MELCITY"
      category: "小形機械室レスエレベーター"
      machine_room: "MRL"
      model_abbreviations: ["AC-PB"]
      control_method_labels: ["VFGR"]
    - product: "MELWIDE"
      category: "小形機械室レスエレベーター"
      machine_room: "MRL"
      model_abbreviations: ["AC-CB"]
      control_method_labels: ["VFGR"]
    - product: "機械室レス荷物用"
      category: "荷物用機械室レスエレベーター"
      machine_room: "MRL"
      model_abbreviations: ["KF-ETC", "KF-MTC"]
      control_method_labels: ["VFGLB"]
    - product: "中小形荷物用エレベーター"
      category: "中小形荷物用エレベーター"
      machine_room: "MR"
      model_abbreviations: ["FE-TA", "FM-TA"]
      control_method_labels: ["VFEL"]
    - product: "駅舎用エレベーター"
      category: "駅舎用エレベーター"
      machine_room: "MRL"
      model_abbreviations: ["KE-SA", "KE-SAT", "KM-SA", "KM-SAT"]
      control_method_labels: ["VFGL"]
  terminology:
    - source_term: "MRL"
      normalized_term: "Machine room less"
      term_type: "other"
      context: "画像脚注の機械室区分"
      verification_status: "verified"
      evidence_source_id: "evidence-elv-model-list-user-image-20261009"
    - source_term: "MR"
      normalized_term: "Machine room"
      term_type: "other"
      context: "画像脚注の機械室区分"
      verification_status: "verified"
      evidence_source_id: "evidence-elv-model-list-user-image-20261009"
    - source_term: "CMR"
      normalized_term: "Compact machine room"
      term_type: "other"
      context: "画像脚注の機械室区分"
      verification_status: "verified"
      evidence_source_id: "evidence-elv-model-list-user-image-20261009"
  source_notes:
    - "本記録はユーザー提供画像の可読範囲を転記したもの。Vault原文・原画像との同一性、画像の版、適用条件は未照合。"
    - "画像の結合セルを含む制御方式欄は表示文字を記録した。AXIEZのVFGLB/VFGLB-JB等、結合セルの厳密な行対応は原画像の高解像度版または所管資料で再確認する。"
    - "Nexcube低速エレベーター（ME-BL）の機械室欄は画像上で対応値を判読できないため空欄とした。"
    - "画像外の海外機種展開領域、機種別仕様、現行適用性は本記録に含めない。"
---

# エレベーター機種略称・制御方式一覧（提供画像）

## 画像に記載された対応

| 商品名 | 区分 | 機械室 | 機種略称 | 制御方式欄の表示 |
| --- | --- | --- | --- | --- |
| AXIEZ | 機械室レスエレベーター | MRL | KE-PF、KE-RF、KE-RFS、KE-BF、KE-WF/HF | VFGLB、VFGLB-JB（結合セル。個別の略称との厳密な対応は要確認） |
| Nexcube | 低速大容量エレベーター | CMR | KM-LD | VFGLB-WB |
| Nexcube | 省スペース型低速エレベーター | CMR | CM-LB | VFGLB-K |
| Nexcube | 省スペース型高速エレベーター | CMR | CM-MA | VFGH |
| Nexcube | 超高速エレベーター | MR | ME-CH | VFGH |
| Nexcube | 高速エレベーター | MR | ME-CM | VFGH |
| Nexcube | 低速エレベーター | 判読できず | ME-BL | VFEL |
| MELCITY | 小形機械室レスエレベーター | MRL | AC-PB | VFGR |
| MELWIDE | 小形機械室レスエレベーター | MRL | AC-CB | VFGR |
| 機械室レス荷物用 | 荷物用機械室レスエレベーター | MRL | KF-ETC、KF-MTC | VFGLB |
| 中小形荷物用エレベーター | 中小形荷物用エレベーター | MR | FE-TA、FM-TA | VFEL |
| 駅舎用エレベーター | 駅舎用エレベーター | MRL | KE-SA、KE-SAT、KM-SA、KM-SAT | VFGL |

画像脚注の機械室区分は、`MRL: Machine room less`、`MR: Machine room`、`CMR: Compact machine room`。

## 確認上の制限

ユーザーは本画像を「エレ機種一覧」と特定している。Vaultの[[技術メモ【ELV】２/ELV-一般/エレ機種一覧]]は4画像の埋め込み参照を持つが、実ファイルは確認できておらず、本画像がどの埋め込み画像に対応するかは未照合。結合セルにまたがる対応は本表で確定せず、画像に見える略称一覧として記録した。本記録は「提供画像に当該表記がある」という確認には使用できるが、機種の現行適用、製造時期、改訂、個別仕様や適用保証は示さない。

## 出典

- ユーザー提供画像（2026-10-09に受領）。Vault内の原画像/添付として登録していない。
- 関連する原資料ページ: [[技術メモ【ELV】２/ELV-一般/エレ機種一覧]]。同ページの埋め込み画像・画像対応は未確認。