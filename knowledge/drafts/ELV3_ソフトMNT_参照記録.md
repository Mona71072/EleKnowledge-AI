---
schema_version: 1
record_id: "catalog-elv3-soft-maintenance-mode-reference"
record_version: 3
title: "ソフトMNTの発報リスクと前提条件"
category: "技術メモ【ELV】３"
record_type: "technical_reference"
product: "エレベーター"
model_type: []
document_number: ""
revision: ""
effective_date: ""
review_status: "in_review"
publication_status: "not_published"
classification: "unknown"
cloud_approval: "not_reviewed"
keywords: ["ソフトMNT", "安全回路", "保守モード"]
source_path: "技術メモ【ELV】３/モード/ソフトMNTの設定方法.md"
source_filename: "ソフトMNTの設定方法.md"
onenote_id: "51232edc-3051-4d66-b01e-2e33ee73bc9c:1"
related_ids:
  - "catalog-field-work-1-post-handover-maintenance-reference"
attachment_paths: []
reference_links: []
document_references:
  - document_number: ""
    title: "ソフトMNTの設定方法"
    locator: "SharePoint技術情報リストID 170。リンク先未閲覧"
    source_path: ""
evidence_sources:
  - source_id: "evidence-elv3-soft-mnt-001"
    source_type: "vault_original"
    title: "ソフトMNTの設定方法"
    source_path: "技術メモ【ELV】３/モード/ソフトMNTの設定方法.md"
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-09"
    supports: ["引渡し後の是正作業における安全回路遮断時の外部発報可能性、保守合理化S/W要件の記載"]
  - source_id: "evidence-list-elv-soft-mnt-alarm-risk-170"
    source_type: "vault_original"
    title: "首都工・不具合情報共有リスト: ソフトMNTの設定方法（ID170）"
    source_path: "首都工・不具合情報共有リスト.xlsx"
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-14"
    supports:
      - "MRLでのソフトMNT前提と、保守合理化ソフトウェアがある場合のR/M戻し忘れ機能に関する記載"
      - "MNT経過時間・運転モード条件と監視盤発報機能の関係、および発報は別の要因がある場合との注記"
structured_data:
  safety_warnings:
    - "原文は、引渡し後/保守開始後の是正時にP1基板トグルスイッチがR/M状態で安全回路（#29）を遮断すると、仕様によって外部発報する可能性があると記載。発報の有無は物件仕様に依存し、本記録では特定できない。"
    - "警報盤が警備会社と連携する場合、警備員の臨場や対応費用が発生する可能性があると原文に記載。事前連絡に関する案内はあるが、本記録は連絡手順や連絡先を示さない。"
    - "対象機種、保守契約、警報連携、現行安全手順を所管者に確認するまで、安全回路操作や保守モード変更の判断に使用しない。"
  source_notes:
    - "原文は保守合理化S/WのインストールをソフトMNT機能の前提として記載し、かご内からブロックサインでMNT状態へ移行可能と説明。現行適用は未確認。"
    - "具体的なブロックサイン投入操作、解除操作、表示/ブザー手順、警備会社名や連絡先情報は転載していない。"
    - "一次リストID170はMRLを対象として、保守合理化ソフトウェアがある場合のR/M戻し忘れ機能と、MNT経過後に監視盤発報機能が有効になる条件を説明する。具体的な時間値・モード条件・タイマーリセット操作は転載せず、現行仕様として確認していない。"
---

# ソフトMNTの発報リスクと前提条件

## 原文記載の発報リスク

引渡し後（保守開始後）の是正作業で保守担当者が立ち会わない場合があると原文は説明する。P1基板トグルスイッチがR/M状態で安全回路（#29）を遮断した場合、仕様によっては外部発報する可能性がある。

警報盤が警備会社と連携している場合は警備員が臨場し、対応費用が発生する可能性もあると原文に記載。発報の有無や連携状態は物件仕様に依存し、本記録では確定できない。

## ソフトMNTに関する前提

原文は保守合理化S/Wのインストールを前提として挙げ、かご内からブロックサインでMNT状態へ移行できると説明する。具体的な投入・解除操作や表示手順は転載していない。現行の機種適用性も未確認。

## R/M戻し忘れ機能に関する別出典（リストID170）

一次リストID170はMRLを対象に、保守合理化ソフトウェアがある場合、MNT状態が一定時間続くとR/M戻し忘れ機能が働き、監視盤の発報機能が有効になると説明する。同リストは、状態移行だけで発報するのではなく、別の発報要因がある場合に警報となる旨も明記する。条件の正確性、時間値、機種・物件への適用、現行仕様は未確認。

具体的なMNT投入/解除、モード切替、電源操作、タイマーリセットの手順と時間値は記録しない。対象機種・物件仕様・警報連携と承認済み現行手順を所管者に確認するまで、状態判断や作業に使用しない。

対象機種、保守契約、警報連携、現行安全手順を所管者に確認し、必要な承認を得るまで、安全回路操作・運転モード変更・作業開始判断に使用しない。

出典: `技術メモ【ELV】３/モード/ソフトMNTの設定方法.md`（OneNote ID `51232edc-3051-4d66-b01e-2e33ee73bc9c:1`）。本文確認日: 2026-10-09。
