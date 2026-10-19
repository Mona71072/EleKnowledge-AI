---
schema_version: 1
record_id: "elv-vfglf-sd-t12-contactor-brake-not-releasing-id95"
record_version: 1
title: "VFGLFのSD-T12コンタクタ吸引後にブレーキが作動しない報告（ID95）"
category: "不具合対応(ELV)"
record_type: "troubleshooting_case"
product: "エレベーター"
model_type:
  - "VFGLF"
document_number: ""
revision: ""
effective_date: ""
review_status: "unreviewed"
publication_status: "not_published"
classification: "unknown"
cloud_approval: "not_reviewed"
keywords:
  - "SD-T12"
  - "コンタクタ"
  - "ブレーキ不作動"
  - "接触抵抗"
  - "417"
  - "41A"
  - "439"
  - "43C"
  - "943"
  - "953"
related_ids:
  - "elv-contactor-not-pulling-source-knowledge-id64"
source_path: ""
source_filename: "技術情報リスト（協力会社展開用）.xlsx"
onenote_id: ""
attachment_paths: []
reference_links: []
document_references: []
evidence_sources:
  - source_id: "evidence-list-case-id95"
    source_type: "user_provided_extract"
    title: "首都工・不具合情報共有リスト Excel出力 ID95"
    source_path: ""
    s3_uri: ""
    revision: "原本リスト未照合"
    accessed_at: "2026-10-09"
    supports:
      - "VFGLFのSD-T12コンタクタに関する症状、エラー表示、接触抵抗を原因とする原文記載、製造元調査・交換記載と進捗"
structured_data:
  equipment: "VFGLF エレベーター"
  symptom: "コンタクタは吸引するが、ブレーキが作動しないとの報告。エラー表示欄は417、41A、439、43C、943、953。"
  error_codes:
    - "417"
    - "41A"
    - "439"
    - "43C"
    - "943"
    - "953"
  cause: "原リストはSD-T12コンタクタの接点接触抵抗が大きくなることを原因として記載する。記載された原因、対象範囲、因果関係は独立確認されていない。"
  verified_actions: []
  outcome: "進捗欄では、不発返却品を製造元で確認中、接触抵抗が大きくなる原因を調査中、Qシート発行予定と記載する。不具合原因・対応欄にはLBA/LBBコンタクタの交換が記載されるが、交換の実施確認、Qシート発行、交換後の確認結果は記載されていない。"
---

# VFGLFのSD-T12コンタクタ吸引後にブレーキが作動しない報告（ID95）

## 概要

首都工・不具合情報共有リストID95は、VFGLFでコンタクタが吸引する一方、ブレーキが作動しない事象を報告する。対象部品欄にはSD-T12、エラー表示欄には417、41A、439、43C、943、953が記載されている。共有日は2022-02-14。

## 原文の原因説明と調査経過

原リストは、コンタクタの接点接触抵抗が大きくなることを原因として記載する。進捗欄では、不発返却品を製造元で確認中で、接触抵抗が大きくなる原因を調査中、Qシートを発行予定としている。これらはリスト上の報告であり、原因やエラー表示との因果関係は独立確認されていない。

## 対応記載と結果

不具合原因・対応欄にはLBA/LBBコンタクタの交換が記載されている。ただし、交換の実施確認、製造元調査やQシートの完了、交換後にブレーキが作動したかは記載されていない。

## 関連資料

- [[ELV_コンタクタ不吸引の原文知識_ID64]]: ID64は、#5コンタクタが吸引指令なしでは吸引しないという一般説明。ID95はコンタクタが吸引するがブレーキが作動しない個別報告であり、症状・原因説明が異なる。相互参照は識別のためで、同一原因や適用範囲を示さない。
- [[不具合対応【ELV】/索引]]: ELV整備資料の索引。

## 出典・確認状態

- 出典: Excel出力のID95行にあるA列・E〜N列・O列。B/C/D列は参照していない。
- 測定条件・閾値、端子名・測定位置、遮断器操作、コンタクタの手動操作等の具体的な電気診断手順は転記していない。
- 返却品、接点状態、交換実施、製造元調査、Qシート発行、交換後の結果は未確認。機種別の適用性・現行性と専門レビューも未確認。
- 本記録は未レビューであり、電気測定、部品交換、ブレーキ・運転系の診断や作業手順を示すものではない。
