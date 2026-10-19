---
knowledge_id: KH-ALL-TOUCHLESS-LHS1050A-RESET-321
kind: practice_guide
status: draft
card_version: 1
title: "タッチレス — LHS-1050A 初期化・振替時リセット"
symptoms:
  - "LHS-1050A"
  - "タッチレス"
  - "戸閉ボタン"
  - "COM2"
model_scope:
  lists_model_label: ["全エレ機種"]
  may_apply_to: ["かご操作盤タッチレス"]
source_refs:
  - ref_type: lists_item
    list_item_id: "321"
  - ref_type: kb_document
    document_number: "C-32-A902.1"
    kb_verify_status: pending
---

# タッチレス — LHS-1050A 初期化・振替時リセット

## 使う場面・対象条件

**かご操作盤タッチレス全階不良**、または **戸閉タッチレスのみ不良**（Lists 321）。

## 症状・現象

- 全階タッチレス・戸開閉タッチレス不動、または **戸閉のみ**（Lists）。

## ソース要約

### Lists（321）

- **原因1**: **LHS-1050A** 中継基板 **設定不良** — LED 点滅から **センサ認識/基板間通信** 異常疑い → **C-32-A902.1** で **初期化・再設定**（Lists）。
- **原因2**: **戸閉ボタンユニット** 不良 — 車いす盤 **戸閉信号コネクタ** を正操作盤へ **振替** で切り分け（Lists）。
- **注意**: 基板振替・**コネクタのみ振替** も **必ずリセット再設定** — しないと **原因遠回り**（Lists Notes）。

## 統合した回答・ノウハウ

[110 誤呼び](../case-summaries/KH-VFGLB-TOUCHLESS-PHANTOM-CALL-110.md)・Lists **365**（初期設定）と **症状が重なる** — 本件は **LHS-1050A 手順** が中心。

## 調査・確認手順

1. **COM2** へ **12V**（Lists）。
2. 嵌合・結線。
3. 基板 **LED 点滅** の意味。
4. **C-32-A902.1** 初期化（pending 詳細）。
5. 戸閉のみ → **コネクタ振替**（基板替え時はリセット必須）。

## 関連事例と条件の違い

| list | 備考 |
| --- | --- |
| **321** | 動作不良 |
| [110](../case-summaries/KH-VFGLB-TOUCHLESS-PHANTOM-CALL-110.md) | 誤登録 |
| [365](./KH-VFGLF-TOUCHLESS-INIT-365.md) | 設定不良 |

## KB確認に基づく追記

（C-32-A902 系 pending）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | §321 |
| KB | C-32-A902.1（pending） |

## 未確認事項

- C 資料手順の KB 本文照合。
