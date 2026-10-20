---
knowledge_id: KH-ELENAVI-MELSAFETY-GATE-RESET-205
kind: practice_guide
status: draft
card_version: 1
title: "エレナビ — MELSAFTY ゲート非常解除状態の復帰"
symptoms:
  - "MELSAFTY"
  - "セキュリティゲート"
  - "カード認証"
model_scope:
  lists_model_label: ["エレナビ"]
source_refs:
  - ref_type: lists_item
    list_item_id: "205"
---

# エレナビ — MELSAFTY ゲート非常解除状態の復帰

## 使う場面・対象条件

**連動試験** 後 **カード認証不可** — MELSAFTY **非常解除状態** 残留（Lists 205）。

## 症状・現象

- Lists **症状** は情報管理 **保留**。

## ソース要約

### Lists（205）

- **原因**: 連動試験で **非常解除復帰前** に **ゲート電源 OFF**。
- **復帰**: ゲート電源を **再度 OFF** → 非常解除状態解除 → 正常。
- **Notes**: 履歴は **MELSAFTY-G エラー履歴に出ない** — **カード認証不可** 時に疑う。

### OneNote

- タイトル一致索引なし。

## 統合した回答・ノウハウ

[336 エレナビまとめ](./KH-ELENAVI-ISSUES-INDEX-336.md) **セキュリティ連動** と併読。

## 調査・確認手順

1. MELSAFTY **ゲート状態**（Lists cause）。
2. **非常解除→電源** 操作順の見直し。
3. ゲート **再 OFF** 復帰手順（Lists）。

## 関連事例と条件の違い

| カード | 備考 |
| --- | --- |
| **205** | **非常解除ラッチ** |
| [336](./KH-ELENAVI-ISSUES-INDEX-336.md) | **エレナビ** |

## KB確認に基づく追記

（Lists のみ）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | §205 |

## 未確認事項

- progress 識別 — 保留。
