---
schema_version: 1
record_id: "elv-axiez-links-slow-dn-relevel-stop-id55-case"
record_version: 1
title: "AXIEZ-LINKSの低速DN時リレベル検知による停止事例（ID55）"
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
  - "低速DN"
  - "リレベルプレート"
  - "847"
  - "終点スイッチ"
related_ids:
  - "elv-temporary-slow-issues"
source_path: ""
source_filename: ""
onenote_id: ""
attachment_paths: []
reference_links: []
document_references: []
evidence_sources:
  - source_id: "evidence-list-axiez-links-slow-dn-relevel-stop-055"
    source_type: "user_provided_extract"
    title: "首都工・不具合情報共有リスト: スローDN時リレベルプレート検知による停止（ID55）"
    source_path: ""
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-09"
    supports:
      - "PADプレート取付後の低速DN時にリレベル検知で停止・速度変化した症状、847表示、下部終点スイッチ系のピン保持不良との原因報告、一時対応・交換予定"
structured_data:
  equipment: "AXIEZ-LINKS"
  symptom: "本スロー中にPADプレートを取り付けた条件で、DN時にリレベルを検知すると一旦停止し、再DN時の速度が変化したとの報告。リレベルを外れると元の速度に戻り、UP運転では問題がなかったとする。4 m/min・15 m/minは単一事例の記録値であり、設定値や運転指示ではない。"
  error_codes:
    - "847（PSL ON故障。原リスト記載。現行コード定義未確認。）"
  cause: "下部終点スイッチ系のコネクタでピン保持不良があったことを原因としている。原因・因果関係はリスト上の報告であり独立確認していない。"
  verified_actions: []
  outcome: "ピン保持不良への一時対応後に確認運転を行い、そのまま使用中とする記載がある。一方、保持状態が再発し得るため代品を手配し、調整時に交換予定としており、恒久対応は未完了。具体的なコネクタ識別、ピン操作、固定・確認運転の方法は記録しない。"
---

# AXIEZ-LINKSの低速DN時リレベル検知による停止事例（ID55）

首都工・不具合情報共有リストID55は、本スロー中にPADプレートを取り付けた条件で、DN時にリレベルを検知すると一旦停止し、再DN時の速度が変化したと報告する。リレベルを外れると元の速度に戻り、UP運転では問題がなかったとの記載がある。4 m/min・15 m/minは単一事例の記録値であり、設定値や運転指示ではない。エラー表示欄には847（PSL ON故障）が記載されるが、現行コード定義は未確認である。

## 原因報告と進捗

リストは下部終点スイッチ系コネクタのピン保持不良を原因としている。一時対応後に確認運転を行い使用中とする一方、保持不良が再発し得るため代品を手配し、調整時に交換予定としている。したがってリスト上は暫定対応段階であり、恒久対応の完了・原因の独立確認は未確認である。

ID342も低速DN時のリレベル検知と847表示を含む類似報告だが、原因箇所の記載が異なるため別事例として扱う。原文中の共有URLや個別接続部品の識別、ピン操作・固定方法・確認運転の手順は記録しない。本記録は事例検索用で、運転・診断・復旧手順ではない。