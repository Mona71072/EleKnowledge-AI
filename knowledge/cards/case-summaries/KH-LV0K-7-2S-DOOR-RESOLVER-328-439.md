---

knowledge_id: KH-LV0K-7-2S-DOOR-RESOLVER-328-439
kind: case_summary
status: draft
card_version: 1
title: "LV0K-7-2S ドア駆動基板レゾルバ異常（328）"
symptoms:
  - "328"
  - "レゾルバ"
  - "ドア駆動基板"
  - "LV0K-7-2S"
  - "ドアモーター"
  - "MRL"
model_scope:
  lists_model_label:
    - "MRL機種"
  product_lines: []
  control_methods: []
  door_families: []
  door_types:
    - "LV0K-7-2S"
  model_abbreviations: []
  observed_on:
    - "LV0K-7-2S"
  may_apply_to:
    - "Lists Notes の戸型に該当する MRL ドア駆動（制御は Lists 未特定）"
  excludes:
    - "LV5K/LV6K CLT 事例（432）との混同"
source_refs:
  - ref_type: lists_item
    list_item_id: "439"
  - ref_type: onenote_page
    onenote_id: "a8c15103-95f4-4d08-897a-403d412bffb5:160"
  - ref_type: kb_document
    document_number: "C-18-D50.1"
    kb_verify_status: pending
    locator: "2.1.2 パラメータ設定"
---
# LV0K-7-2S ドア駆動基板レゾルバ異常（328）

## 使う場面・対象条件

**door_types: LV0K-7-2S**（Lists §439 Notes）。**Lists Model=MRL機種**（機種略称・制御は本文不足）。

ドア駆動基板 **エラー 328（レゾルバ異常）** の切り分け。Lists 439（対応済）。

## 症状・現象

- ドア駆動基板 **328**（Lists error display）
- Lists 症状行はスナップショット上 **情報管理確認まで保留**（識別情報の可能性）

## ソース要約

### Lists（439）

- **Notes**: ドア型名 **LV0K-7-2S**。モダニ物件・不発手順の支店依頼（Lists）。
- **原因（Lists 結論）**: OLT/CLT・パラメータ・配線確認後、**ドアモーター交換**で解消。**基板戻し**で再発なし → **モーター単体不良**（Lists）。
- **切り分け（progress 要約）**:
  1. OLT/CLT 動作点（Lists: 各 5 mm で良好 — **432 の LV5K/LV6K 基準とは別戸型**）
  2. **C-18-D50.1** 2.1.2 — リア側かご駆動基板パラメータ・ジャンパー
  3. 桁上 JB～駆動基板間配線・かご上配線外観
  4. 基板交換→未解消 → **モーター交換**で解消
- **初期判断**: モーター傷なし・取扱問題なし → モーター初期不良疑い、稲電返却調査（Lists）。

### OneNote

- **索引頁** `a8c15103-95f4-4d08-897a-403d412bffb5:160`（`onenote-d5f6c3af486bdf5471385f01.md`）— **navigation のみ**。 他テーマタイトルはカード本文に載せない。リンク先本文はスナップショット参照。


## 統合した回答・ノウハウ

**LV0K-7-2S** で **328** は Lists 439 の順（OLT/CLT → D50.1 パラメータ → 配線 → **モーター/基板**）を参照。**LV5K/LV6K の CLT 3–4 mm** と **本件 5 mm 記載**を混同しない。

## 調査・確認手順

1. 品目表で **LV0K-7-2S** を確認。
2. トラブルシュートマニュアル＋Lists progress ①–④。
3. **C-18-D50.1** パラメータ・ジャンパー一致確認。
4. 基板交換でも残る場合 **ドアモーター** を疑う（Lists 439 結論）。

## 関連事例と条件の違い

| list | door_types | 焦点 |
| --- | --- | --- |
| **439** | LV0K-7-2S | 328 / モーター |
| [432](../practice-guides/KH-LV5K-LV6K-CLT-432.md) | LV5K/LV6K CLT/OLT **基準値** |
| **434** | （未記載） | 基板 **31** |

## KB確認に基づく追記

（未実施 — C-18-D50.1）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | §439 |
| OneNote | a8c15103…:160（索引） |
| KB | C-18-D50.1 |

## 未確認事項

- Lists 症状原文（情報管理保留）。
- MRL 機種と **制御方式・機種略称**の対応（Lists Model のみ）。
