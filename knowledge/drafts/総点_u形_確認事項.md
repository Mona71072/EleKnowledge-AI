---
schema_version: 1
record_id: "esc-inspection-handover-checklist-reference"
record_version: 1
title: "u形エスカレーター確認事項の原文記録"
category: "総点(u型エス)"
record_type: "catalog"
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
  - "確認事項"
  - "総点検"
  - "引継検査"
  - "安全対策"
source_path: "総点(u型エス)/その他/確認事項.md"
source_filename: "確認事項.md"
onenote_id: "c3c2f392-7d60-46db-b6a4-f3973a5f37e4:64"
related_ids:
  - "esc-safety-switch-contact-settings"
  - "esc-safety-switch-error-code-reference"
attachment_paths: []
reference_links: []
document_references:
  - document_number: ""
    title: "エスカ安全対策品"
    locator: ""
    source_path: ""
evidence_sources:
  - source_id: "evidence-esc-inspection-checklist-original"
    source_type: "vault_original"
    title: "その他 確認事項（原文）"
    source_path: "総点(u型エス)/その他/確認事項.md"
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-01"
    supports:
      - "操作ボタン、締付・配線、検査値、安全対策、引継ぎに関する原文記載項目"
structured_data:
  items:
    - item: "操作ボタン"
      detail: "押しボタンスイッチの動作がスムーズ。キースイッチ表面からの出代AはA<=1 mm。"
    - item: "締付・勘合"
      detail: "制御盤・各JB内端子の締付、コネクタ勘合、ピン抜けを確認。"
    - item: "配線状態"
      detail: "可動部と配線ケーブルの接触がないこと。手摺との接触に注意。"
    - item: "時計設定"
      detail: "RSW(2/1/0) -> (2/0/*) と原文に記載。"
    - item: "異常コード"
      detail: "安全スイッチのA接点を確認する記述。"
    - item: "手摺スリップ率補正"
      detail: "JRE物件LonWorks付のみとの条件記載。"
    - item: "光電装置"
      detail: "センサーケーブル状態、分離型表示タイプの配線、待機運転時の検出・逆乗り検出時の動作確認を記載。"
    - item: "スカート隙間"
      detail: "片側a: 0.5<=a<=4.0 mm、左右合計b: b<=7.0 mm。"
    - item: "運転確認"
      detail: "駅ラッチ内等で官検なしの場合、各安全スイッチの実動作を確認する記述。"
    - item: "ステップ・清掃"
      detail: "ステップのマーキング・ナンバリング、傷・汚れを確認する記述。"
    - item: "引継検査"
      detail: "指摘項目の処理を確認し、未完の場合は進捗を特記事項または指摘一覧に残す記述。"
    - item: "調査改造"
      detail: "依頼の完了およびBILNET登録完了を確認する記述。"
    - item: "安全対策品"
      detail: "据付図で取付部品を確認し、検査報告書記載寸法を満たすか確認する記述。"
    - item: "インナーデッキ"
      detail: "突出がないこと。"
    - item: "エラー確認"
      detail: "RSW(2/1/0) -> (0/0/0) と原文に記載。"
  source_notes:
    - "原文の確認項目一覧であり、承認済み検査要領・完了記録・検査結果ではない。"
    - "対象機種・適用条件・値の改訂現行性は未確認。"
---

# u形エスカレーター確認事項の原文記録

## 原文に列挙された確認項目

| 項目 | 原文記載の内容 |
| --- | --- |
| 操作ボタン | 押しボタンスイッチの動作がスムーズ。キースイッチ表面からの出代AはA<=1 mm。 |
| 締付・勘合 | 制御盤・各JB内端子の締付、コネクタ勘合、ピン抜けを確認。 |
| 配線状態 | 可動部と配線ケーブルの接触がないこと。手摺との接触に注意。 |
| 時計設定 | RSW(2/1/0) -> (2/0/*) と原文に記載。 |
| 異常コード | 安全スイッチのA接点を確認する記述。 |
| 手摺スリップ率補正 | JRE物件LonWorks付のみとの条件記載。 |
| 光電装置 | センサーケーブル状態、分離型表示タイプの配線、待機運転時の検出・逆乗り検出時の動作確認を記載。 |
| スカート隙間 | 片側a: 0.5<=a<=4.0 mm、左右合計b: b<=7.0 mm。 |
| 運転確認 | 駅ラッチ内等で官検なしの場合、各安全スイッチの実動作を確認する記述。 |
| ステップ・清掃 | ステップのマーキング・ナンバリング、傷・汚れを確認する記述。 |
| 引継検査 | 指摘処理を確認し、未完の場合は進捗を特記事項または指摘一覧に残す記述。 |
| 調査改造 | 依頼の完了およびBILNET登録完了を確認する記述。 |
| 安全対策品 | 据付図で取付部品を確認し、検査報告書記載寸法を満たすか確認する記述。 |
| インナーデッキ | 突出がないこと。 |
| エラー確認 | RSW(2/1/0) -> (0/0/0) と原文に記載。 |

## 適用上の注意

このページは原文ノートの確認項目を整理したもので、検査結果や実施済み作業を示さない。対象機種、条件、値の現行性、作業の順序は承認済み最新版で確認すること。設定値変更、通電運転、安全回路の試験を指示する資料として使用しない。

## 出典

- 原文ノート: [[総点(u型エス)/その他/確認事項]]
- 関連原文: [[総点(u型エス)/その他/安全スイッチ情報の確認]]、[[総点(u型エス)/その他/異常コード一覧（エラーコード）]]
- 技術・安全・改訂レビュー前のドラフト。