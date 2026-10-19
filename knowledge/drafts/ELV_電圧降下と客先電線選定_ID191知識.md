---
schema_version: 1
record_id: "knowhow-elv-voltage-drop-customer-wiring-id191"
record_version: 1
title: "電圧降下と客先電線選定に関する情報（ID191）"
category: "技術メモ【ELV】２"
record_type: "knowhow"
product: "エレベーター"
model_type: []
document_number: ""
revision: ""
effective_date: ""
review_status: "in_review"
publication_status: "not_published"
classification: "unknown"
cloud_approval: "not_reviewed"
keywords:
  - "電圧降下"
  - "客先電線"
  - "受電盤"
  - "圧着端子"
  - "内線規程"
source_path: "首都工・不具合情報共有リスト.xlsx"
source_filename: "首都工・不具合情報共有リスト.xlsx"
onenote_id: ""
related_ids: []
attachment_paths: []
reference_links: []
document_references:
  - document_number: ""
    title: "内線規程"
    locator: "1310-1（ID191に記載。本文・版・現行性未確認）"
    source_path: ""
evidence_sources:
  - source_id: "evidence-list-elv-voltage-drop-id191"
    source_type: "vault_original"
    title: "首都工・不具合情報共有リスト: 電圧降下を考慮した客先電線サイズについて（ID191）"
    source_path: "首都工・不具合情報共有リスト.xlsx"
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-14"
    supports:
      - "電圧降下と電線サイズに関する原リストの説明"
      - "端子台と圧着端子のサイズ不一致による破損リスクの注意"
      - "端子台損傷原因に関する未解決の問い"
structured_data:
  knowledge_items:
    - topic: "電圧降下と電線サイズ"
      statement: "一次リストは、電線長・負荷電流・電線抵抗/断面積を関係要因として挙げ、受電位置から受電盤までの距離を考慮して電線サイズを決めると説明する。これは出典上の一般説明であり、個別設備の設計値や選定承認ではない。"
      conditions:
        - "一次リストは内線規程1310-1を参照するが、規程本文・版・現行性は未確認。"
        - "電圧降下の数値基準・緩和条件・計算式は、適用確認前のため本文に転載していない。"
      exceptions:
        - "仮設盤の電線サイズは電気担当者に計算を依頼するのが無難との説明がある。"
      rationale: "電線長や電気的条件により負荷端の電圧が変化し得るとの説明。現行規程・個別設計への適用は未確認。"
      verification_status: "source_recorded"
      evidence_source_ids:
        - "evidence-list-elv-voltage-drop-id191"
    - topic: "電線・圧着端子と端子台の適合"
      statement: "一次リストは、電線に対して大きい圧着端子が端子台に適合しない場合、端子台を損傷するおそれがあると注意する。適合する端子の選定や施工指示は示していない。"
      conditions:
        - "CB型圧着端子の一部にJIS規格外のものがあるとの記載は、具体的製品・規格本文・適用範囲を未確認。"
      exceptions: []
      rationale: "端子台と圧着端子のサイズ不一致が破損リスクとなるとの原リスト説明。"
      verification_status: "source_recorded"
      evidence_source_ids:
        - "evidence-list-elv-voltage-drop-id191"
    - topic: "端子台破損の発生原因"
      statement: "上部受電と下部受電の取り違えが原因かという問いがあるが、ID191は原因を特定していない。"
      conditions: []
      exceptions: []
      rationale: "原リストの問いかけを、確認済み原因と混同しないため。"
      verification_status: "unresolved"
      evidence_source_ids:
        - "evidence-list-elv-voltage-drop-id191"
---

# 電圧降下と客先電線選定に関する情報（ID191）

## 出典上の説明

首都工・不具合情報共有リストのID191は、電圧降下と客先電線サイズの関係を説明し、内線規程1310-1を参照する。受電位置から受電盤までの距離、電線長や負荷条件を考慮するという一般説明は原リスト上の記載であり、個別設備の設計値・承認条件ではない。規程本文・版・現行性は未確認。

電線と圧着端子のサイズが端子台に適合しない場合の破損リスク、および一部のCB型圧着端子に関する規格上の注意も記載されるが、製品・規格・適用範囲は確認していない。

## 未解決事項

端子台損傷の原因として受電方式の取り違えが質問されているが、ID191は原因を確定していない。個別端子台損傷の原因、適合部品、電線選定、規程の数値基準・計算式はいずれも未確認のため、本記録では数値・式・具体的な選定方法を掲載しない。

内線規程の現行版、対象設備の承認済み設計図書、電気担当部門の確認が得られるまで、電線/端子の選定、接続、適合・規格判断に使用しない。

## 出典・確認状態

- 出典: `首都工・不具合情報共有リスト.xlsx`（ID191、sheet1 row233）。
- 端子台破損の原因、現行規程の内容、製品適合、個別設計条件は未確認。電圧降下の基準値・緩和値・計算式、端子識別、接続/測定手順は転載していない。
- 技術・電気レビュー前の下書きであり、設計・施工・検査判断に使用しない。