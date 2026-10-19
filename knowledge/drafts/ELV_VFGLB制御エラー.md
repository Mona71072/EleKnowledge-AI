---
schema_version: 1
record_id: "elv-vfglb-error-codes"
record_version: 2
title: "VFGLB制御エラー表の参照情報"
category: "不具合対応(ELV)"
record_type: "technical_reference"
product: "エレベーター"
model_type:
  - "VFGLB"
document_number: ""
revision: ""
effective_date: ""
review_status: "in_review"
publication_status: "not_published"
classification: "unknown"
cloud_approval: "not_reviewed"
keywords:
  - "VFGLB"
  - "制御エラー"
  - "MON1/0"
source_path: "不具合対応【ELV】/エラー/エラー確認時のポイント/VFGLB制御　エラーコード.md"
source_filename: "VFGLB制御　エラーコード.md"
onenote_id: "a8c15103-95f4-4d08-897a-403d412bffb5:125"
related_ids:
  - "elv-error-check-points"
attachment_paths: []
reference_links: []
document_references:
  - document_number: "C-7-C3300.1-J"
    title: "VFGLB電気システム据付調整資料"
    locator: ""
    source_path: ""
evidence_sources:
  - source_id: "evidence-elv-vfglb-error-codes-original"
    source_type: "vault_original"
    title: "VFGLB制御 エラーコード（原文）"
    source_path: "不具合対応【ELV】/エラー/エラー確認時のポイント/VFGLB制御　エラーコード.md"
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-09"
    supports:
      - "表示モードとエラー表・資料番号の原文記載"
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
    - "原文のエラー表画像10点に対応する実ファイルは、2026-10-09のVault確認で指定フォルダーおよびカテゴリ共通OneNoteフォルダー内に見つからなかった。実在未確認のためattachment_pathsには登録しない。コード表の内容は未読解。"
    - "原文中の単独のXは意味・対応関係を確認できず未解決。"
    - "C-7-C3300.1-Jの最新版・適用性は未確認。"
---

# VFGLB制御エラー表示の技術参照

## 原文記載

- エラー確認画面の表示区分とMON1/0値を原文本文の記載から整理した。コード表画像の内容は含まない。
- 原文はエラーコード表・小分類詳細表とリモコンによる確認図版を参照する構成だが、対応する画像ファイルはVault内で確認できていない。
- リアルタイム、ラッチ、一時停止モードについて、本文で読めるMON1/0値を下記に示す。
- 参照資料としてC-7-C3300.1-Jを記載。
- 原文中に単独の「X」があるが、意味は未確認。

| 表示区分 | MON1/0 | 原文上の条件 |
| --- | --- | --- |
| リアルタイム表示 | 1/0 | 通常表示 |
| ラッチ表示 | 1/1 | 検出済みエラー |
| 一時停止モードのリアルタイム表示 | 1/9 | 一時停止モード |
| 一時停止モードの検出済みエラー表示 | 1/8 | 一時停止モード・検出済みエラー |

エラーコードと意味は図版内容を確認できていないため記載していない。実機の診断・復旧手順として使用しない。

## 出典

- 原文ノート: [[不具合対応【ELV】/エラー/エラー確認時のポイント/VFGLB制御　エラーコード]]
- 原文は画像10点を参照。2026-10-09時点で指定フォルダーおよびカテゴリ共通OneNoteフォルダーに実ファイルを確認できず、コード表・資料改訂・適用性は未確認。