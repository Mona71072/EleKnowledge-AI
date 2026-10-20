---

knowledge_id: KH-LINKS-CPDK-INTERCOM-RESET-328
kind: case_summary
status: draft
card_version: 1
title: "LINKs — CPD-K+S と多階インターホンリセット結線"
symptoms:
  - "CPD-K"
  - "インターホン"
  - "リセット回路"
  - "EZ-01M60"
  - "防犯ボタン"
model_scope:
  lists_model_label: ["AXIEZ-LINKS"]
  product_lines: ["AXIEZ-LINKs"]
source_refs:
  - ref_type: lists_item
    list_item_id: "328"
  - ref_type: onenote_page
    onenote_id: "053f163d-7a20-4cfd-950d-005f567aaf6f:1"
    page_role: cross_cutting
    note: "Lists タイトル一致 — snapshot `onenote-fbfb975fa6c1e4a0e2524288.md`（本文未転載）"
---
# LINKs — CPD-K+S と多階インターホンリセット結線

## 使う場面・対象条件

**CPD-K+S** 試験で **着床後に全自動復帰**、**乗場ブザー一瞬で停止** — **多階 EZ-01M60 混在**（Lists 328）。

## 症状・現象

- **配線誤り**（Lists）。

## ソース要約

### Lists（328）

- **構成例**: 管理人親機＋ **1 階（モード付）**＋ **5 階（モード無 EZ-01M60N2）**。
- **原因**: **インターホンリセット回路** 結線ミス。
- **progress**: CO/NO/COM 組合せ試行後、**5 階は COM のみ**（7-8 浮き）、**1 階 CO-COM** で **CPD・ブザー良好**。
- **Notes**: 類似配置の **標準結線図なし** — 図面は A/B 接点記載のみ。

### OneNote

- **onenote_id**: `053f163d-7a20-4cfd-950d-005f567aaf6f:1` — Lists タイトル一致 — snapshot `onenote-fbfb975fa6c1e4a0e2524288.md`（本文未転載）


## 統合した回答・ノウハウ

[423](./KH-JRE-EMER-INTERCOM-MONITOR-423.md)（JRE 非常 IH）等 **IH 分岐** とは別 — **328** は **リセット回路 CO/NO**。

## 調査・確認手順

1. CPD-K+S / SOS 再現。
2. 各階 **リセット端子 7(CO)/8(NO)/9(COM)**。
3. **モード付/無** 混在時の **浮き COM** 試験（Lists progress）。
4. 乗場電源 BOX **通話線**。

## 関連事例と条件の違い

| カード | 備考 |
| --- | --- |
| **328** | **リセット IH** |
| [423](./KH-JRE-EMER-INTERCOM-MONITOR-423.md) | JRE **IH** |

## KB確認に基づく追記

（Lists のみ）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | §328 |

## 未確認事項

- 標準結線図が後追いでないか設計照会。
