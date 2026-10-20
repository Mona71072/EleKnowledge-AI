---
schema_version: 1
record_id: "catalog-elv3-cfs-crowded-floor-reference"
record_version: 2
title: "CFS混雑階待機の原文動作条件"
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
keywords: ["CFS", "混雑階", "群管理"]
source_path: "技術メモ【ELV】３/群管理（技術メモ）/混雑階待機動作（CFS）.md"
source_filename: "混雑階待機動作（CFS）.md"
onenote_id: "839f5e88-68d9-4fc8-a200-72a5c73c3ac6:1"
related_ids: []
attachment_paths: []
reference_links: []
document_references: []
evidence_sources:
  - source_id: "evidence-elv3-cfs-001"
    source_type: "vault_original"
    title: "混雑階待機動作（CFS）"
    source_path: "技術メモ【ELV】３/群管理（技術メモ）/混雑階待機動作（CFS）.md"
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-09"
    supports: ["CFS前半/後半の動作説明、降車/乗車負荷の閾値と混雑階設定先が原文に記載されていること"]
structured_data:
  specifications:
    - name: "CFS前半（CFS-Z）"
      value: "降車混雑階で降車負荷（降りた人）20%以上を検出した際、出発時のかご負荷70%以上を検出した階へ優先的に配車し待機"
      unit: "%"
      condition: "原文記載の動作説明。閾値の現行性、負荷検出定義、機種/設定適用は未確認"
    - name: "CFS後半（CFS-K）"
      value: "乗車混雑階で乗車負荷（乗った人）20%以上を検出した際、乗車混雑階へ配車し待機"
      unit: "%"
      condition: "原文記載の動作説明。閾値の現行性、負荷検出定義、機種/設定適用は未確認"
    - name: "混雑階設定先"
      value: "降車混雑階および乗車混雑階は群管理モニターで設定可能と原文に記載"
      unit: ""
      condition: "設定画面/操作方法は未確認。現行の設定権限・承認条件は未確認"
  safety_warnings:
    - "本記録の負荷値・動作説明は原文転記であり、現行仕様・設定値・試験基準・運転判断を保証しない。承認済み機種別資料と所管者確認なしに設定/試験/運転へ使用しない。"
  source_notes:
    - "原文の20%/70%は動作説明に含まれる負荷閾値として保持。測定方法・負荷定義の詳細・適用条件は原文だけでは確認できない。"
    - "手動/スケジュール設定、強制選択、階設定、仮想負荷操作、状態表示確認などの試験/操作手順は転載していない。"
    - "埋め込み画像8点はファイル名検索でVault内の実体を確認できず、図版内容は未確認。"
---

# CFS混雑階待機の原文動作条件

原文は、乗客による一時的な混雑に対し、かごを集中させて混雑緩和を図る動作としてCFSを説明している。

## 原文記載の動作条件

- **前半サービス（CFS-Z）:** 降車混雑階で降車負荷（原文補足: 降りた人）20%以上を検出した際、出発時のかご負荷70%以上を検出した階へ優先的に配車し、待機する。
- **後半サービス（CFS-K）:** 乗車混雑階で乗車負荷（原文補足: 乗った人）20%以上を検出した際、乗車混雑階へ配車し、待機する。
- 降車混雑階・乗車混雑階は群管理モニターで設定可能と原文にある。

上記は原文の説明を記録したもので、閾値の現行性、負荷検出の定義、機種/設定適用、設定権限は未確認。埋め込み画像8点もVault内で実体を確認できず、画面内容は未確認。

## 利用上の制約

原文にある手動/スケジュール設定、強制選択、階設定、仮想負荷操作、状態表示の確認などの試験・操作手順は転載していない。承認済み機種別仕様と試験要領を所管者に確認するまで、設定・試験・運転判断に使用しない。

出典: `技術メモ【ELV】３/群管理（技術メモ）/混雑階待機動作（CFS）.md`（OneNote ID `839f5e88-68d9-4fc8-a200-72a5c73c3ac6:1`）。本文確認日: 2026-10-09。
