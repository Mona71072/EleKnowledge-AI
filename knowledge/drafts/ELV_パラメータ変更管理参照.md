---
schema_version: 1
record_id: "elv-parameter-change-management"
record_version: 2
title: "パラメータ変更ノートの管理・参照記録"
category: "不具合対応(ELV)"
record_type: "procedure"
knowledge_domain: "engineering_business"
organizational_scope: "unknown"
product: "エレベーター"
model_type: []
document_number: "C-8-S451-J; C-8-S436.1-J（原文記載）"
revision: ""
effective_date: ""
review_status: "in_review"
publication_status: "not_published"
classification: "unknown"
cloud_approval: "not_reviewed"
keywords:
  - "パラメータ変更"
  - "S/W変更連絡シート"
  - "EPITS"
  - "不干渉時間"
  - "予約タイマー"
source_path: "不具合対応【ELV】/メンテコン/パラメータ書換.md"
source_filename: "パラメータ書換.md"
onenote_id: "a8c15103-95f4-4d08-897a-403d412bffb5:116"
related_ids:
  - "elv-vfgr-parameter-change"
  - "elv-epits-sw-acquisition"
  - "list-id292-reservation-timer-parameter-change"
reference_links: []
document_references:
  - document_number: "C-8-S451-J"
    title: "LINKs各台管理パラメータ調整"
    locator: "原文は全機種と注記"
    source_path: ""
  - document_number: "C-8-S436.1-J"
    title: "群管理据付調整資料 パラメータ調整"
    locator: ""
    source_path: ""
evidence_sources:
  - source_id: "evidence-elv-parameter-change-management"
    source_type: "vault_original"
    title: "パラメータ書換（原文）"
    source_path: "不具合対応【ELV】/メンテコン/パラメータ書換.md"
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-01"
    supports:
      - "変更後の連絡票発行と参照要領に関する原文記載"
  - source_id: "evidence-list-elv-reservation-timer-parameter-change-292"
    source_type: "user_provided_extract"
    title: "協力会社展開用Excel: メンテコン無しで予約タイマーを設定する方法（ID292）"
    source_path: ""
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-13"
    supports:
      - "メンテコン不調時の代替パラメータ変更案内と内部資料参照があるとの原リスト記載"
structured_data:
  source_notes:
    - "原文はパラメータ変更とS/W変更連絡シートの関係を記載し、書換手順の項目5は未記入。操作手順として再構成しない。"
    - "協力会社検印の要否に関する記述は社内運用として現行性未確認。"
    - "別ノートの連絡シート実体・アクセス権と参照PDF本文は未確認。"
    - "Excel ID292はメンテコン不調時の代替パラメータ変更を案内するが、具体操作/対象値/内部資料識別は非転載。原リストの記載、参照先の本文/版/適用性、代替方法の承認状況は未確認。"
---

# パラメータ変更ノートの管理・参照記録

原文は、施主要望や特殊工事で仕様の一部を変更する場面、S/W変更連絡シートの発行、C-8-S451-JおよびC-8-S436.1-Jへの参照を記載している。書換手順の項目5は未記入である。

協力会社展開用リストID292は、メンテコン不調時の代替パラメータ変更と内部資料参照を案内している。具体操作、対象値、参照資料の識別、本文/版/適用性および代替方法の承認状況は未確認のため記載しない。

本記録は変更管理上の参照で、パラメータ設定・書換手順ではない。変更要求、承認、対象機・指定値、現地とEPITSのソフト版、バックアップ/復旧、変更記録の発行要件を現行の社内ルールで確認すること。

## 出典

- 原文ノート: [[不具合対応【ELV】/メンテコン/パラメータ書換]]
- 連絡シートおよび参照PDFの本文・版は未確認。社内URLは複写していない。
