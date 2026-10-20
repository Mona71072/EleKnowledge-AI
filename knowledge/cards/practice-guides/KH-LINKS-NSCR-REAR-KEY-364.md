---
knowledge_id: KH-LINKS-NSCR-REAR-KEY-364
kind: practice_guide
status: draft
card_version: 1
title: "LINKs — リア NSCR-XR キーSW（フロント CPU 経由）"
symptoms:
  - "NSCR-XR"
  - "リア操作盤"
  - "キースイッチ"
model_scope:
  lists_model_label: ["VFGLB", "VFGLF"]
source_refs:
  - ref_type: lists_item
    list_item_id: "364"
---

# LINKs — リア NSCR-XR キーSW（フロント CPU 経由）

## 使う場面・対象条件

**リア** かご内操作盤 **NSCR-XR キーSW** 無効（Lists 364）。

## 症状・現象

- リア **NSCR-XR** 操作で **不動作**（Lists）。

## ソース要約

### Lists（364）

- **原因**: リア CPU からの信号では **SW 仕様上動作しない** — **フロント LHS-103XX** 取込が必要。
- **対策**: リア B7（XH）→ **延長ハーネス** → フロント CPU B7。

### OneNote

- タイトル一致索引なし。

## 統合した回答・ノウハウ

[315 NS 一時解除](./KH-LINKS-NS-TEMP-RELEASE-BLINK-315.md) は **表示** — **364** は **リアキー配線**。

## 調査・確認手順

1. キーSW・XH **ピンアサイン**（Lists progress）。
2. KSWA **6 V** 等。
3. **フロント CPU** 経路の有無。

## 関連事例と条件の違い

| カード | 備考 |
| --- | --- |
| **364** | **リア NSCR** |
| [315](./KH-LINKS-NS-TEMP-RELEASE-BLINK-315.md) | **NS** 運転 |

## KB確認に基づく追記

（Lists のみ）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | §364 |

## 未確認事項

- なし。
