---
knowledge_id: KH-CM-MA-FIN-THERMO-MGMT-218
kind: case_summary
status: draft
card_version: 1
title: "CM-MA — 養生・室温でフィンサーモ管理外"
symptoms:
  - "028"
  - "038"
  - "04B"
  - "フィンサーモ"
  - "管理外"
  - "養生"
model_scope:
  lists_model_label: ["CM-MA"]
  machine_room: ["MR"]
  control_methods: ["CM-MA"]
source_refs:
  - ref_type: lists_item
    list_item_id: "218"
  - ref_type: kb_document
    document_number: "YE204C552"
    kb_verify_status: pending
---

# CM-MA — 養生・室温でフィンサーモ管理外

## 使う場面・対象条件

**CM-MA** 工事中使用 **管理外** — **リセット不要で自動復帰**（Lists 218・↑高）。

## 症状・現象

- 028/038/04B **フィンサーモ**（90°/70° A/D）（Lists）。
- リアルタイム表示 **なし**、**ラッチ** に残存（Lists progress）。

## ソース要約

### Lists（218）

- **原因**: **機械室空調停止**＋**高温**、**制御盤養生** で **ファン放熱不良**（Lists）。
- **対応**: 養生剥がし＋**換気** → 再発なし（Lists）。
- **YE204C552** — 投入時 **剥がす養生位置**（Lists Notes — pending）。

### OneNote

- タイトル一致索引なし。

## 統合した回答・ノウハウ

エラー **非表示でもラッチ確認**（Lists progress）。**据付養生** は **YE204C552** とセット。[216 意匠養生](../practice-guides/KH-ALL-FINISH-PROTECTION-SHEET-216.md) は **かご意匠** 別件。

## 調査・確認手順

1. 機械室 **温度・空調**。
2. 制御盤 **養生** 残存（YE204C552 — pending）。
3. **ラッチ** で 028/038/04B。
4. 換気・養生除去後 **管理外解消**。

## 関連事例と条件の違い

| list | 備考 |
| --- | --- |
| **218** | フィンサーモ・養生 |
| **303** | 工事 AC 不使用（別件） |

## KB確認に基づく追記

（YE204C552 pending）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | §218 |
| KB | YE204C552（pending） |

## 未確認事項

- 028/038/04B の各閾値定義（KB 未照合）。
