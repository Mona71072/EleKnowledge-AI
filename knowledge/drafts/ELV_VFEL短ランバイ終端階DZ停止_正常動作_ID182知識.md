---
schema_version: 1
record_id: "elv-vfel-short-runby-terminal-dz-stop-id182"
record_version: 1
title: "VFELの短ランバイ適用時における終端階DZ停止の報告（ID182）"
category: "不具合対応(ELV)"
record_type: "knowhow"
product: "エレベーター"
model_type: ["VFEL"]
document_number: ""
revision: ""
effective_date: ""
review_status: "in_review"
publication_status: "not_published"
classification: "unknown"
cloud_approval: "not_reviewed"
keywords:
  - "VFEL"
  - "短ランバイ"
  - "終端階"
  - "DZ停止"
source_path: "首都工・不具合情報共有リスト.xlsx"
source_filename: "首都工・不具合情報共有リスト.xlsx"
onenote_id: ""
related_ids:
  - "elv-fms-terminal-floor-limit"
attachment_paths: []
reference_links: []
document_references: []
evidence_sources:
  - source_id: "evidence-list-elv-vfel-short-runby-terminal-dz-stop-182"
    source_type: "vault_original"
    title: "首都工・不具合情報共有リスト: 手動運転で終端階走行時、DZプレートにてかごが停止する件（ID182）"
    source_path: "首都工・不具合情報共有リスト.xlsx"
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-14"
    supports:
      - "VFELで短ランバイ条件時に終端階の手動走行がDZプレート位置で停止するとの報告"
      - "一次リストが当該停止を正常動作と説明し、独立自動運転は問題ないと報告したこと"
      - "現行仕様・機種適用・現場での独立確認が未確認であること"
structured_data:
  knowledge_items:
    - topic: "VFEL短ランバイ条件時の終端階DZ停止"
      statement: "一次リストID182は、VFELの短ランバイ条件では終端階からの手動走行がDZプレート位置で停止することを正常動作と説明する。独立自動運転は問題ないとの報告もある。"
      conditions:
        - "対象は一次リストの機種欄にVFELと記載された一事例。物件や機種群への一般適用は未確認。"
        - "短ランバイ条件に関する説明は一次リスト記載であり、現行の設計仕様と独立照合していない。"
      exceptions:
        - "具体的な運転方向、DZプレートの状態変更、速度値、制御設定、試験方法は記録しない。"
        - "既存のVFGH向け短ランバイ終端階知識とは機種条件が異なる。条件や数値を相互に流用しない。"
      rationale: "原リストが正常動作と説明する終端階停止を、不具合と即断せず、対象設備の承認済み仕様で確認するため。"
      verification_status: "source_recorded"
      evidence_source_ids:
        - "evidence-list-elv-vfel-short-runby-terminal-dz-stop-182"
  source_notes:
    - "原リストは停止位置の確認のため速度設定を変更する方法も記載するが、本記録には設定値・操作・DZプレート変更を含めない。現行承認と安全性は未確認。"
---

# VFELの短ランバイ適用時における終端階DZ停止の報告（ID182）

首都工・不具合情報共有リストID182は、VFELの短ランバイ条件における終端階の手動走行がDZプレート位置で停止することを正常動作と説明する。独立自動運転は問題ないとの報告がある。原因説明、対象設備の適用、現行仕様は独立確認していない。

この記録は一事例の出典要約であり、運転・検査・調整の指示ではない。DZプレートを外す、制限を超えて走行させる、速度や制御設定を変更する方法は記録しない。対象設備の責任者が承認済みの現行仕様で確認する。

既存の[[ELV_FMS終端階制限]]はVFGH向けの別記録である。短ランバイの一般題材が共通しても、機種条件や記載値を本件へ適用しない。

## 出典

- 首都工・不具合情報共有リスト.xlsx、ID182（sheet1 row242）。
- 具体的な速度値、プレート状態、走行操作、測定/調整方法は転載していない。