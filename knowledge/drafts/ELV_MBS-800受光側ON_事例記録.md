---
schema_version: 1
record_id: "case-elv-links-mbs800-receiver-on-20261009"
record_version: 1
title: "AXIEZ-LINKS MBS-800受光側ON故障の報告事例"
category: "不具合対応(ELV)"
record_type: "troubleshooting_case"
product: "エレベーター"
model_type:
  - "AXIEZ-LINKS"
document_number: ""
revision: "リスト記載。現行性未確認"
effective_date: ""
review_status: "in_review"
publication_status: "not_published"
classification: "unknown"
cloud_approval: "not_reviewed"
keywords:
  - "MBS-800"
  - "受光器"
  - "緑点滅"
source_path: ""
source_filename: ""
onenote_id: ""
related_ids:
  - "catalog-elv-sensors-reference"
  - "elv-mbs-replacement"
attachment_paths: []
reference_links: []
document_references:
  - document_number: ""
    title: "EA-112（リストID4の参考資料欄）"
    locator: "資料種別・実体・本文・改訂・適用範囲は未確認"
    source_path: ""
  - document_number: ""
    title: "ASHO29247（リストID4の参考資料欄）"
    locator: "資料種別・実体・本文・改訂・適用範囲は未確認"
    source_path: ""
evidence_sources:
  - source_id: "evidence-list-links-mbs800-receiver-on-004"
    source_type: "user_provided_extract"
    title: "首都工・不具合情報共有リスト: MBS-800受光側ON故障報告"
    source_path: ""
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-09"
    supports:
      - "AXIEZ-LINKSのMBS-800受光側の表示状態、閉扉位置に関する報告、原因評価と交換記録"
structured_data:
  equipment: "AXIEZ-LINKSのMBS-800受光側（リスト記載）"
  symptom: "リストID4は、受光側が継続して緑点滅し、遮光物ありと認識されたと報告する。投光側は赤点灯と記載。閉扉位置に関する100mmの記述もあるが、その測定対象・意味・適用条件は不明で、検出境界や試験基準として扱えない。"
  error_codes: []
  cause: "リストはノイズ、センサー軸ずれ、汚れ等に問題がなかったとし、MBS単体不良の可能性が高いと評価する。確認方法と原因はいずれも独立検証していない。"
  verified_actions: []
  outcome: "リストには現地で投受光器を交換したとあるが、交換後の結果・再発有無は確認できない。"
---

# AXIEZ-LINKS MBS-800受光側ON故障の報告事例

## 報告された現象

首都工・不具合情報共有リストID4は、AXIEZ-LINKSのMBS-800受光側が継続して緑点滅し、遮光物ありと認識される状態を報告している。投光側は赤点灯と記載されている。

報告には、閉扉位置と戸当り柱からの距離に関する100mmの記載がある。ただし、その距離の測定対象・意味・条件は明らかでなく、検出境界、設計値、点検基準として解釈できない。一定時間後に強制戸閉となりシステム上は正常との説明もリスト上の評価であり、安全機能の正常性を確認したものではない。

## 報告上の原因評価と結果

リストはノイズ、センサー軸ずれ、汚れ等に問題がないと評価し、MBS単体不良の可能性が高いとしている。現地で投受光器を交換したとの記載はあるが、原因評価、交換後の動作、再発有無は独立確認できていない。部品番号、確認・交換手順は転載しない。

## 確認上の制限

本事例は個別報告の記録であり、現行仕様、検出性能、閉扉の安全性、機種適用を保証しない。LED状態や距離の記載を点検・試験・故障判定の基準にせず、操作・調整・交換の手順として使用しない。参照資料欄のEA-112およびASHO29247は資料種別・実体・本文・改訂を未確認で、根拠にはしていない。

## 関連資料

- [[整備済み資料/技術資料/ELV_センサー関係_参照記録]]
- [[整備済み資料/技術資料/ELV_MBS交換記録]]