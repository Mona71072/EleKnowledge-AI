---
schema_version: 1
record_id: "catalog-elv3-ups-group-control-parent-reference"
record_version: 3
title: "UPSサービス選択の制御元優先関係"
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
keywords: ["UPS", "DPS", "群管理"]
source_path: "技術メモ【ELV】３/群管理（技術メモ）/UPS（アップピークサービス）.md"
source_filename: "UPS（アップピークサービス）.md"
onenote_id: "a556a262-6275-4d00-b70a-c492c569169a:1"
related_ids: []
attachment_paths: []
reference_links: []
document_references: []
evidence_sources:
  - source_id: "evidence-list-ups-control-source-mismatch-350"
    source_type: "user_provided_extract"
    title: "首都工・不具合情報共有リスト: UPS不作動の制御元不一致事例"
    source_path: ""
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-09"
    supports:
      - "引渡し後のUPS不作動、監視盤制御有無と群管理設定の食い違いに関するリスト記載"
  - source_id: "evidence-elv3-ups-parent-001"
    source_type: "vault_original"
    title: "UPS（アップピークサービス）"
    source_path: "技術メモ【ELV】３/群管理（技術メモ）/UPS（アップピークサービス）.md"
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-09"
    supports: ["監視盤による制御が優先される場合に群管理ソフト側UPSが選択されず、予約時刻も無効となる旨が原文にあること"]
structured_data:
  specifications:
    - name: "制御元の優先関係"
      value: "原文記載の監視盤側制御パラメーターが有効な場合、監視盤制御が優先され、群管理ソフトによるUPSは選択されない"
      unit: ""
      condition: "原文の機能説明。パラメーターアドレス/値、機種条件、現行仕様は本記録に含めず未確認"
    - name: "UPS予約時刻への影響"
      value: "上記状態ではUPSの予約時刻を設定しても無効と原文に記載"
      unit: ""
      condition: "原文記載。具体的な制御状態や現行挙動は未確認"
    - name: "関連サービス"
      value: "DPS、LTS、IUPも同様と原文に記載"
      unit: ""
      condition: "原文記載の範囲。サービス別の個別条件/現行適用は未確認"
  knowledge_items:
    - topic: "群管理サービスの不作動では監視盤・群管理間の制御元認識を照合する"
      statement: "首都工・不具合情報共有リストID 350は、引渡し後にUPSが動作せず、リスト記載の原因として監視盤側にUPS制御がない構成と、UPSが監視盤制御ありとして扱われて群管理側制御が無効になる設定の不一致を記録する。既存の原文記録にある監視盤優先の説明と整合する個別事例だが、実機の現行設定や根本原因を独立確認したものではない。"
      conditions: ["UPSに関する個別事例。対象機種欄と物件仕様の適用範囲は未確認。"]
      exceptions: ["アドレス・設定値・予約設定・強制操作・動作試験の方法を本記録から指示しない。", "現行仕様・設定状態・是正結果はリスト本文以外で未確認。"]
      rationale: "機能が動かない場合に、単一の設定欄だけで判断せず、承認済み設計と制御責任の整合を確認する観点を残すため。"
      verification_status: "source_recorded"
      evidence_source_ids: ["evidence-list-ups-control-source-mismatch-350"]
  safety_warnings:
    - "原文はアドレス/設定値と動作確認に言及するが、本記録は設定変更を指示しない。承認済み機種別仕様・所管者確認なしに設定/動作試験/運転判断へ使用しない。"
    - "原文は監視盤の制御/表示がなくてもUPS等の動作確認を確実に行うよう注意している。これは原文注記の記録であり、本記録は試験方法や現行の作業指示を示さない。"
  source_notes:
    - "制御優先の関係と予約時刻への影響を整理し、原文中の具体的なパラメーターアドレス/値は転載していない。"
    - "埋め込み画像1点はファイル名検索でVault内の実体を確認できず、図版内容は未確認。"
---

# UPSサービス選択の制御元優先関係

## 原文記載の制御関係

- PC式監視盤側の制御が有効な場合は監視盤制御が優先され、群管理ソフトによるUPSは選択されないと原文に記載。
- この状態ではUPSの予約時刻を設定しても無効と原文にある。
- DPS、LTS、IUPも同様と原文は記載している。各サービスの個別条件は未確認。
- 原文冒頭は、監視盤からの制御や表示がなくてもUPS等の動作確認を確実に行うよう注意している。

首都工・不具合情報共有リストID 350には、監視盤側と群管理側の制御前提が一致せず、引渡し後にUPSが動作しなかった事例が記録されている。これはリスト記載の一事例であり、現行仕様や設定・試験手順を示すものではない。

上記は原文の機能説明/注意であり、現行仕様・対象機種・設定状態の確認には別途承認済み資料が必要。埋め込み画像1点はVault内で実体を確認できず、内容未確認。

## 利用上の制約

原文中の設定アドレス/値、切替方法、動作確認手順は転載していない。本記録を設定変更や試験指示として使用せず、現行の群管理仕様を設計担当/所管者に確認する。

出典: `技術メモ【ELV】３/群管理（技術メモ）/UPS（アップピークサービス）.md`（OneNote ID `a556a262-6275-4d00-b70a-c492c569169a:1`）。本文確認日: 2026-10-09。
