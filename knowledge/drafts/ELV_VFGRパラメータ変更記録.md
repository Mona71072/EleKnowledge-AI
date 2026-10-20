---
schema_version: 1
record_id: "elv-vfgr-parameter-change"
record_version: 1
title: "VFGRパラメータ書換ノートの構造化記録"
category: "不具合対応(ELV)"
record_type: "procedure"
knowledge_domain: "engineering_business"
organizational_scope: "unknown"
product: "エレベーター"
model_type:
  - "VFGR"
document_number: ""
revision: ""
effective_date: ""
review_status: "in_review"
publication_status: "not_published"
classification: "unknown"
cloud_approval: "not_reviewed"
keywords:
  - "VFGR"
  - "パラメータ書換"
  - "アドレス設定"
  - "CPU種別"
source_path: "不具合対応【ELV】/メンテコン/S-W書換方法/VFGR（パラメータ書換）.md"
source_filename: "VFGR（パラメータ書換）.md"
onenote_id: "a8c15103-95f4-4d08-897a-403d412bffb5:112"
related_ids:
  - "elv-vfgr-sw-change"
attachment_paths:
  - "不具合対応【ELV】/メンテコン/S-W書換方法/OneNote/VFGR（パラメータ書換） image.jpg"
  - "不具合対応【ELV】/メンテコン/S-W書換方法/OneNote/VFGR（パラメータ書換） image.png"
  - "不具合対応【ELV】/メンテコン/S-W書換方法/OneNote/VFGR（パラメータ書換） image 1.png"
  - "不具合対応【ELV】/メンテコン/S-W書換方法/OneNote/VFGR（パラメータ書換） image 1.jpg"
reference_links: []
document_references: []
evidence_sources:
  - source_id: "evidence-elv-vfgr-parameter-change"
    source_type: "vault_original"
    title: "VFGRパラメータ書換（原文）"
    source_path: "不具合対応【ELV】/メンテコン/S-W書換方法/VFGR（パラメータ書換）.md"
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-01"
    supports:
      - "パラメータ書換画面と設定項目の原文記載"
  - source_id: "evidence-elv-vfgr-parameter-mode"
    source_type: "vault_original"
    title: "VFGRライトモード画面例"
    source_path: "不具合対応【ELV】/メンテコン/S-W書換方法/OneNote/VFGR（パラメータ書換） image.png"
    s3_uri: ""
    revision: "画面表記: Ver.22.6、2022-12-22"
    accessed_at: "2026-10-04"
    supports:
      - "ライトモード特殊画面の表示例。画面版は現行性を保証しない"
  - source_id: "evidence-elv-vfgr-parameter-result"
    source_type: "vault_original"
    title: "VFGRパラメータ設定・結果画面例"
    source_path: "不具合対応【ELV】/メンテコン/S-W書換方法/OneNote/VFGR（パラメータ書換） image 1.jpg"
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-04"
    supports:
      - "CPU種別・セグメント・アドレス・データ入力欄の例"
      - "書換成功/失敗表示の例。具体値と画面操作は転載しない"
structured_data:
  source_notes:
    - "原文はメンテコン接続、基板スイッチ・リセット、ライトモード、CPU種別・セグメント・アドレス・データ入力を列挙。操作順・入力値は転載しない。"
    - "入力値は別の指定資料に依存。参照資料の版・対象機・承認は未確認。"
    - "添付画像4点は内容確認済み。単体処理画面、CPU種別・セグメント・アドレス・データ欄、成功/失敗表示がある。画面上の設定例は指示値ではない。"
    - "画面例に2022-12-22・Ver.22.6の表示がある。現行画面・対応OSは未確認。"
---

# VFGRパラメータ書換ノートの構造化記録

原文と添付図版は、VFGRのパラメータ変更に際してCPU種別・セグメント・アドレス・データを扱う画面例、および書換成功/失敗の表示例を含む。画面例の値は個別の変更指示ではなく、指定資料との照合なしに使用できない。画面には2022年・Ver.22.6の表記があり、現行性は確認していない。

## 概略確認フロー（変更手順ではない）

対象機・変更要求・承認者を確認し、適用する指定資料からCPU種別・アドレス・データを照合する。バックアップと復旧方法を確認したうえで、有資格担当者が承認済み最新版の手順に従って変更し、結果表示と所定の事後確認を行う。失敗表示や指定値との不一致があれば作業を進めず、責任部門へ確認する。

パラメータ変更は機能・運転特性へ影響し得る。本ページは変更指示ではなく、具体的な画面操作や値を示さない。

## 出典

- 原文ノート: [[不具合対応【ELV】/メンテコン/S-W書換方法/VFGR（パラメータ書換）]]
- 添付画像4点: 実在と内容を確認。入力欄と結果表示の意味のみを反映し、個別設定値や操作順は転載していない。
