---
schema_version: 1
record_id: "knowhow-elv-long-period-vibration-jumper-id416"
list_item_id: "416"
record_version: 1
title: "長周期振動感知器の短絡ジャンパとBSER/BSER-CP"
category: "不具合対応(ELV)"
record_type: "knowhow"
product: "エレベーター"
model_type:
  - "VFGH"
document_number: ""
revision: ""
effective_date: ""
review_status: "in_review"
publication_status: "not_published"
classification: "unknown"
cloud_approval: "not_reviewed"
keywords:
  - "長周期振動感知器"
  - "短絡ジャンパ"
  - "BSER"
  - "BSER-CP"
related_ids: []
source_path: ""
source_filename: ""
onenote_id: ""
attachment_paths: []
reference_links: []
document_references:
  - document_number: "C-6-R56.1"
    title: "短絡箇所参照（リスト記載）"
    locator: "本文未確認"
    source_path: ""
  - document_number: "S-1-Z06.1"
    title: "BSER/BSER-CP適用条件（リスト記載）"
    locator: "本文未確認"
    source_path: ""
evidence_sources:
  - source_id: "evidence-list-long-period-vibration-jumper-id416"
    source_type: "lists_csv_snapshot"
    title: "首都工・不具合情報共有リスト: 長周期振動感知器の短絡ジャンパについて"
    source_path: ""
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-19"
    supports:
      - "短絡ジャンパ外れ、旧BSERのみ時代は外す運用、2024年4月以降原則BSER-CPでジャンパ付けたまま、C-6-R56.1/S-1-Z06.1参照、LV2まで自動復帰・スローリセット必要"
structured_data:
  equipment: "VFGH（リスト）"
  symptom: "短絡ジャンパが外れた状態であった、との報告。"
  cause: "付加動作がBSERのみだった時代の認識のまま対応し、2024年4月以降のBSER-CP仕様と合わなかった、とリスト説明。"
  verified_actions:
    - "短絡ジャンパを正規位置に復旧"
  outcome: "リスト上は復旧完了・対応不要。"
---

# 長周期振動感知器の短絡ジャンパとBSER/BSER-CP

共有リスト上の記録 は、長周期振動感知器の短絡ジャンパが外れていた事象を、付加動作仕様の世代差（BSER → 原則 BSER-CP）と結び付けて説明する。

## リスト上の要点

- 以前は付加動作 BSER のみの仕様で、ジャンパを外す運用だった、とリスト。
- 2024年4月以降は原則 BSER-CP のため、**短絡ジャンパは付けたまま**が正しい、とリスト。
- 短絡箇所は C-6-R56.1、BSER/BSER-CP 適用条件は S-1-Z06.1 を参照、とリスト。
- ジャンパ付け状態で長周期 LV2 まで自動復帰する仕様で、**スローリセットが必要**、とリスト Notes。

## 未確認事項

- C-6-R56.1 / S-1-Z06.1 / D-C-844.1 の現行版と該当節
- 対象号機の付加動作設定の実測

本記録は作業前確認の索引であり、設定変更手順の正本ではない。
