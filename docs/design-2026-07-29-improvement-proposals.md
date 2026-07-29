# 改善提案の届け方（v0）

> **状態:** 実装済（v0）  
> **日付:** 2026-07-29  
> **関連:** [decisions-2026-07-29-layer1-eval-ops.md](./decisions-2026-07-29-layer1-eval-ops.md) / [api/chat.md](./api/chat.md)

---

## 目的

現場の 👎／not_found と「こうなってほしい」文字を、admin が **何を直すか** に落とせるようにする。  
LLM 自動起票は v0 では行わない（ルールベース＋人手）。

## 2 系統の入力

| 入力 | 誰 | 保存 | admin 側 |
|---|---|---|---|
| 👍 / 👎 + 理由チップ | 全利用者 | chatlogs assistant 行 | 失敗一覧 |
| 「こうなってほしい」フォーム | 全利用者 | chatlogs `role=product_wish` | 失敗一覧上部 |

## 改善提案パネル（admin）

- 場所: `/admin/failures` 上部
- 集計: `GET /chat/admin/failures?kind=all` のレスポンスを **クライアント集計**（summary API は未実装）
- しきい値: 同一信号が **3 件以上** で定型カード表示
- `unresolved`: KB が悪いと決め打ちしない。failures で人手振り分け

## やらないこと（v0）

- LLM による改善案自動生成
- Notion / Slack 通知
- 自動 PR / sam deploy
- 現場向け改善提案の表示

## コード

- 集計・ルール: `frontend/src/lib/improvement-proposals.ts`
- UI: `frontend/src/app/admin/failures/page.tsx`
- 要望 API: `POST /chat/suggestions`, `GET /chat/admin/suggestions`

## デプロイ後の実機確認

**itai が phase2 を `sam deploy` したら実施。** 手順チェックリストは  
[impl-log-2026-07-29-clarify-and-page.md](./impl-log-2026-07-29-clarify-and-page.md) の  
「phase2 デプロイ後の実機確認（itai 実施）」を参照。

流れ: **👎 → `/admin/failures` → 要望フォーム → 改善提案カード（≥3 件）**
