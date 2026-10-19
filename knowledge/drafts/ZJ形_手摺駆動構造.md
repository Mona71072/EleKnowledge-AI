---
schema_version: 1
record_id: "zj2-handrail-drive"
record_version: 1
title: "ZJ形エスカレーターの手摺駆動構造"
category: "エスカ　(ZJ2)"
record_type: "technical_reference"
product: "エスカレーター"
model_type:
  - "ZJ形"
document_number: ""
revision: ""
effective_date: ""
review_status: "in_review"
publication_status: "not_published"
classification: "unknown"
cloud_approval: "not_reviewed"
keywords:
  - "手摺駆動"
  - "駆動ローラ"
  - "加圧ローラ"
  - "上部水平トラス"
source_path: "エスカ　(ZJ2)/手摺駆動の構造.md"
source_filename: "手摺駆動の構造.md"
onenote_id: "f87a85a3-f59a-40cb-8a51-d6c41d5b5abb:21"
related_ids:
  - "r-r2-handrail-drive"
attachment_paths:
  - "エスカ　(ZJ2)/OneNote/手摺駆動の構造 image.png"
reference_links: []
document_references: []
evidence_sources:
  - source_id: "evidence-zj2-handrail-original"
    source_type: "vault_original"
    title: "ZJ形エスカレーターの手摺駆動構造（原文）"
    source_path: "エスカ　(ZJ2)/手摺駆動の構造.md"
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-01"
    supports:
      - "駆動力の伝達経路"
      - "ZJ形の設計上の特徴"
structured_data:
  specifications:
    - name: "基本の駆動力伝達"
      value: "上部水平トラス内の駆動機からチェーンを介して手摺駆動装置の駆動ローラへ伝達する"
      unit: ""
      condition: "ZJ形エスカレーター"
    - name: "手摺の駆動"
      value: "手摺を駆動ローラと加圧ローラで挟んで駆動する"
      unit: ""
      condition: "ZJ形エスカレーター"
  design_features:
    - "手摺駆動力を増加させるため、手摺駆動装置を増やす対策がある"
    - "階高によって手摺駆動装置（駆動ローラ）を増やしている"
  source_notes:
    - "押し付け力と乗客負荷の関係について、原文だけでは比較条件・意図を確定できないため、原文確認要"
---

# ZJ形エスカレーターの手摺駆動構造

## 概要

原資料によると、ZJ形エスカレーターの手摺駆動構造は、基本的にJ形エスカレーターと同様である。上部水平トラス内の駆動機からチェーンを介して手摺駆動装置の駆動ローラへ力を伝え、手摺を駆動ローラと加圧ローラで挟んで駆動する。

## 適用範囲

- 対象: ZJ形エスカレーター
- 比較対象として原資料に記載: J形、R形
- 原資料に階高ごとの装置数・適用条件の具体値はない。

## 駆動力の伝達

1. 上部水平トラス内の駆動機が駆動力を発生させる。
2. チェーンを介して手摺駆動装置の駆動ローラへ伝える。
3. 手摺を駆動ローラと加圧ローラで挟み、駆動する。

![[エスカ　(ZJ2)/OneNote/手摺駆動の構造 image.png]]

## ZJ形の特徴

- 原資料では、手摺駆動力を増加させるため、手摺駆動装置を増やす対策があると説明している。
- 手摺駆動装置（駆動ローラ）の数は階高によって増やすと記載されている。

## 原文確認が必要な箇所

原資料には「手摺駆動の押し付け力を増加させた場合、R形のように乗客負荷で駆動力が変動しないため、常に駆動ローラーを押し付けられない」とある。この文の比較条件と因果関係は原文だけでは明確でないため、意味を補って解釈していない。担当者または関連図面による確認が必要。

R形整備版には、手摺走行負荷に応じて挟圧力が変化する機構が記録されている。ただし、ZJ形原文の比較文がこの機構のどの条件を指すかは確認できていないため、両方式の優劣・適用条件の比較は保留する。

## 関連資料

- 原文ノート: [[エスカ　(ZJ2)/手摺駆動の構造]]
- 関連資料: [[整備済み資料/技術資料/R形エスカレーター_手摺駆動構造]]
- 同分類の索引: [[エスカ　(ZJ2)/索引]]
- [[EleKnowledge-AI向け資料整備ルール]]
- [[資料構造化データ仕様]]

## 出典・確認履歴

- 出典: `エスカ　(ZJ2)/手摺駆動の構造.md`
- OneNote ID: `f87a85a3-f59a-40cb-8a51-d6c41d5b5abb:21`
- 画像出典: `エスカ　(ZJ2)/OneNote/手摺駆動の構造 image.png`
- 状態: 原文との照合済み。技術内容の承認・最新版確認は未実施。
- クラウド利用承認: 未確認。EleKnowledge/S3公開対象にはしない。
