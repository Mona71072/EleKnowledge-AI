---
schema_version: 1
record_id: "elv-long-period-vibration-sensor-level1-reset-id357"
record_version: 1
title: "長周期振動感知器Lv1自動復帰不良事例（ID357）"
category: "不具合対応(ELV)"
record_type: "troubleshooting_case"
product: "エレベーター"
model_type:
  - "MR機種"
document_number: ""
revision: ""
effective_date: ""
review_status: "in_review"
publication_status: "not_published"
classification: "unknown"
cloud_approval: "not_reviewed"
keywords:
  - "長周期振動感知器"
  - "Lv1"
  - "自動復帰"
  - "標準図誤記"
source_path: ""
source_filename: "技術情報リスト（協力会社展開用）.xlsx"
onenote_id: ""
related_ids: []
attachment_paths: []
reference_links: []
document_references: []
evidence_sources:
  - source_id: "evidence-list-elv-long-period-sensor-level1-reset-357"
    source_type: "user_provided_extract"
    title: "協力会社展開用Excel: 長周期振動感知器Lv1自動復帰不良（ID357）"
    source_path: ""
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-13"
    supports:
      - "Lv0とLv1の復帰動作差、標準図の信号指定誤りとの原因説明、メーカー見解の記載"
structured_data:
  equipment: "MR機種の長周期振動感知器"
  symptom: "Lv0は自動復帰したが、Lv1は自動復帰せず状態が保持されたとの報告。"
  cause_assessment: "原リストは、長周期振動感知器に対するリセット信号の標準図上の指定誤りを原因としている。図面・実機・添付訂正指示による独立確認はない。"
  reported_response: "メーカーは配線是正と静観可能との見解を示したと原リストに記載されている。具体的な端子、信号極性、電圧、配線変更内容は記録しない。是正実施と復帰確認は未確認。"
  outcome: "是正後のLv1復帰、継続監視結果、再発有無は記載から確認できない。"
  limitations:
    - "端子番号、信号名、極性、電圧値、回路図、配線変更・リセット手順は転載しない。"
    - "添付の結線訂正指示、標準図本文・改訂・現行適用は未確認。"
    - "メーカーの静観可能との見解は、現行の設備別技術・安全承認として扱わない。"
---

# 長周期振動感知器Lv1自動復帰不良事例（ID357）

## 症状

首都工・不具合情報共有リストID357は、長周期振動感知器のLv0は自動復帰した一方、Lv1は復帰せず状態が保持されたと報告する。原リストでは結線に問題がないと判断して調査を開始した後、標準図上のリセット信号指定に誤りがあったと説明している。

## 原因説明と対応状態

標準図の指定誤りが原因という説明は原リスト記載であり、図面・実機・添付訂正指示を用いた独立確認はない。メーカーは配線是正および静観可能との見解を示したと記録されているが、具体的な端子・極性・電圧・配線変更内容は転載しない。この見解は現行の設備別技術・安全承認ではない。

是正実施、Lv1の復帰確認、継続監視結果、再発有無は未確認。添付の結線訂正指示と標準図の本文・改訂・現行適用も確認できていない。本記録をリセット・配線変更・運転継続の判断に使用しない。