---
schema_version: 1
record_id: "case-elv-wos-suppression-diode-failure-id180"
record_version: 1
title: "WOS運転不能とサージ抑制用ダイオード不良の報告（ID180）"
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
  - "WOS運転"
  - "コンタクタ"
  - "サージ抑制用ダイオード"
  - "制御カード"
source_path: "首都工・不具合情報共有リスト.xlsx"
source_filename: "首都工・不具合情報共有リスト.xlsx"
onenote_id: ""
related_ids: []
attachment_paths: []
reference_links: []
document_references: []
evidence_sources:
  - source_id: "evidence-list-elv-wos-suppression-diode-failure-180"
    source_type: "vault_original"
    title: "首都工・不具合情報共有リスト: コンダクタのダイオード不良により、かご運転不能になった件（ID180）"
    source_path: "首都工・不具合情報共有リスト.xlsx"
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-14"
    supports:
      - "WOS運転不能時の表示・動作と、調査段階で確認された所見"
      - "サージ抑制用ダイオードの特性異常との一次リスト説明と、サージによるカード損傷という推定"
      - "制御カード交換後に正常動作したとの報告、および独立確認・現行適用が未確認であること"
structured_data:
  equipment: "エレベーターのWOS運転系"
  symptom: "モーター空回し後のWOS運転で、上・下方向とも動かなかったとの報告。コンタクタが一時的に動作した後に落ち、制御カードの表示も消灯したと記載されている。"
  error_codes: []
  cause: "一次リストは、コンタクタのサージ抑制用ダイオードで整流特性が失われていたと説明する。制御カードへの影響があると判断し、サージ電圧によるカード故障を推定しているが、因果関係は独立確認されていない。"
  verified_actions: []
  outcome: "WOS治具の交換では解消せず、配線・絶縁の確認では問題なしとの報告。制御カードを交換したところ正常動作となったとの記載がある。各確認・交換・結果は一次リスト上の報告で、独立確認されていない。"
---

# WOS運転不能とサージ抑制用ダイオード不良の報告（ID180）

## 症状と対象

首都工・不具合情報共有リストID180は、対象範囲を「全エレ機種」と記載する。モーター空回し後にWOS運転を試みたところ、上・下方向とも動かず、コンタクタが一時的に動作した後に落ち、制御カードの表示が消灯したとの報告である。対象機種への現行適用は確認していない。

## 調査経過と原因説明

一次リストでは、WOS治具を交換しても解消せず、配線・絶縁の確認では問題がなかったと記録されている。その後、コンタクタに接続されたサージ抑制用ダイオードの整流特性が失われていたと説明する。確認方法や端子・部品の識別情報は記録しない。

リストは制御カードにも影響が及んだと判断してカードを交換し、正常動作となったと報告する。サージ電圧がカード故障を引き起こしたとの説明は推定であり、損傷原因・交換後の継続動作は独立確認していない。

## 適用上の注意

本記録は一事例の調査結果と報告を整理したもので、電気測定、コンタクタ/ダイオードの選定・接続、カード交換、WOS運転の手順ではない。端子・配線・部品記号、測定方法、仮設置換、運転・復旧操作は転載していない。実機への適用は、承認済みの機種別資料と所管技術者の確認を要する。

ID101のMELDバッテリー極性誤接続による別回路のダイオード損傷とは、対象回路・原因説明・症状が異なる。ID64のコンタクタ吸引条件の一般説明も、本件の原因を裏付けるものではない。

## 出典

- 首都工・不具合情報共有リスト.xlsx、ID180（sheet1 row244）。
- 個人名、現場名、端子/配線/部品の識別、具体的な測定・交換・運転手順は転載していない。