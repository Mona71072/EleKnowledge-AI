---
schema_version: 1
record_id: "elv-rear-ns-key-switch-no-response-id364"
record_version: 1
title: "リア側NS用キースイッチ不動作事例（ID364）"
category: "不具合対応(ELV)"
record_type: "troubleshooting_case"
product: "エレベーター"
model_type:
  - "VFGLB"
  - "VFGLF"
document_number: ""
revision: ""
effective_date: ""
review_status: "in_review"
publication_status: "not_published"
classification: "unknown"
cloud_approval: "not_reviewed"
keywords:
  - "NS用キースイッチ"
  - "サービス階切放し一時解除"
  - "制御構成"
  - "入力信号"
source_path: ""
source_filename: "技術情報リスト（協力会社展開用）.xlsx"
onenote_id: ""
related_ids: []
attachment_paths: []
reference_links: []
document_references: []
evidence_sources:
  - source_id: "evidence-list-elv-rear-ns-key-switch-364"
    source_type: "user_provided_extract"
    title: "協力会社展開用Excel: リア側NS用キースイッチ不動作（ID364）"
    source_path: ""
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-13"
    supports:
      - "リア側の対象キースイッチ操作に応答しなかった症状、異常所見なしとの調査報告、制御構成に関する原因説明"
structured_data:
  equipment: "エレベーター（VFGLB・VFGLF）"
  function: "原文は、解除釦機能付きのかご呼びサービス階切放し一時解除運転に関わるNS用キースイッチとして説明する。"
  symptom: "リア側の対象キースイッチを操作しても、意図した機能が動作しなかったとの報告。"
  findings: "キースイッチ、信号経路の確認および電気的確認では異常が見つからなかったとの記載。具体的な電圧値、ピン、コネクタ識別は記録しない。"
  cause_assessment: "原リストは、リア側制御部からの信号を当該機能が処理しない制御構成であり、所定の入力元からの信号のみを受け付ける仕様と説明する。設計資料や当該機での独立確認は行っていない。"
  reported_response: "原リストには信号経路のハードウェア構成変更が対応として記載されている。具体的な基板、コネクタ、配線経路および作業内容は記録せず、実施・承認・結果も未確認。"
  outcome: "対応後の機能確認結果は記載から確認できない。"
  limitations:
    - "サービス機能の有効化、信号経路変更、基板位置、端子/コネクタ識別、配線情報は記録しない。"
    - "現場・建物・号機・担当者情報は転記しない。"
    - "本記録は参考用であり、サービス機能の設定・配線変更・運転操作手順ではない。"
---

# リア側NS用キースイッチ不動作事例（ID364）

## 症状と調査

首都工・不具合情報共有リストID364は、VFGLB・VFGLFで、リア側のNS用キースイッチを操作しても対象機能が動作しなかったと報告する。原文はこの機能を、解除釦機能付きのかご呼びサービス階切放し一時解除運転に関わるものと説明している。

キースイッチや信号経路の確認、電気的確認では異常が見つからなかったとの記載がある。具体的な電圧値、ピン、コネクタ識別は転記しない。

## 原因説明と対応状態

原リストは、リア側制御部からの信号を対象機能が処理しない制御構成であり、所定の入力元からの信号のみを受け付ける仕様と説明する。この説明は原リスト上の記載で、設計資料や当該機で独立確認していない。

原リストには信号経路のハードウェア構成変更が対応として記載されているが、具体的な基板・コネクタ・配線経路・作業内容は含めない。変更の実施・設計承認・対応後の機能確認結果は未確認である。

## 利用上の制限

本件はサービス階の切放しを一時解除する機能に関する報告であり、本記録をサービス機能の設定、信号経路変更、配線、運転操作の手順として使用しない。変更要否・設計適合性は承認済み設計資料と所管担当で確認する。