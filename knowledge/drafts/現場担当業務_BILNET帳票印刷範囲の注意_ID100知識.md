---
schema_version: 1
record_id: "work-bilnet-template-print-area-note-id100"
record_version: 1
title: "BILNET帳票の印刷範囲に関する注意（ID100）"
category: "現場担当業務"
record_type: "knowhow"
product: "BILNET"
model_type: []
document_number: ""
revision: ""
effective_date: ""
review_status: "unreviewed"
publication_status: "not_published"
classification: "unknown"
cloud_approval: "not_reviewed"
keywords:
  - "BILNET"
  - "帳票"
  - "雛形"
  - "印刷範囲"
source_path: ""
source_filename: "技術情報リスト（協力会社展開用）.xlsx"
onenote_id: ""
related_ids: []
attachment_paths: []
reference_links: []
document_references: []
evidence_sources:
  - source_id: "evidence-list-knowledge-id100"
    source_type: "user_provided_extract"
    title: "首都工・不具合情報共有リスト Excel出力 ID100"
    source_path: ""
    s3_uri: ""
    revision: "原本リスト未照合"
    accessed_at: "2026-10-09"
    supports:
      - "BILNET出力が複数ページに分かれる場合の雛形印刷範囲設定に関する原文記載"
structured_data:
  knowledge_items:
    - topic: "帳票の印刷範囲"
      statement: "原リストは、BILNETから帳票を印刷した際に1ページに収まらない場合、該当する雛形の印刷範囲設定を変更するよう案内している。"
      conditions:
        - "BILNET出力が1ページに収まらない場合という原文記載。"
        - "どの雛形を使うかは出力する帳票の種類による。"
      exceptions: []
      rationale: "帳票内容が複数ページに分かれる場合の印刷範囲調整について、原リストが案内している。"
      verification_status: "source_recorded"
      evidence_source_ids:
        - "evidence-list-knowledge-id100"
---

# BILNET帳票の印刷範囲に関する注意（ID100）

## 概要

首都工・不具合情報共有リストID100は、BILNETから帳票を印刷した際に1ページに収まらない場合の、雛形の印刷範囲設定に関する案内を記載する。共有日は2022-03-03、現象区分は「豆知識」。

## 原文記載

原リストは、印刷結果が1ページに収まらない場合、該当する雛形の印刷範囲設定を変更するよう案内している。対象として複数種の不発関連帳票、工事完了検査成績表、品目表、手配依頼書、エスカレーター安全対策品の帳票を列挙する。

## 適用・情報管理上の注意

原リストにある内部保存先と雛形ファイル識別子はここへ複写していない。現行のBILNET構成、承認済み帳票、印刷設定の操作方法、帳票内容の保持・改ページ要件は未確認である。正式帳票を扱う際は、所管の現行手順と対象帳票を確認し、この記録だけを根拠に雛形を変更しない。

## 出典・確認状態

- 出典: Excel出力のID100行にあるA列・E〜N列・O列。B/C/D列は参照していない。
- 元Microsoft Lists項目、BILNETの現行仕様、雛形の実体、印刷結果と改ページ要件、設定変更の承認者は未確認。
- 内部保存先・雛形ファイル名/識別子および具体的な変更手順は転載していない。
- 本記録は未レビューであり、現行の帳票作成・印刷手順や帳票内容の変更を承認するものではない。
