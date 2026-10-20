---
schema_version: 1
record_id: "knowhow-elv-links-wos-switch-dldp-connector-id345"
list_item_id: "345"
record_version: 1
title: "GAWからWOSへの切替でDL・DPコネクタが無い"
category: "不具合対応(ELV)"
record_type: "knowhow"
product: "エレベーター"
model_type:
  - "AXIEZ-LINKS"
  - "全エレ機種"
document_number: ""
revision: ""
effective_date: ""
review_status: "in_review"
publication_status: "not_published"
classification: "unknown"
cloud_approval: "not_reviewed"
keywords:
  - "WOS工法"
  - "GAW工法"
  - "DLコネクタ"
  - "DPコネクタ"
  - "TI-1335"
related_ids: []
source_path: ""
source_filename: ""
onenote_id: ""
attachment_paths: []
reference_links: []
document_references:
  - "TI-1335"
evidence_sources:
  - source_id: "evidence-list-links-wos-dldp-id345"
    source_type: "lists_csv_snapshot"
    title: "首都工・不具合情報共有リスト: LINKsでWOS工法に切り替える際にDL,DPコネクタが制御盤側に無い"
    source_path: ""
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-19"
    supports:
      - "23年度/4A生産からDL,DPコネクタ抹消、WOS/足場工法では不使用、GAW→WOS切替時のKB3AB3500 G02と100V引込、ブザー・コンセント不動作、東日本支社のKB3AB428 G01出荷対策とNMOPダミーコネクタ注意"
structured_data:
  equipment: "LINKs（リストは全エレ機種欄だが本文はAXIEZ-LINKs GAW→WOS）"
  symptom: "GAW工法からWOS工法へ切替え時、制御盤側にDL・DPコネクタが無く接続できない。足場・WOS工法単体ではDL/DPを使わないため問題にならない、とリスト記載。"
  cause: "23年度/4A生産からDL,DPコネクタが抹消されたこと。GAW→WOS切替時は TI-1335 等に沿い KB3AB3500 G02 等で100Vを引き込む前提で、コネクタ欠落時は100V供給不可→ブザー不鳴・コンセント不可、とリスト説明。"
  verified_actions: []
  outcome: "リスト上は対応済み。恒久対策は支社予算により異なり、東日本支社は KB3AB428 G01 を治工具センターで付けて出荷、と記載。"
---

# GAWからWOSへの切替でDL・DPコネクタが無い

共有リスト上の記録 は、LINKs 制御盤を GAW 工法から WOS 工法へ切り替える際、DL・DP コネクタが制御盤側に無く接続できない、という注意を共有する。足場工法・WOS 工法では DL/DP を使用しないため単独では問題にならない、とリストは述べる。

## リスト上の機序（報告ベース）

- GAW→WOS 切替時: 制御盤ケーブル（KB3AB3500 G02 等）で DL/DP コネクタから 100 V を引き込み、カゴ上 JB のブザー・コンセントへ供給する、と TI-1335 展開がある、とリスト記載
- DL/DP に接続できない場合: 100 V が供給されず、ブザーが鳴らない・コンセントが使えない

## 東日本支社の恒久対策（リスト記載）

- アタッチメント KB3AB428 G01 を治工具センターで付けてから出荷
- NMOP のダミーコネクタを無くさない、治工具使用後に戻す
- 制御盤側 NMOP は出荷時に袋入れで分かりにくい、との注意

## 未確認事項

- 他支社の恒久対策の有無（リストは東日本のみ具体記載）
- 現行出荷仕様・図面との一致
- TI-1335 の現行版と該当節

本記録は注意点の索引であり、配線・切替手順の正本ではない。正式手順は TI-1335 等の所管資料を優先する。
