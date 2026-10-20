---
schema_version: 1
record_id: "elv-battery-issues-reference"
record_version: 2
title: "バッテリー関連不具合・接続点検資料の参照記録"
category: "不具合対応(ELV)"
record_type: "catalog"
product: "エレベーター"
model_type:
  - "VFGLF"
  - "VFGLB"
  - "VFGH"
document_number: "C-7-F2900.1-J; C-7-C3300.1-J; C-7-C3600-J; C-7-C3900-J（原文記載）"
revision: ""
effective_date: ""
review_status: "in_review"
publication_status: "not_published"
classification: "unknown"
cloud_approval: "not_reviewed"
keywords:
  - "バッテリー"
  - "MELD"
  - "B48V"
  - "バッテリー接続点検"
source_path: "不具合対応【ELV】/現象（不具合対応）/バッテリー（不具合対応）.md"
source_filename: "バッテリー（不具合対応）.md"
onenote_id: "a8c15103-95f4-4d08-897a-403d412bffb5:148"
related_ids:
  - "elv-meld-operation-reference"
  - "case-elv-vfglb-low-battery-meld-failure-entrapment-id174"
attachment_paths:
  - "不具合対応【ELV】/現象（不具合対応）/OneNote/バッテリー（不具合対応） image.png"
  - "不具合対応【ELV】/現象（不具合対応）/OneNote/バッテリー（不具合対応） image 1.png"
  - "不具合対応【ELV】/現象（不具合対応）/OneNote/バッテリー（不具合対応） image 2.png"
  - "不具合対応【ELV】/現象（不具合対応）/OneNote/バッテリー（不具合対応） image 3.png"
reference_links: []
document_references:
  - document_number: "C-7-F2900.1-J"
    title: "VFGH関連資料"
    locator: ""
    source_path: ""
  - document_number: "C-7-C3300.1-J"
    title: "VFGLB関連資料"
    locator: ""
    source_path: ""
  - document_number: "C-7-C3600-J"
    title: "VFGLB（機械室あり）関連資料"
    locator: ""
    source_path: ""
  - document_number: "C-7-C3900-J"
    title: "VFGLF関連資料"
    locator: ""
    source_path: ""
evidence_sources:
  - source_id: "evidence-elv-battery-issues"
    source_type: "vault_original"
    title: "バッテリー（不具合対応）（原文）"
    source_path: "不具合対応【ELV】/現象（不具合対応）/バッテリー（不具合対応）.md"
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-01"
    supports:
      - "低電圧・バックアップ動作の事例タイトルと機種別接続点検資料の参照"
  - source_id: "evidence-list-elv-vfglb-low-battery-meld-entrapment-id174"
    source_type: "vault_original"
    title: "首都工・不具合情報共有リスト: VFGLBのバッテリー低電圧によるMELD移行不成立・閉じ込め（ID174）"
    source_path: "首都工・不具合情報共有リスト.xlsx"
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-14"
    supports:
      - "低電圧でMELDへ移行せず閉じ込めとなったとの個別報告"
      - "対応欄「対応不要」と、解消・機能確認が不明であること"
structured_data:
  source_notes:
    - "原文は低電圧時のバックアップ動作、バッテリー用途、誤接続による損傷の事例タイトルを含む。ID174の低電圧・MELD移行不成立・閉じ込め報告を個別記録へ接続したが、解消・機能確認は未確認。"
    - "接続確認機能の条件・表示・警報・電源動作は機種やソフトウェア版に依存する。画像記載を現行機能として保証しない。"
    - "接続点検図は画像4点を目視確認済み。具体的な電圧、時間、設定、操作・復帰条件は転載しない。参照PDFの改訂は未確認。"
---

# バッテリー関連不具合・接続点検資料の参照記録

原文は、低電圧時のバックアップ動作、バックアップ用バッテリーの用途、誤接続による機器損傷に関する共有事例を挙げ、機種別のバッテリー接続点検資料を参照している。添付図にはモデルやソフトウェア版で異なる点検・表示・警報の条件が記載されている。

この記録は過去事例と資料の検索用であり、バッテリー接続、充電・放電、MELD動作、警報解除や復帰を判断する手順・基準ではない。条件は対象機種・ソフトウェア版に適用する現行の承認済み資料と専門担当者に確認する。

一次リストID174は、VFGLBでバッテリー低電圧によりMELDへ移行せず閉じ込めとなったと報告する。対応欄は「対応不要」だが、閉じ込め解消・バッテリー状態の是正・MELD機能の復旧確認は不明。詳細は[[ELV_VFGLB低電圧_MELD移行不成立_閉じ込め_ID174事例]]を参照。電圧値・測定/交換/救出手順は転載しない。

## 出典

- 原文ノート: [[不具合対応【ELV】/現象（不具合対応）/バッテリー（不具合対応）]]
- 添付画像4点は目視確認済み。参照C資料本文・改訂、共有事例の個別本文は未確認。