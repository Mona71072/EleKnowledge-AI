---
knowledge_id: KH-ALL-ALARM-HISTORY-MC3-300
kind: practice_guide
status: draft
card_version: 1
title: "メンテコン — アラーム履歴採取（稲電解析）"
symptoms:
  - "メンテコン"
  - "アラーム履歴"
  - "400h"
  - "DMP"
model_scope:
  lists_model_label: ["全エレ機種"]
  may_apply_to: ["AXIEZ-LINKS"]
source_refs:
  - ref_type: lists_item
    list_item_id: "300"
---

# メンテコン — アラーム履歴採取（稲電解析）

## 使う場面・対象条件

**工事期** など **エラー不明** で **稲電解析** を依頼するとき（Lists 300）。

## 症状・現象

- （豆知識 — 採取手順）

## ソース要約

### Lists（300）

- **連続データ** でアドレス採取 — **先頭から 400h ずつ 5 回**:
  - 制御: **100E6810, 100E6C10, 100E7010, 100E7410, 100E7810**
  - SETS: **100DD020, 100DD420, 100DD820, 100DDC20**
- 保存 **C:\Program Files\Mc3\Data**（**.DMP** 送付）（Lists）。
- 依頼時 **日時・停止位置・運転モード・直前作業** 必須（Lists Notes）。

## 統合した回答・ノウハウ

[77 3桁エラー](./KH-ALL-ERROR-CODE-3DIGIT-77.md)・[305 UCMP 副番](../case-summaries/KH-ALL-UCMP-SW-PARAM-MISMATCH-305.md) と **現場表示** を併用 — 本件は **事後ログ**。

## 調査・確認手順

1. 現象メモ（Lists Notes 項目）。
2. 上記 **アドレス 5+4 ブロック** 採取。
3. **DMP** 送付。
4. 稲電解析依頼。

## 関連事例と条件の違い

| list | 備考 |
| --- | --- |
| **300** | Mc3 履歴 |
| [77](./KH-ALL-ERROR-CODE-3DIGIT-77.md) | 3 桁表示 |

## KB確認に基づく追記

（該当なし）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | §300 |

## 未確認事項

- LINKs 以外制御のアドレス差異。
