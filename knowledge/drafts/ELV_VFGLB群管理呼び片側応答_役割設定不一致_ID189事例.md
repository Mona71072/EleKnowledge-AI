---
schema_version: 1
record_id: "case-elv-vfglb-group-call-role-setting-id189"
record_version: 1
title: "VFGLBの2C-2BC運転時に乗場呼びが片側応答した事例（ID189）"
category: "不具合対応(ELV)"
record_type: "troubleshooting_case"
product: "エレベーター"
model_type: ["VFGLB"]
document_number: ""
revision: ""
effective_date: ""
review_status: "in_review"
publication_status: "not_published"
classification: "unknown"
cloud_approval: "not_reviewed"
keywords:
  - "VFGLB"
  - "2C-2BC"
  - "群管理"
  - "乗場呼び"
  - "役割設定"
source_path: "首都工・不具合情報共有リスト.xlsx"
source_filename: "首都工・不具合情報共有リスト.xlsx"
onenote_id: ""
related_ids:
  - "elv-group-operation-issues"
attachment_paths: []
reference_links: []
document_references:
  - document_number: ""
    title: "品目表"
    locator: "203（ID189に記載。実体・改訂・適用範囲未確認）"
    source_path: ""
evidence_sources:
  - source_id: "evidence-list-elv-vfglb-group-call-id189"
    source_type: "vault_original"
    title: "首都工・不具合情報共有リスト: ジャンパーピンの設定不良で、2C-2B時乗場押釦が接続号機しか聞かない（ID189）"
    source_path: "首都工・不具合情報共有リスト.xlsx"
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-14"
    supports:
      - "VFGLBの2C-2BC時に乗場呼びが一方の接続号機のみ応答したとの報告"
      - "制御役割の設定不一致を原因とする原リストの説明"
      - "対応済み欄に対し、具体的な設定修正と復旧結果が記載されていないこと"
structured_data:
  equipment: "VFGLB"
  symptom: "2C-2BC運転時、一般乗場呼びと車椅子乗場呼びがそれぞれ接続された一方の号機側だけで応答したとの報告。両号機が車椅子仕様との記載がある。"
  error_codes: []
  cause: "一次リストは、対向する制御機器の役割設定が重複していたことを原因として挙げる。設定内容と因果関係は独立確認されていない。"
  verified_actions: []
  outcome: "対応状況欄は対応済みとする。詳細欄には盤間/号機間の結線確認で問題がなく、特筆すべきエラー表示がなかったとの記載があるが、設定修正や修正後の呼び応答確認は記載されていない。"
---

# VFGLBの2C-2BC運転時に乗場呼びが片側応答した事例（ID189）

## 事例の概要

首都工・不具合情報共有リストのID189は、VFGLBで2C-2BC運転を行った際、一般呼び・車椅子呼びがそれぞれ接続された号機側だけで応答したと報告する。両号機が車椅子仕様との記載がある。

原因欄は対向する制御機器の役割設定が重複していたと説明する。ただし設定の具体値、変更内容、原因との因果は独立確認されていない。設定値・ジャンパー位置・基板端子情報は掲載しない。

## 対応・結果の記載

対応状況欄は対応済みとする一方、詳細欄で確認できるのは結線上の問題が見つからなかったことと、特筆すべきエラー表示がなかったことまでである。原因欄に挙げた設定の是正、実施者、変更後の呼び応答確認は記載されておらず、復旧状態は確認できない。

## 関連事例との区別

[[ELV_群管理不具合一覧]]にあるID384も2C-2BC運転に関するが、対象はCM-MAで、原因/対応欄が途中で終わり、原因・対応結果は不明。本件ID189とは機種、症状の説明、原因記載が異なり、同一事例・共通原因とは扱わない。

## 出典・確認状態

- 出典: `首都工・不具合情報共有リスト.xlsx`（ID189、sheet1 row235）。
- 品目表203の実体・版・適用、設定修正の実施、呼び応答の復旧確認、原因の独立検証、現行適用性は未確認。
- 号機/現場の識別情報、ジャンパー位置・設定値・基板識別・変更操作は転載していない。本記録を設定・試験・運転・復旧手順として使用しない。