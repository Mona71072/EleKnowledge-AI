---
schema_version: 1
record_id: "elv-health-air-aircon-wrong-timer-relay-id98"
record_version: 1
title: "ヘルスエアー併設エアコンでタイマーリレーの定格違いが報告された事例（ID98）"
category: "不具合対応(ELV)"
record_type: "troubleshooting_case"
product: "ヘルスエアー併設エアコン"
model_type: []
document_number: ""
revision: ""
effective_date: ""
review_status: "unreviewed"
publication_status: "not_published"
classification: "unknown"
cloud_approval: "not_reviewed"
keywords:
  - "ヘルスエアー"
  - "併設エアコン"
  - "タイマーリレー"
  - "定格違い"
  - "AC200V"
  - "DC24V"
related_ids: []
source_path: ""
source_filename: "技術情報リスト（協力会社展開用）.xlsx"
onenote_id: ""
attachment_paths: []
reference_links: []
document_references:
  - document_number: ""
    title: "技術メモ【ELV】２/ELV-付加仕様（その他）/ヘルスエア.md"
    locator: "併設エアコン設定・結線注意および関連する共有リストへの参照を記載。リンク先未閲覧、ID98との関係未確認。"
    source_path: "技術メモ【ELV】２/ELV-付加仕様（その他）/ヘルスエア.md"
evidence_sources:
  - source_id: "evidence-list-case-id98"
    source_type: "user_provided_extract"
    title: "首都工・不具合情報共有リスト Excel出力 ID98"
    source_path: ""
    s3_uri: ""
    revision: "原本リスト・添付未照合"
    accessed_at: "2026-10-09"
    supports:
      - "エアコンとヘルスエアーの症状、タイマーリレーの定格違いを原因とする原文記載、交換予定および進捗欄の確認事項"
structured_data:
  equipment: "ヘルスエアー併設エアコン"
  symptom: "エアコンは起動するが、併設されたヘルスエアーが起動しなかったとの報告。エラー表示は未確認。"
  error_codes: []
  cause: "原リストは、AC200V用ではなくDC24V用のタイマーリレーが取り付けられていたと原因記載する。これは原文上の原因説明であり、現物・定格・因果関係は独立確認されていない。"
  verified_actions: []
  outcome: "原リストは後日交換予定と記載する。交換の実施、交換後の動作確認および復旧結果は記載されていない。"
---

# ヘルスエアー併設エアコンでタイマーリレーの定格違いが報告された事例（ID98）

## 概要

首都工・不具合情報共有リストID98は、エアコン併設型ヘルスエアーでエアコンは起動する一方、ヘルスエアーが起動しなかったと報告する。共有日は2022-02-21、エラー表示は未確認。対象機種欄は空欄である。

## 原文の原因説明

原リストは、AC200V用ではなくDC24V用のタイマーリレーが取り付けられていたことを原因として記載する。定格違いの記述は原文上の報告であり、現物、定格、因果関係は独立確認していない。

## 対応状況

不具合原因・対応欄には後日交換予定とある。交換が実施されたか、ヘルスエアーが復帰したかは記載されていない。したがって、解決済みとは扱わない。

進捗欄には、機器設定、結線、配線状態、電源・リレー周辺の確認、施工元への照会について記載があるが、具体的な設定・結線・電気測定の手順や確認点は転載しない。添付に詳細情報と動作原理をまとめたとの記載があるものの、添付は提供されておらず未確認である。

## 関連資料

- [[技術メモ【ELV】２/ELV-付加仕様（その他）/ヘルスエア]]: 原ページには併設エアコンの設定・結線注意や関連する共有リストへの参照がある。リンク先の内容は未閲覧で、ID98との同一性・因果関係・適用性は確認していない。
- [[不具合対応【ELV】/索引]]: ELV整備資料の索引。

## 出典・確認状態

- 出典: Excel出力のID98行にあるA列・E〜N列・O列。B/C/D列は参照していない。
- ID98が参照する添付の実体・内容、タイマーリレーの現物と定格、交換実施・結果、機種適用、現行性、施工元照会結果は未確認。
- 設定変更、結線確認、電源・端子の測定などの具体的な電気作業手順は転載していない。
- 本記録は未レビューであり、部品選定、交換、電気測定、設備の運転・復旧手順を示すものではない。
