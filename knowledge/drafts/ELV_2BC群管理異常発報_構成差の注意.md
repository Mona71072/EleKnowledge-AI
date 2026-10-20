---
schema_version: 1
record_id: "knowhow-elv-2bc-group-error-annunciation-topology-caveat-20261009"
record_version: 2
title: "群管理異常の意図的発報に関する構成差と安全上の注意"
category: "不具合対応(ELV)"
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
  - "2BC"
  - "群管理異常"
  - "構成差"
  - "意図的な異常発生"
related_ids:
  - "elv-group-operation-issues"
  - "list-id286-group-management-alarm-forcing-method"
source_path: ""
source_filename: ""
onenote_id: ""
attachment_paths: []
reference_links: []
document_references: []
evidence_sources:
  - source_id: "evidence-list-2bc-group-error-annunciation-topology-047"
    source_type: "user_provided_extract"
    title: "首都工・不具合情報共有リスト: 2BCの群管理異常発報に関する記載（ID47）"
    source_path: ""
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-09"
    supports:
      - "2BCにはLANケーブルがないとの記載、およびリスト上の対応状況が未確認であること"
  - source_id: "evidence-list-group-error-annunciation-method-286"
    source_type: "user_provided_extract"
    title: "協力会社展開用Excel: 群管理異常を発報させる方法（ID286）"
    source_path: ""
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-13"
    supports:
      - "群管理異常を意図的に発生させる操作案内が原リストにあること"
      - "群管理方式により発報方法が異なるとの説明"
structured_data:
  knowledge_items:
    - topic: "2BCではLAN経路を前提とする群管理異常の発報方法をそのまま適用できないとの注意"
      statement: "首都工・不具合情報共有リストID47は、2BCにはLANケーブルがないと記載している。このため、LAN経路を前提とする他構成の群管理異常発報方法を2BCへそのまま当てはめられない。"
      conditions:
        - "2BCについての個別記載。現行構成・機種適用は未確認。"
        - "原リストの対応状況欄は『未確認』。"
      exceptions:
        - "原文にある異常を意図的に発報させる電気操作は転載せず、本記録は試験・診断手順ではない。"
      rationale: "異なる群管理構成へ発報方法を誤って一般化しないため。"
      verification_status: "source_recorded"
      evidence_source_ids:
        - "evidence-list-2bc-group-error-annunciation-topology-047"
    - topic: "群管理異常を意図的に発報させる操作に関する注意"
      statement: "協力会社展開用Excel ID286には、群管理方式ごとに異なる発報方法と、意図的に異常を発生させる操作が記載されている。具体操作は転載しない。"
      conditions:
        - "対象構成・目的・承認状態・現行手順は未確認。"
      exceptions:
        - "本記録は発報試験/診断手順ではない。"
      rationale: "誤った構成へ操作を適用したり、稼働設備に意図的な通信/群管理異常を生じさせたりする危険を避ける。"
      verification_status: "source_recorded"
      evidence_source_ids:
        - "evidence-list-group-error-annunciation-method-286"
  source_notes:
    - "出典にある具体的な発報操作、盤内部品の識別、操作時間は、意図的な異常発生につながるため転載していない。構成差と未確認状態のみを記録。"
    - "Excel ID286のネットワーク/端子接続を利用した発報操作も、手順化・転載していない。実施権限、設備の状態、承認済み試験方法は未確認。"
---

# 2BC群管理異常の発報方法に関する構成差の注意

首都工・不具合情報共有リストID47は、2BCにはLANケーブルがないと記載している。このため、LAN経路を前提とする他構成の群管理異常発報方法を、2BCへそのまま当てはめることはできない。

原リストの対応状況欄は「未確認」である。これは構成差に関するリスト記載であり、現行構成、異常発報の意味、適用範囲は未確認である。原文にある意図的な異常発報の操作、盤内部品の識別、操作時間は記録していない。本記録を試験・診断手順として使用しない。

## 異常を意図的に発報させる操作に関する記載（リストID286）

協力会社展開用Excel ID286は、群管理方式に応じた異常発報方法を案内し、意図的な異常発生につながる操作を含む。具体的なネットワーク/端子操作、部品識別、待機時間は転載しない。対象構成、目的、承認、現行手順および試験設備の隔離状態は未確認である。

本記録を発報試験、故障診断、ネットワーク/端子操作、稼働設備の異常発生に使用しない。試験が必要な場合は、設備状態と構成に応じた承認済み手順を所管者に確認する。