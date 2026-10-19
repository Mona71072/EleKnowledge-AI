---
schema_version: 1
record_id: "elv-putty-scu-log"
record_version: 1
title: "SCU-20/ELSGWログ採取ノートの参照記録"
category: "不具合対応(ELV)"
record_type: "troubleshooting_case"
product: "エレベーター"
model_type:
  - "SCU-20"
  - "ELSGW"
document_number: ""
revision: ""
effective_date: ""
review_status: "in_review"
publication_status: "not_published"
classification: "unknown"
cloud_approval: "not_reviewed"
keywords:
  - "SCU-20"
  - "ELSGW"
  - "PuTTY"
  - "TRFLOG"
  - "COMLOG"
  - "ERRLOG"
source_path: "不具合対応【ELV】/メンテコン/PuTTY使用方法/エレコール盤(SCU-20)・ELSGW盤のログ採取方法・手順.md"
source_filename: "エレコール盤(SCU-20)・ELSGW盤のログ採取方法・手順.md"
onenote_id: "a8c15103-95f4-4d08-897a-403d412bffb5:107"
related_ids:
  - "elv-maintenance-console-overview"
attachment_paths:
  - "不具合対応【ELV】/メンテコン/PuTTY使用方法/OneNote/エレコール盤(SCU-20)・ELSGW盤のログ採取方法・手順 image.png"
  - "不具合対応【ELV】/メンテコン/PuTTY使用方法/OneNote/エレコール盤(SCU-20)・ELSGW盤のログ採取方法・手順 image 1.png"
  - "不具合対応【ELV】/メンテコン/PuTTY使用方法/OneNote/エレコール盤(SCU-20)・ELSGW盤のログ採取方法・手順 image 2.png"
  - "不具合対応【ELV】/メンテコン/PuTTY使用方法/OneNote/エレコール盤(SCU-20)・ELSGW盤のログ採取方法・手順 image 3.png"
  - "不具合対応【ELV】/メンテコン/PuTTY使用方法/OneNote/エレコール盤(SCU-20)・ELSGW盤のログ採取方法・手順 image 4.png"
  - "不具合対応【ELV】/メンテコン/PuTTY使用方法/OneNote/エレコール盤(SCU-20)・ELSGW盤のログ採取方法・手順 image 5.png"
  - "不具合対応【ELV】/メンテコン/PuTTY使用方法/OneNote/エレコール盤(SCU-20)・ELSGW盤のログ採取方法・手順 image 6.png"
reference_links: []
document_references:
  - document_number: "C-7-C3333.1-J"
    title: "ELSGW保守ツール操作説明書"
    locator: ""
    source_path: ""
evidence_sources:
  - source_id: "evidence-elv-putty-scu-log"
    source_type: "vault_original"
    title: "SCU-20/ELSGWログ採取ノート（原文）"
    source_path: "不具合対応【ELV】/メンテコン/PuTTY使用方法/エレコール盤(SCU-20)・ELSGW盤のログ採取方法・手順.md"
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-01"
    supports:
      - "ログ種別、現象メモ、担当部門への照会に関する原文記述"
  - source_id: "evidence-elv-putty-scu-command-matrix"
    source_type: "vault_original"
    title: "コマンド種別と対応版の図表"
    source_path: "不具合対応【ELV】/メンテコン/PuTTY使用方法/OneNote/エレコール盤(SCU-20)・ELSGW盤のログ採取方法・手順 image 1.png"
    s3_uri: ""
    revision: "図表記載: コマンド別に適応副版が異なる"
    accessed_at: "2026-10-04"
    supports:
      - "ログ種別ごとに対応副版が異なるため、版確認が必要であること"
  - source_id: "evidence-elv-putty-scu-log-overwrite"
    source_type: "vault_original"
    title: "PuTTYログ保存画面例"
    source_path: "不具合対応【ELV】/メンテコン/PuTTY使用方法/OneNote/エレコール盤(SCU-20)・ELSGW盤のログ採取方法・手順 image 2.png"
    s3_uri: ""
    revision: "画面例のファイル日時: 2017-11-07"
    accessed_at: "2026-10-04"
    supports:
      - "既定ログファイルが次回採取で上書きされるという原文記載の画面例"
  - source_id: "evidence-elv-putty-scu-log-analysis"
    source_type: "vault_original"
    title: "通行ログと機器設定の照合例"
    source_path: "不具合対応【ELV】/メンテコン/PuTTY使用方法/OneNote/エレコール盤(SCU-20)・ELSGW盤のログ採取方法・手順 image 5.png"
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-04"
    supports:
      - "事象時刻・機器間の設定差をログ例と照合する考え方"
      - "カード・部屋番号など個別情報を含むため、画面例の値は転載しない"
structured_data:
  items:
    - item: "ログ種別"
      detail: "原文は通行履歴、通信履歴、エラー履歴等を挙げる。コマンド・画面画像は本記録に転載しない。"
    - item: "現象との対応"
      detail: "事象の時刻・設備位置・再現内容等を記録して照会に添える考え方を説明。"
  source_notes:
    - "添付画像7点は内容確認済み。コマンド・ログ保存画面・ネットワーク/機器構成・解析例を含む。画面例の個別物件情報は転載しない。"
    - "コマンド対応副版は種類ごとに異なる。画面中のコマンド、件数範囲、ファイルパスは版・環境依存のため転載しない。"
    - "既定ログファイルは次回取得時に上書きされる旨の記載がある。保管先・ファイル名は現行の承認手順で確認する。"
    - "ログ取得・保存・送付は最新承認手順と情報管理規則に従うこと。ログに個人・入退館情報が含まれる可能性がある。"
---

# SCU-20/ELSGWログ採取ノートの参照記録

原文は、SCU-20/ELSGW関連の障害調査で通行・通信・エラー等の履歴を参照し、発生時刻・場所・再現事象を添えて担当部門へ照会する流れを説明している。

添付図版では、コマンドごとに対応副版が異なること、既定ログファイルが後続の取得で上書きされることが示されている。また、通行ログの解析例は複数機器間の設定差を照合する考え方を示すが、個別のカード・建物情報や結論を一般化しない。

## 概略調査フロー（取得手順ではない）

事象の時刻・場所・操作内容を記録し、対象盤と版を特定する。承認済み説明書で必要なログ種別と対応版を確認し、取得後は上書きを避けて許可された方法で保管する。事象記録と関連機器の設定を照合し、必要な最小限の情報を担当部門へ共有する。

コマンド、接続操作、ソフト起動権限、保存場所は再掲していない。ログに個人・入退館情報が含まれる可能性を考慮し、共有先・保管期間・送付方法を確認する。

## 出典

- 原文ノート: [[不具合対応【ELV】/メンテコン/PuTTY使用方法/エレコール盤(SCU-20)・ELSGW盤のログ採取方法・手順]]
- 添付画像7点は実在確認済み。画像中のコマンド画面・ログ例は未読解。