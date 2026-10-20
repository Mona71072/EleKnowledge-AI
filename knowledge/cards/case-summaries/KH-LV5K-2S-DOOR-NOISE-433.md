---

knowledge_id: KH-LV5K-2S-DOOR-NOISE-433
kind: case_summary
status: draft
card_version: 1
title: "LV5K-2S かごドア開閉時のキュルキュル異音（G寸法・STSベルト）"
symptoms:
  - "LV5K-2S"
  - "異音"
  - "G寸法"
  - "STSベルト"
  - "ドア調整"
  - "VFGLF"
model_scope:
  lists_model_label:
    - "VFGLF"
  product_lines:
    - "AXIEZ-LINKs"
  control_methods:
    - "VFGLF"
  door_families: []
  door_types:
    - "LV5K-2S"
  model_abbreviations: []
  observed_on:
    - "LV5K-2S"
  may_apply_to:
    - "LV5K 系 2S 戸型で G寸法・STS ベルト平行度が変わった現場"
  excludes:
    - "CLT/OLT 寸法のみの不具合（432/434）"
source_refs:
  - ref_type: lists_item
    list_item_id: "433"
  - ref_type: onenote_page
    onenote_id: "48423b33-c60c-4add-b7e8-73c7287c93ba:1"
  - ref_type: kb_document
    document_number: "C-18-A9-491.1"
    kb_verify_status: pending
    locator: "G寸法・STSベルト"
    summary_from_kb: ""
---
# LV5K-2S かごドア開閉時のキュルキュル異音（G寸法・STSベルト）

## 使う場面・対象条件

**door_types: LV5K-2S**（Lists 本文「ドアタイプが LV5K-2S」）。**制御 VFGLF** は Lists Model ラベル。

かごドア **調整中** に開閉で **ゴム擦れ様のキュルキュル異音**。Lists 433（2025）。

## 症状・現象

- かごドア開閉時のキュルキュル異音
- ドア調整後に G寸法変化の可能性

## ソース要約

### Lists（433）

- **原因（Lists）**: 調整で **G寸法** 変化 → STSベルトと桁の平行度変化 → プーリー縁等への **STSベルト片当たり**。
- **Notes**: ドア傾きで G寸法が変わるため **据付時も確認**。26/5C 生産以降、桁ベルトが全黒→内側ベージュに変わり本不具合多発（Lists 記載）。
- **対応**: 動画確認 → G寸法確認（基準外）→ **C-18-A9-491.1** 要領で G寸法調整 → 異音解消。
- **参照**: C18-A9-491.1、IN-EL-12-104-42。

### OneNote

- **索引頁** `48423b33-c60c-4add-b7e8-73c7287c93ba:1`（`onenote-336038a945aa30442bbf4b8d.md`）— **navigation のみ**。 他テーマタイトルはカード本文に載せない。リンク先本文はスナップショット参照。


## 統合した回答・ノウハウ

**LV5K-2S** で調整起因の擦れ音は **G寸法・STSベルトと桁の平行度** を C 資料要領で確認する。VFGLF 制御ラベルだけでは戸型が分からないため **Lists 本文の LV5K-2S** を必須条件とする。

## 調査・確認手順

1. 戸型が **LV5K-2S** であることを品目表/Lists 本文で確認。
2. 異音を動画等で STS ベルト関連か判断（Lists progress）。
3. **G寸法** を C-18-A9-491.1 基準で測定・調整。
4. 据付時のドア傾き・G寸法も再確認（Lists Notes）。

## 関連事例と条件の違い

| list | 焦点 |
| --- | --- |
| **433** | G寸法 / STS ベルト異音 |
| [432](../practice-guides/KH-LV5K-LV6K-CLT-432.md) | CLT/OLT **寸法基準** |
| **435** | カプラカバー **結束バンド** |
| [据付・試験・調整ハブ](../practice-guides/KH-ALL-INSTALL-TEST-ADJUST-HUB.md) | 設定・寸法・本スロー **横断** |

## KB確認に基づく追記

（未実施）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | §433 |
| OneNote | 48423b33…:1（索引） |
| KB | C-18-A9-491.1、IN-EL-12-104-42（pending） |

## 未確認事項

- 26/5C 生産以降ベルト色変更の現行適用範囲（Lists 記載のみ）。
