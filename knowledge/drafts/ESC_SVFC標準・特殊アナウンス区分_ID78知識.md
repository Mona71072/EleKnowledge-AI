---
schema_version: 1
record_id: "esc-svfc-standard-special-announcement-id78"
record_version: 1
title: "SVFC制御エスカレーターの標準・特殊アナウンス区分（ID78）"
category: "エスカ機種一覧"
record_type: "knowhow"
product: "エスカレーター"
model_type:
  - "SVFC（原リストの対象。個別制御構成への適用は未確認。）"
document_number: "C-60-631-VF35.1（原リスト記載。本文・版未確認。）"
revision: ""
effective_date: ""
review_status: "in_review"
publication_status: "not_published"
classification: "unknown"
cloud_approval: "not_reviewed"
keywords:
  - "SVFC"
  - "アナウンス"
  - "標準メッセージ"
  - "特殊メッセージ"
  - "音声案内"
related_ids:
  - "catalog-esc-auto-announcement-image-review-hold"
source_path: ""
source_filename: "技術情報リスト（協力会社展開用）.xlsx"
onenote_id: ""
attachment_paths: []
reference_links: []
document_references:
  - document_number: "C-60-631-VF35.1"
    title: "原リストが参照するSVFC関連資料"
    locator: "P5～P9。本文・版・適用範囲は未確認。"
    source_path: ""
evidence_sources:
  - source_id: "evidence-list-svfc-announcement-standard-special-078"
    source_type: "user_provided_extract"
    title: "首都工・不具合情報共有リスト: 【SVFC制御】エスカレーター標準アナウンスの変更について（ID78）"
    source_path: ""
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-09"
    supports:
      - "SVFC制御時の標準/特殊メッセージ区分に関する原文説明、RSW設定方法に関する参照案内"
structured_data:
  knowledge_items:
    - topic: "標準アナウンスと特殊アナウンスの区分"
      statement: "原リストは、参照資料P5表4に記載された内容のみを話すものを標準メッセージ、それ以外の内容をアナウンスするものを特殊メッセージと説明する。"
      conditions:
        - "SVFC制御の場合として紹介された原リスト上の説明。対象機種・制御構成への適用は未確認。"
      exceptions: []
      rationale: "原リストが示す区分説明。参照資料本文との照合は未実施。"
      verification_status: "source_recorded"
      evidence_source_ids:
        - "evidence-list-svfc-announcement-standard-special-078"
---

# SVFC制御エスカレーターの標準・特殊アナウンス区分（ID78）

首都工・不具合情報共有リストID78は、共有日欄を2021-12-20（Excel値44550の換算）とする「豆知識」で、SVFC制御の標準アナウンス変更に関する説明を記録する。

## 原リストの説明

原リストは、参照資料P5表4に記載された内容のみを話すものを標準メッセージ、それ以外の内容をアナウンスするものを特殊メッセージと説明する。対象資料としてC-60-631-VF35.1のP5～P9を挙げるが、資料本文・版・適用条件は未確認。

## 未確認事項と利用上の注意

原リストは、機種によって上位/下位設定に使うRSW値が異なるだけとして他機種にも参考適用するよう述べるが、この一般化は独立確認していない。RSW値の算出・設定方法、メッセージ選択値、未確認の添付Excelは本記録に転載していない。アナウンス設定や運転変更の手順・根拠として使用せず、対象機の承認済み現行資料と所管担当者に照合する。

[[ESC_オートアナウンス画像レビュー保留]]は別原資料の画像レビュー記録であり、画像内容が未確認のため本記録の区分説明を裏付けるものではない。