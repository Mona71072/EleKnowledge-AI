---
schema_version: 1
record_id: "elv-epits-sw-acquisition"
record_version: 1
title: "EPITSソフト取得ノートの参照記録"
category: "不具合対応(ELV)"
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
keywords:
  - "EPITS"
  - "S/W取得"
  - "改造要領図"
  - "強制アセンブラ日付"
source_path: "不具合対応【ELV】/メンテコン/EpitsでのS-W採取方法.md"
source_filename: "EpitsでのS-W採取方法.md"
onenote_id: "a8c15103-95f4-4d08-897a-403d412bffb5:109"
related_ids: []
attachment_paths:
  - "不具合対応【ELV】/メンテコン/OneNote/EpitsでのS-W採取方法 image.emf"
  - "不具合対応【ELV】/メンテコン/OneNote/EpitsでのS-W採取方法 image 1.emf"
  - "不具合対応【ELV】/メンテコン/OneNote/EpitsでのS-W採取方法 image 2.emf"
  - "不具合対応【ELV】/メンテコン/OneNote/EpitsでのS-W採取方法 image 3.emf"
  - "不具合対応【ELV】/メンテコン/OneNote/EpitsでのS-W採取方法 image 4.emf"
  - "不具合対応【ELV】/メンテコン/OneNote/EpitsでのS-W採取方法 image.png"
  - "不具合対応【ELV】/メンテコン/OneNote/EpitsでのS-W採取方法 image.jpg"
reference_links: []
document_references:
  - title: "対象号機の改造要領図"
    locator: "原文が対象機・項目・プログラムファイル名・強制アセンブラ日付の照合に指定"
evidence_sources:
  - source_id: "evidence-elv-epits-sw-acquisition"
    source_type: "vault_original"
    title: "EpitsでのS-W採取方法（原文）"
    source_path: "不具合対応【ELV】/メンテコン/EpitsでのS-W採取方法.md"
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-01"
    supports:
      - "EPITSからのS/W参照に関する原文説明"
  - source_id: "evidence-elv-epits-item-map"
    source_type: "vault_original"
    title: "機種群別のアイテム表記一覧"
    source_path: "不具合対応【ELV】/メンテコン/OneNote/EpitsでのS-W採取方法 image.jpg"
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-04"
    supports:
      - "アイテム表記とS/W種別の対応が機種群・群管理で異なること"
  - source_id: "evidence-elv-epits-order-check"
    source_type: "vault_original"
    title: "改造要領図のS/W照合例"
    source_path: "不具合対応【ELV】/メンテコン/OneNote/EpitsでのS-W採取方法 image 3.emf"
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-04"
    supports:
      - "改造要領図の対象号機、アイテム、プログラムファイル名、強制アセンブラ日付の記載例"
      - "画像中の個別物件情報・ファイル名は一般情報として転載しない"
  - source_id: "evidence-elv-epits-list"
    source_type: "vault_original"
    title: "EPITSのS/W一覧画面例"
    source_path: "不具合対応【ELV】/メンテコン/OneNote/EpitsでのS-W採取方法 image 4.emf"
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-04"
    supports:
      - "EPITS一覧に項目、ファイル名、更新関連情報が表示される例"
  - source_id: "evidence-elv-epits-download-info"
    source_type: "vault_original"
    title: "EPITSダウンロード情報画面例"
    source_path: "不具合対応【ELV】/メンテコン/OneNote/EpitsでのS-W採取方法 image.png"
    s3_uri: ""
    revision: "画面例の最終更新表示: 2025-02-24"
    accessed_at: "2026-10-04"
    supports:
      - "ダウンロード理由、ファイル最終更新日時、サイズの表示例。承認や現行性の証明ではない"
structured_data:
  source_notes:
    - "添付7点は内容確認済み。5点のEMFは一時PNGに変換して確認し、原本は変更していない。画面例にはポータル経路、対象物件、個別ファイル名等があるため転記しない。"
    - "添付図版のアイテム表記は機種群・群管理で異なる。アイテム記号だけでS/W種別を判断せず、対象機の改造要領図と照合する。"
    - "原文は強制アセンブラ日付が他アイテムと同じ場合にS/W未登録の可能性を挙げ、電気設計への確認を指示。図版の最終更新日時・サイズは承認や現行性の根拠ではない。"
    - "イントラアクセス権・対象物件・承認済み改造指示・現行ファイルの真正性を確認する必要がある。認証情報・社内ポータルURLは転記しない。"
---

# EPITSソフト取得ノートの参照記録

原文は、承認された改造要領図と対象号機を参照してEPITS上のS/Wを確認し、取得ファイル名と要領図の指定を照合する考え方を説明している。

## 照合の要点

添付表では、アイテム記号とS/W種別の対応が機種群・群管理で異なる。対象機の改造要領図で指定された機種、項目（アイテムまたはパラメータ）、S/Wファイル名、強制アセンブラ日付を一組として照合する。アイテム記号だけで取得対象を決めない。

原文は、強制アセンブラ日付が他アイテムと同じ場合、EPITSに新しいS/Wが登録されていない可能性があるため電気設計へ確認するよう記載している。EPITS画面のファイル更新日時やサイズだけでは、改造指示への適合・承認・現行性を確認できない。

## 概略フロー（取得手順ではない）

承認済み改造要領図と対象機を特定し、機種群に応じた項目区分を確認する。要領図とEPITS表示の項目・ファイル名・日付を照合し、不一致や未登録の疑いがあれば電気設計へ確認する。取得を行う場合は、権限のある現行手順に従い、取得後もファイル名を要領図と照合する。

## 適用上の注意

社内ポータルへのアクセス、物件番号入力、ファイル取得・展開は本ページに再掲していない。認証情報、社内URL、物件番号、個別ファイル名も転記しない。改造指示の真正性、対象機・項目・版、社内アクセス権を担当部門と確認し、本ページをS/W書換作業の手順として使用しない。

## 出典

- 原文ノート: [[不具合対応【ELV】/メンテコン/EpitsでのS-W採取方法]]
- 添付7点: 実在と内容を確認。画面例の照合ポイントのみを反映し、社内識別情報や取得操作は転載していない。