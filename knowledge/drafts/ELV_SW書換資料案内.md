---
schema_version: 1
record_id: "elv-sw-change-reference"
record_version: 4
title: "S/W書換関連資料案内"
category: "不具合対応(ELV)"
record_type: "catalog"
product: "エレベーター"
model_type:
  - "VFGLB"
  - "SCU-20"
document_number: ""
revision: ""
effective_date: ""
review_status: "in_review"
publication_status: "not_published"
classification: "unknown"
cloud_approval: "not_reviewed"
keywords:
  - "S/W書換"
  - "VFGLB"
  - "SCU-20"
  - "書換要領"
source_path: "不具合対応【ELV】/メンテコン/S-W書換方法.md"
source_filename: "S-W書換方法.md"
onenote_id: "a8c15103-95f4-4d08-897a-403d412bffb5:110"
related_ids:
  - "elv-vfgr-sw-change"
  - "elv-vfgr-parameter-change"
  - "elv-door-board-sw-change"
  - "elv-indicator-board-sw-change"
  - "elv-white-mc-setup"
  - "elv-scu20-flash-rewrite-tool-compatibility-id233"
  - "list-id118-rewrite-program-4-error-item"
reference_links: []
document_references:
  - document_number: "SW書換要領(VFGLB)_改訂C"
    title: "S/W書換要領(VFGLB) 改訂C（原文記載）"
    locator: ""
    source_path: ""
evidence_sources:
  - source_id: "evidence-elv-sw-change-reference"
    source_type: "vault_original"
    title: "S-W書換方法（原文）"
    source_path: "不具合対応【ELV】/メンテコン/S-W書換方法.md"
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-01"
    supports:
      - "S/W書換関連の参照先と改定案内"
  - source_id: "evidence-elv-sw-change-overview-figure"
    source_type: "vault_original"
    title: "S/W書換要領の作業構成図版"
    source_path: "不具合対応【ELV】/メンテコン/OneNote/S-W書換方法 image.png"
    s3_uri: ""
    revision: "図版記載: 改定C、2021-01-21"
    accessed_at: "2026-10-04"
    supports:
      - "バックアップ、書換、メモリコンペア、復帰等の作業章立てと注意事項が図版にあること"
      - "図版日付は現行性・承認を示すものではない"
  - source_id: "evidence-elv-sw-change-item-map"
    source_type: "vault_original"
    title: "機種群別S/W項目表"
    source_path: "不具合対応【ELV】/メンテコン/OneNote/S-W書換方法 image.jpg"
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-04"
    supports:
      - "機種群・群管理によってプログラム/パラメータ項目記号が異なること"
  - source_id: "evidence-list-scu20-rewrite-tool-compatibility-233"
    source_type: "vault_original"
    title: "首都工・不具合情報共有リスト.xlsx: SCU-20書換情報（ID233）"
    source_path: "首都工・不具合情報共有リスト.xlsx"
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-13"
    supports:
      - "後年のメンテコン更新に伴う書換プログラム対応追加の共有リスト記載"
      - "旧ツール利用時に設定関連エラーが起きる可能性についての共有リスト記載"
  - source_id: "evidence-list-rewrite-program-4-error-id118"
    source_type: "vault_original"
    title: "首都工・不具合情報共有リスト: 書換プログラム4 エラー対応（ID118）"
    source_path: "首都工・不具合情報共有リスト.xlsx"
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-14"
    supports:
      - "書換プログラム4のエラー対応に関する共有項目と参照先の存在"
      - "対応欄は完了表示だが、対象機種/版、解決内容、現在の適用性は未確認"
attachment_paths:
  - "不具合対応【ELV】/メンテコン/OneNote/S-W書換方法 image.png"
  - "不具合対応【ELV】/メンテコン/OneNote/S-W書換方法 image 1.png"
  - "不具合対応【ELV】/メンテコン/OneNote/S-W書換方法 image 2.png"
  - "不具合対応【ELV】/メンテコン/OneNote/S-W書換方法 image 3.png"
  - "不具合対応【ELV】/メンテコン/OneNote/S-W書換方法 image 4.png"
  - "不具合対応【ELV】/メンテコン/OneNote/S-W書換方法 image 5.png"
  - "不具合対応【ELV】/メンテコン/OneNote/S-W書換方法 image 6.png"
  - "不具合対応【ELV】/メンテコン/OneNote/S-W書換方法 image 7.png"
  - "不具合対応【ELV】/メンテコン/OneNote/S-W書換方法 image 8.png"
  - "不具合対応【ELV】/メンテコン/OneNote/S-W書換方法 image.jpg"
structured_data:
  source_notes:
    - "本文はSCU-20の書換共有情報、VFGLB改訂Cの参照、改定時の差替え案内。添付画像10点は内容確認済み。"
    - "添付図版には機種別項目表、バックアップ、書換、パラメータ復元、メモリコンペア、復帰、ビットインモード解除の詳細がある。機種・改訂ごとの適用差を一つの手順に統合しない。"
    - "図版は改定C・2021-01-21の表記を含む。SharePointリンク先の現行版・アクセス可否・承認状況は未確認。"
    - "SharePointリンク、物件情報、アドレス・設定値、操作手順は転記していない。"
    - "共有リストID233のSCU-20対応プログラム追加と旧ツールのエラー報告は[[ELV_SC20書換ツール互換性_ID233]]に分けて記録。具体的なツール選択・接続・書換・設定ファイル変更方法は記載していない。"
    - "一次リストID118は書換プログラム4のエラー対応に関する項目と制限付き参照先を含む。対象機種/版、参照先の内容、解決結果、現行適用は未確認。リンク、エラー詳細、設定変更/書換の方法は転載せず、SCU-20固有のID233情報とも同一視しない。"
---

# S/W書換関連資料案内

原文はSCU-20書換情報とVFGLB向け書換要領（改訂C）を参照し、改定時は参照資料を更新するよう案内している。添付図版は、機種別の項目表と、バックアップ・書換・パラメータ復元・メモリコンペア・復帰に関する詳細要領を含む。機種間で項目記号や作業条件が異なるため、共通手順にはまとめていない。

首都工・不具合情報共有リストID233のSCU-20対応プログラム追加と旧ツールのエラー報告は、[[ELV_SC20書換ツール互換性_ID233]]に分けて記録する。ここでは個別の接続・書換・設定変更を示さない。

同リストID118には、書換プログラム4のエラー対応に関する項目と制限付き参照先がある。対応欄は完了表示だが、対象機種/版、参照先の内容、解決結果、現在の適用性は確認できていない。ID233のSCU-20情報と同一事象とはみなさず、リンク・エラー詳細・設定変更/書換方法は本案内に転載しない。

## 概略確認フロー（書換手順ではない）

承認済み工事指示と対象機種を特定し、適用する要領の改訂と機種別項目を照合する。作業前にバックアップと復旧計画を確認し、有資格担当者が現行の承認済み要領に従って作業・事後照合を行う。項目や条件が一致しない場合は作業を進めず、担当部門に確認する。

図版は改定C・2021-01-21の表記であり、現在の承認済み版とは確認できていない。SharePointリンク先の現行改訂、アクセス可否、承認状況を確認すること。このページは資料案内であり、S/W取得・書換・復旧の詳細手順ではない。

## 出典

- 原文ノート: [[不具合対応【ELV】/メンテコン/S-W書換方法]]
- 添付画像10点: 実在と内容を確認。機種差と確認観点を反映し、具体的な配線・アドレス・設定値・操作手順は転載していない。