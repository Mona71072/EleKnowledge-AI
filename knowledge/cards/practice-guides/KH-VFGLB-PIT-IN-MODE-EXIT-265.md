---
knowledge_id: KH-VFGLB-PIT-IN-MODE-EXIT-265
kind: practice_guide
status: draft
card_version: 1
title: "VFGLB — Pit In（Pin）解除手順"
symptoms:
  - "Pit In"
  - "Pin"
  - "据付完了フラグ"
model_scope:
  lists_model_label: ["VFGLB"]
  control_methods: ["VFGLB"]
source_refs:
  - ref_type: lists_item
    list_item_id: "265"
---

# VFGLB — Pit In（Pin）解除手順

## 使う場面・対象条件

**S/W 書換後** **7seg「Pin」** で **自動運転不可** — **据付完了フラグ ON** で **蓋閉じだけでは解除不可**（Lists 265）。

## 症状・現象

- **#29 落ち相当** を S/W 保持 — **CPU リセットでも Pit In 維持**（Lists）。

## ソース要約

### Lists（265）

- **移行条件**: **保守 S/W＋据付完了フラグ**（VFGLB）。VFGLF は **引渡し完了→保守見守り**（Lists Notes）。
- **解除①**: R/M、**SET1/0=0/8**、**MON1/0=8/E** → **CPU リセット 7 秒後** — **蓋 SW 短絡状態** でリセット→MCB 手順（Lists）。
- **解除②**: HAND・**最下階以外** — 最下階 **戸開+ピット SW 復帰→釦 5 s** → **戸閉→釦 5 s**（Lists）。**LINKs ピット制限と異なり HAND**。
- **乗場 RUN 長押 5 s+** で #5 P.U. → **HAND UP/DN のみ**（Lists）。

## 統合した回答・ノウハウ

[317 書換](../case-summaries/KH-ALL-P1-CE1-EMPTY-SW-317.md)・[12 DL 暫定](../practice-guides/KH-LINKS-DL-SHORT-12.md)（LINKs ピット系）と **#29/安全** を混同しない — 本件は **VFGLB Pit In**。

## 調査・確認手順

1. **Pin** 表示と **据付完了フラグ**。
2. 解除 **① or ②**（Lists）。
3. **蓋 SW** と MCB 順序（Lists 注意）。
4. 遠隔監視 **MNT 通報** 有無（Lists Notes）。

## 関連事例と条件の違い

| 制御 | Pit 系 |
| --- | --- |
| **VFGLB** | 保守 SW + 完了フラグ |
| VFGLF | 引渡し完了（Notes） |

## KB確認に基づく追記

（該当なし）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | §265 |

## 未確認事項

- KM-LD 非対応理由（Lists Notes）の KB 裏取り。
