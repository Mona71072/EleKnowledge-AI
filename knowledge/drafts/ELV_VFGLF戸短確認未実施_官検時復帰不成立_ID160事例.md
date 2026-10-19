---
schema_version: 1
record_id: "case-elv-vfglf-door-short-check-recovery-id160"
record_version: 1
title: "VFGLFの官検時に戸短確認が未実施となり復帰できなかった事例（ID160）"
category: "不具合対応(ELV)"
record_type: "troubleshooting_case"
product: "エレベーター"
model_type: ["VFGLF"]
document_number: ""
revision: ""
effective_date: ""
review_status: "in_review"
publication_status: "not_published"
classification: "unknown"
cloud_approval: "not_reviewed"
keywords:
  - "VFGLF"
  - "官庁検査"
  - "戸短検出"
  - "復帰不能"
source_path: "首都工・不具合情報共有リスト.xlsx"
source_filename: "首都工・不具合情報共有リスト.xlsx"
onenote_id: ""
related_ids:
  - "catalog-elv-1d2g-2d2g-gate-and-door-short-reference"
attachment_paths: []
reference_links: []
document_references:
  - document_number: "C-7-C3900"
    title: "戸短検出機能（原リスト記載）"
    locator: "P10, 1-9。資料本文・版未確認"
    source_path: ""
evidence_sources:
  - source_id: "evidence-list-elv-vfglf-door-short-recovery-160"
    source_type: "vault_original"
    title: "首都工・不具合情報共有リスト: 戸短検出による起動不能（ID160）"
    source_path: "首都工・不具合情報共有リスト.xlsx"
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-14"
    supports:
      - "VFGLFの官検時に復帰できず、戸短確認が未実施だったとの報告"
      - "確認前提を満たさない復帰状態が原因とする説明"
      - "対応状況欄が完了である一方、現行手順・復帰後結果は独立確認されていないこと"
structured_data:
  equipment: "VFGLF"
  symptom: "官庁検査時の復帰でエレベーターが管理状態へ戻らず、復帰できなかったとの報告。戸短確認が未実施だったと説明されている。"
  error_codes: []
  cause: "一次リストは、選択されていた復帰状態では戸短確認の前提が成立せず、確認が実施されなかったことを原因として説明する。具体的な状態名、安全回路状態、運転・復帰操作は記録しない。"
  verified_actions: []
  outcome: "対応状況欄は完了。対応内容欄には戸短確認状態に関する記載があるが、具体操作と対応後の復帰・安全確認結果は本記録に転載せず、独立確認もしていない。"
---

# VFGLFの官検時に戸短確認が未実施となり復帰できなかった事例（ID160）

## 事例の概要

首都工・不具合情報共有リストID160は、官庁検査時に復帰できなかったVFGLFの事例を報告する。一次リストの説明では、選択された復帰状態で戸短確認の前提が成立せず、必要な確認が未実施となったことでエレベーターが管理状態へ戻らなかった。

対応状況欄は完了とされる。対応内容欄には戸短確認状態に関する記載があるが、具体的な運転状態、安全回路の動作、操作・確認・復帰手順は転載しない。

## 確認状態と参照

参照資料としてC-7-C3900、P10、1-9が挙げられているが、資料本文・版・現行適用は未確認。添付参照の実体も未確認。対応後の復帰状態、安全確認、原因の独立検証も未確認である。

本記録は事例の検索用であり、戸短検査、官検、運転、復帰、安全回路の確認や異常解除の手順として使用しない。現行の機種別承認済み要領と安全レビューを別途確認する必要がある。

## 関連資料

[[ELV_1D2G_2D2G戸短とゲート確認_参照記録]]は戸短関連の一般参照だが、本件の復帰手順・適用範囲を裏付ける資料ではない。

## 出典

- 首都工・不具合情報共有リスト.xlsx、ID160（sheet1 row262）。
- 現場/施設/担当者識別情報、具体的な運転状態・安全回路状態・操作手順は転載していない。