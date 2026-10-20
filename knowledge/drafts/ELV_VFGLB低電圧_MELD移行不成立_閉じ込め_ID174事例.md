---
schema_version: 1
record_id: "case-elv-vfglb-low-battery-meld-failure-entrapment-id174"
record_version: 1
title: "VFGLBのバッテリー低電圧によるMELD移行不成立・閉じ込め報告（ID174）"
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
  - "バッテリー低電圧"
  - "MELD"
  - "移行不成立"
  - "閉じ込め"
source_path: "首都工・不具合情報共有リスト.xlsx"
source_filename: "首都工・不具合情報共有リスト.xlsx"
onenote_id: ""
related_ids:
  - "elv-meld-operation-reference"
  - "elv-battery-issues-reference"
  - "elv-meld-battery-polarity-m1-card-damage-id101"
attachment_paths: []
reference_links: []
document_references: []
evidence_sources:
  - source_id: "evidence-list-elv-vfglb-low-battery-meld-entrapment-id174"
    source_type: "vault_original"
    title: "首都工・不具合情報共有リスト: バッテリー電圧が低く、MELD動作に移行せず閉じ込めになってしまう（ID174）"
    source_path: "首都工・不具合情報共有リスト.xlsx"
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-14"
    supports:
      - "VFGLBでバッテリー低電圧によりMELDへ移行しなかったとの閉じ込め報告"
      - "対応欄が対応不要とされていること"
      - "閉じ込め解消、バッテリー状態、MELD機能の独立確認が未確認であること"
structured_data:
  equipment: "VFGLBのバッテリーとMELD機能"
  symptom: "バッテリー電圧が低く、MELD動作に移行しないまま閉じ込めに至ったとの報告。"
  error_codes: []
  cause: "一次リストはバッテリー電圧低下をMELDへ移行しなかった要因として示す。電圧低下の根本原因、測定条件、設備状態は未確認。"
  verified_actions: []
  outcome: "対応欄は「対応不要」。閉じ込め解消、バッテリー状態の是正、MELD機能の復旧・安全確認を示す記載としては確認できない。"
---

# VFGLBのバッテリー低電圧によるMELD移行不成立・閉じ込め報告（ID174）

## 症状と原因説明

首都工・不具合情報共有リストID174は、VFGLBでバッテリー電圧が低く、MELD動作に移行せず閉じ込めに至ったと報告する。原リストは低電圧を移行不成立の要因としているが、電圧低下の根本原因、測定条件、設備状態は未確認である。

## 対応状況と確認限界

原リストの対応欄は「対応不要」とされている。この表示は、閉じ込めが解消したこと、バッテリー状態が是正されたこと、MELD機能が正常に復旧したことの独立確認を示すものではない。

本記録は事例情報であり、閉じ込め救出、MELD運転、バッテリー充電・交換・測定、電気試験の手順や判断基準ではない。人命安全に関わるため、現行の承認済み救出要領・回路図と所管技術者の確認を要する。電圧値、端子、極性、測定・操作・救出手順は転載しない。

## 類似事例との区別

[[ELV_MELDバッテリー極性誤接続_M1カード損傷_ID101事例]]は、極性誤接続とM1カード損傷の別報告である。本件の低電圧やMELD移行不成立の原因・対応を裏付けない。

## 出典

- 首都工・不具合情報共有リスト.xlsx、ID174（sheet1 row250）。
- 個人/現場情報、電圧・端子・極性、測定/交換/救出/運転手順は転載していない。