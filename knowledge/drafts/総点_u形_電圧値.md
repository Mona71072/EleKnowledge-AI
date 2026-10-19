---
schema_version: 1
record_id: "esc-voltage-check"
record_version: 1
title: "u形エスカレーター 電圧測定に関する原文記述と未解決注釈"
category: "総点(u型エス)"
record_type: "technical_reference"
product: "エスカレーター"
model_type:
  - "u形"
document_number: "IN-ES-0B-019-13"
revision: ""
effective_date: ""
review_status: "in_review"
publication_status: "not_published"
classification: "unknown"
cloud_approval: "not_reviewed"
keywords:
  - "電圧測定"
  - "Δ結線"
  - "Y結線"
  - "対地電圧"
source_path: "総点(u型エス)/上部機械室/電圧値.md"
source_filename: "電圧値.md"
onenote_id: "c3c2f392-7d60-46db-b6a4-f3973a5f37e4:70"
related_ids: []
attachment_paths:
  - "総点(u型エス)/上部機械室/OneNote/電圧値 image.jpg"
  - "総点(u型エス)/上部機械室/OneNote/電圧値 image.png"
  - "総点(u型エス)/上部機械室/OneNote/電圧値 image 1.jpg"
  - "総点(u型エス)/上部機械室/OneNote/電圧値 image 1.png"
  - "総点(u型エス)/上部機械室/OneNote/電圧値 image 2.png"
  - "総点(u型エス)/上部機械室/OneNote/電圧値 image 3.png"
  - "総点(u型エス)/上部機械室/OneNote/電圧値 image 4.png"
reference_links: []
document_references:
  - document_number: "IN-ES-0B-019-13"
    title: "IN-ES-0B-019-13"
    locator: "P.3"
    source_path: ""
  - document_number: "IN-ES-0B-019-13"
    title: "IN-ES-0B-019-13"
    locator: "P.32"
    source_path: ""
evidence_sources:
  - source_id: "evidence-esc-voltage-original"
    source_type: "vault_original"
    title: "電圧値（原文）"
    source_path: "総点(u型エス)/上部機械室/電圧値.md"
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-01"
    supports:
      - "動力および照明系統の測定項目と注釈状態"
structured_data:
  specifications:
    - name: "各相間電圧"
      value: "定格の±5%"
      unit: ""
      condition: "原文記載。対象相はR-S、S-T、T-R"
    - name: "各相間電圧不平衡率"
      value: "3%以内"
      unit: ""
      condition: "原文記載"
    - name: "接地相Δ結線のS相-対地間"
      value: "約0"
      unit: "V"
      condition: "原文記載。R/T-対地測定は不要との記述あり"
    - name: "接地相Y結線の各相-対地間電圧"
      value: "約230-254"
      unit: "V"
      condition: "400 V系と原文に記載"
  source_notes:
    - "色付きの質問、回答メモ、同じ条件の重複記載を、検証済み仕様へ統合していない。"
    - "照明回路の許容範囲について質問と回答メモがあり、引用先本文・適用条件は未確認。"
    - "図版7点は実在確認のみ。回路・計算内容は未読解。"
---

# u形エスカレーター 電圧測定に関する原文記述と未解決注釈

## 原文本文に記載された項目

- 動力測定対象としてR-S、S-T、T-R相およびS-対地間を挙げ、R/T-対地測定は不要と記載されている。
- 各相間電圧は定格の±5%、各相間電圧の不平衡率は3%以内と記載されている。
- 接地相Δ結線はS-対地間が約0 Vと記載され、対地間が300 Vを超えないことの確認という説明もある。
- 接地相Y結線は400 V系の各相-対地間が約230-254 Vと記載されている。
- 照明はL1-L2間、L2-対地間を測定対象としている。

## 未解決の質問・回答メモ

- 原文には「照明の許容範囲は±5%ではないか」という質問が残っている。
- 回答メモには「AC100～105 V±5%（95～110.25 V）」およびIN-ES-0B-019-13 P.32への参照が記されているが、その参照資料本文は未確認。
- 「L2-対地間で0 V」とする記述と、両方とも0 Vでない場合に電設担当へ連絡する記述がある。質問・回答の解決状態と適用条件は確定できない。
- Δ/Y結線の説明にも確認コメントが残る。添付回路図・計算図は未読解。

これらは原文内の質問・メモを分けて記録したもので、承認済み判定基準として統合していない。電圧測定・電気作業には使用せず、最新の承認済み要領と電設担当の確認を優先する。

## 出典・確認履歴

- 原文ノート: [[総点(u型エス)/上部機械室/電圧値]]
- 添付7点はVault内で実在確認済み。画像・IN-ES-0B-019-13本文・版は未確認。
- 技術・安全レビュー前のドラフト。電気作業判断に使わない。