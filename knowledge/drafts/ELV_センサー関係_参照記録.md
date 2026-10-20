---
schema_version: 1
record_id: "catalog-elv-sensors-reference"
record_version: 3
title: "各種センサー資料の参照記録"
category: "技術メモ【ELV】２"
record_type: "catalog"
product: "エレベーター"
model_type: ["LINKs"]
document_number: "C-6-S197.1-J; C-6-S35.1-J"
revision: ""
effective_date: ""
review_status: "in_review"
publication_status: "not_published"
classification: "unknown"
cloud_approval: "not_reviewed"
keywords: ["TOF", "MBS", "CREQ", "LSDS", "HMS"]
source_path: "技術メモ【ELV】２/ELV-付加仕様（その他）/センサー関係.md"
source_filename: "センサー関係.md"
onenote_id: "97d4ebd4-396d-4083-b8ca-0bf27391d4ea:1"
related_ids:
  - "case-elv-links-mbs800-receiver-on-20261009"
  - "case-elv-mbs-connection-car-indicator-off-id240"
attachment_paths: []
reference_links: []
document_references:
  - document_number: "C-6-S197.1-J"
    title: "TOFセンサー資料"
    locator: "原資料内社内PDFリンク。未閲覧"
    source_path: ""
  - document_number: "C-6-S35.1-J"
    title: "CREQセンサー資料"
    locator: "原資料内社内PDFリンク。未閲覧"
    source_path: ""
evidence_sources:
  - source_id: "evidence-elv-sensors-001"
    source_type: "vault_original"
    title: "センサー関係"
    source_path: "技術メモ【ELV】２/ELV-付加仕様（その他）/センサー関係.md"
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-08"
    supports: ["各種センサーの資料/不具合/調整情報が含まれること"]
  - source_id: "evidence-list-vfgh-mbs-hms-interface-miswiring-352"
    source_type: "user_provided_extract"
    title: "協力会社展開用Excel: MBS/HMS誤配線による戸閉不良（ID352）"
    source_path: ""
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-13"
    supports:
      - "戸閉間際のHMS反応と戸反転、MBS/HMSインターフェース誤配線、是正後の動作報告"
      - "センサー角度調整で症状が一時的に見えなくなり誤配線が見逃される可能性があるとの注意"
  - source_id: "evidence-list-vfg-mbs-car-indicator-off-240"
    source_type: "user_provided_extract"
    title: "協力会社展開用Excel: MBS接続後のかご内表示消灯（ID240）"
    source_path: ""
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-13"
    supports:
      - "ID240の個別ケース記録に分離した据付時のかご内表示/ボタン不作動と配線不整合報告"
structured_data:
  source_notes:
    - "センサー無効化、機種別調整、誤配線/故障事例の詳細は転載していない。現場識別情報は除外。"
    - "リストID4のAXIEZ-LINKS MBS-800受光側事例は、個別ケース記録に分離。本カタログへ詳細を重複記載しない。"
    - "協力会社展開用Excel ID352はVFGHのMBS/HMS誤配線に関する別事例として追記。戸閉間際のセンサー反応、誤配線と是正後の動作報告、角度調整が症状を覆い原因を見逃す可能性を記録した。端子/コネクタ識別、センサー無効化、運転・調整方法、物件情報は転載しない。現行適用と安全確認は未確認。"
    - "協力会社展開用Excel ID240はMBS接続後の表示/ボタン不作動に関する個別ケース記録に分離。かご内表示の消灯と接続割当不整合が原因とされた報告を記録した。電圧/コネクタ/端子/ピン配列/作業方法/現場識別は非転載。"
---

# 各種センサー資料の参照記録

原資料は複数方式のセンサー資料、情報共有、不具合、調整に関する記述と図版を含む。センサー無効化、機種別設定・調整、故障処置は転記していない。現場識別情報も記録していない。

## MBS/HMS誤配線の報告（リストID352）

協力会社展開用Excel ID352は、VFGHで戸閉間際にHMSが反応して戸が閉まりきらない事例を報告する。原リストは、MBS/HMSインターフェースの誤配線により、HMS信号が別系統の信号として扱われたことを原因として挙げ、配線是正後に動作が良好になったとしている。現行図面・設備仕様との照合、是正後の継続的な正常性は未確認。

原リストは、センサー角度の調整で症状が見えなくなり、誤配線が見つからない可能性も指摘する。端子/コネクタ識別、センサー無効化、角度調整、試運転や配線修正手順は記載しない。参照資料本文・版・機種適用も未確認であり、本記録をセンサーの調整・無効化や運転判断に使用しない。

安全装置に関わるため、対象機種の現行設計/保守資料と設計・安全承認を確認するまで、無効化・調整・故障判断に使用しない。

## MBS接続後のかご内表示消灯報告（リストID240）

ID240の据付時表示/ボタン不作動と接続割当不整合の報告は、[[整備済み資料/技術資料/ELV_MBS接続後かご内表示消灯_ID240事例]]に分離した。電圧値、コネクタ/端子/ピン配列、接続や通電確認の手順は転載せず、回路図・保守要領との照合と作業判断は所管者確認を要する。

出典: `技術メモ【ELV】２/ELV-付加仕様（その他）/センサー関係.md`（OneNote ID `97d4ebd4-396d-4083-b8ca-0bf27391d4ea:1`）。確認日: 2026-10-08。
