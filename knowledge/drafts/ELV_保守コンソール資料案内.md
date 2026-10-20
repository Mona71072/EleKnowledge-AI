---
schema_version: 1
record_id: "elv-maintenance-console-overview"
record_version: 3
title: "保守コンソール関連資料案内"
category: "不具合対応(ELV)"
record_type: "catalog"
product: "エレベーター"
model_type:
  - "SCU-20"
  - "ELSGW"
  - "ZJ2/u形 (SVFC)"
document_number: ""
revision: ""
effective_date: ""
review_status: "in_review"
publication_status: "not_published"
classification: "unknown"
cloud_approval: "not_reviewed"
keywords:
  - "保守コンソール"
  - "PuTTY"
  - "ログ採取"
  - "SCU-20"
  - "ELSGW"
  - "SVFC"
source_path: "不具合対応【ELV】/メンテコン/PuTTY使用方法.md"
source_filename: "PuTTY使用方法.md"
onenote_id: "a8c15103-95f4-4d08-897a-403d412bffb5:106"
related_ids:
  - "elv-putty-scu-log"
  - "elv-putty-svfc-log"
  - "list-id130-putty-installation-reference"
  - "list-id119-putty-log-collection-unavailable"
reference_links: []
document_references:
  - document_number: "C-7-C3333.1-J"
    title: "エレベーターセキュリティゲートウェイ（ELSGW）保守ツール操作説明書"
    locator: ""
    source_path: ""
  - document_number: "C-7-C3345.1-J"
    title: "エレベーターセキュリティ(SCU-20)盤保守ツール操作説明書"
    locator: "P.25（原文記載）"
    source_path: ""
  - document_number: "C-60-631-VF32.1-J"
    title: "データ取得・S/W書換要領(SVFC)"
    locator: ""
    source_path: ""
evidence_sources:
  - source_id: "evidence-elv-maintenance-console-overview"
    source_type: "vault_original"
    title: "PuTTY使用方法（原文）"
    source_path: "不具合対応【ELV】/メンテコン/PuTTY使用方法.md"
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-01"
    supports:
      - "対象盤・機種と関連説明資料の案内"
  - source_id: "evidence-list-elv-putty-installation-id130"
    source_type: "vault_original"
    title: "首都工・不具合情報共有リスト: PuTTYインストール方法（ID130）"
    source_path: "首都工・不具合情報共有リスト.xlsx"
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-14"
    supports:
      - "エレコール用メンテコンのPuTTYインストール項目と外部リンクの存在"
      - "対応欄「対応不要」。配布元・版・リンク先内容は未確認"
  - source_id: "evidence-list-elv-putty-log-unavailable-id119"
    source_type: "vault_original"
    title: "首都工・不具合情報共有リスト: PuTTYログが採取できない（ID119）"
    source_path: "首都工・不具合情報共有リスト.xlsx"
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-14"
    supports:
      - "エレコールのメンテコンでログを採取できないとの報告"
      - "対応欄「対応不要」。原因・解決・実際の採取結果は未確認"
structured_data:
  items:
    - item: "対象として挙げられている設備"
      detail: "エレコール盤（SCU-20）、ロボット連動/エレナビ（ELSGW）、ZJ2/u形（SVFC）。"
    - item: "関連資料"
      detail: "C-7-C3333.1-J、C-7-C3345.1-J、C-60-631-VF32.1-J。各最新版・適用性は未確認。"
  source_notes:
    - "原文には社内SharePoint項目へのリンクがあるが、アクセス権付きURLは転記していない。"
    - "個別のログ採取ノートは関連記録を参照。PuTTYの設定・コマンド操作は本案内に記載しない。"
    - "一次リストID130はエレコール用メンテコンのPuTTYインストール項目と外部リンクを含む。対応欄は「対応不要」。リンク先・配布元・版・認証/接続情報は未確認のため、URLやインストール方法を転記しない。"
    - "一次リストID119はエレコールのメンテコンでPuTTYログを採取できないとの報告。対応欄「対応不要」は原因解消や採取成功の確認ではない。原因・回避策・接続情報・コマンドは未確認/非転載。"
---

# 保守コンソール関連資料案内

原文が対象としているのは、エレコール盤（SCU-20）、ロボット連動/エレナビ（ELSGW）、ZJ2/u形（SVFC）。対象別の操作説明資料を列挙している。

一次リストID130は、エレコール用メンテコンのPuTTYインストール項目を案内する。対応欄は「対応不要」だが、外部リンク先、ソフトウェア配布元、版、認証/接続要件は確認していない。インストーラーの取得先や手順を本記録から提供しない。

一次リストID119には、エレコールのメンテコンでPuTTYログを採取できないとの報告がある。対応欄は「対応不要」だが、原因、実際の採取結果、解決の確認を意味しない。具体的な接続情報やコマンド、回避策は記録していない。

本ページは資料案内であり、PuTTYのインストール、接続、設定、ログ採取手順ではない。対象機種と盤構成を照合し、承認済み最新版の説明書・社内指示を確認すること。

ログには設備識別情報や利用履歴等が含まれる場合がある。取得・共有は必要範囲に限定し、組織の情報管理ルールに従う。

## 出典

- 原文ノート: [[不具合対応【ELV】/メンテコン/PuTTY使用方法]]