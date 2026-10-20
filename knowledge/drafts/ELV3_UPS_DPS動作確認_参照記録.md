---
schema_version: 1
record_id: "catalog-elv3-ups-dps-test-reference"
record_version: 2
title: "UPS/DPS動作確認時の原文注意事項"
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
keywords: ["UPS", "DPS", "試験"]
source_path: "技術メモ【ELV】３/群管理（技術メモ）/UPS（アップピークサービス）/UPS,DPSの確認方法.md"
source_filename: "UPS,DPSの確認方法.md"
onenote_id: "1e0ad6f4-e63b-463a-bc40-8a9000843691:1"
related_ids: []
attachment_paths: []
reference_links: []
document_references:
  - document_number: ""
    title: "UPS,DPS動作確認方法.pptx"
    locator: "原資料内SharePointリンク。保管パスに2017年度の記載あり。未閲覧"
    source_path: ""
evidence_sources:
  - source_id: "evidence-elv3-ups-dps-test-001"
    source_type: "vault_original"
    title: "UPS,DPSの確認方法"
    source_path: "技術メモ【ELV】３/群管理（技術メモ）/UPS（アップピークサービス）/UPS,DPSの確認方法.md"
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-09"
    supports: ["負荷変動の検知、仕様別予約時間、ホテル/住宅仕様のアナウンスに関する原文注意"]
structured_data:
  specifications:
    - name: "負荷変動の確認に関する原文注意"
      value: "負荷の変動を検知するため、主階床で20%乗車・降車した際に負荷設定するよう記載"
      unit: "%"
      condition: "原文の動作確認上の注意。試験時の負荷設定文脈であり、UPS/DPSの起動閾値とは記載されていない。現行試験条件は未確認"
    - name: "標準予約時間"
      value: "オフィス・ホテル・住宅仕様で異なると記載。個別時間値は原文ページに記載なし"
      unit: ""
      condition: "原文注意。仕様別の現行値・設定根拠は未確認"
    - name: "群管理モニター利用に関する原文注意"
      value: "1台に保守合理化S/Wを入れておくことと記載"
      unit: ""
      condition: "原文記載。現行ソフト要件/承認済み作業条件は未確認"
    - name: "UPS/DPSアナウンスに関する原文注意"
      value: "UPS『おはようございます』、DPS『お疲れ様でした』のアナウンスについて、ホテル・住宅用はアナウンス無し設定と記載。原文はUPS標準時間が夕方であることを理由としている"
      unit: ""
      condition: "原文の説明。個別物件/仕様の現行設定・適用性は未確認"
  safety_warnings:
    - "本記録は原文にある確認上の注意であり、動作試験の実施手順・合否基準ではない。現行の承認済み試験要領と物件仕様を確認するまで試験/設定判断に使用しない。"
  source_notes:
    - "原文の20%は主階床における試験時の乗車/降車負荷設定に関する注意。機能起動閾値や一般適用値へ読み替えない。"
    - "埋め込み画像7点はファイル名検索でVault内の実体を確認できず、内容未確認。SharePoint PowerPointリンクとVault内PowerPoint参照も未閲覧。"
    - "SharePoint保管パスの2017年度という文字列は、リンク先資料の改訂/適用年度を証明するものではない。"
---

# UPS/DPS動作確認時の原文注意事項

## 原文にある確認上の注意

- 負荷変動を検知するため、主階床で20%乗車・降車した際に負荷設定するよう記載。これは原文の動作確認文脈であり、サービス起動閾値とは記載されていない。
- 標準予約時間はオフィス・ホテル・住宅仕様で異なると記載されているが、個別の時間値はこのノート本文にない。
- 群管理モニターに入る場合、1台に保守合理化S/Wを入れておくことと記載。
- UPS「おはようございます」/DPS「お疲れ様でした」のアナウンスについて、ホテル・住宅用はアナウンス無し設定とし、UPS標準時間が夕方のためと説明している。

以上は原文記載の注意であり、現行仕様・物件別設定・試験条件を保証しない。図版7点とSharePoint PowerPointは未確認。2017年度はSharePoint保管パス上の表記であり、資料の改訂/適用年度とは確定していない。

## 利用上の制約

原資料の具体的な試験条件、監視盤操作、設定や動作確認方法は手順化していない。承認済みの現行試験要領と物件仕様を確認するまで、試験・設定判断に使用しない。

出典: `技術メモ【ELV】３/群管理（技術メモ）/UPS（アップピークサービス）/UPS,DPSの確認方法.md`（OneNote ID `1e0ad6f4-e63b-463a-bc40-8a9000843691:1`）。本文確認日: 2026-10-09。
