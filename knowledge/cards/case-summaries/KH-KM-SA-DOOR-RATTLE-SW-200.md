---
knowledge_id: KH-KM-SA-DOOR-RATTLE-SW-200
kind: case_summary
status: draft
card_version: 1
title: "KM-SA — 一般戸閉ボタンでドアガタつき"
symptoms:
  - "戸閉"
  - "ガタつき"
  - "車いすボタン"
  - "固定ベーン"
  - "KM-SA"
model_scope:
  lists_model_label: ["KM-SA"]
  machine_room: ["MR"]
  control_methods: ["KM-SA"]
source_refs:
  - ref_type: lists_item
    list_item_id: "200"
  - ref_type: kb_document
    document_number: "YP671C067B"
    kb_verify_status: pending
---

# KM-SA — 一般戸閉ボタンでドアガタつき

## 使う場面・対象条件

**KM-SA** **駅舎エレ** で **一般＋車いす戸閉** 併設、**戸閉中ガタつき**（Lists 200・中）。

## 症状・現象

- **一般ボタン** 戸閉で **かご/乗場扉スピード差** ガタつき — **車いすのみ** では出にくい（Lists）。

## ソース要約

### Lists（200）

- **原因**: 建物内据付で **一般＋車いす** — **固定ベーン** では **一般戸閉速度** が合わない（Lists）。
- **引渡し後**: 可動ベーン不可 → **S/W 変更**（全自動/独立/管制で **一般を車いす速度**）で解消（Lists）。
- progress: レール清掃・シュー・遮煙ゴム・ジャンパー等 **未解消** → S/W（Lists）。
- YP671C067B（Lists — pending）。

### OneNote

- タイトル一致索引なし。

## 統合した回答・ノウハウ

**設計段階** で **可動ベーン** 検討 — 引渡し後は Lists の **S/W 戸閉速度統一** 経路。

## 調査・確認手順

1. **一般/車いす** ボタン有無。
2. **固定 vs 可動ベーン**。
3. 機械調整後も残るか → **S/W**（Lists progress）。
4. YP671C067B（pending）。

## 関連事例と条件の違い

| list | 備考 |
| --- | --- |
| **200** | KM-SA 戸閉速度 |
| **227** 系 | 遮煙（別論点） |

## KB確認に基づく追記

（YP671C067B pending）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | §200 |
| KB | YP671C067B（pending） |

## 未確認事項

- S/W パラメータ値（Lists 添付 — 本文未転載）。
