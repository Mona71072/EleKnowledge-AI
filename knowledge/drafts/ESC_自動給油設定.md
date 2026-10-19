---
schema_version: 1
record_id: "esc-auto-lubrication-nozzle"
record_version: 1
title: "エスカレーター自動給油装置の設定に関する原文整理"
category: "エスカ機種一覧"
record_type: "procedure"
knowledge_domain: "engineering_business"
organizational_scope: "unknown"
product: "エスカレーター"
model_type:
  - "SVFB"
  - "SVFC"
  - "R形"
document_number: ""
revision: ""
effective_date: ""
review_status: "in_review"
publication_status: "not_published"
classification: "unknown"
cloud_approval: "not_reviewed"
keywords:
  - "自動給油"
  - "給油ノズル"
  - "SVFB"
  - "SVFC"
source_path: "エスカ機種一覧/エス検査(総点)/自動給油装置(給油ノズル).md"
source_filename: "自動給油装置(給油ノズル).md"
onenote_id: "6f5ba25b-61e7-445e-ab15-77b81a9664e5:94"
related_ids:
  - "esc-svfc-energy-saving"
attachment_paths:
  - "エスカ機種一覧/エス検査(総点)/OneNote/自動給油装置(給油ノズル) image.png"
  - "エスカ機種一覧/エス検査(総点)/OneNote/自動給油装置(給油ノズル) image.emf"
  - "エスカ機種一覧/エス検査(総点)/OneNote/自動給油装置(給油ノズル) image 1.png"
  - "エスカ機種一覧/エス検査(総点)/OneNote/自動給油装置(給油ノズル) image 2.png"
  - "エスカ機種一覧/エス検査(総点)/OneNote/自動給油装置(給油ノズル) image 3.png"
  - "エスカ機種一覧/エス検査(総点)/OneNote/自動給油装置(給油ノズル) image.xps"
  - "エスカ機種一覧/エス検査(総点)/OneNote/自動給油装置(給油ノズル) image 1.xps"
reference_links: []
document_references:
  - document_number: "AF-323"
    title: "AF-323"
    locator: ""
    source_path: "エスカ機種一覧/エス検査(総点)/OneNote/AF-323.pdf"
evidence_sources:
  - source_id: "evidence-esc-auto-lubrication-original"
    source_type: "vault_original"
    title: "自動給油装置（給油ノズル）（原文）"
    source_path: "エスカ機種一覧/エス検査(総点)/自動給油装置(給油ノズル).md"
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-01"
    supports:
      - "制御方式・u形区分ごとのスイッチ状態"
      - "R形給油ノズル取付方向についての原文記述"
structured_data:
  preconditions:
    - "作業前に対象機種、制御方式、製造時期、最新の承認済み手順を照合する。"
  steps:
    - order: 1
      action: "原文記載の制御方式・機種区分に対応する設定を確認する。"
      expected_result: "下表のスイッチ状態と一致する。"
    - order: 2
      action: "R形の対象号機では、給油ノズルの適用と取付方向を最新資料で確認する。"
      expected_result: "原文は25/2A生産以降の号機について鉛直方向（重力方向）と記載する。"
  safety_warnings:
    - "この整理は作業指示ではない。図版・改訂・適用号機の確認前に設定を変更しない。"
  source_notes:
    - "u形エスの追加説明とフード取付方法は画像中心で、画像内容は未確認。"
    - "「25/2A生産以降」は原文表記をそのまま保持し、年月等へ読み替えていない。"
---

# エスカレーター自動給油装置の設定に関する原文整理

## 制御方式別のスイッチ状態

| 制御方式・機種区分 | 給油装置スイッチを押す前の設定 |
| --- | --- |
| SVFB | ACB: OFF、LIGHT: ON |
| SVFC（u形以外） | ACB: OFF、MTB: ON |
| SVFC（u形） | ACB: ON、SCP: OFF、短絡コネクタ抜取 |

原文はu形エスについて別途参照を示しているが、その詳細は添付画像にあり、ここでは読み取っていない。

## R形給油ノズル

- 原文は、R形の自動給油装置組立で給油ノズル取付方法が変更されたと記載している。
- 原文は「25/2A生産以降の号機」について全箇所のノズル先端を針付きに変更し、取付方向を鉛直方向（重力方向）にするとしている。
- フード取付方法と図示内容は添付画像・XPSにあり、未確認。

この資料は制御方式、機種、製造時期で条件が分かれる。対象機の最新承認資料を照合せず、作業手順として使用しない。

## 関連資料

- 原文ノート: [[エスカ機種一覧/エス検査(総点)/自動給油装置(給油ノズル)]]
- SVFC省エネ運転（運転速度の資料であり、給油設定とは別）: [[整備済み資料/技術資料/SVFC省エネ運転]]
- 参照資料: [[エスカ機種一覧/エス検査(総点)/OneNote/AF-323.pdf]]

## 出典・確認履歴

- OneNote ID: `6f5ba25b-61e7-445e-ab15-77b81a9664e5:94`
- 画像・EMF・XPS計7点とAF-323.pdfはVault内で実在確認済み。中身は未確認。
- 技術レビュー・製造時期の解釈・改訂確認・情報管理承認前のドラフト。
