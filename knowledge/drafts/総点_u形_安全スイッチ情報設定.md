---
schema_version: 1
record_id: "esc-safety-switch-contact-settings"
record_version: 1
title: "u形エスカレーター 安全スイッチ情報設定の原文記述"
category: "総点(u型エス)"
record_type: "technical_reference"
product: "エスカレーター"
model_type:
  - "u形"
document_number: ""
revision: ""
effective_date: ""
review_status: "in_review"
publication_status: "not_published"
classification: "unknown"
cloud_approval: "not_reviewed"
keywords:
  - "安全スイッチ"
  - "A接点"
  - "RSW(2/1/0)"
  - "7SEG"
source_path: "総点(u型エス)/その他/安全スイッチ情報の確認.md"
source_filename: "安全スイッチ情報の確認.md"
onenote_id: "c3c2f392-7d60-46db-b6a4-f3973a5f37e4:65"
related_ids: []
attachment_paths: []
reference_links: []
document_references: []
evidence_sources:
  - source_id: "evidence-esc-safety-switch-contact-original"
    source_type: "vault_original"
    title: "その他 安全スイッチ情報の確認（原文）"
    source_path: "総点(u型エス)/その他/安全スイッチ情報の確認.md"
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-01"
    supports:
      - "A接点情報のラッチ設定と安全スイッチ動作時の表示に関する原文記述"
structured_data:
  source_notes:
    - "設定値は原文の記述をそのまま転記したもので、承認済み設定値・変更指示として検証していない。"
    - "原文はHSSのみ別設定と注意書きしている。適用機種・制御版・変更条件は未確認。"
---

# u形エスカレーター 安全スイッチ情報設定の原文記述

## 原文記載

- A接点情報ラッチなしとして、`RSW(2/1/0) -> (0/0/3)` に設定する記述。
- HSSのみ `RSW(2/1/0) -> (0/0/0)` とする注意書き。
- 各安全スイッチ動作時に、該当コードが7SEGに表示されるとの記述。

設定対象の機種・制御版、値の現行性、変更権限は確認していない。実機設定や安全回路の作業指示として使用しない。

## 出典・確認履歴

- 原文ノート: [[総点(u型エス)/その他/安全スイッチ情報の確認]]
- 関連する安全スイッチ機能資料への原文リンク: [[エスカ（u形）/エス安全スイッチの機能]]
- 技術・安全・制御レビュー前のドラフト。