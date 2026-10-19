---
knowledge_id: KH-LINKS-RHQ-CONNECTOR-87
kind: case_summary
status: draft
card_version: 1
title: "RHQ コネクタ忘れ — USL ON 故障でかご上 UP 不可"
symptoms:
  - "RHQ"
  - "USL"
  - "USR"
  - "着床"
  - "かご上"
  - "UP"
  - "AXIEZ-LINKS"
model_scope:
  lists_model_label:
    - "AXIEZ-LINKS"
  product_lines:
    - "AXIEZ-LINKs"
  control_methods:
    - "VFGLF"
  observed_on: []
  may_apply_to:
    - "本スロー後・着床取付後、かご上 UP ができない"
  excludes: []
source_refs:
  - ref_type: lists_item
    list_item_id: "87"
---

# RHQ コネクタ忘れ — USL ON 故障でかご上 UP 不可

## 使う場面・対象条件

**product: AXIEZ-LINKs**（制御 **VFGLF**）**本スロー出し後**、着床取付完了。**かご上ポータブル UP 不可**（Lists 87）。

## 症状・現象

- DZU/DZD が着床プレート検出で停止 → **かご上 UP 不可**。
- 多数エラー（845 系、95D、64E 等）— **USL ON 故障** が鍵（Lists）。

## ソース要約

### Lists（87）

- **RHQ**: **USR** 信号を USL より下の終点 SW へ中継。**短絡コネクタ（RHQ）未装着** → 制御盤で **USR OFF** → 最上階着床で **USL ON 故障** 認識 → **かご上 UP 制限**。
- **対応**: **RHQ コネクタ装着**（出荷時 R1 短絡コネクタの取付忘れ例）。
- **Notes**: 情報管理 **保留**。

### OneNote

- タイトル一致索引なし。

## 統合した回答・ノウハウ

R1 **基板交換前** に **RHQ（短絡コネクタ）** の有無を確認。**319**（RUN SW）とは別経路。[209 USL/CWL](../practice-guides/KH-LINKS-END-SW-USL-CWL-209.md) で **USR/USL 用語**。

## 調査・確認手順

1. **RHQ コネクタ** 装着（R1 基板）。
2. USL/USR/着床 **検出順**（Lists 説明）。
3. エラー USL ON 故障の有無。
4. かご上 UP 再試験。

## 関連事例と条件の違い

| list | 内容 |
| --- | --- |
| **87** | **RHQ → USL** |
| **172** | **RDK 120-1 切断** 乗場 PT |
| **12** | **DL 短絡** 暫定 |
| [392](../case-summaries/KH-VFGLF-BRAKE-SW-392.md) | 本スロー後 UP — 同 **`:156`** 索引 |
| [据付・試験・調整ハブ](../practice-guides/KH-ALL-INSTALL-TEST-ADJUST-HUB.md) | 設定・寸法・本スロー **横断** |

## KB確認に基づく追記

（該当なし）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | §87 |
| OneNote | なし |
| KB | なし |

## 未確認事項

- Notes **保留** — progress の現場固有情報は再掲しない。
