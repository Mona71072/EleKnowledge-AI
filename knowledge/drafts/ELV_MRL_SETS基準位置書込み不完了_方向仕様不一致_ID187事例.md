---
schema_version: 1
record_id: "case-elv-mrl-sets-position-write-direction-spec-id187"
record_version: 1
title: "MRLのSETS基準位置書込み不完了と方向仕様不一致の事例（ID187）"
category: "不具合対応(ELV)"
record_type: "troubleshooting_case"
product: "エレベーター"
model_type: ["MRL"]
document_number: ""
revision: ""
effective_date: ""
review_status: "in_review"
publication_status: "not_published"
classification: "unknown"
cloud_approval: "not_reviewed"
keywords:
  - "MRL"
  - "SETS"
  - "基準位置書込み"
  - "方向仕様不一致"
source_path: "首都工・不具合情報共有リスト.xlsx"
source_filename: "首都工・不具合情報共有リスト.xlsx"
onenote_id: ""
related_ids:
  - "catalog-elv-sets-failure-reference"
  - "elv-sets-position-reference-signal-open-circuit-id358"
attachment_paths: []
reference_links: []
document_references:
  - document_number: "EA-98"
    title: "原リストが参照する技術資料（正式題名未確認）"
    locator: "p.45。本文・版・適用範囲未確認"
    source_path: ""
evidence_sources:
  - source_id: "evidence-list-elv-mrl-sets-position-write-187"
    source_type: "vault_original"
    title: "首都工・不具合情報共有リスト: SETS基準位置書き込みが完了しない件（ID187）"
    source_path: "首都工・不具合情報共有リスト.xlsx"
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-14"
    supports:
      - "MRLでSETS基準位置書込みが完了せず可変速状態へ移行しなかったとの報告"
      - "ガバナエンコーダーに関する方向仕様の設計不一致との原因説明"
      - "変換部品の適用後に動作良好となったとの原リスト報告"
structured_data:
  equipment: "MRLのSETS関連設備"
  symptom: "SETS基準位置書込みが完了せず、可変速状態へ移行しなかったとの報告。具体的な表示コード、測定/位置値、運転方向は記録しない。"
  error_codes: []
  cause: "一次リストは、ガバナエンコーダーに関する方向仕様が設計上不一致だったと説明する。方向、型式、品目識別および接続情報は記録しない。"
  verified_actions: []
  outcome: "原リストは変換部品の適用後に動作良好となったと報告する。実施記録、対応後の継続確認、安全確認、原因の独立検証は未確認。"
---

# MRLのSETS基準位置書込み不完了と方向仕様不一致の事例（ID187）

## 事例の概要

首都工・不具合情報共有リストID187は、MRLでSETS基準位置書込みが完了せず、可変速状態へ移行しなかった事例を報告する。一次リストは、ガバナエンコーダーに関する方向仕様の設計不一致を原因として挙げている。

対応後について、原リストは変換部品の適用後に動作良好となったと記載する。これは出典上の報告であり、原因・対応との因果、作業の承認、対応後の継続動作や安全状態は独立確認されていない。

## 関連事例との区別

[[ELV_SETS不具合_参照記録]]はSETS関連不具合の参照一覧であり、個別内容の根拠ではない。[[ELV_SETS位置基準信号断線_ID358事例]]もMRLの位置基準に関する事例だが、同記録は信号経路の断線報告であり、本件の方向仕様不一致とは原因説明が異なる。

## 参照・未確認事項

原リストはEA-98 p.45を参照するが、資料本文・版・対象機種への適用は未確認。エラーコード、位置値、運転方向、機種/部品識別、配線・接続、部品の手配・取付方法は記録しない。本記録をSETSの設定、書込み、運転、部品選定、復旧の手順として使用しない。

## 出典

- 首都工・不具合情報共有リスト.xlsx、ID187（sheet1 row237）。
- 現場/設備識別情報、エラーコード、具体的な方向・位置値・配線/接続情報は転載していない。