---
schema_version: 1
record_id: "catalog-elv3-sfps-priority-floor-reference"
record_version: 2
title: "SFPS特定階優先の原文動作条件"
category: "技術メモ【ELV】３"
record_type: "technical_reference"
product: "エレベーター"
model_type: []
document_number: ""
revision: ""
effective_date: ""
review_status: "in_review"
publication_status: "not_published"
classification: "unknown"
cloud_approval: "not_reviewed"
keywords: ["SFPS", "特定階", "群管理"]
source_path: "技術メモ【ELV】３/群管理（技術メモ）/特定階優先サービス（SFPS）.md"
source_filename: "特定階優先サービス（SFPS）.md"
onenote_id: "2282807b-e7c6-4d45-9b80-ddcd9dea8c0a:1"
related_ids: []
attachment_paths: []
reference_links: []
document_references: []
evidence_sources:
  - source_id: "evidence-elv3-sfps-001"
    source_type: "vault_original"
    title: "特定階優先サービス（SFPS）"
    source_path: "技術メモ【ELV】３/群管理（技術メモ）/特定階優先サービス（SFPS）.md"
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-09"
    supports: ["SFPSの群管理上の優先配車、登録階数上限、優先度時間を超過した場合の非移行条件が原文に記載されていること"]
structured_data:
  specifications:
    - name: "サービスの配車特性"
      value: "特定のかごを群管理から切り離さず、特定階へのサービスを一般の乗場より優先すると説明"
      unit: ""
      condition: "原文の概要説明。現行仕様・機種適用は未確認"
    - name: "特定階の登録上限"
      value: "最大2階床まで登録可能"
      unit: "階床"
      condition: "原文記載。現行仕様/設定条件は未確認"
    - name: "優先度時間"
      value: "標準10秒。優先階へ配車する所要時間がこの時間を超える場合、SFPS動作へ移行しないと記載"
      unit: "秒"
      condition: "原文記載の標準値と非移行条件。現行値・判定仕様は未確認。設定変更値は記録しない"
    - name: "急行ゾーンとの関係"
      value: "急行ゾーンがあると配車時間が長くなり、優先度時間を超えてSFPSへ移行しない可能性が高くなると原文に記載"
      unit: ""
      condition: "原文の説明。個別設備での発生・制御論理は未確認"
    - name: "優先配車の限界"
      value: "特定かごを群管理から切り離さず、乗場呼びをスキップして特定階へ向かう動作ではないと原文に記載"
      unit: ""
      condition: "原文記載。具体的な呼び割当ては運転状態に依存し、現行性未確認"
  safety_warnings:
    - "優先度時間・登録上限等は原文記載であり、現行仕様・設定値・運転保証ではない。機種別の承認済み群管理資料と所管者確認なしに設定/運転判断へ使用しない。"
    - "原文にある設定アドレス変更、メンテコン接続、複数階呼びを用いる試験操作は転載していない。"
  source_notes:
    - "優先度時間の原文標準値10秒と、超過時に動作へ移行しない条件を保持。原文記載の設定アドレス値/変更方法は記録していない。"
    - "埋め込み画像2点はファイル名検索でVault内の実体を確認できず、図版内容は未確認。"
    - "原文の手動/スケジュール設定、複数かご/階呼びによる動作確認などの試験手順は転載していない。"
---

# SFPS特定階優先の原文動作条件

## 原文記載の動作条件

- SFPSは、特定のかごを群管理から切り離さず、特定階へのサービスを一般の乗場より優先する機能として説明されている。
- 特定階は最大2階床まで登録可能と記載。
- 優先度時間は標準10秒とされ、優先階への配車所要時間がこれを超える場合はSFPS動作に移行しない。急行ゾーンがあると配車時間が長くなり、超過により移行しない可能性が高くなると原文にある。
- 特定かごを群管理から切り離したり、乗場呼びをスキップして特定階へ向かったりする動作ではないと原文に記載。

上記は原文の動作説明であり、現行値、判定ロジック、機種適用は未確認。埋め込み画像2点はVault内で実体を確認できず、画面内容も未確認。

## 利用上の制約

原文にある設定アドレス変更、メンテコン接続、複数階呼びを用いた試験手順は転載していない。現行の承認済み群管理仕様と所管者確認なしに設定・試験・運転判断へ使用しない。

出典: `技術メモ【ELV】３/群管理（技術メモ）/特定階優先サービス（SFPS）.md`（OneNote ID `2282807b-e7c6-4d45-9b80-ddcd9dea8c0a:1`）。本文確認日: 2026-10-09。
