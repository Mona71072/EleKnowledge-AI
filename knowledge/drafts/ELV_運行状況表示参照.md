---
schema_version: 1
record_id: "elv-operation-status-display"
record_version: 1
title: "運行状況表示画面の参照記録"
category: "不具合対応(ELV)"
record_type: "catalog"
product: "エレベーター"
model_type: []
document_number: ""
revision: ""
effective_date: ""
review_status: "in_review"
publication_status: "not_published"
classification: "unknown"
cloud_approval: "not_reviewed"
keywords:
  - "運行状況表示"
  - "メンテコン"
  - "画面参照"
source_path: "不具合対応【ELV】/メンテコン/運行状況表示.md"
source_filename: "運行状況表示.md"
onenote_id: "a8c15103-95f4-4d08-897a-403d412bffb5:104"
related_ids: []
attachment_paths:
  - "不具合対応【ELV】/メンテコン/OneNote/運行状況表示 image.png"
  - "不具合対応【ELV】/メンテコン/OneNote/運行状況表示 image 1.png"
  - "不具合対応【ELV】/メンテコン/OneNote/運行状況表示 image 2.png"
  - "不具合対応【ELV】/メンテコン/OneNote/運行状況表示 image 3.png"
  - "不具合対応【ELV】/メンテコン/OneNote/運行状況表示 image 4.png"
  - "不具合対応【ELV】/メンテコン/OneNote/運行状況表示 image 5.png"
  - "不具合対応【ELV】/メンテコン/OneNote/運行状況表示 image 6.png"
  - "不具合対応【ELV】/メンテコン/OneNote/運行状況表示 image 7.png"
  - "不具合対応【ELV】/メンテコン/OneNote/運行状況表示 image 8.png"
  - "不具合対応【ELV】/メンテコン/OneNote/運行状況表示 image 9.png"
reference_links: []
document_references: []
evidence_sources:
  - source_id: "evidence-elv-operation-status-display"
    source_type: "vault_original"
    title: "運行状況表示（原文）"
    source_path: "不具合対応【ELV】/メンテコン/運行状況表示.md"
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-01"
    supports:
      - "運行状況表示に関する画面画像が添付されていること"
  - source_id: "evidence-elv-operation-status-event"
    source_type: "vault_original"
    title: "故障時運行状況の画面説明"
    source_path: "不具合対応【ELV】/メンテコン/OneNote/運行状況表示 image 1.png"
    s3_uri: ""
    revision: "図版記載: 2005-12-26"
    accessed_at: "2026-10-04"
    supports:
      - "故障時の運行状況画面が数値データと接点データを時系列で表示すること"
      - "画面表示項目の区分と故障時刻・検出内容の表示例"
  - source_id: "evidence-elv-operation-status-latch"
    source_type: "vault_original"
    title: "状態表示の検出状態説明"
    source_path: "不具合対応【ELV】/メンテコン/OneNote/運行状況表示 image 3.png"
    s3_uri: ""
    revision: "図版記載: 2005-12-26"
    accessed_at: "2026-10-04"
    supports:
      - "リアルタイム状態とラッチ状態の説明"
  - source_id: "evidence-elv-operation-status-undefined"
    source_type: "vault_original"
    title: "状態表示の未定義信号に関する注記"
    source_path: "不具合対応【ELV】/メンテコン/OneNote/運行状況表示 image 4.png"
    s3_uri: ""
    revision: "図版記載: 2005-12-26"
    accessed_at: "2026-10-04"
    supports:
      - "未定義表示は、エリアが確保されていて信号が定義されていない個所を示すという注記"
  - source_id: "evidence-elv-operation-status-door-history"
    source_type: "vault_original"
    title: "ドア異常時動作履歴の画面説明"
    source_path: "不具合対応【ELV】/メンテコン/OneNote/運行状況表示 image 9.png"
    s3_uri: ""
    revision: "図版記載: 2008-03-28"
    accessed_at: "2026-10-04"
    supports:
      - "ドア異常時動作履歴のグラフ構成と最新2レコード表示という図版説明"
structured_data:
  source_notes:
    - "原文ノート本文はなく、添付図版10点を内容確認した。画面説明には2005〜2008年の記載があり、現行機能・適用機種・判定条件は確認していない。"
    - "図版は故障時の時系列、現在の検出状態、ドア異常時の動作履歴を区別している。各画面の実装有無や表示項目は機種・S/Wにより異なる可能性がある。"
    - "画面上のサンプル異常、信号値、時刻、ボタン配置は一般仕様や診断基準ではないため転載していない。"
---

# 運行状況表示画面の参照記録

原文ノートに説明本文はなく、以下は添付図版の説明から確認できた範囲をまとめたもの。画面の記載は2005〜2008年の資料で、現行機能や機種適用性を示すものではない。

## 画面の用途

- **故障時運行状況**: 故障時刻・検出内容に加え、運行の数値データと主要接点の状態を時系列で表示する。図版では今回（最新）または前回の故障データを選択する例が示されている。
- **状態表示**: 制御・駆動、ドア、各台管理、群管理など、S/Wごとの検出状態を表示する。図版の「リアルタイム」は現在の検出状態、「ラッチ」は前回CPUリセット後から現在までに検出した状態を示す。
- **ドア異常時動作履歴**: ドア異常発生時の動作履歴をグラフ表示する。図版には最新2レコードを表示する例があるが、現行の記録件数とは確認していない。

## 概略フロー（作業手順ではない）

確認したい時点と対象機を明確にし、故障時の記録・現在の検出状態・ドア異常時履歴のうち目的に合う情報を選ぶ。表示項目の意味と時点を確認し、対象機の適用資料と照合する。異常の有無を画面例だけで判断せず、詳細な操作・判定は適用確認済みの資料に従う。

## 読み取り上の注意

図版には「未定義」と表示される箇所について、エリアは確保されているが信号が定義されていない個所との注記がある。「未定義」を異常検出や故障判定と読み替えない。

画面が空欄であることや表示項目がないことだけで、設備全体に異常がないとは判断できない。図版のサンプル値・信号名・異常表示は個別例であり、合否基準や診断基準として転用しない。

## 添付図版

添付画像10点は、メニューと故障時表示、状態表示、異常詳細、ドア異常時履歴の旧画面例で構成される。操作手順、例示信号値、画面上の色・配置は転載せず、必要な画面詳細は原図で確認する。

## 出典

- 原文ノート: [[不具合対応【ELV】/メンテコン/運行状況表示]]
- 添付画像10点: 実在と内容を確認。画面用途と明記された注意のみを反映し、旧画面のサンプル値や操作手順は一般化していない。