---
knowledge_id: KH-AXIEZ-LINKS-ROPE-STRING-VIB-111
kind: case_summary
status: draft
card_version: 1
title: "かご吊り車 — 弦振動による微振動・騒音"
symptoms:
  - "振動"
  - "騒音"
  - "弦振動"
  - "最高速"
  - "ブーン"
model_scope:
  lists_model_label: ["AXIEZ-LINKS"]
  machine_room: ["MRL"]
  control_methods: ["LINKS"]
source_refs:
  - ref_type: lists_item
    list_item_id: "111"
  - ref_type: kb_document
    document_number: "C-1-E1.1"
    kb_verify_status: pending
---

# かご吊り車 — 弦振動による微振動・騒音

## 使う場面・対象条件

**AXIEZ-LINKS** **規格 MRL** で **高速走行時のかご微振動・継続振動音**（Lists 111・中部支情報）。

## 症状・現象

- 高速で **小刻み振動**（UP/DN、起動約1秒後最大）。
- 乗員増で **振動減** の報告。
- **レゾルバ誤差学習完了済**（Lists）。

## ソース要約

### Lists（111）

- **原因**: かご下吊り車間ロープの **弦共振周波数** と **ロープ噛み込み周波数** の一致・近似 → 共振・個体伝搬騒音（C-1-E1.1 参照、Lists）。
- **周波数目安**（Lists 記載）: 新 AXIEZ 90/105/120 m/min → 23/27/31 Hz；LINKs → 29/34/38 Hz。
- **対策**: かご吊り車間中央に **弦振動対策品** — ロープ振れ拘束（対応済）。
- **Notes**: 巻上機磁極要因もある → **レゾルバ誤差学習で切り分け**。90 m/min 以上で確認例。不発 ASME17639 / ASME17657 参照。

## 統合した回答・ノウハウ

微振動は **弦振動対策** と **磁極／レゾルバ** を分ける。**C-1-E1.1** が正本（KB pending）。

## 調査・確認手順

1. 速度・現象（最高速・1秒付近）を記録。
2. **レゾルバ誤差学習** 再確認。
3. C-1-E1.1 **弦振動対策品** 要否。
4. 中部支同型事例（Lists Notes）と照合。

## 関連事例と条件の違い

| list | 焦点 |
| --- | --- |
| **111** | 吊り車 **弦** |
| **1/2** | かご内振動（別テーマ） |

## KB確認に基づく追記

（C-1-E1.1 未レビュー）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | §111 |
| KB | C-1-E1.1（pending） |

## 未確認事項

- 現行 C-1-E1.1 改訂と対策品品番。
