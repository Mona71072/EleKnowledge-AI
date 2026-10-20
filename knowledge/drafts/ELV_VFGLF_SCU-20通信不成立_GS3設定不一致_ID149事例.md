---
schema_version: 1
record_id: "case-elv-vfglf-scu20-gs3-setting-mismatch-id149"
record_version: 1
title: "VFGLFのSCU-20通信不成立とGS3設定不一致の報告（ID149）"
category: "不具合対応(ELV)"
record_type: "troubleshooting_case"
product: "エレベーター"
model_type:
  - "VFGLF"
document_number: ""
revision: ""
effective_date: ""
review_status: "in_review"
publication_status: "not_published"
classification: "unknown"
cloud_approval: "not_reviewed"
keywords:
  - "VFGLF"
  - "SCU-20"
  - "GS3基板"
  - "群管理通信"
  - "設定不一致"
source_path: "首都工・不具合情報共有リスト.xlsx"
source_filename: "首都工・不具合情報共有リスト.xlsx"
onenote_id: ""
related_ids:
  - "case-elv-gs3-board-part-number-setting-scu20-communication-id422"
attachment_paths: []
reference_links: []
document_references:
  - document_number: "C-7-C3343.1-J"
    title: "C資料（原リスト記載のトラブル対応資料）"
    locator: "トラブル時の対応方法。P43の連絡用情報も原リストが参照。本文・版・現行適用は未確認。"
    source_path: ""
evidence_sources:
  - source_id: "evidence-list-elv-vfglf-scu20-gs3-setting-mismatch-149"
    source_type: "vault_original"
    title: "首都工・不具合情報共有リスト: エレベーターとSCU-20盤との通信ができない件（ID149）"
    source_path: "首都工・不具合情報共有リスト.xlsx"
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-14"
    supports:
      - "VFGLFのエレベーターとSCU-20盤の通信不成立および調査経過"
      - "品目表の基板品番表記と実際の設定との不一致、変更後に通信状態が良好となったとの報告"
      - "参照資料・現行設定・変更後動作が独立確認されていないこと"
structured_data:
  equipment: "VFGLFのエレベーターとSCU-20盤"
  symptom: "業者とのエレコール対抗試験時に通信が動作せず、エレベーターとSCU-20盤の通信不成立が判明したとの報告。"
  error_codes: []
  cause: "一次リストは、品目表に記載されたGS3基板の品番表記と、設定要領図に基づく正規品番との不一致を原因として説明する。現地設定と原リストが正規設定とする値にも差があったと記載し、変更後に通信状態が良好となったと報告する。設定値、基板品番、変更操作、参照資料の現行性・機種適用は確認されていない。"
  verified_actions: []
  outcome: "C資料のトラブルシュートフローに沿って調査し、エレベーター側とI/O盤の結線・導通は問題なし、連絡用情報の照会先からも問題ない旨の回答があったと報告されている。品目表の記載差を受けた設定変更後、通信状態が良好となったとの記録。調査・変更・結果はいずれも独立確認されていない。"
---

# VFGLFのSCU-20通信不成立とGS3設定不一致の報告（ID149）

## 症状と調査

首都工・不具合情報共有リストID149は、VFGLFで業者とのエレコール対抗試験を行った際に通信が動作せず、エレベーターとSCU-20盤との通信不成立が判明したと報告する。C資料のトラブル対応方法に沿った調査では、エレベーター側とI/O盤の結線・導通確認に問題はなく、C資料の連絡用情報を用いた照会先からも問題ない旨の回答があったと記載されている。C資料の本文・版は確認していない。

## 原因説明と対応報告

電気設計への確認により、品目表のGS3基板品番表記が正規品番と異なり、基板の現地設定も原リストが正規設定とする値に一致していなかったことが原因として記載されている。具体的な品番・設定値は転載しない。設定変更後に通信状態が良好となったとの報告があるが、原因・設定の適用・対応後の状態は独立確認していない。

## 関連事例と適用上の注意

[[ELV_GS3品番設定不一致_SCU-20通信不成立_ID422事例]]もGS3基板とSCU-20の通信不成立報告だが、対象基板の品番不一致の内容が異なる別事例である。設定値・品番・処置を相互に流用しない。

本記録は出典上の一事例であり、群管理盤の設定変更や通信試験の手順・判断基準ではない。品番・設定値・設定位置、端子/配線識別、結線・導通確認方法、設定変更操作は転載していない。C-7-C3343.1-Jと品目表の版・本文・現行適用、変更後通信の独立確認は未完了である。

## 出典

- 首都工・不具合情報共有リスト.xlsx、ID149（sheet1 row273）。
- C-7-C3343.1-Jは原リストが参照する資料として記録。本文・版は未確認で、内容の根拠には使用していない。