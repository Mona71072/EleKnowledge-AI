---
schema_version: 1
record_id: "case-elv-e-can-special-operation-hall-call-failure-id171"
record_version: 1
title: "E-CAN通信異常に伴う特殊運転時の乗場呼び切放し不作動報告（ID171）"
category: "不具合対応【ELV】"
record_type: "troubleshooting_case"
product: "エレベーター群管理"
model_type: []
document_number: ""
revision: ""
effective_date: ""
review_status: "in_review"
publication_status: "not_published"
classification: "unknown"
cloud_approval: "not_reviewed"
keywords:
  - "E-CAN"
  - "群管理"
  - "特殊運転"
  - "乗場呼び"
  - "通信異常"
source_path: "首都工・不具合情報共有リスト.xlsx"
source_filename: "首都工・不具合情報共有リスト.xlsx"
onenote_id: ""
related_ids:
  - "elv-group-operation-issues"
  - "elv-group-control-error-codes"
attachment_paths: []
reference_links: []
document_references:
  - document_number: "C-8-S438.1"
    title: "群管理盤エラー確認資料（ID171の参考資料表記）"
    locator: "p.22の参照記載。本文・版未確認"
    source_path: ""
  - document_number: ""
    title: "群管理盤・GCカード上でのエラー読み取り方"
    locator: "ID171の備考が添付を参照。添付実体・本文未確認"
    source_path: ""
evidence_sources:
  - source_id: "evidence-list-elv-e-can-special-operation-hall-call-failure-171"
    source_type: "vault_original"
    title: "首都工・不具合情報共有リスト: E-CAN通信不良によるNS動作しない件（ID171）"
    source_path: "首都工・不具合情報共有リスト.xlsx"
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-14"
    supports:
      - "特殊運転時に乗場呼び切放しが動作しなかった症状と調査経過"
      - "E-CAN通信異常と接続不良を原因とする原リスト説明、復旧後の動作報告"
      - "新AXIEZ・3Car・SAI-22との記載、およびC-8-S438.1の参照"
structured_data:
  equipment: "群管理盤、E-CAN通信、特殊運転時の乗場呼び切放し機能"
  symptom: "新AXIEZ・3Car・SAI-22との原記載がある構成の1台で、特殊運転にしても乗場呼びが切り放されなかったと報告される。構成の一般適用範囲は未確認。"
  error_codes: []
  cause: "E-CAN通信線の接続不良が原因との一次リスト記載。接続箇所の識別情報は記録せず、原因を独立確認していない。"
  verified_actions: []
  outcome: "一次リストは接続復旧後に所定の乗場呼び切放し動作を確認したと報告する。独立確認・継続確認はしていない。"
---

# E-CAN通信異常に伴う特殊運転時の乗場呼び切放し不作動報告（ID171）

## 事象

首都工・不具合情報共有リストID171は、新AXIEZ・3Car・SAI-22との記載がある構成の1台で、特殊運転にしても乗場呼びが切り放されなかった事例を報告する。調整時には動作を確認したとの補足がある一方、官検時は未確認だったとしており、設備構成への一般適用は未確認。

## 調査経過と結果

原リストによれば、初期の切り分けではカードリーダー側要因を除いても解消せず、特殊運転信号の結線は良好と判断された。その後、群管理盤の診断でE-CAN系の通信異常が示され、接続調査で一方の接続不良が見つかったと説明される。接続を復旧した後、乗場呼び切放しが所定どおり動作したとの報告がある。確認手順、表示値、接続箇所、操作順序は記録していない。

原リストは、官検等でカバーを開閉した際に接続が外れた可能性を挙げるが、これは推定であり、発生時点・原因は独立確認されていない。また、絶縁抵抗試験時の接続状態に関する注意も記載するが、適用根拠・現行性は未確認であり、承認済み試験要領の代替にはならない。

## 参照資料と制限

参考資料はC-8-S438.1、p.22と記載され、群管理盤・GCカード上のエラー読み取り方を示す添付にも言及する。本文・版・添付実体は未確認。既存の群管理エラー参照記録が挙げるC-8-S438.1-Jとの同一性は確認できていない。

エラー表示値、カード/コネクタ/接続位置の識別情報、電気計測・配線・復旧操作、現場・号機・担当者情報は記録しない。本記録を診断、接続作業、絶縁抵抗試験、運転・検査判断に使用しない。