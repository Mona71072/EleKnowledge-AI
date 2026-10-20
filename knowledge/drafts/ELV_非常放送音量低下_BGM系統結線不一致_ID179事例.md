---
schema_version: 1
record_id: "case-elv-emergency-broadcast-low-volume-bgm-wiring-mismatch-id179"
record_version: 1
title: "非常放送の音量低下とBGM系統の結線不一致報告（ID179）"
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
  - "非常放送"
  - "BGM"
  - "音量低下"
  - "結線不一致"
  - "2線式"
  - "3線式"
source_path: "首都工・不具合情報共有リスト.xlsx"
source_filename: "首都工・不具合情報共有リスト.xlsx"
onenote_id: ""
related_ids:
  - "catalog-elv-bgm-emergency-broadcast-reference"
attachment_paths: []
reference_links: []
document_references:
  - document_number: "品証-06-118"
    title: "協力会社連絡メモ"
    locator: "結線変更の根拠として原リストが記載。本文・版・適用範囲は未確認。"
    source_path: ""
evidence_sources:
  - source_id: "evidence-list-elv-emergency-broadcast-low-volume-bgm-mismatch-179"
    source_type: "vault_original"
    title: "首都工・不具合情報共有リスト: BGM結線ミスで非常放送の音量が小さい件（ID179）"
    source_path: "首都工・不具合情報共有リスト.xlsx"
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-14"
    supports:
      - "非常放送のみの現場での音量低下と、かご上でも同様だったとの報告"
      - "アッテネーター設定ではなく、入線構成と放送設備側の結線方式の不一致を原因とする説明"
      - "連絡メモに基づく変更後の音量増加報告と、独立確認・現行適用が未確認であること"
structured_data:
  equipment: "エレベーターのBGM/非常放送系統"
  symptom: "非常放送のみの現場で放送動作を確認したところ音量が小さく、かご上でも同様だったとの報告。アッテネーター設定に問題はなかったと記載されている。"
  error_codes: []
  cause: "一次リストは、機械室への入線構成と放送設備側の結線方式が一致しておらず、一般放送と非常放送で結線方式が異なることへの理解が不足していたと説明する。具体的な配線割当・端子情報は記録しない。"
  verified_actions: []
  outcome: "原リストは、連絡メモに基づく結線変更後に音量が大きくなったと報告し、対応欄は完了としている。変更の実施・安全承認・放送機能の独立確認・現行適用は未確認。"
---

# 非常放送の音量低下とBGM系統の結線不一致報告（ID179）

## 症状と原因説明

首都工・不具合情報共有リストID179は、非常放送のみの現場で放送動作を確認した際に音量が小さく、かご上でも同様だったと報告する。アッテネーターの設定には問題がなかったとの記載がある。

原因欄は、機械室への入線構成と放送設備側の結線方式が一致せず、一般放送と非常放送で結線方式が異なることを理解していなかったと説明する。端子・線番・具体的な信号割当は転載しない。

## 対応状況と確認限界

原リストは、協力会社連絡メモ（品証-06-118）に基づく結線変更後に音量が大きくなったと報告し、対応欄を完了としている。連絡メモの本文・版・適用範囲、変更の実施状況、非常放送の機能・音量の独立確認、現行設備への適用は未確認である。

本記録は一事例の原因説明と結果報告であり、非常放送の設計・配線・結線変更・音量試験の手順や判断基準ではない。結線図、端子/線番、個々の接続先、変更方法、試験操作は転載していない。生命安全に関わる放送設備への適用は、承認済みの現行設計資料と所管技術者の確認を要する。

## 類似報告との区別

[[ELV_BGM非常放送_参照記録]]が扱うID363もBGM結線と音量低下の報告だが、VFGLB/VFGLFのかご上スピーカーに関する別事例である。対象設備と条件を混同せず、ID363の結線・是正内容を本件へ流用しない。

## 出典

- 首都工・不具合情報共有リスト.xlsx、ID179（sheet1 row245）。
- 個人名・現場名、端子/線番/具体配線割当、結線変更・試験手順は転載していない。