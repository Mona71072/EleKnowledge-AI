---
knowledge_id: KH-LINKS-DL-SHORT-12
kind: practice_guide
status: draft
card_version: 1
title: "LINKs — DL 短絡暫定手順（S2A・ED モード）"
symptoms:
  - "DL"
  - "短絡"
  - "1D2G"
  - "LINKs"
  - "ゲート"
  - "ピット"
model_scope:
  lists_model_label:
    - "AXIEZ-LINKS"
  product_lines:
    - "AXIEZ-LINKs"
  control_methods:
    - "VFGLF"
  observed_on: []
  may_apply_to:
    - "最下階リアのみ等で DL 短絡が必要だが正規方法未確立"
  excludes: []
source_refs:
  - ref_type: lists_item
    list_item_id: "12"
---

# LINKs — DL 短絡暫定手順（S2A・ED モード）

## 使う場面・対象条件

**product: AXIEZ-LINKs**（Lists `AXIEZ-LINKS`、制御 **VFGLF**）で **1D2G 2 停止・最下階リアのみ** 等、**DL 短絡** が要るが **正規方法未確立** のときの **稲電・据技回答暫定**（Lists 12）。

## 症状・現象

- ゲート設定・検査が **DL 短絡なし** では進めない（Lists）。

## ソース要約

### Lists（12）暫定手順

1. ピットつなぎ箱 **S2A コネクタ短絡**（手順本体は以下）。
2. **ETP で ED 運転モード**（DOT 短絡状態）。
3. **かごを 2F に停止**。
4. **電源遮断**。
5. ピットで **S2A の DL 短絡可能コネクタ** 接続（**ミニダイナミック 12 極 A01(420)-A02(DL)** — YE317C147 参照）。
6. かご内運転で **カゴドア点検位置まで DN**。
7. 点検後 **逆手順で復帰**。

現地問合せ時は **暫定** として上記を伝える（Lists progress）。

### OneNote

- タイトル一致索引なし。

## 統合した回答・ノウハウ

**暫定** — 正規確立前の稲電回答。**87**（RHQ）等とは別論点。

## 調査・確認手順

1. 停止構成（最下階リア等）が DL 短絡要件か。
2. Lists 手順 **ED→2F→遮断→S2A** の順守。
3. 復帰手順の実施。

## 関連事例と条件の違い

| list | 内容 |
| --- | --- |
| **12** | **DL 暫定** |
| [11](../case-summaries/KH-LINKS-FMS-BDD-WIRING-11.md) | **BDD** 短絡・FMS |
| **172** | 官検 **乗場 PT** |

## KB確認に基づく追記

（該当なし）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | §12 |
| OneNote | なし |
| KB | YE317C147（未 KB 照合） |

## 未確認事項

- 正規短絡方法の後続確定 — Lists は暫定のまま。
