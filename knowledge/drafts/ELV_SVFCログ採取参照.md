---
schema_version: 1
record_id: "elv-putty-svfc-log"
record_version: 1
title: "ZJ2/u形（SVFC）ログ採取ノートの参照記録"
category: "不具合対応(ELV)"
record_type: "catalog"
product: "エレベーター"
model_type:
  - "ZJ2/u形 (SVFC)"
document_number: ""
revision: ""
effective_date: ""
review_status: "in_review"
publication_status: "not_published"
classification: "unknown"
cloud_approval: "not_reviewed"
keywords:
  - "SVFC"
  - "ZJ2"
  - "ログ採取"
  - "PuTTY"
source_path: "不具合対応【ELV】/メンテコン/PuTTY使用方法/ZJ2 -u形（SVFC）のログ採取方法・手順.md"
source_filename: "ZJ2 -u形（SVFC）のログ採取方法・手順.md"
onenote_id: "a8c15103-95f4-4d08-897a-403d412bffb5:108"
related_ids:
  - "elv-maintenance-console-overview"
  - "elv-trace-data-reference"
attachment_paths:
  - "不具合対応【ELV】/メンテコン/PuTTY使用方法/OneNote/ZJ2 -u形（SVFC）のログ採取方法・手順 image.png"
  - "不具合対応【ELV】/メンテコン/PuTTY使用方法/OneNote/ZJ2 -u形（SVFC）のログ採取方法・手順 image 1.png"
  - "不具合対応【ELV】/メンテコン/PuTTY使用方法/OneNote/ZJ2 -u形（SVFC）のログ採取方法・手順 image 2.png"
  - "不具合対応【ELV】/メンテコン/PuTTY使用方法/OneNote/ZJ2 -u形（SVFC）のログ採取方法・手順 image 3.png"
reference_links: []
document_references:
  - document_number: "C-60-631-VF32.1-J"
    title: "データ取得・S/W書換要領(SVFC)"
    locator: ""
    source_path: ""
evidence_sources:
  - source_id: "evidence-elv-putty-svfc-log"
    source_type: "vault_original"
    title: "ZJ2/u形（SVFC）ログ採取方法・手順（原文）"
    source_path: "不具合対応【ELV】/メンテコン/PuTTY使用方法/ZJ2 -u形（SVFC）のログ採取方法・手順.md"
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-01"
    supports:
      - "技術情報リスト、依頼内容、対応内容の画像参照"
  - source_id: "evidence-elv-putty-svfc-request-context"
    source_type: "vault_original"
    title: "トレースデータ依頼メールの画像"
    source_path: "不具合対応【ELV】/メンテコン/PuTTY使用方法/OneNote/ZJ2 -u形（SVFC）のログ採取方法・手順 image.png"
    s3_uri: ""
    revision: "画像内メール日付: 2024-01-18"
    accessed_at: "2026-10-04"
    supports:
      - "パラメータ変更時点を調べるためトレースデータを依頼した事例"
      - "特定の現場・顧客・担当者情報は転載しない"
  - source_id: "evidence-elv-putty-svfc-log-format"
    source_type: "vault_original"
    title: "SVFCログ取得・出力例"
    source_path: "不具合対応【ELV】/メンテコン/PuTTY使用方法/OneNote/ZJ2 -u形（SVFC）のログ採取方法・手順 image 3.png"
    s3_uri: ""
    revision: "図版にPuTTY 0.63表記"
    accessed_at: "2026-10-04"
    supports:
      - "保存データの範囲が異なる取得方式とログ出力形式の例"
      - "コマンド・通信設定・取得所要時間は特定版の説明で現行性未確認"
structured_data:
  source_notes:
    - "本文は見出しと画像埋め込みのみ。画像4点は内容確認済み。個別現場の事象、トレースデータ依頼、PuTTY設定画面、ログ出力例を含む。"
    - "事例は出荷試験後のパラメータ変更時点を調べる目的でトレースデータを求めたもの。画像内のメールには特定できる現場・顧客・担当者情報があるため複写しない。"
    - "PuTTY 0.63表記の取得例に複数の取得方式、コマンド、通信設定、所要時間がある。旧画面の詳細は現行の承認手順と照合するまで転載しない。"
    - "個別事例の見解を一般的な故障原因や解決済み判定として扱わない。"
---

# ZJ2/u形（SVFC）ログ採取ノートの参照記録

画像には、出荷試験後にパラメータが変更された時点を確認するためトレースデータを求めた事例がある。これは個別事例の調査依頼であり、原因や解決状態を一般化する根拠ではない。現場・顧客・担当者情報は本記録に含めていない。

## 概略調査フロー（取得手順ではない）

対象機・現象・発生時刻を整理し、依頼元が確認したい事象を明確にする。対象機に適用する承認済み要領でPuTTYの版・通信設定・取得方式を確認し、許可された方法でログを保存する。ログとトレースデータを時刻で照合し、個別の診断は担当部門へ依頼する。

添付のPuTTY 0.63画面にあるコマンド、通信設定、取得件数・所要時間は現行仕様として転載していない。実作業前に原文が挙げるC-60-631-VF32.1-Jの最新版と対象機適用性を確認すること。ログやメールには個人・顧客情報が含まれるため、共有範囲を限定する。

## 出典

- 原文ノート: [[不具合対応【ELV】/メンテコン/PuTTY使用方法/ZJ2 -u形（SVFC）のログ採取方法・手順]]
- 添付画像4点: 実在と内容を確認。調査目的とログ形式の要点を反映し、個別現場情報・PuTTY設定・コマンドは転載していない。