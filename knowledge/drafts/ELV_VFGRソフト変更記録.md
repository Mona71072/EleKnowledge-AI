---
schema_version: 1
record_id: "elv-vfgr-sw-change"
record_version: 2
title: "VFGR S/W書換ノートの構造化記録"
category: "不具合対応(ELV)"
record_type: "procedure"
knowledge_domain: "engineering_business"
organizational_scope: "unknown"
product: "エレベーター"
model_type:
  - "VFGR"
document_number: "EA-30（原文記載、正式番号・版未確認）"
revision: ""
effective_date: ""
review_status: "in_review"
publication_status: "not_published"
classification: "unknown"
cloud_approval: "not_reviewed"
keywords:
  - "VFGR"
  - "S/W書換"
  - "メモリコンペア"
  - "フラッシュメモリ"
source_path: "不具合対応【ELV】/メンテコン/S-W書換方法/VFGR　（S-W書換）.md"
source_filename: "VFGR　（S-W書換）.md"
onenote_id: "a8c15103-95f4-4d08-897a-403d412bffb5:113"
related_ids:
  - "elv-white-mc-setup"
  - "elv-vfgr-parameter-change"
attachment_paths:
  - "不具合対応【ELV】/メンテコン/S-W書換方法/OneNote/VFGR　（S-W書換） image.png"
  - "不具合対応【ELV】/メンテコン/S-W書換方法/OneNote/VFGR　（S-W書換） image 1.png"
  - "不具合対応【ELV】/メンテコン/S-W書換方法/OneNote/VFGR　（S-W書換） image.jpg"
  - "不具合対応【ELV】/メンテコン/S-W書換方法/OneNote/VFGR　（S-W書換） image 1.jpg"
  - "不具合対応【ELV】/メンテコン/S-W書換方法/OneNote/VFGR　（S-W書換） image 2.png"
  - "不具合対応【ELV】/メンテコン/S-W書換方法/OneNote/VFGR　（S-W書換） image 3.png"
reference_links: []
document_references: []
evidence_sources:
  - source_id: "evidence-elv-vfgr-sw-change"
    source_type: "vault_original"
    title: "VFGR S/W書換（原文）"
    source_path: "不具合対応【ELV】/メンテコン/S-W書換方法/VFGR　（S-W書換）.md"
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-01"
    supports:
      - "バックアップ、書換、メモリコンペア、Private-IDに関する原文記載"
  - source_id: "evidence-elv-vfgr-sw-item-map"
    source_type: "vault_original"
    title: "機種群別S/W項目対応図"
    source_path: "不具合対応【ELV】/メンテコン/S-W書換方法/OneNote/VFGR　（S-W書換） image 1.jpg"
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-04"
    supports:
      - "機種群・群管理に応じてS/W項目表記が異なること"
  - source_id: "evidence-elv-vfgr-sw-selection"
    source_type: "vault_original"
    title: "フラッシュメモリ書換プログラム選択画面例"
    source_path: "不具合対応【ELV】/メンテコン/S-W書換方法/OneNote/VFGR　（S-W書換） image 1.png"
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-04"
    supports:
      - "プログラム種別の選択肢と対象S/W一覧の画面例。具体設定値は転載しない"
  - source_id: "evidence-elv-vfgr-sw-connection"
    source_type: "vault_original"
    title: "VFGR接続構成図"
    source_path: "不具合対応【ELV】/メンテコン/S-W書換方法/OneNote/VFGR　（S-W書換） image.png"
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-04"
    supports:
      - "メンテコン、白MCカード、P1基板間の接続構成例とPP12表記"
      - "機種・基板によるコネクタ差異の現行適用性は裏付けない"
  - source_id: "evidence-elv-vfgr-private-id-compatibility"
    source_type: "vault_original"
    title: "Private-IDインストーラー互換性画面例"
    source_path: "不具合対応【ELV】/メンテコン/S-W書換方法/OneNote/VFGR　（S-W書換） image 3.png"
    s3_uri: ""
    revision: "画面中の実行ファイル更新日時: 2013-02-21"
    accessed_at: "2026-10-04"
    supports:
      - "古いインストーラーの互換性案内画面。ファイルの真正性・現行OS適合性は裏付けない"
  - source_id: "evidence-list-vfgr-software-write-interface-conflict-284"
    source_type: "user_provided_extract"
    title: "協力会社展開用Excel: VFGR書換エラーと接続状態の報告（ID284）"
    source_path: ""
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-13"
    supports:
      - "ソフト書換機能を開く際のエラーと、複数インターフェース接続状態が原因とされたとの原リスト記載"
structured_data:
  source_notes:
    - "原文は起動環境設定、電源・コネクタ操作、フラッシュメモリ、スイッチ・リセット、メモリコンペアに関する操作列を含む。具体手順は転載しない。"
    - "添付画像6点は内容確認済み。機種群別のS/W項目、接続構成、書換前後の画面、Private-IDの互換性案内を含む。"
    - "Private-ID再インストールのOS操作も含む。画像の実行ファイルには2013年の更新日時表記があり、真正性・OS互換性・現行手順は未確認。"
    - "古い機種でコネクタ名称が異なるとの注記とPP12接続例がある。適用条件は対象機資料で要確認。"
    - "協力会社展開用Excel ID284は、VFGRソフト書換時のエラーと複数インターフェース接続状態が原因とされた報告。具体的な接続機器/ポート/ケーブル/画面操作は転載しない。原因・対象構成・現行要領との整合は未確認。"
---

# VFGR S/W書換ノートの構造化記録

原文は、VFGRの起動環境設定、バックアップ、S/W書換、メモリコンペア、およびライブラリーエラー時のPrivate-ID再インストールを扱う。古い機種で接続部名称が異なるとの注記もある。

協力会社展開用Excel ID284は、ソフト書換機能を開く際にエラーが発生し、複数インターフェースの接続状態が原因とされたと報告する。原因、対象構成、現行要領との整合は独立確認していない。接続機器/ポート/ケーブル/画面操作などの具体情報は記録しない。

## 図版から確認できる要点

添付図版では、機種群・群管理によってS/W項目の表記や選択肢が異なる。また、メンテコン・白MCカード・P1基板間の接続構成例と、PP12の表記がある。原文にも古い機種ではコネクタ名称が異なるとの注記があるため、項目記号やコネクタ名だけで対象を判断しない。

図版は書換前のバックアップ、書換後のメモリコンペア、Private-IDの互換性案内も示す。Private-ID画面の実行ファイルには古い更新日時が表示されるが、真正性や現行OSでの安全性は確認できない。

## 概略確認フロー（書換手順ではない）

対象機・基板・S/W版と承認済み改造指示を特定する。機種群に応じたS/W項目、接続条件、バックアップと復旧方法を現行の適用資料で確認し、有資格担当者が承認済み手順に従って作業・照合する。ライブラリーエラーやPrivate-ID再導入が必要な場合は、実行ファイルの真正性とOS適合性を担当部門に確認する。

## 重大な注意

原文・画像には電源遮断、コネクタ接続、ジャンパー、スイッチ変更、CPUリセット、書換値、OSインストールの詳細があるが、本ページに転載していない。機種・基板・ソフト版、作業資格、安全措置、バックアップ/復旧計画と承認済み最新版を責任部門で確認すること。

## 出典

- 原文ノート: [[不具合対応【ELV】/メンテコン/S-W書換方法/VFGR　（S-W書換）]]
- 添付画像6点: 実在と内容を確認。機種差・確認要点のみを反映し、具体的な書換・配線・OS操作は転載していない。
