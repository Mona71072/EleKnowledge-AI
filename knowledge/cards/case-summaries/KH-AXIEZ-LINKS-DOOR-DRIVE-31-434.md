---
knowledge_id: KH-AXIEZ-LINKS-DOOR-DRIVE-31-434
kind: case_summary
status: draft
card_version: 1
title: "ドア駆動基板エラー31と CLT/OLT（基板上表示確認）"
symptoms:
  - "エラー31"
  - "CLT"
  - "OLT"
  - "ドア駆動基板"
  - "AXIEZ-LINKS"
  - "位置スイッチ"
model_scope:
  lists_model_label:
    - "AXIEZ-LINKS"
  product_lines:
    - "AXIEZ-LINKs"
  control_methods:
    - "VFGLF"
  door_families:
    - "L型"
  door_types: []
  model_abbreviations: []
  observed_on:
    - "AXIEZ-LINKS"
  may_apply_to:
    - "LINKs 系で駆動基板 7seg/2桁表示に 31、ドア速度は正常な現場"
    - "L型で駆動装置桁上 — 基板 LED と位置 SW LED の取り違え（OneNote）"
  excludes:
    - "LV5K/LV6K の CLT 規定値のみの確認（432 — 戸型明示時）"
  scope_note: "Lists に LV 戸型コードなし。L型は OneNote 注意とセット"
source_refs:
  - ref_type: lists_item
    list_item_id: "434"
  - ref_type: onenote_page
    onenote_id: "6ba79df1-5eac-487b-ba83-2ec0fbc4e471:1"
  - ref_type: onenote_page
    onenote_id: "48423b33-c60c-4add-b7e8-73c7287c93ba:1"
  - ref_type: kb_document
    document_number: "C-18-D60.1-J"
    kb_verify_status: pending
---

# ドア駆動基板エラー31と CLT/OLT（基板上表示確認）

## 使う場面・対象条件

**制御 AXIEZ-LINKS（Lists Model）**。ドア駆動基板表示 **「31」**（正常時 d/F）、**ドア速度・動きは正常** なのにエラーが残るとき（Lists 434）。

**door_families: L型** — OneNote が **L型ドア・桁上駆動** で **装置内基板 LED** と **位置スイッチ LED** の取り違えを警告（Lists 434 本文には L/K なし）。

## 症状・現象

- 駆動基板エラー **31**
- CLT 動作寸法わずか不良（Lists: 0.1 mm 悪化例）
- 遮光板取付不良でセンサ検知不全の **推測**（Lists）

## ソース要約

### Lists（434）

- **切り分け**: 引上げ時は制御盤に加え **ドア駆動基板エラー** 確認。31 でコネクタ断線・接触不良が無ければ **C-18-D60.1-J** に基づき **基板上の位置スイッチ動作距離表示** を確認。
- **事例**: 目測 CLT 4 mm / OLT 5 mm でもエラー継続 → C 資料で基板上取り込み位置確認 → CLT **4.1 mm**（基準外）→ **3.5 mm** 是正 → 自動開閉でエラー消灯。
- **アクチュエータ形 GS** を基板で 5–6 mm 確認、二桁エラーの論理詳細は不明（Lists）。

### OneNote（6ba79df1…:1）

- 434・432 を索引。
- **L型・桁上**: OLT/CLT を **ドア駆動装置内基板 LED** で合わせない → **位置スイッチ LED**。VFGH 総点注意。
- 2光軸 GS、基板 LED 調整と 7seg **314** GS OFF 故障の関連注意（別 PDF 参照・未レビュー）。

## 統合した回答・ノウハウ

エラー **31** は **駆動基板上の CLT/OLT 表示** と **C-18-D60.1-J** で詰める。目測だけで消えない場合は基板表示での寸法確認（Lists 434）。L型・桁上現場では **432 の mm 基準**と **LED の見る場所**（OneNote）を混同しない。

## 調査・確認手順

1. 制御盤＋**ドア駆動基板**エラー（Lists 依頼）。
2. エラー 31 → コネクタ・配線確認。
3. **C-18-D60.1-J** で基板上 OLT/CLT 取り込み位置・表示確認。
4. CLT/OLT 是正（Lists 事例: CLT 3.5 mm）。
5. L型・桁上なら **位置スイッチ LED** で調整していたか OneNote 注意を確認。

## 関連事例と条件の違い

| list | 焦点 |
| --- | --- |
| **434** | 基板 **31**・基板上寸法表示 |
| [432](../practice-guides/KH-LV5K-LV6K-CLT-432.md) | **LV5K/LV6K** CLT/OLT **規定値** |
| **403** | かご上 ST **釦・D14** 信号 |

## KB確認に基づく追記

（未実施 — C-18-D60.1-J）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | §434 |
| OneNote | 6ba79df1…:1、48423b33…:1 |
| KB | C-18-D60.1-J |

## 未確認事項

- エラー 31 のコード定義（KB 未確認）。
- 434 現場の **door_types（LV/KV）** — Lists 未記載。
