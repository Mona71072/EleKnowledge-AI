---
schema_version: 1
record_id: "elv-vfgh-converter-status"
record_version: 2
title: "VFGHコンバータ基板状態表示の参照"
category: "不具合対応(ELV)"
record_type: "technical_reference"
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
  - "VFGH"
  - "コンバータ"
  - "状態表示"
source_path: "不具合対応【ELV】/エラー/エラー確認時のポイント/コンバータ基板状態表示（VFGH）.md"
source_filename: "コンバータ基板状態表示（VFGH）.md"
onenote_id: "a8c15103-95f4-4d08-897a-403d412bffb5:130"
related_ids:
  - "elv-error-check-points"
  - "elv-vfgh-error-codes"
attachment_paths:
attachment_paths: []
reference_links: []
document_references:
  - document_number: "C-7-F2900.108"
    title: "コンバータ基板状態表示機能の参照資料（図版記載）"
    locator: "表示機能・換算表の参照先として画像に記載"
    source_path: ""
evidence_sources:
  - source_id: "evidence-elv-vfgh-converter-status-original"
    source_type: "vault_original"
    title: "コンバータ基板状態表示（VFGH）（原文）"
    source_path: "不具合対応【ELV】/エラー/エラー確認時のポイント/コンバータ基板状態表示（VFGH）.md"
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-01"
    supports:
      - "VFGHコンバータ状態表示資料の存在"
  - source_id: "evidence-elv-vfgh-converter-status-map"
    source_type: "vault_original"
    title: "VFGHコンバータ7SEG表示機能表"
    source_path: "不具合対応【ELV】/エラー/エラー確認時のポイント/OneNote/コンバータ基板状態表示（VFGH） image.png"
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-04"
    supports:
      - "C1カード上の7SEGとRSWで選択する表示モードの説明"
      - "トレーストリガ検出時に7SEGが点滅するという図版記載"
  - source_id: "evidence-elv-vfgh-converter-status-version-warning"
    source_type: "vault_original"
    title: "VFGHコンバータ表示の版依存注意"
    source_path: "不具合対応【ELV】/エラー/エラー確認時のポイント/OneNote/コンバータ基板状態表示（VFGH） image 1.png"
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-04"
    supports:
      - "特定S/W版で母線電圧・相電流表示が適切でない場合があり、基板別換算表を参照するという警告"
      - "換算係数の現行適用性は裏付けない"
structured_data:
  source_notes:
    - "原文本文は画像3点の埋め込みのみ。過去の内容確認記録には表示機能と版依存警告の要約がある。2026-10-09の指定フォルダー・カテゴリ共通OneNoteフォルダー・添付画像フォルダー・画像名検索で実ファイルを確認できず、現在は再照合できないためattachment_pathsには登録しない。"
    - "図版は一部S/W版で母線電圧・相電流表示が適切でない場合を警告し、基板型式別の換算表を示す。版・基板適用性が未確認のため係数は転載しない。"
    - "トレーストリガがある場合の点滅表示も記載されるが、現行診断基準とは確認していない。"
---

# VFGHコンバータ基板状態表示の技術参照

## 表示機能

図版によると、VFGH方式ではC1カード上のCPUがコンバータ制御を行い、C1カード上の7SEGで状態を表示する。ロータリースイッチRSWで表示データを選択し、トレーストリガがある場合には7SEGを点滅させる説明がある。表示モードとコードの詳細は、対象基板に適用する資料で確認する。

## 重要な版依存注意

図版は、特定のS/Wバージョンで母線電圧・R相電流・S相電流の7SEG表示が適切でない場合があると警告し、C1基板型式別の換算表を示している。換算係数は本ページに転載していない。対象S/W版・基板型式・現行換算表を照合するまでは、表示値を実電圧・電流の判定に用いない。

## 概略確認フロー（操作手順ではない）

対象機の制御方式、C1基板型式、コンバータS/W版を特定する。RSWの表示モードと7SEGの状態を記録し、適用版の表示表・換算表で意味を確認する。版や基板が一致しない場合は診断に使わず、承認済み資料と担当者へ照合する。

## 出典

- 原文ノート: [[不具合対応【ELV】/エラー/エラー確認時のポイント/コンバータ基板状態表示（VFGH）]]
- 原文は画像3点を参照。2026-10-09の指定フォルダー・カテゴリ共通OneNoteフォルダー・添付画像フォルダー・画像名検索では実ファイルを確認できず、過去の図版内容を再検証できない。換算係数・修理判断は転記していない。
- 診断・修理判断には、対象基板・ソフト版に適用する承認済み最新版を確認すること。