---
schema_version: 1
record_id: "elv-7seg-led-status"
record_version: 3
title: "エレベーター7SEG・発光ダイオード状態表示の参照"
category: "不具合対応(ELV)"
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
keywords:
  - "7SEG"
  - "発光ダイオード"
  - "DCV"
  - "インバーター"
source_path: "不具合対応【ELV】/エラー/エラー確認時のポイント/７SEG表示、発光ダイオード機能.md"
source_filename: "７SEG表示、発光ダイオード機能.md"
onenote_id: "a8c15103-95f4-4d08-897a-403d412bffb5:124"
related_ids:
  - "elv-error-check-points"
attachment_paths:
attachment_paths: []
reference_links: []
document_references: []
evidence_sources:
  - source_id: "evidence-elv-7seg-led-original"
    source_type: "vault_original"
    title: "7SEG表示、発光ダイオード機能（原文）"
    source_path: "不具合対応【ELV】/エラー/エラー確認時のポイント/７SEG表示、発光ダイオード機能.md"
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-01"
    supports:
      - "表示資料の存在およびDCVに関する原文警告"
  - source_id: "evidence-elv-7seg-led-table"
    source_type: "vault_original"
    title: "基板別LED表示一覧図"
    source_path: "不具合対応【ELV】/エラー/エラー確認時のポイント/OneNote/７SEG表示、発光ダイオード機能 image.png"
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-04"
    supports:
      - "DCV、WDT、DZ等のLED機能が基板型式ごとに掲載されていること"
  - source_id: "evidence-elv-7seg-display-map"
    source_type: "vault_original"
    title: "7SEG運転状態表示例"
    source_path: "不具合対応【ELV】/エラー/エラー確認時のポイント/OneNote/７SEG表示、発光ダイオード機能 image 1.png"
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-04"
    supports:
      - "MON設定と7SEG表示に応じた運転状態・階床表示の図示例"
      - "表示表は特定基板に関する例で、他機種への適用を保証しない"
  - source_id: "evidence-elv-7seg-flashing-example"
    source_type: "vault_original"
    title: "7SEG点滅検出の注記"
    source_path: "不具合対応【ELV】/エラー/エラー確認時のポイント/OneNote/７SEG表示、発光ダイオード機能 image 2.png"
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-04"
    supports:
      - "CFOの点滅とC1基板7SEGの点滅についての図版注記。現行判定基準は未確認"
structured_data:
  safety_warnings:
    - "原文はDCV表示消灯後もインバーター主回路に触れないこと、回路に触れる場合は直流電圧を測定して放電を確認する旨を記載。"
  source_notes:
    - "原文は添付画像3点を参照している。過去の内容確認記録では基板別LED・7SEG表示例を含むが、2026-10-07時点で指定パスに画像実体がなく再検証できない。"
    - "原文は添付画像3点を参照している。過去の確認記録には基板別LED・7SEG表示例の内容記録がある。2026-10-09の指定フォルダー・カテゴリ共通OneNoteフォルダー・添付画像フォルダー・Vault画像名検索では該当ファイルを確認できず、現在の再照合はできないためattachment_pathsには登録しない。"
    - "図版にはCFOの点滅とC1基板7SEG表示の点滅に関する注記があるが、現行機種の診断基準・対象範囲は未確認。"
---

# エレベーター7SEG・発光ダイオード状態表示の参照

## 原文にある注意

原文は発光ダイオード・エレベーター状態表示の画像を参照している。また、DCV表示が消灯してもインバーター主回路に触れないこと、回路に触れる場合は電解コンデンサ端子電圧を測定して放電を確認することを警告している。原文には消灯まで時間がかかる旨もある。

## 表示図から確認できる範囲

添付表は基板型式別にLED名と機能を示す。例としてDCVは主回路コンデンサの充電検出、WDTはウォッチドッグタイマー、DZはドアゾーンに関する表示として説明されている。7SEGはMON設定や運転状態に応じて階床・状態を示し、図版には特定表示の点滅に関する例もある。表示の意味は基板型式と設定に対応する表で確認し、他機種へ読み替えない。

## 概略確認フロー（電気作業手順ではない）

対象基板の型式と表示モードを確認し、LED・7SEGの状態と発生時点を記録する。適用する基板別表示表で意味を確認し、異常の判断は承認済み資料と担当者へ照合する。電気回路に触れる作業は本ページから判断・実施しない。

## 出典・確認履歴

- 原文ノート: [[不具合対応【ELV】/エラー/エラー確認時のポイント/７SEG表示、発光ダイオード機能]]
- 原文は画像3点を参照。2026-10-09の指定フォルダー・カテゴリ共通OneNoteフォルダー・添付画像フォルダー・Vault画像名検索では実ファイルを確認できず、過去の画像内容確認を再検証できない。基板共通仕様とはしていない。
- 原文の警告を要約したドラフトであり、電気作業の承認済み手順に代わるものではない。