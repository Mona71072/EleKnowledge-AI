---
schema_version: 1
record_id: "nexway-vfgh-control-panel-quality-check-english-notes"
record_version: 2
title: "NEXWAY（CM-MAのVFGH）制御盤のCAN接続・バックアップ電源要約"
category: "NEXWAY(VFGH)：　Quality Check"
record_type: "technical_reference"
product: "CM-MA"
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
  - "VFGH"
  - "CM-MA"
  - "NEXWAY"
  - "CAN Link Adapter"
  - "終端抵抗"
  - "P1基板"
  - "バックアップコイン電池"
  - "磁極学習"
source_path: "NEXWAY(VFGH)：　Quality Check/Machine Room/Control Panel/Connector - CAN Link Adapter.md"
source_filename: "Connector - CAN Link Adapter.md"
onenote_id: "4fd4eb57-ccb4-42ad-8733-37598686fd63:181"
related_ids: []
attachment_paths: []
reference_links: []
document_references: []
evidence_sources:
  - source_id: "evidence-nexway-vfgh-can-link-adapter-181"
    source_type: "vault_original"
    title: "Connector - CAN Link Adapter"
    source_path: "NEXWAY(VFGH)：　Quality Check/Machine Room/Control Panel/Connector - CAN Link Adapter.md"
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-14"
    supports:
      - "コネクタ/配線のチェック項目とCAN Link Box/終端抵抗の説明"
      - "終端不備による信号反射/リンギングと通信異常の説明"
  - source_id: "evidence-nexway-vfgh-control-panel-battery-177"
    source_type: "vault_original"
    title: "Battery Power Supply (Control Panel)"
    source_path: "NEXWAY(VFGH)：　Quality Check/Machine Room/Control Panel/Battery Power Supply (Control Panel).md"
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-14"
    supports:
      - "P1基板コイン電池とRAM/ROMデータ保持に関する原文説明"
      - "磁極学習未学習エラー94Dの事例、原因説明、原文記載の対策"
  - source_id: "evidence-user-product-series-nexway-cm-ma-vfgh"
    source_type: "user_provided_extract"
    title: "ユーザー指定の製品系列対応: NEXWAY VFGHとCM-MA"
    source_path: ""
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-14"
    supports:
      - "本VaultではNEXWAYのVFGH資料をCM-MAのVFGHとして記録する"
structured_data:
  source_notes:
    - "英語記述を含む2ページを日本語で要約。原ノート/画像は変更していない。"
    - "NEXWAYのVFGH資料をCM-MAのVFGHとして記録するとのユーザー指定を反映。原ノートの製品名・パスは維持し、この分類ラベルを他の仕様の根拠にしない。"
    - "CAN終端や信号反射の説明は原文記載。現行機器構成・終端抵抗の仕様/設置位置は別途確認していない。"
    - "コイン電池・磁極学習の事例/対策は出典上の記載。エラー定義、因果関係、対象ソフト/機種への適用、現行性は未確認で、操作指示にしない。"
    - "参照画像2点は内容未確認。画像から部品位置/仕様を補っていない。"
  terminology:
    - source_term: "NEXWAY（VFGH）"
      normalized_term: "CM-MA（VFGH）"
      term_type: "other"
      context: "ユーザー指定による本Vaultの製品系列分類・検索対応。原資料の名称・パスは保持する。"
      verification_status: "verified"
      evidence_source_id: "evidence-user-product-series-nexway-cm-ma-vfgh"
---

# NEXWAY（CM-MAのVFGH）制御盤のCAN接続・バックアップ電源要約

## 概要

NEXWAY品質確認フォルダーのVFGH資料2ページを、日本語で要約した。分類上はCM-MAのVFGHとして記録する。CAN Link Adapterの説明と、P1基板のバックアップコイン電池に関するチェック項目/不具合事例を扱う。原文記載の説明・対策は未検証であり、承認済みの検査・作業手順ではない。

## CAN Link Adapter

原ノートは、コネクタの差込状態にピン抜け/浮きがないこと、配線損傷や過度な力がないことをチェック項目としている。また、CAN Link Box（BUC/BIC）を、CANケーブルの分岐・中継を行い終端抵抗を備える配線基板と説明する。

同ノートの説明では、CAN通信線の両端に終端抵抗がないと信号反射が起き、波形の乱れやリンギングが通信エラー/誤動作につながる可能性がある。抵抗値、接続箇所の特定、配線変更方法は本記録に含めない。現行の承認済み図面・要領で機器構成を確認すること。

## P1基板バックアップコイン電池

原ノートは、P1基板のコイン電池が未装着の場合、電源遮断時にRAM上のデータがROMへ書き込まれないと説明する。付属の事例では、磁極学習データがRAMにのみ残り、長時間の停電後に失われたことで磁極学習未完了となり、エラーコード「94D」が表示されて低速運転できなくなったと報告している。また、事象が遅れて発生する場合があるとの注記がある。

原文はコイン電池装着と磁極学習に関する対策を記載するが、原因説明・エラー定義・対策の適用条件/実施結果・現行性は独立確認していない。ここでは確認手順や学習操作を再掲せず、実作業には対象設備の承認済み最新版を使用する。

## 画像・確認状態

両ノートに画像参照があるが、画像内容は未確認。コネクタ構成、部品位置、現行適用、制御ソフト版は未確認。

## 出典

- [[NEXWAY(VFGH)：　Quality Check/Machine Room/Control Panel/Connector - CAN Link Adapter]]（OneNote ID `4fd4eb57-ccb4-42ad-8733-37598686fd63:181`）
- [[NEXWAY(VFGH)：　Quality Check/Machine Room/Control Panel/Battery Power Supply (Control Panel)]]（OneNote ID `4fd4eb57-ccb4-42ad-8733-37598686fd63:177`）