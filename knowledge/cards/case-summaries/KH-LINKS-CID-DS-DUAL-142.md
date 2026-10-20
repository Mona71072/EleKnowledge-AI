---
knowledge_id: KH-LINKS-CID-DS-DUAL-142
kind: case_summary
status: draft
card_version: 1
title: "CID-DS — かご内インジ 2 画面にならない"
symptoms:
  - "CID-DS"
  - "2画面"
  - "10.1インチ"
  - "ブルースクリーン"
  - "インジ基板"
  - "AXIEZ-LINKS"
model_scope:
  lists_model_label:
    - "AXIEZ-LINKS"
  machine_room:
    - "MRL"
  control_methods:
    - "AXIEZ-LINKS"
  observed_on:
    - "AXIEZ-LINKS"
  may_apply_to:
    - "CID-DS なのに 1 画面のみ（下半分ブルー想定）"
  excludes: []
source_refs:
  - ref_type: lists_item
    list_item_id: "142"
---

# CID-DS — かご内インジ 2 画面にならない

## 使う場面・対象条件

**AXIEZ-LINKS** **CID-DS**（かご内 10.1 インチ **2 画面**）で **1 画面表示** のとき。

## 症状・現象

- 仕様 **CID-DS** なのに **1 画面**
- 外部入力無し時は **下半分ブルースクリーン** が正（Lists Notes）

## ソース要約

### Lists（142）

- **原因（報告）**: **インジ基板パラメータ設定ミス** — 稲電 **書換ケーブル** で現地 SW 書換予定。
- **progress**: 結線 OK、ロータリー OK、CID-DS は **MELTEC 保守無関係でも下半分に外部映像**（Lists）。
- **Notes**: 不発・対策品受領待ち経路あり。

### OneNote

- タイトル一致索引なし。

## 統合した回答・ノウハウ

2 画面仕様は **ハード結線 OK でもパラメータ/SW**。**107**（VFGLF 予報灯）と制御系が異なる。

## 調査・確認手順

1. 現場仕様 **CID-DS** 確認。
2. 結線・ロータリー（Lists progress ①②）。
3. **下半分ブルー** か完全 1 画面か（Lists Notes）。
4. インジ基板 **SW 書換**（Lists 稲電ケーブル — 手順 KB 待ち）。

## 関連事例と条件の違い

| list | 内容 |
| --- | --- |
| **142** | **2 画面** CID-DS |
| **318** | 乗場 LHH 基板誤品（別） |

## KB確認に基づく追記

（該当なし）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | §142 |
| OneNote | なし |
| KB | なし |

## 未確認事項

- 書換完了後の最終確認（Lists progress 段階）。
