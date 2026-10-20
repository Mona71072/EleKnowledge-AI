---
schema_version: 1
record_id: "case-elv-vfglb-terminal-switch-mechanical-failure-id177"
record_version: 1
title: "VFGLBで最上階到着後に起動できない終点スイッチ機械故障報告（ID177）"
category: "不具合対応(ELV)"
record_type: "troubleshooting_case"
product: "エレベーター"
model_type:
  - "VFGLB"
document_number: ""
revision: ""
effective_date: ""
review_status: "in_review"
publication_status: "not_published"
classification: "unknown"
cloud_approval: "not_reviewed"
keywords:
  - "VFGLB"
  - "最上階"
  - "起動不能"
  - "終点スイッチ"
  - "スイッチ機械故障"
  - "バネ脱落"
  - "SETS"
source_path: "首都工・不具合情報共有リスト.xlsx"
source_filename: "首都工・不具合情報共有リスト.xlsx"
onenote_id: ""
related_ids:
  - "elv-sets-position-reference-signal-open-circuit-id358"
attachment_paths: []
reference_links: []
document_references: []
evidence_sources:
  - source_id: "evidence-list-elv-vfglb-terminal-switch-failure-id177"
    source_type: "vault_original"
    title: "首都工・不具合情報共有リスト: 自動運転で最上階に着床後、起動不能になる件（ID177）"
    source_path: "首都工・不具合情報共有リスト.xlsx"
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-14"
    supports:
      - "VFGLBで最上階到着後に起動できないとの報告"
      - "終点スイッチの機械的異常とON故障を原因とする説明"
      - "位置確認表示の限界に関する原文説明、対応後に解消を確認したとの報告"
      - "具体的な確認・復旧方法と独立確認が未確認であること"
structured_data:
  equipment: "VFGLBの終点スイッチと自動運転"
  symptom: "自動運転で最上階に着床した後、起動できなくなったとの報告。"
  error_codes: []
  cause: "一次リストは終点スイッチの機械的異常によりON故障となったことを原因として説明する。部品識別、信号状態の確認方法、復旧操作は記録しない。"
  verified_actions: []
  outcome: "原リストは対応後に不具合解消を確認したと報告し、対応欄を完了としている。具体的対応内容、独立確認、他号機への適用は未確認。"
---

# VFGLBで最上階到着後に起動できない終点スイッチ機械故障報告（ID177）

## 症状と原因説明

首都工・不具合情報共有リストID177は、VFGLBの自動運転で最上階に着床した後、起動できなくなったと報告する。原因欄は終点スイッチの機械的異常によるON故障と説明し、位置確認表示だけではスイッチの電気的な状態を判定しない旨を記載している。これは原リストの説明であり、独立した技術検証や適用範囲は未確認である。

## 対応状況と確認限界

原リストは対応後に不具合解消を確認したと報告し、対応欄を完了としている。具体的な確認・復旧方法、スイッチの識別、対応後の独立確認、他号機への適用は確認できない。操作・点検・交換・運転復帰の手順や安全機能の判定基準として使用しない。

## 類似事例との区別

[[ELV_SETS位置基準信号断線_ID358事例]]も最上階到着後の起動不能を扱うが、MRLにおける位置基準信号経路の断線報告であり、本件の終点スイッチ機械故障とは原因・対象機種が異なる。両事例の復旧・運転条件を相互に流用しない。

## 出典

- 首都工・不具合情報共有リスト.xlsx、ID177（sheet1 row247）。
- 信号識別子、電気/機械的な点検・復旧・交換・運転手順、個人/現場情報は転載していない。