---
schema_version: 1
record_id: "esc-svfc-energy-saving"
record_version: 3
title: "SVFCエスカレーターの省エネ運転速度に関する原文記述"
category: "エスカ機種一覧"
record_type: "technical_reference"
product: "エスカレーター"
model_type:
  - "SVFC"
document_number: ""
revision: ""
effective_date: ""
review_status: "in_review"
publication_status: "not_published"
classification: "unknown"
cloud_approval: "not_reviewed"
keywords:
  - "SVFC"
  - "省エネ運転"
  - "低速待機"
  - "停止待機"
source_path: "エスカ機種一覧/ESC-付加仕様（その他）/自動運転・センサー【SVFC】.md"
source_filename: "自動運転・センサー【SVFC】.md"
onenote_id: "6f5ba25b-61e7-445e-ab15-77b81a9664e5:84"
related_ids:
  - "catalog-escalator-u-models"
  - "esc-auto-lubrication-nozzle"
attachment_paths:
  - "エスカ機種一覧/ESC-付加仕様（その他）/OneNote/自動運転・センサー【SVFC】 image.png"
  - "エスカ機種一覧/ESC-付加仕様（その他）/OneNote/自動運転・センサー【SVFC】 image 1.png"
reference_links: []
document_references:
  - document_number: "C-60-631-VF30.4"
    title: "SVFC省エネ運転に関する参照資料"
    locator: "リストID339に参照記載。本文・版・適用範囲未確認"
    source_path: ""
  - document_number: "S-60-631-VF5.1-J"
    title: "自動運転と省エネ効果（SVFC,国内向）"
    locator: ""
    source_path: ""
evidence_sources:
  - source_id: "evidence-list-svfc-speed-selector-339"
    source_type: "user_provided_extract"
    title: "首都工・不具合情報共有リスト: SVFC速度切替条件"
    source_path: ""
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-09"
    supports:
      - "省エネ運転モードと速度切替スイッチ併用時のLOW/HIGH別速度条件のリスト記載"
      - "個別現場からの照会に対し、電気設計が仕様どおりと回答したとの原リスト記載"
  - source_id: "evidence-esc-svfc-energy-original"
    source_type: "vault_original"
    title: "自動運転・センサー【SVFC】（原文）"
    source_path: "エスカ機種一覧/ESC-付加仕様（その他）/自動運転・センサー【SVFC】.md"
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-01"
    supports:
      - "利用状況および省エネ運転モードごとの速度記述"
structured_data:
  knowledge_items:
    - topic: "速度切替スイッチ併用時の省エネ運転速度は別条件として照合する"
      statement: "首都工・不具合情報共有リストID 339は、SVFCで省エネ運転モードと速度切替スイッチがある条件について、LOW時は利用者の混雑にかかわらず25m/min、HIGH時は混雑時30m/min・閑散時25m/minと記録する。既存の原文記録にある待機モード別速度とは条件別の情報として保持し、条件を単純統合しない。"
      conditions: ["スイッチ併用条件の一事例としてのリスト記載", "HIGH時の利用者なし条件はリストに明記なし"]
      exceptions: ["速度切替の操作方法や個別機の適用可否は示さない。", "S-60-631-VF5.1-JとC-60-631-VF30.4の原本・現行版・適用範囲は未確認。"]
      rationale: "標準速度表とスイッチ併用時の回答を混同せず、利用者状態と運転モードを分けて照合するため。"
      verification_status: "source_recorded"
      evidence_source_ids: ["evidence-list-svfc-speed-selector-339"]
  specifications:
    - name: "通常の省エネ運転速度"
      value: "閑散時25、混雑時30、利用者なし20"
      unit: "m/min"
      condition: "原文がいう国内標準仕様。低速待機・停止待機なし"
    - name: "低速待機速度"
      value: "10"
      unit: "m/min"
      condition: "省エネ運転モード付で低速待機・停止待機がある場合"
    - name: "停止待機速度"
      value: "0"
      unit: "m/min"
      condition: "省エネ運転モード付で低速待機・停止待機がある場合"
  source_notes:
    - "参照PDFと画像2点の内容・改訂は未確認。"
    - "同じSVFC表記でもu形など機種条件により別資料に異なる設定がある。ここに記載した速度と制御盤スイッチ設定を混同しない。"
---

# SVFCエスカレーターの省エネ運転速度に関する原文記述

## 原文記載の速度

| 運転条件 | 速度 | 原文の適用条件 |
| --- | ---: | --- |
| 閑散時 | 25 m/min | 原文がいう国内標準仕様。低速待機・停止待機なし |
| 混雑時 | 30 m/min | 原文がいう国内標準仕様。低速待機・停止待機なし |
| 利用者なし | 20 m/min | 原文がいう国内標準仕様。低速待機・停止待機なし |
| 低速待機 | 10 m/min | 低速待機・停止待機を備える省エネ運転モード |
| 停止待機 | 0 m/min | 低速待機・停止待機を備える省エネ運転モード |

原文には、省エネ運転モードを無効にすることで従来相当の低速待機・停止待機にできるとの記述がある。設定方法、機種適用範囲、現行仕様は参照資料で未確認。

## 速度切替スイッチ併用時のリスト記載

首都工・不具合情報共有リストID 339は、LOW時25m/min（利用者の混雑にかかわらず）、HIGH時は混雑30m/min・閑散25m/minと記載する。この情報は上表の待機モード別速度と条件が異なるため、別条件として保持する。HIGH時の利用者なし条件、適用機種・現行性は未確認であり、速度切替や設定の手順ではない。

協力会社展開用Excelの個別現場報告では、現地確認後に電気設計へ照会し、当該挙動は仕様との回答を得たとしている。現場識別情報と電気的な確認方法・作業詳細は記録しない。設計回答の対象範囲、参照仕様書の内容・現行版、および他機種への適用性は独立確認していない。

## 関連資料

- 原文ノート: [[エスカ機種一覧/ESC-付加仕様（その他）/自動運転・センサー【SVFC】]]
- u形機種情報: [[整備済み資料/技術資料/u形エスカレーター_機種一覧]]（SVFC記載あり。速度の適用機種を示す根拠ではない）
- 制御方式別の給油装置設定: [[整備済み資料/技術資料/ESC_自動給油設定]]（運転速度とは別の設定情報）

## 出典・確認履歴

- 画像2点はVault内で実在確認済み。画像・参照PDF・現行版は未確認。
- 協力会社展開用Excelの個別現場報告は、現地確認後に電気設計へ照会し、挙動は仕様との回答を得たと記載する。物件識別情報・電気確認の方法は転載していない。回答と適用範囲は独立確認していない。
- 技術レビューと適用機種の確認前は、個別機の設定判断に使用しない。