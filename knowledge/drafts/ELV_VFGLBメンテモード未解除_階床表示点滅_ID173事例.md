---
schema_version: 1
record_id: "case-elv-vfglb-maintenance-mode-floor-indicator-blink-id173"
record_version: 1
title: "VFGLBのメンテモード未解除による階床表示点滅報告（ID173）"
category: "不具合対応(ELV)"
record_type: "troubleshooting_case"
product: "エレベーター"
model_type:
  - "VFGLB"
document_number: ""
revision: ""
effective_date: ""
review_status: "in_review"
publication_status: "not_published"
classification: "unknown"
cloud_approval: "not_reviewed"
keywords:
  - "VFGLB"
  - "保守点検機能"
  - "メンテモード"
  - "階床表示"
  - "液晶インジ"
  - "点滅"
source_path: "首都工・不具合情報共有リスト.xlsx"
source_filename: "首都工・不具合情報共有リスト.xlsx"
onenote_id: ""
related_ids: []
attachment_paths: []
reference_links: []
document_references: []
evidence_sources:
  - source_id: "evidence-list-elv-vfglb-maintenance-mode-display-blink-id173"
    source_type: "vault_original"
    title: "首都工・不具合情報共有リスト: 保守点検機能未解除による階床表示点滅（ID173）"
    source_path: "首都工・不具合情報共有リスト.xlsx"
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-14"
    supports:
      - "VFGLBでメンテモード未解除により階床表示が点滅したとの報告"
      - "対応欄が対応済みであること。運転再開・安全確認の独立確認を示さない"
  - source_id: "evidence-vault-elv-post-handover-maintenance-mode-note"
    source_type: "vault_original"
    title: "引渡し後の物件に関する現場対応時の注意点"
    source_path: "工技業務（現場系）１/現場対応時の注意点/引渡し後の物件.md"
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-14"
    supports:
      - "同じ階床表示点滅の事象を記載し、ID173の情報共有リストを参照していること"
      - "既存ページに解除操作や機能動作に関する記載があるが、本記録では手順として転載しないこと"
structured_data:
  equipment: "VFGLBの保守点検機能表示"
  symptom: "保守点検機能（メンテモード）が未解除となり、かご内正操作盤の階床表示が点滅したとの報告。"
  error_codes: []
  cause: "一次リストはメンテモードの解除忘れを原因として示す。個別設備の状態や原因の独立確認は未確認。"
  verified_actions: []
  outcome: "原リストの対応欄は対応済みだが、解除状態、運転再開、安全機能の状態に関する独立確認は確認できない。"
---

# VFGLBのメンテモード未解除による階床表示点滅報告（ID173）

## 症状と原因説明

首都工・不具合情報共有リストID173は、VFGLBで保守点検機能（メンテモード）が未解除となり、かご内正操作盤の階床表示が点滅したと報告する。原リストの原因説明を個別事例として保持し、モード遷移の操作方法や個別設備の状態を一般化しない。

## 対応状況と確認限界

原リストの対応欄は対応済みだが、解除状態、運転再開、安全機能の状態に関する独立確認は確認できない。対応済み表示だけで運転可能・安全確認済みとは判断しない。

既存の引渡し後注意ページは同じ症状とID173への参照を含むが、操作手順は本記録へ転載しない。本記録はモード切替・解除、運転確認、官検の手順や判断基準ではない。適用時は承認済みの現行要領と所管技術者の確認を要する。外部URL、表示設定、解除操作、運転手順は記録していない。

## 出典

- 首都工・不具合情報共有リスト.xlsx、ID173（sheet1 row251）。
- [[工技業務（現場系）１/現場対応時の注意点/引渡し後の物件]]。