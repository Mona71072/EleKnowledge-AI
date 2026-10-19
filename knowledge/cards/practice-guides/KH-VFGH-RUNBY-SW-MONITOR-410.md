---
knowledge_id: KH-VFGH-RUNBY-SW-MONITOR-410
kind: practice_guide
status: draft
card_version: 1
title: "VFGH — ランバイ予報 SW の監視盤発報先（MIC/監視盤）"
symptoms:
  - "ランバイ予報"
  - "張り車"
  - "10093CC8"
  - "監視盤"
  - "MIC"
model_scope:
  lists_model_label: ["VFGH"]
  machine_room: ["MRL"]
  control_methods: ["VFGH"]
source_refs:
  - ref_type: lists_item
    list_item_id: "410"
---

# VFGH — ランバイ予報 SW の監視盤発報先（MIC/監視盤）

## 使う場面・対象条件

**ランバイ予報 SW**（かご/CWT 張り車、コンペン、ロックダウン等）が **監視盤に出ない** とき（Lists 410）。

## 症状・現象

- 監視盤 **未発報**（Lists 症状）。

## ソース要約

### Lists（410）

- **発報先**（アドレス変更）: ① **監視盤（デフォルト）** ② **MIC**（保守側変更あり得る）。
- **② MIC 時**: 監視盤へ **発報なし** — **異常灯・ブザーなし**。
- **アドレス**: **10093CC8** — **MIC=00**、**監視盤=FF**。
- **Notes**: OH・調整から **遠隔装置** 取付時、誤って **②** のことがある — 監視盤チェックで予報 SW 不具合時は **発報先確認**。

### OneNote

- タイトル一致索引なし。

## 統合した回答・ノウハウ

[350 UPS](./KH-UPS-PEAK-SERVICE-350.md) も **監視盤 vs 群管理** の **設定優先** — **410** は **ランバイ予報の MIC 切替**。

## 調査・確認手順

1. 監視盤で **予報 SW** 再現。
2. **10093CC8** が **FF（監視盤）** か。
3. 遠隔/MIC 導入履歴（Lists Notes）。
4. 必要なら保守側と **発報先** 合意。

## 関連事例と条件の違い

| カード | 備考 |
| --- | --- |
| **410** | **10093CC8** |
| [350](./KH-UPS-PEAK-SERVICE-350.md) | UPS **監視盤優先** |

## KB確認に基づく追記

（Lists のみ）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | §410 |

## 未確認事項

- アドレス変更手順の詳細は保守ソフト／稲電資料で確認。
