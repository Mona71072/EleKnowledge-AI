---
schema_version: 1
record_id: "elv-vfgh-error-codes"
record_version: 2
title: "VFGH制御エラー表の参照情報"
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
  - "制御エラー"
  - "MON1/0"
source_path: "不具合対応【ELV】/エラー/エラー確認時のポイント/VFGH制御　エラーコード.md"
source_filename: "VFGH制御　エラーコード.md"
onenote_id: "a8c15103-95f4-4d08-897a-403d412bffb5:123"
related_ids:
  - "elv-error-check-points"
attachment_paths:
attachment_paths: []
reference_links: []
document_references:
  - document_number: "C-7-F2900.1-J"
    title: "VFGH方式エレベーター据付調整資料"
    locator: ""
    source_path: ""
evidence_sources:
  - source_id: "evidence-elv-vfgh-error-codes-original"
    source_type: "vault_original"
    title: "VFGH制御 エラーコード（原文）"
    source_path: "不具合対応【ELV】/エラー/エラー確認時のポイント/VFGH制御　エラーコード.md"
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-01"
    supports:
      - "表示モードとエラー表・資料番号の原文記載"
  - source_id: "evidence-elv-vfgh-error-display-structure"
    source_type: "vault_original"
    title: "VFGH 7SEGエラー表示の桁構成図"
    source_path: "不具合対応【ELV】/エラー/エラー確認時のポイント/OneNote/VFGH制御　エラーコード image.png"
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-04"
    supports:
      - "4桁の7SEGそれぞれがエラー有無・異常分類・動作分類・詳細を表示する図版説明"
      - "MONモードごとのリアルタイム/ラッチ表示と空欄の意味"
  - source_id: "evidence-elv-vfgh-error-class-tables"
    source_type: "vault_original"
    title: "VFGHエラー分類・小分類表"
    source_path: "不具合対応【ELV】/エラー/エラー確認時のポイント/OneNote/VFGH制御　エラーコード image 1.png"
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-04"
    supports:
      - "異常分類および動作分類の一覧が画像にあること"
      - "コード別詳細表が複数の分類に分かれること"
structured_data:
  specifications:
    - name: "リアルタイム表示"
      value: "MON1/0=1/0"
      condition: "通常のリアルタイム表示として原文に記載。"
    - name: "ラッチ表示"
      value: "MON1/0=1/1"
      condition: "検出済みエラーのラッチ表示として原文に記載。"
    - name: "一時停止モードのリアルタイム表示"
      value: "MON1/0=1/9"
      condition: "原文で一時停止モードと記載。"
    - name: "一時停止モードの検出済みエラー表示"
      value: "MON1/0=1/8"
      condition: "原文で一時停止モード・検出済みエラー表示と記載。"
  source_notes:
    - "原文は添付画像6点を参照している。過去の内容確認記録には7SEGの役割、表示モード、分類・小分類表の要約がある。2026-10-09の指定フォルダー・カテゴリ共通OneNoteフォルダー・添付画像フォルダー・画像名検索で実ファイルを確認できず、現在は再照合できないためattachment_pathsには登録しない。"
    - "コード表はVFGH向けC-7-F2900.1-Jの抜粋。全コードの再転記はせず、対象機の適用版で詳細を確認する。"
    - "C-7-F2900.1-Jの最新版・適用性は未確認。"
---

# VFGH制御エラー表示の技術参照

## 原文記載

- VFGH制御エラー表および小分類エラー詳細表を参照する構成。
- リアルタイム、ラッチ、一時停止モードの表示切替としてMON1/0の値を記載。
- 参照資料としてC-7-F2900.1-Jを記載。

## 7SEG表示の読み方

添付図版は4桁の役割を、7SEG4=エラー有無、7SEG3=異常分類、7SEG2=動作分類、7SEG1=詳細コードとして示す。表の空欄や「-」も表示モード上の意味があるため、コードの欠落・異常なしと即断しない。リアルタイム、ラッチ、一時停止中の表示モードを先に確認する。

小分類コード表は複数の分類に分かれ、VFGH向け資料の抜粋である。コードと原因・処置の全一覧は本ページに複写せず、C-7-F2900.1-Jの対象機に適用する最新版で確認する。

## 概略確認フロー（診断手順ではない）

対象機がVFGH方式であることと参照資料の適用版を確認する。表示モードを特定し、4桁の役割に沿って記録したコードを分類表・小分類表で照合する。コードの重篤度や原因、処置はコード表だけで断定せず、承認済み最新版と担当者へ確認する。

## 出典

- 原文ノート: [[不具合対応【ELV】/エラー/エラー確認時のポイント/VFGH制御　エラーコード]]
- 原文は添付画像6点を参照。2026-10-09の指定フォルダー・カテゴリ共通OneNoteフォルダー・添付画像フォルダー・画像名検索では実ファイルを確認できず、過去の画像内容を再検証できない。コード一覧は再転記していない。
- 適用機種・参照資料の改訂は未確認。