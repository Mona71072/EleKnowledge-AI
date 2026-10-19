---
schema_version: 1
record_id: "elv-scu20-flash-rewrite-tool-compatibility-id233"
record_version: 1
title: "SCU-20書換プログラム対応と旧ツールのエラー報告（ID233）"
category: "不具合対応(ELV)"
record_type: "technical_reference"
product: "エレベーター"
model_type:
  - "SCU-20"
document_number: ""
revision: ""
effective_date: ""
review_status: "in_review"
publication_status: "not_published"
classification: "unknown"
cloud_approval: "not_reviewed"
keywords:
  - "SCU-20"
  - "フラッシュ書換えプログラム"
  - "メンテコン"
  - "パワーマネージメント制御設定"
source_path: "首都工・不具合情報共有リスト.xlsx"
source_filename: "首都工・不具合情報共有リスト.xlsx"
onenote_id: ""
related_ids:
  - "elv-sw-change-reference"
attachment_paths: []
reference_links: []
document_references:
  - document_number: "C-6-S951.1"
    title: "SCU-20書換時の参照資料（原リスト記載）"
    locator: "A.2項目"
    source_path: ""
  - document_number: "C-7-C3343"
    title: "原リスト参照欄に併記された資料番号（関係未確認）"
    locator: ""
    source_path: ""
evidence_sources:
  - source_id: "evidence-list-scu20-rewrite-tool-compatibility-233"
    source_type: "vault_original"
    title: "首都工・不具合情報共有リスト.xlsx: SCU-20書換情報（ID233）"
    source_path: "首都工・不具合情報共有リスト.xlsx"
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-14"
    supports:
      - "SCU-20用の書換ツールと制御盤書換ツールの区別"
      - "2023-10-25のメンテコン更新で書換プログラム4にSCU-20が追加されたとの記載"
      - "書換ツールver.4.2で設定関連エラーが起きる可能性との報告"
structured_data:
  specifications:
    - name: "SCU-20対応プログラム"
      value: "フラッシュ書換えプログラム4"
      unit: ""
      condition: "2023-10-25のメンテコン更新でSCU-20が追加されたとのリスト記載。現在の対応状況は未確認。"
    - name: "エラー報告の対象ツール版"
      value: "4.2"
      unit: "version"
      condition: "当該版の使用時に「パワーマネージメント制御設定」エラーが表示され、メニューが終了する可能性があるとのリスト記載。"
  source_notes:
    - "リストはSCU-20用ツールが制御盤書換ツールとは別と説明する。具体的な接続・書換手順は記録しない。"
    - "旧ツール版とエラーの因果関係、現行ソフトでの再現性、エラー解消結果は未確認。リストにある設定ファイルの変更方法は転載しない。"
    - "C-6-S951.1はA.2項目参照と明記。C-7-C3343は参照欄に連結表記され、ID233との関係は未確認。"
    - "同リストに添付インストーラーへの言及があるが、実ファイルは本記録の根拠として確認していない。"
---

# SCU-20書換プログラム対応と旧ツールのエラー報告（ID233）

首都工・不具合情報共有リストID233は、SCU-20の書換には制御盤書換ツールとは別のツールが必要と記載する。また、2023年10月25日のメンテコン更新で「フラッシュ書換えプログラム4」にSCU-20が追加されたと記録している。この更新記録は当時の情報であり、現行ツール・対象機種への適用は未確認である。

同リストは、フラッシュ書換ツールver.4.2の使用時に「パワーマネージメント制御設定」エラーが表示され、メニューが終了する可能性を報告する。原因、現行版での再現性、解消結果は確認できていない。設定ファイルの変更方法や書換操作は転載しない。

参照資料番号C-6-S951.1のA.2項目を参照する記載がある。C-7-C3343も参照欄に連結して記載されるが、ID233との関係は未確認。添付インストーラーの実ファイル・内容も未確認である。