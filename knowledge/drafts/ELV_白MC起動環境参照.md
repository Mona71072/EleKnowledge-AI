---
schema_version: 1
record_id: "elv-white-mc-setup"
record_version: 1
title: "白MCカード起動環境設定ノートの参照記録"
category: "不具合対応(ELV)"
record_type: "procedure"
knowledge_domain: "engineering_business"
organizational_scope: "unknown"
product: "エレベーター"
model_type: []
document_number: "EA-030-0C-01-_（原文記載、末尾未確定）"
revision: ""
effective_date: ""
review_status: "in_review"
publication_status: "not_published"
classification: "unknown"
cloud_approval: "not_reviewed"
keywords:
  - "白MCカード"
  - "MC-101A"
  - "起動環境設定"
  - "COMポート"
source_path: "不具合対応【ELV】/メンテコン/S-W書換方法/白MCカード起動環境設定.md"
source_filename: "白MCカード起動環境設定.md"
onenote_id: "a8c15103-95f4-4d08-897a-403d412bffb5:111"
related_ids:
  - "elv-vfgr-sw-change"
attachment_paths:
  - "不具合対応【ELV】/メンテコン/S-W書換方法/OneNote/白MCカード起動環境設定 image.png"
  - "不具合対応【ELV】/メンテコン/S-W書換方法/OneNote/白MCカード起動環境設定 image 1.png"
  - "不具合対応【ELV】/メンテコン/S-W書換方法/OneNote/白MCカード起動環境設定 image 2.png"
  - "不具合対応【ELV】/メンテコン/S-W書換方法/OneNote/白MCカード起動環境設定 image 3.png"
  - "不具合対応【ELV】/メンテコン/S-W書換方法/OneNote/白MCカード起動環境設定 image 4.png"
  - "不具合対応【ELV】/メンテコン/S-W書換方法/OneNote/白MCカード起動環境設定 image 5.png"
reference_links: []
document_references:
  - document_number: "EA-030-0C-01-_"
    title: "MCカード起動環境設定手順"
    locator: "5.1項（原文記載）"
    source_path: ""
evidence_sources:
  - source_id: "evidence-elv-white-mc-setup"
    source_type: "vault_original"
    title: "白MCカード起動環境設定（原文）"
    source_path: "不具合対応【ELV】/メンテコン/S-W書換方法/白MCカード起動環境設定.md"
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-01"
    supports:
      - "白MCカードの事前設定・参照要領に関する原文記載"
  - source_id: "evidence-elv-white-mc-cable-diagram"
    source_type: "vault_original"
    title: "白MCカード接続構成図"
    source_path: "不具合対応【ELV】/メンテコン/S-W書換方法/OneNote/白MCカード起動環境設定 image 1.png"
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-04"
    supports:
      - "白MCカードのWP/WSとメンテコンの接続経路が別図示されていること"
  - source_id: "evidence-elv-white-mc-rsw-warning"
    source_type: "vault_original"
    title: "白MCカードRSW条件の警告画面"
    source_path: "不具合対応【ELV】/メンテコン/S-W書換方法/OneNote/白MCカード起動環境設定 image 4.png"
    s3_uri: ""
    revision: "画面表記: Ver.2.0"
    accessed_at: "2026-10-04"
    supports:
      - "出荷直後のカードに関するRSW2位置と完了後の復帰についての画面記載。原文本文と条件差があり未解決"
  - source_id: "evidence-elv-white-mc-completion"
    source_type: "vault_original"
    title: "白MCカード起動環境設定完了画面"
    source_path: "不具合対応【ELV】/メンテコン/S-W書換方法/OneNote/白MCカード起動環境設定 image 5.png"
    s3_uri: ""
    revision: "画面表記: Ver.2.0"
    accessed_at: "2026-10-04"
    supports:
      - "起動環境設定完了を示す画面例"
structured_data:
  source_notes:
    - "原文はMC-101A、LED状態、カード設定、メンテコンメニュー、COMポートに関する操作手順を含む。具体操作値・画面手順は転載しない。"
    - "参照PDFのSharePointコピーと版の現行性は未確認。"
    - "添付画像6点は内容確認済み。接続図、設定画面、完了表示を含み、画面例はVer.2.0。現行の機器・OS適用性は未確認。"
    - "原文本文はRSWを常時0/0と記載する一方、画像の警告は出荷直後のカードについてRSW2=B、完了後に0へ戻す旨を記載。条件差は未解決のため、いずれも作業指示として採用しない。"
---

# 白MCカード起動環境設定ノートの参照記録

原文は、白MCカード（MC-101A）の起動環境設定と参照PDF EA-030-0C-01-_ を扱い、カード状態・メンテコン設定・COMポートに言及する。添付図版にはWP/WSの接続構成、設定画面、完了表示がある。

## 要確認差分

原文本文はRSWを常時0/0にするよう記載する一方、画像の警告画面は出荷直後のカードではRSW2をBにし、完了後に0へ戻すよう記載する。条件差や対象範囲は確認できていないため、記載を一つに統合せず、正式版の承認済み資料で解決するまで操作値として使用しない。

## 概略確認フロー（設定手順ではない）

対象カードとPC/メンテコン構成を特定し、資料の正式番号・改訂・適用条件を確認する。電源・接続状態およびRSW記載の差分を承認済み資料で解決したうえで、有資格担当者がその資料に従って設定し、完了表示と最終状態を確認する。

本文中のカード設定値、具体的な接続・メニュー操作は再掲していない。参照PDFのSharePointコピーと版の現行性も未確認である。

## 出典

- 原文ノート: [[不具合対応【ELV】/メンテコン/S-W書換方法/白MCカード起動環境設定]]
- 添付画像6点: 実在と内容を確認。接続・完了表示と本文との条件差を記録し、具体操作値・画面手順は転載していない。
