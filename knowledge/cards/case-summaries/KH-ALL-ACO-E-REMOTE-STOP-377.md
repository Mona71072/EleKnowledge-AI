---
knowledge_id: KH-ALL-ACO-E-REMOTE-STOP-377
kind: case_summary
status: draft
card_version: 1
title: "ACO-E — 遠方発停後 25 分送風継続"
symptoms:
  - "ACO-E"
  - "クーラー"
  - "遠方発停"
  - "送風機"
  - "25分"
model_scope:
  lists_model_label:
    - "全エレ機種"
  observed_on: []
  may_apply_to:
    - "停止条件満たしてもクーラーが即停しない"
  excludes: []
source_refs:
  - ref_type: lists_item
    list_item_id: "377"
  - ref_type: kb_document
    document_number: "C-30-G5.3"
    kb_verify_status: pending
  - ref_type: kb_document
    document_number: "D-C-845.1"
    kb_verify_status: pending
---

# ACO-E — 遠方発停後 25 分送風継続

## 使う場面・対象条件

**全エレ** **クーラー付き運転（ACO-E）** — **遠方発停** 動作確認（Lists 377）。

## 症状・現象

- 停止条件満たしても **クーラーが止まらない**（Lists）。

## ソース要約

### Lists（377）

- **仕様**: 停止条件で **ACOE ライン break** → **圧縮機即停**、**送風機は 25 分後停止**（エアコン取説、Lists）。
- **注意**: 送風しない場合 **DC48V 遠方発信未入力** あり（Lists）。
- **C/D 資料** に 25 分記載なし — 改善提案・DarWin 取説追加（Lists Notes）。
- **progress**: SW6-3 ON、ACOE リレー・配線 OK、取説で確認（Lists）。
- 参照: D-C-845.1 P5、C-30-G5.3 P13、YX201B879 取説 P12（Lists）。

### OneNote

- なし。

## 統合した回答・ノウハウ

不具合では **取説仕様** — **221**（HA 併設 AC）等と系統を分ける。

## 調査・確認手順

1. 停止条件成立確認。
2. **25 分** 待って送風停止か。
3. ACOE リレー・DC48V・SW6-3（Lists progress）。
4. エアコン取説（pending KB）。

## 関連事例と条件の違い

| list | 内容 |
| --- | --- |
| **377** | **ACO-E 25 分** |
| **221** | **HA 併設 AC** |

## KB確認に基づく追記

（C-30-G5.3 / D-C-845.1 — pending）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | §377 |
| OneNote | なし |
| KB | C-30-G5.3、D-C-845.1、YX201B879 |

## 未確認事項

- C/D 改訂反映 — Lists Notes（2025/2 DarWin）。
