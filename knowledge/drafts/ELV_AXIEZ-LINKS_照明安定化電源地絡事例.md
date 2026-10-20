---
schema_version: 1
record_id: "case-elv-axiez-links-car-flex-lighting-power-ground-fault-id398"
list_item_id: "398"
record_version: 1
title: "AXIEZ-LINKS かごの撓みで照明電源が地絡する"
category: "不具合対応(ELV)"
record_type: "troubleshooting_case"
product: "エレベーター"
model_type:
  - "AXIEZ-LINKS"
document_number: ""
revision: ""
effective_date: ""
review_status: "in_review"
publication_status: "not_published"
classification: "unknown"
cloud_approval: "not_reviewed"
keywords:
  - "照明安定化"
  - "地絡"
  - "吊天井"
  - "撓み"
related_ids: []
source_path: ""
source_filename: ""
onenote_id: ""
attachment_paths: []
reference_links: []
document_references: []
evidence_sources:
  - source_id: "evidence-list-axiez-links-lighting-ground-id398"
    source_type: "lists_csv_snapshot"
    title: "首都工・不具合情報共有リスト: カゴが撓むことで照明安定化電源が地絡する件"
    source_path: ""
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-19"
    supports:
      - "カゴ内安定化基板地絡で照明不能、設計隙間5mm、輸送たわみ3mm、作業時踏み込みによる接触、暫定基板交換と補強、周知事項と恒久対策品出荷予定（リスト記載）"
structured_data:
  equipment: "AXIEZ-LINKS"
  symptom: "カゴ内安定化基板が地絡し、照明が点灯しなくなったとの報告。"
  error_codes: []
  cause: "リストは、基板と吊天井間の設計隙間5mmに対し輸送で3mmたわみ、作業時に基板部を踏み隙間が無くなり接触して地絡したと報告。寝台用などかご幅が広い LINKs で発生しやすい、との記載。因果はリスト上の説明であり独立確認していない。"
  verified_actions:
    - "リスト記載: 基板交換（暫定）、天蓋と吊天井間への補強追加（たわみ対策）"
  outcome: "リスト上は対応済み。恒久対策品は早くて6月中旬出荷、図面改定後にQシート展開予定、と記載（時点はリスト共有日 2025-05-19 時点の情報）。"
---

# AXIEZ-LINKS かごの撓みで照明電源が地絡する

共有リスト上の記録 は、カゴ内照明安定化基板の地絡で照明不能になった事象を報告する。原因説明は、設計上の基板—吊天井隙間が輸送たわみと作業時の踏み込みで失われ、接触により地絡した、というリスト上の記録である。

## リスト上の原因・対応（報告ベース）

- 設計値: 基板と吊天井の隙間 5 mm
- 報告された経緯: 輸送で約 3 mm たわみ、作業時に基板部を上から踏み、隙間が無くなって接触
- 対応: 基板交換（暫定）、天蓋—吊天井間の補強追加
- 周知（リスト記載）: 該当部に重量物を置かない、該当部を極力踏まずに作業する

## 未確認事項

- 当該物件の機種仕様・図面との突合
- 恒久対策品の型式・適用範囲（リストは出荷時期の見込みのみ）
- 地絡の電気的確認手順（リスト本文に詳細なし）

本記録は事例検索用であり、運転・診断・復旧手順ではない。
