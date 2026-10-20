---
schema_version: 1
record_id: "case-elv-gs3-board-part-number-setting-scu20-communication-id422"
record_version: 1
title: "群管理盤GS3基板の構成不一致によるSCU-20通信不成立（ID422）"
category: "不具合対応(ELV)"
record_type: "troubleshooting_case"
product: "エレベーター群管理"
model_type: []
document_number: "C-7-C3343.1-J"
revision: ""
effective_date: ""
review_status: "in_review"
publication_status: "not_published"
classification: "unknown"
cloud_approval: "not_reviewed"
keywords:
  - "群管理"
  - "GS3基板"
  - "SCU-20"
  - "品番指定"
  - "通信不成立"
source_path: ""
source_filename: "技術情報リスト（協力会社展開用）.xlsx"
onenote_id: ""
related_ids:
  - "elv-group-operation-issues"
attachment_paths: []
reference_links: []
document_references:
  - document_number: "C-7-C3343.1-J"
    title: "群管理盤関連資料"
    locator: "Excel記載の参照資料。本文・改訂・適用範囲未確認"
    source_path: ""
evidence_sources:
  - source_id: "evidence-list-elv-gs3-scu20-communication-422"
    source_type: "user_provided_extract"
    title: "協力会社展開用Excel: GS3基板の品番設定不一致によるSCU-20通信不成立（ID422）"
    source_path: ""
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-13"
    supports:
      - "群管理盤とSCU-20の通信不成立、基板品番指定と構成の不一致、是正後に通信状態が良好となったとの報告"
structured_data:
  equipment: "群管理盤（GS3基板）とSCU-20"
  symptom: "高層バンクとSCU-20との通信確立ができなかったとの報告。"
  investigation:
    - "当初の基板設定確認・変更後も通信は回復しなかったと記載。"
    - "通信線の導通確認では問題がなかったとの報告。"
    - "他バンクとの比較および品目表確認で、基板の品番指定と構成が一致していなかったと記載。品番・スイッチ・ジャンパの具体情報は記録しない。"
  cause_assessment: "原リストは、設計段階の基板品番指定誤りを原因としている。設計資料や現行品目表を用いた独立確認はない。"
  reported_response: "原リストは、群管理通信に適合する基板構成へ是正後、通信状態が良好となったと報告する。具体的な設定位置・ジャンパ操作は記録しない。"
  outcome: "是正後に通信状態が良好となったとの出典報告。運用継続、再発有無、設計是正完了は未確認。"
  limitations:
    - "カード品番、ロータリースイッチ位置、ジャンパ位置、端子・通信線識別、設定変更手順は転載しない。"
    - "C-7-C3343.1-Jと品目表の本文、改訂、現行適用は未確認。"
    - "本記録から群管理盤の設定変更・通信試験を実施しない。"
---

# 群管理盤GS3基板の構成不一致によるSCU-20通信不成立（ID422）

## 症状と調査

首都工・不具合情報共有リストID422は、群管理盤とSCU-20との通信が確立しなかったと報告する。原リストは参照資料に基づく設定確認・変更後も通信が回復せず、通信線の導通確認では問題がなかったとしている。

他バンクとの比較と品目表の確認により、基板品番指定と実際の構成に不一致があったと記載されている。カード品番、ロータリースイッチ位置、ジャンパ位置、端子・通信線識別などの再現可能な情報は転記しない。

## 原因説明と結果

原リストは設計段階の基板品番指定誤りを原因として挙げる。設計資料・現行品目表による独立確認は行っていない。群管理通信に適合する基板構成へ是正後、通信状態が良好となったとの報告があるが、運用継続、再発有無、設計是正完了は未確認である。

参照資料C-7-C3343.1-Jの本文・改訂・適用範囲も未確認。本記録は事例参照用であり、群管理盤の設定変更や通信試験の手順として使用しない。