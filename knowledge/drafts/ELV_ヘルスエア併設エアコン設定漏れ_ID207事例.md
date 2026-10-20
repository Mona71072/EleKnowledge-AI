---
schema_version: 1
record_id: "case-elv-health-air-aircon-configuration-omission-id207"
record_version: 1
title: "ヘルスエア併設エアコンの設定漏れによる起動不良報告（ID207）"
category: "不具合対応【ELV】"
record_type: "troubleshooting_case"
product: "ヘルスエア併設エアコン"
model_type:
  - "全エレ機種（一次リスト記載。適用範囲未確認）"
document_number: ""
revision: ""
effective_date: ""
review_status: "in_review"
publication_status: "not_published"
classification: "unknown"
cloud_approval: "not_reviewed"
keywords:
  - "ヘルスエア"
  - "併設エアコン"
  - "設定漏れ"
  - "起動不良"
source_path: "首都工・不具合情報共有リスト.xlsx"
source_filename: "首都工・不具合情報共有リスト.xlsx"
onenote_id: ""
related_ids:
  - "catalog-elv-health-air-reference"
attachment_paths: []
reference_links: []
document_references:
  - document_number: "C-30-G5.3"
    title: "三菱エレベーター専用エアコン（MEA-20B-MI2）設定方法"
    locator: "ID207の備考が設定方法の記載先として参照。本文・版未確認"
    source_path: ""
evidence_sources:
  - source_id: "evidence-list-elv-health-air-aircon-configuration-omission-207"
    source_type: "vault_original"
    title: "首都工・不具合情報共有リスト: ヘルスエアー併設エアコン適用時の設定方法について（ID207）"
    source_path: "首都工・不具合情報共有リスト.xlsx"
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-14"
    supports:
      - "設定漏れによるヘルスエア起動不良、併設エアコンの動作状況、出力に関する原リスト記載"
      - "全エレ機種との原リスト記載、24/08B以降に関する注記、参照資料番号C-30-G5.3"
structured_data:
  equipment: "ヘルスエア併設エアコン"
  symptom: "設定漏れによりヘルスエアが起動しない。原リストは、併設エアコン自体は運転してもMF1コネクタから200 Vが出力されない状態を説明する。"
  error_codes: []
  cause: "据付時に必要とされる基板設定の漏れが原因との原リスト記載。独立確認していない。"
  verified_actions: []
  outcome: "設定漏れに関する事象の記載はあるが、是正実施・復旧確認・再発状況の記載なし。"
  limitations:
    - "具体的なディップスイッチ識別・ON/OFF位置・設定操作は転載しない。"
    - "「全エレ機種」との対象範囲、24/08B以降の注記の意味、現行設定、原因・結果は独立確認していない。"
    - "C-30-G5.3の本文・版・MEA-20B-MI2との対応・現行適用は未確認。"
    - "本記録を設定・結線・電気作業・故障判定の手順として使用しない。"
---

# ヘルスエア併設エアコンの設定漏れによる起動不良報告（ID207）

## 事象

首都工・不具合情報共有リストID207は、ヘルスエア併設エアコンの適用現場で設定漏れがあり、ヘルスエアが起動しなかったと報告する。リストの説明では、併設エアコンが運転していても、設定が漏れるとMF1コネクタから200 Vが出力されず、ヘルスエアが起動しないという。

## 原リストの注記

リストは対象を「全エレ機種」と記載し、「工場設定に変更（24/08B~）」との注記および調整時の確認依頼を含む。この注記の具体的な意味、対象機種・製造時期、現行仕様への適用は未確認であり、確定した変更履歴や設定指示として扱わない。具体的な基板設定識別子と操作位置は記録しない。

## 参照資料と未確認事項

備考にC-30-G5.3「三菱エレベーター専用エアコン（MEA-20B-MI2）」の設定方法が参照されている。資料本文・版・機種対応は未確認。原リストには是正実施、復旧確認、再発状況の記載がないため、本記録を設定・結線・電気作業・故障判定の手順として使用しない。

関連するヘルスエアの他事例・構造変更資料への参照は[[ELV_ヘルスエア_参照記録]]を参照。関連付けは内容の裏付けを意味しない。