---




knowledge_id: KH-LV5K-LV6K-CLT-432
kind: practice_guide
status: draft
card_version: 1
title: "LV5K/LV6K ドアの CLT・OLT 寸法（戸閉終端の挙動）"
symptoms:
  - "CLT"
  - "OLT"
  - "LV5K"
  - "LV6K"
  - "戸閉終端"
  - "加速"
  - "豆知識"
  - "ゲートスイッチ"
model_scope:
  lists_model_label:
    - "全エレ機種"
  product_lines: []
  control_methods: []
  door_families: []
  door_types:
    - "LV5K-CO/2S"
    - "LV6K-CO/2S/SS/2CO"
  model_abbreviations: []
  observed_on: []
  may_apply_to:
    - "Lists/OneNote が LV5K・LV6K 戸型を明示した現場（L型/K型は品目表で確認）"
  excludes:
    - "Lists Model のみで全機種 CLT を一律変更すること"
  scope_note: "Lists Model=全エレだが適用は door_types の LV 戸型のみ"
source_refs:
  - ref_type: lists_item
    list_item_id: "432"
  - ref_type: onenote_page
    onenote_id: "6ba79df1-5eac-487b-ba83-2ec0fbc4e471:1"
    page_role: cross_cutting
  - ref_type: onenote_page
    onenote_id: "48423b33-c60c-4add-b7e8-73c7287c93ba:1"
    page_role: hybrid
  - ref_type: kb_document
    document_number: "C-18-A9-491.1-J"
    kb_verify_status: pending
    locator: ""
    summary_from_kb: ""
  - ref_type: draft_record
    record_id: "elv-lv5k-lv6k-clt-dimension-acceleration-case"
    note: "照合用写し。出典にしない"
  - ref_type: onenote_page
    onenote_id: "a8c15103-95f4-4d08-897a-403d412bffb5:160"
    page_role: index
    note: "監査適用 (title_hit) — `onenote-d5f6c3af486bdf5471385f01.md`（navigation）"
---
# LV5K/LV6K ドアの CLT・OLT 寸法（戸閉終端の挙動）

## 使う場面・対象条件

**door_types: LV5K-CO/2S、LV6K-CO/2S/SS/2CO**（Lists §432 Notes）。Lists **Model=全エレ機種** は無視し、**品目表のドア型名**で開く。

戸閉終端付近で **一時的に加速したように見える**、CLT を **全閉から 5 mm** にしている、など **寸法・挙動** の確認時。

**L型ドア**で駆動装置が桁上にある場合の **基板 LED vs 位置スイッチ LED** の注意は **434 / OneNote 資料索引**（本件の数値基準とは別論点）。

## 症状・現象

- 戸閉終端付近の不自然な加速様挙動（必ず起きるわけではない）
- CLT 5 mm 設定の現場

## ソース要約

### Lists（432）

- **対象戸型（Notes）**: LV5K-CO/2S、LV6K-CO/2S/SS/2CO。
- **基準**: CLT **全閉から 3～4 mm**、OLT **全開から 5±1 mm**。
- **ゲートスイッチ**: 通常型・アクチュエータ型（DS-131）いずれも CLT は **3～4 mm**（形状で CLT を変えない）。
- **説明（Lists）**: CLT 検知後約 2 mm で速度→位置制御切替。CLT 5 mm だと切替が早く、制御ブレーキ力が小さくクローザー戸閉力が優位になり、終端で加速して見える場合がある。
- **是正例**: CLT を 3～4 mm に是正後、不自然挙動解消（Lists 一例）。
- **依頼**: 品目表でドア型名確認のうえ CLT 規定値を確認。

### OneNote

- **索引頁** `48423b33-c60c-4add-b7e8-73c7287c93ba:1`（`onenote-336038a945aa30442bbf4b8d.md`）— **navigation のみ**。 他テーマタイトルはカード本文に載せない。リンク先本文はスナップショット参照。


## 統合した回答・ノウハウ

LV5K/LV6K 戸型では **CLT 3～4 mm / OLT 5±1 mm** を Lists 432 の基準として保持する。終端の加速様挙動は **CLT 過大（例 5 mm）** の疑いと **クローザー・レール条件** をセットで見る。調整の LED の見方は **432 の数値**と **434/OneNote の L型・基板 LED 注意**を混同しない。

## 調査・確認手順

1. 品目表で **LV5K/LV6K 戸型**（CO/2S 等）を確認。
2. CLT・OLT を **検出装置ランプ**（Lists/OneNote 要領）で測定。
3. CLT が **3～4 mm 外**なら是正（Lists 432）。
4. L型・桁上駆動なら **基板 LED だけ**で合わせていないか OneNote 注意を確認。
5. 挙動が残る場合はクローザー戸閉力・レール抵抗（Lists — 条件依存）。

## 関連事例と条件の違い

| list | 焦点 |
| --- | --- |
| **432** | LV 戸型の CLT/OLT **規定値**・5 mm 事例 |
| [310](../case-summaries/KH-LINKS-LV5K-DOOR-CLT-VIB-310.md) | LINKs 戸閉反動 |
| [246](./KH-LINKS-NORDLOCK-WASHER-LV6K-246.md) | LV6K ノルトロック |
| [434](../case-summaries/KH-AXIEZ-LINKS-DOOR-DRIVE-31-434.md) | 駆動基板 **エラー 31** |
| [433](../case-summaries/KH-LV5K-2S-DOOR-NOISE-433.md) | LV5K-2S **G寸法**・異音 |
| [435](./KH-LV5K-LV6K-CAP-COVER-BAND-435.md) | キャップカバー **バンド** |
| [据付・試験・調整ハブ](./KH-ALL-INSTALL-TEST-ADJUST-HUB.md) | 設定・寸法・本スロー **横断** |

## KB確認に基づく追記

（未実施 — C-18-A9-491.1-J 本文未レビュー）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | §432 |
| OneNote | 6ba79df1…:1、48423b33…:1 |
| KB | C-18-A9-491.1-J（Lists/OneNote 参照・pending） |

## 未確認事項

- C-18-A9-491.1-J の現行版と 432 Notes 値の一致。
- LV 戸型と **L型/K型（door_families）** の対照は品目表未確認。
