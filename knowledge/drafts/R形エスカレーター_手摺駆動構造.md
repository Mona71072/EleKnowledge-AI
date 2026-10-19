---
schema_version: 1
record_id: "r-r2-handrail-drive"
record_version: 1
title: "R形エスカレーターの手摺駆動構造"
category: "エスカ（R,R2形)"
record_type: "technical_reference"
product: "エスカレーター"
model_type:
  - "R形"
  - "R2V"
document_number: ""
revision: ""
effective_date: ""
review_status: "in_review"
publication_status: "not_published"
classification: "unknown"
cloud_approval: "not_reviewed"
keywords:
  - "手摺駆動"
  - "挟圧力"
  - "駆動ローラー"
  - "加圧ローラー"
  - "第1チェーン"
  - "第2チェーン"
source_path: "エスカ（R,R2形)/R形手摺駆動構造.md"
source_filename: "R形手摺駆動構造.md"
onenote_id: "d0845977-de8f-471e-9ff8-b6dad78128fe:16"
related_ids:
  - "zj2-handrail-drive"
attachment_paths:
  - "エスカ（R,R2形)/OneNote/R形手摺駆動構造 image.png"
  - "エスカ（R,R2形)/OneNote/R形手摺駆動構造 image 1.xps"
  - "エスカ（R,R2形)/OneNote/R形手摺駆動構造 image 2.xps"
  - "エスカ（R,R2形)/OneNote/R形手摺駆動構造 image 3.xps"
  - "エスカ（R,R2形)/OneNote/R形エスの手摺駆動メカニズム.pptx"
reference_links: []
document_references: []
evidence_sources:
  - source_id: "evidence-r-r2-handrail-original"
    source_type: "vault_original"
    title: "R形手摺駆動構造（原文）"
    source_path: "エスカ（R,R2形)/R形手摺駆動構造.md"
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-01"
    supports:
      - "挟圧力可変方式の概要と構造"
      - "チェーン張力変化による駆動ローラーの動作"
      - "ストッパーボルト間隙に関する注意"
structured_data:
  specifications:
    - name: "挟圧力"
      value: "手摺走行負荷に応じて運転中に変化する"
      unit: ""
      condition: "R形（R2V含む）エスカレーター"
    - name: "駆動ローラーの可動"
      value: "ガイド機能により上下に動く"
      unit: ""
      condition: "手摺チェーン張力の変化に応じる"
  design_features:
    - "加圧ローラー組立はトラスに固定されている"
    - "駆動ローラー組立は上下に動き、手摺への挟圧力を変える"
  source_notes:
    - "動作の説明は原資料の記載を整理したもの。技術内容の承認および最新版確認は未実施。"
---

# R形エスカレーターの手摺駆動構造

## 概要

R形（R2V含む）エスカレーターでは、駆動ローラーと加圧ローラーで手摺を挟み、手摺を駆動する。手摺走行の負荷に応じて挟圧力が運転中に変化する方式である。

加圧ローラー組立はトラスに固定されている。一方、駆動ローラー組立はガイドに沿って上下に動き、手摺チェーンの張力変化に応じて手摺への押し付け力を変える。

![[エスカ（R,R2形)/OneNote/R形手摺駆動構造 image.png]]

## 動作の流れ

1. **手摺の走行抵抗が増える。** 原資料では、乗客が手摺を持つことで手摺が引っ張られ、手摺とクリップガイドの摩擦力が増して走行抵抗が上がると説明している。
2. **チェーン張力が増える。** 走行抵抗によって駆動ローラーには駆動力と逆向きの力が加わる。上部スプロケットからの駆動力と駆動ローラー側の抵抗により第2チェーンの張力が増し、2連スプロケットを介して第1チェーンの張力も増加する。
3. **駆動ローラーが手摺を強く押す。** 第1チェーンの張力で2連スプロケットが引かれ、駆動ローラーが下がる。手摺への押し付けが強まり、駆動力が増す。

動作図（第2チェーン張力の変化）：

![[エスカ（R,R2形)/OneNote/R形手摺駆動構造 image 1.xps]]

動作図（第1チェーン張力の変化）：

![[エスカ（R,R2形)/OneNote/R形手摺駆動構造 image 2.xps]]

動作図（駆動ローラーが下がる方向）：

![[エスカ（R,R2形)/OneNote/R形手摺駆動構造 image 3.xps]]

## 点検上の注意

ストッパーボルトの間隙を広く設定すると、駆動ローラーの押し付けが強くなり、手摺の剥離や損傷につながるおそれがある。総点時の間隙確認・設定方法は、[R形エス検査準備（引渡し前点検・総点）](../../エスカ（R,R2形)/R形エス検査準備(引渡し前点検_総点).md)を参照する。

## 関連資料

- 原文ノート: [[エスカ（R,R2形)/R形手摺駆動構造]]
- 関連する比較資料: [[整備済み資料/技術資料/ZJ形_手摺駆動構造]]。ZJ形原文にはR形との比較記述があるが、比較条件・因果関係は未確定。
- 原資料の説明資料: [R形エスの手摺駆動メカニズム.pptx](../../エスカ（R,R2形)/OneNote/R形エスの手摺駆動メカニズム.pptx)
- [[資料構造化データ仕様]]

## 出典・確認履歴

- 出典: `エスカ（R,R2形)/R形手摺駆動構造.md`
- OneNote ID: `d0845977-de8f-471e-9ff8-b6dad78128fe:16`
- 添付: `エスカ（R,R2形)/OneNote/`
- 状態: 原文の記述を整理。技術内容の承認・最新版確認は未実施。
- クラウド利用承認: 未確認。EleKnowledge/S3公開対象にはしない。
