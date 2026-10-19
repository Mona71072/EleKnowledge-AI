---
schema_version: 1
record_id: "elv-km-ld-regenerative-converter-not-operating-control-power-id80"
record_version: 1
title: "KM-LDの回生コンバーター運転不能と制御電源未投入報告（ID80）"
category: "不具合対応(ELV)"
record_type: "troubleshooting_case"
product: "エレベーター"
model_type:
  - "KM-LD"
document_number: ""
revision: ""
effective_date: ""
review_status: "in_review"
publication_status: "not_published"
classification: "unknown"
cloud_approval: "not_reviewed"
keywords:
  - "回生コンバーター"
  - "WOS"
  - "低速運転"
  - "制御電源"
  - "ハードウェアエラー"
related_ids:
  - "elv-km-ld-regenerative-converter-run-phase-order-case"
source_path: ""
source_filename: "技術情報リスト（協力会社展開用）.xlsx"
onenote_id: ""
attachment_paths: []
reference_links: []
document_references:
  - document_number: "YE310C814"
    title: "PT.14（原リスト参照。本文・適用性未確認）"
    locator: "原リストの調査欄に記載。回路・ピンアサイン等は転載しない。"
    source_path: ""
evidence_sources:
  - source_id: "evidence-list-km-ld-regenerative-converter-control-power-080"
    source_type: "user_provided_extract"
    title: "首都工・不具合情報共有リスト: CCP未投入により回生コンバーターによる運転ができない件（ID80）"
    source_path: ""
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-09"
    supports:
      - "KM-LDの回生コンバーター使用時と非使用時のWOS低速運転可否・速度条件、盤内制御電源状態との原因説明、投入後の運転可能報告および資料改定依頼予定"
structured_data:
  equipment: "KM-LD"
  symptom: "WOS開始時、回生コンバーターを使用した場合は15 m/minで運転できず、使用しない場合は8 m/minで運転できたとの報告。速度は当該記録条件であり、推奨値や試験条件ではない。"
  error_codes: []
  cause: "原リストは、制御盤内の回生コンバーター関連制御電源が投入されていなかったことを原因としている。コネクタ接続、電圧、カード表示等の調査記録もあるが、個別の端子・配線・測定・RSW情報は転載しない。原因の独立確認はしていない。"
  verified_actions: []
  outcome: "原リストは、該当する制御電源を投入した後、回生コンバーターを使用して運転可能となったと報告する。必要性が資料に記載されていないとの指摘があり、連絡メモでの協力会社展開と資料改定依頼を行う予定と記録する。改定依頼の実施・完了は確認できず、運転結果も原文上の報告で独立確認していない。"
---

# KM-LDの回生コンバーター運転不能と制御電源未投入報告（ID80）

首都工・不具合情報共有リストID80は、共有日欄を2021-12-20（Excel値44550の換算）とするKM-LDの報告で、WOS開始時に回生コンバーターを使用すると15 m/minで運転できず、使用しない場合は8 m/minで運転できたと記録する。これらは当該事例の記録値で、推奨速度や試験条件ではない。

## 調査経過と原因報告

原リストにはコネクタ接続、電圧、制御盤から回生コンバーターまでの接続、カード表示に関する調査記録がある。具体的な端子・配線・電圧・コネクタ・RSW設定や確認方法は転載しない。原リストは、制御盤内の回生コンバーター関連制御電源が投入されていなかったことを原因とする。

## 対応結果と残件

原リストは、該当する制御電源を投入した後に回生コンバーターを使用して運転可能となったと報告する。また、この投入要件が資料に記載されていないとの指摘と、連絡メモでの協力会社展開・資料改定依頼の予定を記録する。改定依頼が実施・完了したかは未確認。

## 関連事例

[[ELV_KM-LD回生コンバーター運転不能_事例記録]]（ID54）も同じKM-LD・WOS・回生コンバーター使用時の低速運転不能を扱うが、ID54は客先電源の相順を原因とする別報告。本件とは原因説明が異なり、同一案件や共通の是正方法とは扱わない。電気作業・遮断器操作・運転復旧の手順ではない。