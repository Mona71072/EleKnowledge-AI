---

knowledge_id: KH-VFGLB-DOOR-SHORT-RELEASE-419
kind: practice_guide
status: draft
card_version: 1
title: "VFGLB 戸短検出の解除（ラッチあり/なし）"
symptoms:
  - "戸短"
  - "72E"
  - "73E"
  - "74E"
  - "VFGLB"
  - "ラッチ"
  - "CPUリセット"
model_scope:
  lists_model_label: ["VFGLB"]
  control_methods: ["VFGLB"]
  door_families: []
  door_types: []
  observed_on: ["VFGLB"]
  may_apply_to:
    - "官検・負荷試験・最下階 HAND+ポータブルで戸短検出した現場"
  excludes:
    - "CM-LB 戸短ラッチ注意（KH-CM-LB-DOOR-SHORT-LATCH）— 機種別"
source_refs:
  - ref_type: lists_item
    list_item_id: "419"
  - ref_type: onenote_page
    onenote_id: "4f038f2a-3257-4b3e-9541-400ed69b57c0:1"
    page_role: cross_topic
  - ref_type: kb_document
    document_number: "C-7-C3600-J"
    kb_verify_status: pending
---
# VFGLB 戸短検出の解除（ラッチあり/なし）

## 使う場面・対象条件

**制御 VFGLB** で **戸短検出**（72E/73E/74E 等）後、解除手順が不明なとき（Lists 419）。

**CM-LB + VFGLB-K** のラッチ注意は **別カード**（ELV3/戸短拡大）。

## 症状・現象

- 戸短検出で自動投入できない（Lists）
- ①ラッチあり / ②ラッチなし の2パターン（Lists）

## ソース要約

### Lists（419）

- **①ラッチあり**: スイッチ ON+OLT → 最下から移動→かご戸全閉→CPU/MP リセット→乗場全閉→自動→DZ 内で戸短チェック（戸開閉）解除。**最下+HAND+ポータブル** で検出しやすい（Notes）。
- **②ラッチなし**: 自動→DZ で戸短チェック。**負荷試験ドアカット** で検出しやすい。
- **正本手順**: C-7-C3600-J（Lists progress）。

### OneNote（navigation のみ）

- `4f038f2a-3257-4b3e-9541-400ed69b57c0:1` — `onenote-6ff82bf360b94f38608e12f4.md`。**VFGLB 戸短解除の注意点**（Lists 419 と同テーマ）。添付 PDF は URL 未解決 — 手順断定は **C-7-C3600-J**。

## 統合した回答・ノウハウ

VFGLB 戸短は **ラッチあり/なし** で手順が違う。Lists 419 は **C-7-C3600-J** への索引カード。

## 調査・確認手順

1. 検出条件が ①か②か（Lists 検出条件欄）。
2. C-7-C3600-J の解除手順どおり実施。
3. 官検終盤の **最下+HAND+PO** パターンを Notes で認識。

## 関連事例と条件の違い

| カード | 軸 |
| --- | --- |
| **419** | VFGLB 戸短解除 |
| [CM-LB 戸短](./KH-CM-LB-DOOR-SHORT-LATCH.md) | 機種 **CM-LB** |
| [432 CLT](../practice-guides/KH-LV5K-LV6K-CLT-432.md) / [433 異音](../case-summaries/KH-LV5K-2S-DOOR-NOISE-433.md) | **LV 戸型** |
| [403 D14](../case-summaries/KH-VFGLF-DOR-DOB-403.md) | 釦 **DOB/DCB** |
| [据付・試験・調整ハブ](./KH-ALL-INSTALL-TEST-ADJUST-HUB.md) | 設定・寸法・本スロー **横断** |

## KB確認に基づく追記

（C-7-C3600-J 未レビュー）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | §419 |
| OneNote | 4f038f2a…:1 |
| KB | C-7-C3600-J |

## 未確認事項

- door_types（L/K/LV）Lists 未記載。
