---
schema_version: 1
record_id: "elv-group-control-error-codes"
record_version: 2
title: "エレベーター群管理エラーの参照情報"
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
  - "群管理"
  - "E-CAN"
  - "G-CAN"
  - "I-CAN"
  - "EL-NET"
source_path: "不具合対応【ELV】/エラー/エラー確認時のポイント/群管理　エラーコード.md"
source_filename: "群管理　エラーコード.md"
onenote_id: "a8c15103-95f4-4d08-897a-403d412bffb5:128"
related_ids:
  - "elv-error-check-points"
attachment_paths:
attachment_paths: []
reference_links: []
document_references:
  - document_number: "C-8-S438.1-J"
    title: "群管理関連資料"
    locator: ""
    source_path: ""
evidence_sources:
  - source_id: "evidence-elv-group-error-codes-original"
    source_type: "vault_original"
    title: "群管理 エラーコード（原文）"
    source_path: "不具合対応【ELV】/エラー/エラー確認時のポイント/群管理　エラーコード.md"
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-01"
    supports:
      - "群管理通信の確認案内とエラー表示図の存在"
  - source_id: "evidence-elv-group-error-bit-map"
    source_type: "vault_original"
    title: "GP1 MODE/DATAビット表示表"
    source_path: "不具合対応【ELV】/エラー/エラー確認時のポイント/OneNote/群管理　エラーコード image.png"
    s3_uri: ""
    revision: "参照資料: C-8-S438.1-J"
    accessed_at: "2026-10-04"
    supports:
      - "MODE/DATAロータリー表示と7セグメントのビット列対応"
      - "図版では0を検出、1を未検出として読む説明"
      - "設定値・号機ビットの個別対応は転載しない"
  - source_id: "evidence-elv-group-error-decoding-example"
    source_type: "vault_original"
    title: "群管理通信エラーの読解例"
    source_path: "不具合対応【ELV】/エラー/エラー確認時のポイント/OneNote/群管理　エラーコード image 4.png"
    s3_uri: ""
    revision: "参照資料: C-8-S438.1-J"
    accessed_at: "2026-10-04"
    supports:
      - "ビット列と通信エラー分類を照合する例"
      - "号機・通信方式別の対応値は対象構成の資料確認が必要"
structured_data:
  specifications:
    - name: "GP1 MODE/DATA表示のビット読解"
      value: "0 = 検出、1 = 未検出"
      condition: "過去に確認した原文図版の説明。対象構成・現行適用性は未確認。"
    - name: "群管理エラーの表示照合例"
      value: "ビット列と通信エラー分類を照合する例が図版にある。"
      condition: "号機・通信方式別の対応値は対象構成の資料確認が必要。"
  source_notes:
    - "原文は添付画像5点を参照している。過去の内容確認記録にはGP1 MODE/DATA表示と通信異常例の要約がある。2026-10-09の指定フォルダー・カテゴリ共通OneNoteフォルダー・添付画像フォルダー・画像名検索で実ファイルを確認できず、現在は再照合できないためattachment_pathsには登録しない。"
    - "図版は0を検出、1を未検出としてビットを読む説明。号機対応やMODE/DATAの切替値は構成・版依存のため転載しない。"
    - "ロータリーSW操作は承認済み手順での確認が必要。C-8-S438.1-J最新版・対象構成への適用性と通信方式勉強会リンクは未確認。"
---

# エレベーター群管理エラー表示の技術参照

## 原文の案内

原文は、管制運転・監視盤の不具合で群管理通信（E-CAN、G-CAN、I-CAN、EL-NET、監視盤通信）の異常が関係する可能性を挙げている。GP1カードのMODE/DATAロータリーSWを表に従って変更し、原因を調べる案内がある。

## 表示の読み方

添付図版は、GP1カードのMODE/DATA表示を7セグメントのビット列として読み、0を検出、1を未検出として通信異常種別と照合する例を示す。E-CAN、G-CAN、I-CAN、EL-NET等のどの系統に該当するかは、対象の群管理構成に対応する資料で確認する。ビット列から号機や障害箇所を推測しない。

## 概略調査フロー（設定操作ではない）

管制運転・監視盤の現象と対象群管理構成を整理し、現在表示されているMODE/DATAと7SEG状態を記録する。承認済みの構成表で通信系統と表示を照合し、通信異常時は関連基板・接続系統を担当者と確認する。ロータリーSWの変更は本ページから行わず、適用資料と作業許可を確認する。

切替値・号機対応表は本ページに転載していない。C-8-S438.1-Jの最新版と対象構成への適用性は未確認。

## 出典

- 原文ノート: [[不具合対応【ELV】/エラー/エラー確認時のポイント/群管理　エラーコード]]
- 原文は画像5点を参照。2026-10-09の指定フォルダー・カテゴリ共通OneNoteフォルダー・添付画像フォルダー・画像名検索では実ファイルを確認できず、過去の画像内容を再検証できない。具体的な設定値・号機対応は転載していない。
- C-8-S438.1-Jの本文・改訂は未確認。