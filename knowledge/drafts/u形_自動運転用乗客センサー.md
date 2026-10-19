---
schema_version: 1
record_id: "u-passenger-sensor-operation"
record_version: 1
title: "u形エスカレーター自動運転用乗客センサーの原文設定"
category: "エスカ（u形）"
record_type: "technical_reference"
product: "エスカレーター"
model_type:
  - "u形"
document_number: ""
revision: ""
effective_date: ""
review_status: "in_review"
publication_status: "not_published"
classification: "unknown"
cloud_approval: "not_reviewed"
keywords:
  - "乗客センサー"
  - "自動運転"
  - "タイマB"
  - "タイマE"
source_path: "エスカ（u形）/各種名称/自動運転用乗客センサー.md"
source_filename: "自動運転用乗客センサー.md"
onenote_id: "06535fb9-1e04-44ce-81e8-794ca50b3d11:92"
related_ids:
  - "esc-svfc-energy-saving"
attachment_paths:
  - "エスカ（u形）/各種名称/OneNote/自動運転用乗客センサー image.png"
  - "エスカ（u形）/各種名称/OneNote/自動運転用乗客センサー image 1.png"
  - "エスカ（u形）/各種名称/OneNote/自動運転用乗客センサー image 2.png"
  - "エスカ（u形）/各種名称/OneNote/自動運転用乗客センサー image 3.png"
reference_links: []
document_references: []
evidence_sources:
  - source_id: "evidence-u-passenger-sensor-original"
    source_type: "vault_original"
    title: "自動運転用乗客センサー（原文）"
    source_path: "エスカ（u形）/各種名称/自動運転用乗客センサー.md"
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-01"
    supports:
      - "センサー向き、待機タイマー、混雑時速度の原文記述"
structured_data:
  specifications:
    - name: "正方向乗込み時の低速・停止待機タイマー"
      value: "120"
      unit: "秒"
      condition: "階高6.5 m以下。原文ではタイマB"
    - name: "正方向乗込み時の低速・停止待機タイマー"
      value: "180"
      unit: "秒"
      condition: "階高6.5 mより高い。原文ではタイマB"
    - name: "逆方向乗込み時タイマー"
      value: "10"
      unit: "秒"
      condition: "原文ではタイマE"
    - name: "混雑時運転への切替"
      value: "25から30"
      unit: "m/min"
      condition: "自動運転時、乗込み口側Cセンサーを3.5秒以上検出"
  source_notes:
    - "Bセンサーは斜め、Cセンサーは横と原文に記載。標準設定図の内容は未確認。"
    - "階高の測定定義、設定の対象機種・改訂は原文だけでは確認できない。"
---

# u形エスカレーター自動運転用乗客センサーの原文設定

## センサー配置・タイマー

- Bセンサーは斜め、Cセンサーは横向きと原文にある。
- 正方向乗込み時（タイマB）は、階高6.5 m以下で120秒、6.5 mより高い場合は180秒で低速待機または停止待機になると記載されている。
- 逆方向乗込み時（タイマE）は10秒で動作すると記載されている。

## 自動運転時の速度

原文は省エネ運転モードとして25 m/minで運転し、乗込み口側のCセンサーを3.5秒以上検出すると、混雑時運転の30 m/minになると記載している。

この速度記述は[[整備済み資料/技術資料/SVFC省エネ運転]]にも25 m/min・30 m/minの記述がある。両資料の対象機種・設定条件が同一であることまでは確認できていない。

## 添付図版

原文の画像4点は配置・標準設定図を含むが、図中の設定値や配線情報はこのノートへ転記していない。

## 出典・確認履歴

- 原文ノート: [[エスカ（u形）/各種名称/自動運転用乗客センサー]]
- 添付画像4点はVault内で実在確認済み。技術レビュー・適用機種・改訂確認前のドラフト。
- 設定変更や運転判断には使用しない。