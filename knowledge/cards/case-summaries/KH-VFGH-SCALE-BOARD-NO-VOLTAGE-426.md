---
knowledge_id: KH-VFGH-SCALE-BOARD-NO-VOLTAGE-426
kind: case_summary
status: draft
card_version: 1
title: "秤基板無出力 — DC 基板故障と秤電源 CN1 抜け"
symptoms:
  - "秤"
  - "秤基板"
  - "DC基板"
  - "X59LX"
  - "W5"
  - "地絡"
  - "VFGH"
  - "カゴ上ステーション"
model_scope:
  lists_model_label:
    - "VFGH"
  machine_room:
    - "MR"
  control_methods:
    - "VFGH"
  observed_on:
    - "VFGH"
  may_apply_to:
    - "秤調整時に秤基板から電圧が出ない"
  excludes: []
source_refs:
  - ref_type: lists_item
    list_item_id: "426"
---

# 秤基板無出力 — DC 基板故障と秤電源 CN1 抜け

## 使う場面・対象条件

**VFGH** で **秤調整** 時、**秤基板に電圧が出ない** とき。カゴ上ステーション～制御盤の電源系。

## 症状・現象

- 秤調整時 **秤基板出力なし**（Lists）
- W5 A4/A5 が **DC0V** → DC 基板交換後も 0V → **秤装置用電源 CN1 抜け** で解消

## ソース要約

### Lists（426）

- **原因（複合）**: ① **DC 基板故障**（交換）— 据付中 **MBS 配線地絡** の影響推測。② **秤装置用電源入力 CN1 抜け**（再挿入）。
- **調査経路**: YE401B420 等に沿い秤基板から上流へ電圧 tracing（progress 詳細は Lists）。
- **図面注意**: YE401B420 は **'26/1C 生産まで** — 以降 YE402B279。他仕様は C-41-F403.01。

### OneNote

- タイトル一致索引なし。

## 統合した回答・ノウハウ

DC 基板だけ交換しても **下流 CN1 抜け** で 0V が残る。Lists progress の **D6/D2 電圧→DC 基板→CN1** の順がテンプレ。

## 調査・確認手順

1. 秤基板 W5 A4/A5 電圧。
2. カゴ上 ST D6/D2 側電圧（Lists の AC200/300V 切り分け）。
3. DC 基板交換後再測定。
4. 秤装置用電源 **CN1** 嵌合。
5. 図面 rev（YE401B420 vs YE402B279）。

## 関連事例と条件の違い

| 項目 | 426 |
| --- | --- |
| 主因 | 地絡→DC 基板 + **コネクタ抜け** |
| 302 | 乗場アナウンス電源（別 list・matched） |

## KB確認に基づく追記

（該当なし）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | §426 |
| OneNote | なし |
| KB | YE401B420 / YE402B279 / C-41-F403.01（未レビュー） |

## 未確認事項

- MBS 地絡の一次確認記録（Lists 推測段階）。
- 生産ロットと図面適用の現場突合。
