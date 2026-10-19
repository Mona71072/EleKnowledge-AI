---
schema_version: 1
record_id: "case-axiez-links-gaw-wos-supply-unavailable-20261009"
record_version: 1
title: "AXIEZ-LINKs GAW/WOS工法切替時の供給不成立事例"
category: "技術メモ【ELV】２"
record_type: "troubleshooting_case"
product: "エレベーター"
model_type:
  - "AXIEZ-LINKs"
document_number: ""
revision: "リスト記載。現行性未確認"
effective_date: ""
review_status: "in_review"
publication_status: "not_published"
classification: "unknown"
cloud_approval: "not_reviewed"
keywords:
  - "GAW工法"
  - "WOS工法"
  - "据付工程"
source_path: ""
source_filename: ""
onenote_id: ""
related_ids: []
attachment_paths: []
reference_links: []
document_references:
  - document_number: "TI-1335"
    title: "AXIEZ-LINKs GAW工法からWOS工法切替時の注意事項"
    locator: "リストに記載された参照資料。本文・版・現行性は未確認"
    source_path: ""
evidence_sources:
  - source_id: "evidence-list-axiez-links-gaw-wos-supply-345"
    source_type: "user_provided_extract"
    title: "首都工・不具合情報共有リスト: AXIEZ-LINKs工法切替時の供給不成立"
    source_path: ""
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-09"
    supports:
      - "GAWからWOSへの工法切替時に、制御盤側の接続条件不一致と付帯設備への供給不成立が報告されていること"
structured_data:
  case_summary:
    symptom: "AXIEZ-LINKsでGAWからWOSへ工法を切り替える際、ブザーやコンセントが使用できない事象がリストに報告されている。"
    findings:
      - "リストは、制御盤側の接続条件不一致により付帯設備への供給が成立しない可能性を記載している。"
      - "リストは恒久対策の実施と、対策部材の取付漏れが起こり得ることを報告している。"
    cause_assessment: "記載された原因・対策はリスト上の報告であり、図面・資料本文・実機で独立確認していない。"
    conditions:
      - "AXIEZ-LINKsの個別事例。リストに記載された生産時期の境界表記も未検証。"
      - "足場工法とWOS工法で条件が異なるとのリスト記載は、現行の承認済み資料で未確認。"
  knowledge_items:
    - topic: "工法切替時は対象構成と付帯設備への供給条件を承認資料で照合する"
      statement: "首都工・不具合情報共有リストID345は、AXIEZ-LINKsのGAWからWOSへの切替時に、制御盤側の接続条件不一致に伴ってブザーやコンセントへの供給が成立しない事例を報告する。恒久対策の取付漏れも報告されている。"
      conditions:
        - "特定機種・工法切替に関する一事例であり、他機種・他構成へ一般化しない。"
        - "対象時期、標準構成、対策の現行性は未確認。"
      exceptions:
        - "電圧、端子/コネクタ識別、部品番号、接続・取付・復旧手順は記載しない。"
        - "TI-1335本文と承認済み現行図面を確認するまで、施工・電源・設備使用の判断に使わない。"
      rationale: "工法切替と盤構成の差を設計/施工前の照合事項として残し、未検証のリスト記載を作業手順へ変換しないため。"
      verification_status: "source_recorded"
      evidence_source_ids:
        - "evidence-list-axiez-links-gaw-wos-supply-345"
  source_notes:
    - "現場名・号機・共有者情報、電圧値、部品/端子識別、具体的接続・取付操作は転記していない。"
    - "リスト本文とTI-1335、現行図面、恒久対策の承認・適用範囲は未確認。"
    - "技術・安全レビュー前の社内下書き。施工、電源操作、設備使用の判断に利用しない。AWS/S3送信なし。"
---

# AXIEZ-LINKs GAW/WOS工法切替時の供給不成立事例

## 事例概要

首都工・不具合情報共有リストID345は、AXIEZ-LINKsでGAWからWOSへ工法を切り替える際、制御盤側の接続条件が合わず、ブザーやコンセントが使用できない事象を報告している。リストは恒久対策の実施と、対策部材の取付漏れが起こり得ることも記載する。これらはリスト上の報告であり、原因・対策の独立検証は行っていない。

生産時期の境界表記、対象構成、現行の対策状態は未確認である。足場工法など他の構成への適用を推定しない。

## 確認境界

リストが参照するTI-1335の本文・版・現行性、承認済み図面、恒久対策の適用範囲は未確認。電圧、部品/端子識別、接続・取付・復旧操作は記録していない。技術・安全担当による照合前に、施工・電源・設備使用の判断へ利用しない。