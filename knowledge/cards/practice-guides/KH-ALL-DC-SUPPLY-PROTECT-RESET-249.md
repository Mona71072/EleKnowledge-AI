---
knowledge_id: KH-ALL-DC-SUPPLY-PROTECT-RESET-249
kind: practice_guide
status: draft
card_version: 1
title: "直流電源装置 — 過電流保護後の復帰"
symptoms:
  - "直流電源"
  - "cosel"
  - "TDK-Lambda"
  - "N2"
model_scope:
  lists_model_label: ["全エレ機種"]
source_refs:
  - ref_type: lists_item
    list_item_id: "249"
  - ref_type: onenote_page
    onenote_id: "89aaa87e-d28f-4012-807a-1ef774f0fb6d:230"
    page_role: hybrid
    note: "技術情報リスト — 249 タイトルリンク + 電源BOX点検表"
---

# 直流電源装置 — 過電流保護後の復帰

## 使う場面・対象条件

**乗場釦・ホールランタン不動** 等 — **DC 12 V 系** 不出（Lists 249）。

## 症状・現象

- **電源 BOX 内 DC 変換** — **H10/H20 200 V→12 V** → **N2（621H/601H）**（Lists 例）。

## ソース要約

### Lists（249）

- **過電流/過電圧保護** で **出力停止** — **入力遮断→数分→再投入** で **自動復帰**（Lists）。
- **cosel / TDK-Lambda** 等 — **交換不要** 例（Lists Notes）。

### OneNote（`:230`）

- **技術情報リスト**に Lists 249 **同一タイトル**リンク。過電流/過電圧保護の詳細は **Lists 249 正**。
- 同頁の **電源 BOX 点検表**（コネクタ・アース布設）は 249 本体外 — [267](../case-summaries/KH-ALL-HALL-LANTERN-WRONG-TYPE-267.md) 系調査と併用可。

## 統合した回答・ノウハウ

[267 ランタン取違え](../case-summaries/KH-ALL-HALL-LANTERN-WRONG-TYPE-267.md)・[289 HOS](../case-summaries/KH-ALL-HOS-FL1-HALL-LANTERN-289.md)・[293 PL trip](../case-summaries/KH-ALL-PL-BREAKER-L10A-293.md) と **乗場電源** を切り分け — 本件は **DC 電源保護**。

## 調査・確認手順

1. **12 V 出力** 有無（N2 等）。
2. **過負荷** 疑い → **遮断待ち**（Lists）。
3. 復帰後再測定。
4. 仍不出 → 267/289/配線。

## 関連事例と条件の違い

| カード | 備考 |
| --- | --- |
| **249** | DC 保護 |
| [267](../case-summaries/KH-ALL-HALL-LANTERN-WRONG-TYPE-267.md) | 器具取違え |
| [382](../case-summaries/KH-VFGLF-KEIAIN-HARNESS-PINCH-382.md) | **+12V** 地絡 |

## KB確認に基づく追記

（該当なし）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | §249 |

## 未確認事項

- 復帰時間の型式別目安。
