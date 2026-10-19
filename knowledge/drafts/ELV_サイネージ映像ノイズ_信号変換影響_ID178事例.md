---
schema_version: 1
record_id: "case-elv-signage-video-noise-signal-conversion-id178"
record_version: 1
title: "サイネージ映像の乱れ・一時出力停止に関する報告（ID178）"
category: "不具合対応(ELV)"
record_type: "troubleshooting_case"
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
  - "サイネージ"
  - "映像ノイズ"
  - "映像乱れ"
  - "映像出力停止"
  - "信号変換"
  - "ツイストペア"
  - "同軸"
source_path: "首都工・不具合情報共有リスト.xlsx"
source_filename: "首都工・不具合情報共有リスト.xlsx"
onenote_id: ""
related_ids:
  - "catalog-elv-signage-case-reference"
attachment_paths: []
reference_links: []
document_references: []
evidence_sources:
  - source_id: "evidence-list-elv-signage-video-noise-id178"
    source_type: "vault_original"
    title: "首都工・不具合情報共有リスト: デジタルサイネージ映像にノイズが発生する件（ID178）"
    source_path: "首都工・不具合情報共有リスト.xlsx"
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-14"
    supports:
      - "映像に乱れがあり、時折映像が出力されないとの報告"
      - "信号変換構成が光ケーブルと比べてノイズの影響を受けやすいとの原リストの原因説明"
      - "原リストの対応欄が対応済みであること。具体的な解決内容・復旧確認は確認できない"
structured_data:
  equipment: "エレベーターのデジタルサイネージ映像系統"
  symptom: "改造実施後に映像の乱れが発生し、時折映像が出力されなくなるとの報告。"
  error_codes: []
  cause: "原リストは、ツイストペアから同軸への信号変換が光ケーブル構成よりノイズの影響を受けやすいと説明する。この原因説明の独立検証、設計条件、現行適用は未確認。"
  verified_actions: []
  outcome: "原リストの対応欄は対応済みだが、具体的な処置内容、映像の復旧・安定性、独立確認の記載は確認できない。"
---

# サイネージ映像の乱れ・一時出力停止に関する報告（ID178）

## 症状と原因説明

首都工・不具合情報共有リストID178は、サイネージの改造実施後に映像の乱れがあり、時折映像が出力されなくなると報告する。原リストは、ツイストペアから同軸への信号変換が光ケーブル構成に比べてノイズの影響を受けやすいと説明しているが、原因の独立検証や設計条件は確認できていない。

本記録は一件の報告であり、特定方式の適合性・優劣や不具合原因を一般化するものではない。顧客設備の情報、外部機器の組合せ、図面番号、信号割当、配線・改造手順は記録しない。

## 対応状況と確認限界

原リストの対応欄は対応済みだが、具体的な処置内容、映像の復旧・安定性、独立確認の記載は確認できない。対応済み表示をもって不具合解消または現行設計への適合と判断しない。

映像伝送の設計・機器選定・配線・改造判断には使用せず、承認済みの現行設計資料と所管技術者の確認を要する。

## 類似事例との区別

[[ELV_サイネージ_案件情報除外記録]]はサイネージ配線図と過去の互換性情報に関する参照記録であり、本件の原因や対応を裏付けるものではない。[[ELV_ITV映像ノイズ_分配器出力構成_ID323事例]]はかご内ITV映像の別報告で、設備機能・構成を混同しない。

## 出典

- 首都工・不具合情報共有リスト.xlsx、ID178（sheet1 row246）。
- 個別案件名、顧客/取引先情報、外部リンク、図面番号、配線割当・改造手順は転載していない。