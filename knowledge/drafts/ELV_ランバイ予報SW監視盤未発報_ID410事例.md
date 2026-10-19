---
schema_version: 1
record_id: "elv-runby-forecast-switch-monitoring-not-reported-id410"
record_version: 1
title: "ランバイ予報SWの監視盤未発報事例（ID410）"
category: "不具合対応(ELV)"
record_type: "troubleshooting_case"
product: "エレベーター"
model_type:
  - "VFGH"
document_number: ""
revision: ""
effective_date: ""
review_status: "in_review"
publication_status: "not_published"
classification: "unknown"
cloud_approval: "not_reviewed"
keywords:
  - "ランバイ予報SW"
  - "監視盤"
  - "発報先"
  - "遠隔保守装置"
source_path: ""
source_filename: "技術情報リスト（協力会社展開用）.xlsx"
onenote_id: ""
related_ids: []
attachment_paths: []
reference_links: []
document_references: []
evidence_sources:
  - source_id: "evidence-list-elv-runby-forecast-monitoring-output-410"
    source_type: "user_provided_extract"
    title: "協力会社展開用Excel: ランバイ予報SWの監視盤未発報（ID410）"
    source_path: ""
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-13"
    supports:
      - "監視盤にランバイ予報SWが発報しない状態と、通知先設定に関する説明"
structured_data:
  equipment: "エレベーター（VFGH）と監視盤・遠隔保守装置"
  symptom: "ランバイ予報SWの動作が監視盤へ通知されず、監視盤側の表示灯・ブザーも作動しない場合があるとの報告。"
  source_explanation: "原リストは、ランバイ予報SWの通知先が監視盤または保守側装置となり、保守側装置が通知先の場合は監視盤へ発報しないと説明する。これは出典上の記載であり、対象設備の現行設定や設計仕様は未確認。"
  cause_assessment: "通知先の設定が保守側となっていることが監視盤未発報の要因になり得るとの説明。個別設備での設定状態、設定変更履歴、現行仕様は独立確認していない。"
  outcome: "設定確認・変更後の試験結果や対象設備の復旧状況は記載から確認できない。"
  limitations:
    - "設定アドレス、設定値、メンテナンスコンソール操作、通知先変更手順は転載しない。"
    - "ランバイ予報SWの適用条件、監視盤・遠隔保守装置の仕様、現行設定は未確認。"
    - "現場・建物・担当者情報は記録しない。"
---

# ランバイ予報SWの監視盤未発報事例（ID410）

首都工・不具合情報共有リストID410は、VFGHでランバイ予報SWの動作が監視盤へ発報されず、監視盤の表示灯・ブザーも作動しない場合があると報告する。

原リストは、通知先を監視盤または保守側装置に設定でき、保守側装置が通知先の場合は監視盤へ発報しないと説明する。また、遠隔保守装置を取り付ける工程で通知先が保守側へ変更されることがあると記載している。これらは原リスト上の説明であり、個別設備の現行設定、設計意図、適用条件は未確認である。

設定確認・変更後の試験結果や復旧状況は記録されていない。設定アドレス・値、メンテナンスコンソール操作、通知先変更の手順は本記録に含めない。監視・警報の設計と個別設定は承認済みの現行資料および所管担当で確認する。