---
knowledge_id: KH-VFGLF-DOR-DOB-403
kind: case_summary
status: draft
card_version: 2
title: "ドア開閉釦が効かない（DOR-1280D・D14 DCB/DOB）"
symptoms:
  - "ドア開閉釦"
  - "DOB"
  - "DCB"
  - "D14"
  - "DOR-1280D"
  - "7SEG"
  - "戸開閉指令"
  - "VFGLF"
  - "かご上ステーション"
model_scope:
  lists_model_label:
    - "VFGLF"
  product_lines:
    - "AXIEZ-LINKs"
  control_methods:
    - "VFGLF"
  door_families: []
  door_types: []
  model_abbreviations: []
  observed_on:
    - "VFGLF"
  may_apply_to:
    - "LINKs 系かご上 ST DOR-1280D・D14 DCB/DOB 構成（Lists §403 は戸型未記載）"
  excludes:
    - "LV5K/LV6K 等の戸型固有 CLT 事例（432/433）との混同"
  scope_note: "制御 VFGLF。door_types は Lists 未記載のため空"
source_refs:
  - ref_type: lists_item
    list_item_id: "403"
    source_id: evidence-list-door-button-dob-403
  - ref_type: kb_document
    document_number: "YE402B209"
    kb_verify_status: not_in_catalog
    locator: "D14 DCB/DOB"
    summary_from_kb: ""
---

# ドア開閉釦が効かない（DOR-1280D・D14 DCB/DOB）

## 使う場面・対象条件

**制御 VFGLF（LINKs 系）** で **かご内操作盤・かご上 ST** のドア開閉釦が効かず、ドア駆動基板 7SEG で **戸開閉指令が点灯しない** とき。

Lists §403 に **L型/K型・LV/KV のドア型名は未記載**。先に **DOR-1280D / D14 信号系** を切る。現場が **LV5K-2S 等** なら **432/433/435** 等の **door_types** カードへ。

## 症状・現象

- ドア開閉釦押下無効（かご内・かご上）
- 7SEG: 戸開閉指令不点灯

## ソース要約

### Lists（list_item_id 403）

- **切り分け**: 図 **YE402B209** — ドア駆動基板 **D14** コネクタ **DCB/DOB 対地電圧**。
  - 正常: 通常 **5V**、釦押下時 **0V**。
  - 異常: 押下しても **5V のまま** → **かご上 ST 基板** 疑い。
- **対応**: **DOR-1280D** 交換後、電圧変化・釦動作正常（Lists）。

### OneNote

- Lists §403 **タイトル一致なし**（戸・DOB 系は OneNote 索引に散在）。
- 関連: [408](./KH-VFGH-KEIAIN-HMS-DOOR-408.md)（気配り HMS 戸）、[424](./KH-ALL-KEIAI-RX1-PINCH-424.md)（気配り RX1）、[432](../practice-guides/KH-LV5K-LV6K-CLT-432.md)（LV 戸型 CLT）— **機種・信号系が違えば本文を複製しない**。


## 統合した回答・ノウハウ

戸開閉指令が上がらない場合、Lists 403 は **D14 DCB/DOB の 5V→0V 変化** を見て **DOR-1280D（かご上 ST）** を切り分ける。ドア駆動基板単体断定前に ST 側信号を測る。

## 調査・確認手順

1. 7SEG で戸開閉指令の有無を確認。
2. D14 DCB/DOB 対地電圧（通常 5V / 押下 0V）。
3. 変化なし → DOR-1280D 交換検討（Lists 手順）。
4. 交換後再測定・かご内/上釦試験。

## 関連事例と条件の違い

| list | 焦点 |
| --- | --- |
| **403** | ST 基板 DOB/DCB |
| [105](./KH-VFGLF-DOB-CPU-PORTABLE-105.md) | 釦CPU/60A/据付ポータブル |
| [400](./KH-VFGLF-ACTUATOR-HANGER-400.md) | かご上 ST 釦 D14 |
| [434](../case-summaries/KH-AXIEZ-LINKS-DOOR-DRIVE-31-434.md) | 基板 **31** 寸法表示 |
| [424](./KH-ALL-KEIAI-RX1-PINCH-424.md) | **RX1** 2C-2BC |
| [419 戸短](../practice-guides/KH-VFGLB-DOOR-SHORT-RELEASE-419.md) / [CM-LB 戸短](../practice-guides/KH-CM-LB-DOOR-SHORT-LATCH.md) | 官検・試験 **戸短** |
| [432 CLT](../practice-guides/KH-LV5K-LV6K-CLT-432.md) | **LV** 戸調整 |

## KB確認に基づく追記

（未実施 — YE402B209 図面未レビュー）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | §403 |
| OneNote | なし |
| KB | YE402B209（Lists 参照・未突合） |

## 未確認事項

- YE402B209 の現行版・D14 ピン定義の KB 所在。
