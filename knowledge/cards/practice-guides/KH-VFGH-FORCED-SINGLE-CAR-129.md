---
knowledge_id: KH-VFGH-FORCED-SINGLE-CAR-129
kind: practice_guide
status: draft
card_version: 1
title: "VFGH — 強制シングルカーモード設定"
symptoms:
  - "強制シングルカー"
  - "L1"
  - "PD5"
  - "SET1/0"
  - "MON D/9"
model_scope:
  lists_model_label: ["VFGH"]
  machine_room: ["MRL"]
  control_methods: ["VFGH"]
source_refs:
  - ref_type: lists_item
    list_item_id: "129"
  - ref_type: kb_document
    document_number: "C-8-S450.1-J"
    kb_verify_status: pending
---

# VFGH — 強制シングルカーモード設定

## 使う場面・対象条件

**VFGH** **強制シングルカーモード** 設定（Lists 129）。**原因欄は情報管理保留** — 手順は Lists **症状** 記載どおり索引。

## 症状・現象

- 設定手順の周知（Lists 症状欄）。

## ソース要約

### Lists（129）

- **手順要旨**: ①電源遮断 ② **L1 CN4→P1 PD5** ③ **SET1/0=0/8**, **MON1/0=D/9** ④ **SW2** で 7SEG **on** ⑤ **SW1↓** 確定 ⑥ **CPU リセット** — **設定メモ**（Lists）。
- **C-8-S450.1-J P.13**（Lists 症状欄 — pending）。
- **Reported cause**: 情報管理保留 — 再掲しない。

### OneNote

- タイトル一致索引なし。

## 統合した回答・ノウハウ

群管理 **2CAR** 障害切分 — **212 Z カード** 等と別。**204 P1 リセット** 手順と併記注意。

## 調査・確認手順

1. C-8-S450.1-J P.13（pending）。
2. Lists 手順 **①〜⑥**。
3. 現場 **メモ** 必須（Lists）。

## 関連事例と条件の違い

| カード | 備考 |
| --- | --- |
| **129** | 強制 1CAR |
| [204](../practice-guides/KH-VFGLF-CPU-RESET-HAND-204.md) | P1 リセット |
| [212](../case-summaries/KH-LINKS-Z-CARD-SW-306-212.md) | Z カード群管理 |

## KB確認に基づく追記

（C-8-S450.1-J pending）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | §129 |
| KB | C-8-S450.1-J（pending） |

## 未確認事項

- 保留節の適用条件（Lists cause）。
