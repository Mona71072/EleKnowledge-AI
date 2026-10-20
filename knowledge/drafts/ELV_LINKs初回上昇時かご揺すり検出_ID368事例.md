---
schema_version: 1
record_id: "elv-links-first-upward-run-car-shake-detection-id368"
record_version: 1
title: "LINKsの初回上昇時におけるかご揺すり検出事例（ID368）"
category: "不具合対応(ELV)"
record_type: "troubleshooting_case"
product: "エレベーター"
model_type:
  - "AXIEZ-LINKS"
document_number: ""
revision: ""
effective_date: ""
review_status: "in_review"
publication_status: "not_published"
classification: "unknown"
cloud_approval: "not_reviewed"
keywords:
  - "かご揺すり検出"
  - "初回上昇運転"
  - "レゾルバ"
  - "振動"
source_path: ""
source_filename: "技術情報リスト（協力会社展開用）.xlsx"
onenote_id: ""
related_ids: []
attachment_paths: []
reference_links: []
document_references:
  - document_number: "C-7-C3900"
    title: "原リストが参照する調整資料"
    locator: "原リスト記載。本文・版・適用箇所未確認"
    source_path: ""
  - document_number: "C-22-C300.1-J"
    title: "原リストが参照するローラーガイド資料"
    locator: "原リスト記載。本文・版・適用箇所未確認"
    source_path: ""
evidence_sources:
  - source_id: "evidence-list-elv-links-car-shake-first-upward-368"
    source_type: "user_provided_extract"
    title: "協力会社展開用Excel: LINKs初回上昇時のかご揺すり検出（ID368）"
    source_path: ""
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-13"
    supports:
      - "長時間停止後の初回上昇時に揺すり検出した症状と、調整後に解消したとの報告"
structured_data:
  symptom: "AXIEZ-LINKSで長時間運転しなかった後の初回上昇運転時に揺すり検出となり、その後の運転では再検出しないことがあったとの報告。"
  cause_assessment: "原リストは回転検出の誤差成分と機械系応答との相互作用による振動を原因候補としている。仮説であり、波形・機械状態・信号品質等の独立検証は未実施。"
  outcome: "原リストは制御調整後に症状が解消したと報告する。対象版・変更値・継続確認・他設備への適用性は未確認。"
  limitations:
    - "原リスト記載の制御パラメータ名・値・調整方法、校正/学習運転、波形測定、配線確認や機械点検の手順は転載しない。"
    - "参照資料本文・改訂・機種適用と調整の承認状態は未確認。"
    - "本記録を振動判定、設定変更、運転継続/停止の判断に使用しない。"
---

# LINKsの初回上昇時におけるかご揺すり検出事例（ID368）

首都工・不具合情報共有リストID368は、AXIEZ-LINKSで長時間運転しなかった後の初回上昇運転時に揺すりを検出し、その後の数回の運転では検出しなくなる事例を報告する。

原リストは、回転検出の誤差成分と機械系応答との相互作用が振動を生じさせる可能性を原因候補としているが、これは仮説であり独立確認していない。制御調整後に解消したとの記載はあるものの、対象ソフト/制御版、変更値、継続確認、他設備への適用性は不明である。

原リストが参照する資料の本文・改訂・適用箇所も未確認。パラメータ名・値・調整方法、校正運転、波形測定、配線確認、機械点検の手順は記載しない。本記録を設定変更や運転判断に使用しない。