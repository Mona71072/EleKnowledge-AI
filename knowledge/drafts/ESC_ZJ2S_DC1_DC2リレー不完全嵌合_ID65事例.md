---
schema_version: 1
record_id: "esc-zj2s-dc1-dc2-relay-seating-id65"
record_version: 1
title: "ZJ2SのDC1/DC2リレー不完全嵌合による運転不能報告（ID65）"
category: "不具合対応(ESC)"
record_type: "troubleshooting_case"
product: "エスカレーター"
model_type:
  - "ZJ2S"
document_number: ""
revision: ""
effective_date: ""
review_status: "in_review"
publication_status: "not_published"
classification: "unknown"
cloud_approval: "not_reviewed"
keywords:
  - "安全回路"
  - "E.0.0"
  - "DC1"
  - "DC2"
  - "リレー"
  - "運転不能"
related_ids:
  - "esc-zj-safety-circuit-status-mismatch-buzzer-case"
source_path: ""
source_filename: "技術情報リスト（協力会社展開用）.xlsx"
onenote_id: ""
attachment_paths: []
reference_links: []
document_references:
  - document_number: ""
    title: "全体接続図（原リストの添付参照）"
    locator: "YS139B214。図面本文・改訂・適用性未確認。"
    source_path: ""
evidence_sources:
  - source_id: "evidence-list-zj2s-dc1-dc2-relay-seating-065"
    source_type: "user_provided_extract"
    title: "首都工・不具合情報共有リスト: DC1, DC2リレーの接触不良により、エスが動かない件（ID65）"
    source_path: ""
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-09"
    supports:
      - "運転不能とE.0.0表示、監視盤接続作業の時系列情報、安全回路・リレーの調査、DC1是正後の運転回復報告"
structured_data:
  equipment: "ZJ2S（原リストの機種欄。個別設備への適用は未確認。）"
  symptom: "後工程の引継検査前、2日前までは運転可能だったが当日に運転できなくなった。前日に監視盤業者が入り監視盤接続作業を行ったとの情報があるが、故障との因果関係は確認されていない。表示はE.0.0のみで安全回路が遮断されていたとの報告。安全スイッチA接点情報が一つの設定状態で表示されなかったとも記載するが、設定の識別値は記録しない。"
  error_codes:
    - "E.0.0"
  cause: "原因欄はDC1、DC2リレーが適切に嵌合していなかったとする。調査ではDC1が外れかかっていたと確認し、DC1を適切に取り付けた後に運転可能となったとの報告。DC2の個別状態、監視盤接続作業との関係、原因の独立確認は未確認。"
  verified_actions: []
  outcome: "原リストは、制御盤の電源状態を確認し、全体接続図を参照して安全回路を切り分けた後、DC1の不完全な取付けを是正するとエスカレーターが運転可能になったと記録する。これは原リスト上の結果で独立確認していない。電圧値・測定点・ロータリー設定・配線・回路切り分け操作は転載しない。"
---

# ZJ2SのDC1/DC2リレー不完全嵌合による運転不能報告（ID65）

首都工・不具合情報共有リストID65は、共有日欄を2021-12-07（Excel値44537の換算）とするZJ2Sの報告で、重要度は「中」。引継検査前の工程で、2日前には運転できていたエスカレーターが当日に動かず、E.0.0表示と安全回路遮断があったと記録する。

前日に監視盤業者が監視盤接続作業を行ったとの情報も記載されるが、作業と不具合の因果関係は示されていない。安全スイッチA接点情報が一つの設定状態で表示されなかったとの記載があるものの、具体的なロータリー設定値は転記しない。

## 調査・対応結果

原因欄はDC1、DC2リレーの不完全嵌合を挙げる。対応欄では、電源状態を確認し、全体接続図を参照して安全回路を調べた結果、DC1リレーが外れかかっていたとする。DC1を適切に取り付けたところ運転可能となったとの報告である。測定値、測定点、配線識別、回路切り分け方法は記録せず、監視盤作業との因果やDC2の状態も未確認とする。

## 関連事例と注意

[[ESC_ZJ型安全回路異常表示_事例記録]]も安全回路に関する運転不能報告だが、ID52は安全スイッチ確認中の別症状・下部回路側への絞り込みを記録しており、本件と原因・機種範囲を同一視しない。全体接続図YS139B214の本文・改訂・適用性は未確認である。本記録は電気作業、運転復旧、回路切り分けの手順ではない。