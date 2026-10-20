---
schema_version: 1
record_id: "elv-km-ld-trunk-door-open-extension-misconnection-id70"
record_version: 1
title: "KM-LDのコネクタ誤結線によるトランク戸開延長事例（ID70）"
category: "不具合対応(ELV)"
record_type: "troubleshooting_case"
product: "エレベーター"
model_type:
  - "KM-LD"
document_number: ""
revision: ""
effective_date: ""
review_status: "in_review"
publication_status: "not_published"
classification: "unknown"
cloud_approval: "not_reviewed"
keywords:
  - "ドア"
  - "戸開延長"
  - "強制戸閉"
  - "コネクタ誤結線"
  - "自動運転"
related_ids:
  - "elv-door-issues-reference"
source_path: ""
source_filename: "技術情報リスト（協力会社展開用）.xlsx"
onenote_id: ""
attachment_paths: []
reference_links: []
document_references: []
evidence_sources:
  - source_id: "evidence-list-km-ld-trunk-door-open-extension-070"
    source_type: "user_provided_extract"
    title: "首都工・不具合情報共有リスト: コネクタ誤結により強制戸閉するまでドアが閉じてこない（ID70）"
    source_path: ""
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-09"
    supports:
      - "KM-LDの自動運転時の戸閉遅延、YBO/YBI誤接続との原因説明、是正後の正常動作報告"
structured_data:
  equipment: "KM-LD"
  symptom: "全自動運転中にドアが戸閉せず、30秒経過後に強制戸閉となるとの報告。"
  error_codes: []
  cause: "原文は、カゴ上ST内のYBOコネクタがYBI側に誤接続されていたため、トランク戸開延長機能が動作していたと説明する。原因の独立確認はしていない。"
  verified_actions: []
  outcome: "原リストは、結線是正後に正常動作へ改善したと報告する。事前にMBS表示・配線経路・ドア動作等を確認し、MBS機能無効化やソフトウェア書換えも対応欄に記録するが、個別の確認・設定・結線手順は転載しない。結果は原文上の報告で独立確認していない。"
---

# KM-LDのコネクタ誤結線によるトランク戸開延長事例（ID70）

首都工・不具合情報共有リストID70は、重要度を「重要」とするKM-LDの事例で、全自動運転中にドアが戸閉せず、30秒経過後に強制戸閉となる症状を記録する。

原因欄は、カゴ上ST内でYBOとYBIのコネクタが誤接続され、トランク戸開延長機能が動作していたと説明する。これは原リストの原因説明で、独立確認はしていない。

## 対応結果

原リストの対応欄には、MBS表示や配線経路の確認、MBS機能を無効にした確認、ソフトウェア書換え、カゴ上ST内の結線確認が記載され、原因欄では結線是正後に正常動作へ改善したと報告する。個別の配線・コネクタ識別、機能無効化、ソフトウェア変更や確認手順は転載しない。結果は原文上の報告で独立確認していない。

## 関連資料

[[ELV_ドア不具合事例一覧]]はドア関連の検索用カタログであり、ID407の事例とは別案件。本記録は同カタログへの検索導線で、カタログ項目は本件の独立した根拠を追加するものではない。