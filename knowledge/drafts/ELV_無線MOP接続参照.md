---
schema_version: 1
record_id: "elv-wireless-mop-reference"
record_version: 1
title: "無線MOP接続ノートの参照記録"
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
  - "無線MOP"
  - "昇降機メニュー"
  - "保守合理化ソフト"
source_path: "不具合対応【ELV】/メンテコン/無線 MOP接続方法.md"
source_filename: "無線 MOP接続方法.md"
onenote_id: "a8c15103-95f4-4d08-897a-403d412bffb5:105"
related_ids: []
attachment_paths: []
reference_links: []
document_references:
  - title: "ソフトMNTの設定方法"
    locator: "原文中の相対リンク。技術メモ【ELV】３/モード/ソフトMNTの設定方法.mdに対応"
    source_path: "技術メモ【ELV】３/モード/ソフトMNTの設定方法.md"
evidence_sources:
  - source_id: "evidence-elv-wireless-mop"
    source_type: "vault_original"
    title: "無線 MOP接続方法（原文）"
    source_path: "不具合対応【ELV】/メンテコン/無線 MOP接続方法.md"
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-01"
    supports:
      - "引渡し済み現場での無線接続に関する原文記述"
  - source_id: "evidence-elv-wireless-mop-network-mode"
    source_type: "vault_original"
    title: "ネットワーク切換えツールの画面例"
    source_path: "不具合対応【ELV】/メンテコン/OneNote/無線 MOP接続方法 image.jpg"
    s3_uri: ""
    revision: "画面表記: ver.3.1.8830-15865"
    accessed_at: "2026-10-04"
    supports:
      - "有線/無線ネットワークモードと接続先種別の選択画面例"
      - "携帯回線の接続状態・電波状況表示例。画面中の電話番号等は転記しない"
  - source_id: "evidence-elv-wireless-mop-target-selection"
    source_type: "vault_original"
    title: "無線接続先選択画面例"
    source_path: "不具合対応【ELV】/メンテコン/OneNote/無線 MOP接続方法 image 1.jpg"
    s3_uri: ""
    revision: "画面表記: V3.51"
    accessed_at: "2026-10-04"
    supports:
      - "接続対象の号機一覧と電波状況の表示例"
      - "接続前提に関する画面上の説明。現行の運用要件は裏付けない"
structured_data:
  source_notes:
    - "原文は保守合理化ソフト・MOPに関する前提を疑問符付きで記載し、別ノートの事前設定を参照する。参照先はVault内で未確認のため、条件は確定情報として扱わない。"
    - "参照先のソフトMNTノートは別フォルダーで確認したが、同ノートの操作を本資料の接続手順へ統合しない。対象条件・現行性は未確認。"
    - "原文が参照する画像2点は2026-10-07時点でVaultおよび添付画像フォルダーに確認できない。過去の画面内容確認記録は再検証できない。"
    - "現場・号機識別情報、電話番号、点検モード切替等の具体操作は本記録に転載しない。"
---

# 無線MOP接続の参照記録

原文は、引渡し済み現場でメンテコンから無線で昇降機メニューへ接続する用途を記載している。また、タスクバーに😊が表示されていれば接続良好と記載する。これは原文上の表示説明であり、現行ソフトウェアでの表示・判定条件は未確認。過去の画像確認記録では、有線/無線モード、接続先、対象号機一覧、電波状況・接続状態の画面例が記録されているが、画像実体を再確認できない。

## 概略フロー（接続手順ではない）

対象現場・作業許可・使用機器とソフトウェア版を確認し、現行の承認済み要領で事前条件を確認する。接続モードと対象号機が依頼内容に合っていること、接続状態が確認できることを確かめてから作業に進む。運転/点検モードの切替や具体的な接続操作は、本ページでは指示しない。

## 未確認事項

原文には、保守合理化ソフトとMOPの取付条件に疑問符が付いており、事前設定ノートへのリンクがある。リンク先ノートは別フォルダーで確認したが、そこに記載のモード移行・解除操作を本資料へ転記していない。図版にある点検モード切替や接続操作を現行の作業指示とみなさず、対象設備、作業許可、最新版要領で条件を確認する。原文添付画像2点は現在確認できず、過去の画面記録を再検証できない。

## 出典

- 原文ノート: [[不具合対応【ELV】/メンテコン/無線 MOP接続方法]]
- 原文は添付画像2点を参照するが、2026-10-07時点でVaultと添付画像フォルダーに実ファイルを確認できない。個人・現場識別情報と具体的な切替操作は転載していない。