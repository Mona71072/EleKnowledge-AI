---
schema_version: 1
record_id: "case-elv-vfglf-meld-connector-omission-id132"
record_version: 1
title: "VFGLFのコネクタ差し忘れによるMELD不動作報告（ID132）"
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
  - "MELD"
  - "コネクタ差し忘れ"
  - "不動作"
source_path: "首都工・不具合情報共有リスト.xlsx"
source_filename: "首都工・不具合情報共有リスト.xlsx"
onenote_id: ""
related_ids:
  - "elv-meld-operation-reference"
attachment_paths: []
reference_links: []
document_references: []
evidence_sources:
  - source_id: "evidence-list-elv-vfglf-meld-connector-omission-id132"
    source_type: "vault_original"
    title: "首都工・不具合情報共有リスト: コネクタ差し忘れによるMELD不動作（ID132）"
    source_path: "首都工・不具合情報共有リスト.xlsx"
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-14"
    supports:
      - "VFGLFでコネクタ差し忘れにより、客先ブレーカー遮断時にMELDが実動作しないとの原因/症状報告"
      - "対応欄は完了表示だが、是正内容・復旧結果・独立確認は未確認"
structured_data:
  equipment: "VFGLFのMELD"
  symptom: "客先ブレーカー遮断時にMELDが実動作しなかったとの報告。"
  error_codes: []
  cause: "一次リストはコネクタ差し忘れを原因として説明する。原因の技術的妥当性は独立確認していない。"
  verified_actions: []
  outcome: "対応欄は完了表示だが、是正内容、実施状況、MELD機能の復旧・独立確認は記載から確認できない。"
---

# VFGLFのコネクタ差し忘れによるMELD不動作報告（ID132）

## 報告内容

首都工・不具合情報共有リストID132は、VFGLFでコネクタ差し忘れにより、客先ブレーカー遮断時にMELDが実動作しない事象を報告し、コネクタ差し忘れを原因として挙げている。原因と機能説明は一次資料上の報告であり、独立検証していない。

## 対応状況と確認限界

対応欄は完了表示だが、具体的な是正内容・実施状況、MELD復旧、復旧後の独立確認は確認できない。対応欄の表示を安全な復旧や現行機能の確認と解釈しない。

本記録は一事例の報告であり、MELDの接続・試験・運転・救出手順ではない。コネクタ識別、ピン/端子/線番、回路・配線、リセット操作、ブレーカー操作、試験条件は記録しない。MELD機能および作業の安全性は、対象機の承認済み現行資料と所管者の確認を要する。

## 類似報告との区別

[[ELV_VFGLF_M14コネクタ誤配線_ID429事例]]はM14コネクタのピンアサイン誤りに関する別報告であり、本件の差し忘れと混同しない。[[ELV_VFGLB低電圧_MELD移行不成立_閉じ込め_ID174事例]]はVFGLBの低電圧に関する別事例であり、本件の原因・対策・復旧根拠に流用しない。

## 出典

- 首都工・不具合情報共有リスト.xlsx、ID132（sheet1 row290）。
- コネクタ/電気回路の詳細、リセット/試験/運転/救出手順、個人/現場情報は転載していない。