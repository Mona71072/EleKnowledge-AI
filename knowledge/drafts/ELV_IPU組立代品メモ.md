---
schema_version: 1
record_id: "elv-ipu-assembly-substitution"
record_version: 2
title: "AXIEZ-LINKs IPU組立代品に関する原文記録"
category: "不具合対応(ELV)"
record_type: "troubleshooting_case"
product: "エレベーター"
model_type:
  - "AXIEZ-LINKs"
document_number: ""
revision: ""
effective_date: ""
review_status: "in_review"
publication_status: "not_published"
classification: "unknown"
cloud_approval: "not_reviewed"
keywords:
  - "IPU組立"
  - "DCL"
  - "代品"
source_path: "不具合対応【ELV】/部品交換/IPU組立.md"
source_filename: "IPU組立.md"
onenote_id: "a8c15103-95f4-4d08-897a-403d412bffb5:138"
related_ids: []
attachment_paths: []
reference_links: []
document_references:
  - document_number: "P-6-S900.01"
    title: "原文参照資料"
    locator: "9/N"
    source_path: ""
  - document_number: "P-6-S900.01-B"
    title: "協力会社展開用Excelの参照資料"
    locator: "9/N。P-6-S900.01との同一性、本文、改訂、適用範囲は未確認"
    source_path: ""
evidence_sources:
  - source_id: "evidence-elv-ipu-original"
    source_type: "vault_original"
    title: "IPU組立（原文）"
    source_path: "不具合対応【ELV】/部品交換/IPU組立.md"
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-01"
    supports:
      - "IPU組立の代品型式・DCL有無に関する原文記録"
  - source_id: "evidence-list-elv-ipu-substitute-353"
    source_type: "user_provided_extract"
    title: "協力会社展開用Excel: IPU組立代品の仕様照会（ID353）"
    source_path: ""
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-13"
    supports:
      - "物流登録品と現地適用仕様の差、DCL有無に応じた代替条件があるとの記載"
structured_data:
  equipment: "AXIEZ-LINKs IPU組立"
  source_notes:
    - "原文とExcel ID353は、代替品の適用可否がDCL有無等の仕様条件に依存することを示す。個別型式、部品番号、ハーネス変更方法は本記録に転載しない。"
    - "Excelは物流登録品の範囲に言及するが、現行在庫・部品表・設計承認・対象機への適用は未確認。"
    - "原文参照P-6-S900.01とExcel記載P-6-S900.01-Bは表記が異なる。同一文書・同一改訂とは確認していない。"
    - "M1カード不良による急停止の共有リスト項目もあるが、本文未確認。"
    - "原文は互換表画像1点を参照する。過去の内容確認記録ではDCL区分と一部端子順の注意が記録されているが、2026-10-07時点で指定パスに画像実体がなく再検証できない。"
---

# AXIEZ-LINKs IPU組立代品に関する原文記録

## 原文記載

原文は、AXIEZ-LINKsのIPU組立代品について、DCL有無などの仕様条件によって適用可否が異なることを記載する。代替可否、具体的な機種・部品番号、ハーネス変更条件は本記録に転載しない。

協力会社展開用ExcelのリストID353も、物流登録品と現地適用仕様の差、およびDCL有無に応じた代替条件を説明している。これは原文とは別の出典である。候補部品や対応方法の最新性・適用可否は独立確認していない。

## 添付互換表の注意

過去の確認記録では、添付互換表にDCL区分と接続条件の注意があったとされる。ただし、2026-10-07時点で画像実体を確認できず、内容を再検証できない。対象機に適用する承認済み最新版で照合する。

## 概略確認フロー（交換手順ではない）

現品のIPU型式・DCL仕様・適用機種を確認し、承認済み互換表で代品候補と端子順を照合する。ハーネス条件を含め不明点があれば交換を進めず、設計担当に確認する。原文参照のP-6-S900.01本文・改訂は未確認。

## 適用上の注意

部品の適用、仕様変更、代替可否は承認済み最新版の部品表・設計資料・機体仕様で確認すること。この記録を手配・交換・配線変更の指示として使用しない。P-6-S900.01とP-6-S900.01-Bの同一性は未確認。

## 出典

- 原文ノート: [[不具合対応【ELV】/部品交換/IPU組立]]
- 原文は添付画像1点を参照するが、2026-10-07時点で指定パスに実ファイルを確認できず、過去の内容確認記録を再検証できない。
- P-6-S900.01本文・改訂は未確認。