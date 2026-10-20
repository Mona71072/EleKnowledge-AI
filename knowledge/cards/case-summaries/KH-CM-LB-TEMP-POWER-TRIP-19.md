---
knowledge_id: KH-CM-LB-TEMP-POWER-TRIP-19
kind: case_summary
status: draft
card_version: 1
title: "CM-LB 仮設分電盤トリップ（RA1 被覆地絡）"
symptoms:
  - "CM-LB"
  - "仮設分電盤"
  - "ブレーカートリップ"
  - "地絡"
  - "RA1"
  - "動力線"
model_scope:
  lists_model_label:
    - "CM-LB"
  product_lines:
    - "Nexcube"
  machine_room:
    - "MR"
  model_abbreviations:
    - "CM-LB"
  control_methods:
    - "VFGLB-K"
  observed_on:
    - "CM-LB"
  may_apply_to:
    - "工事使用中の仮設動力・受電～群管理動力線"
  excludes: []
source_refs:
  - ref_type: lists_item
    list_item_id: "19"
    source_id: evidence-list-cm-lb-temporary-breaker-trip-ground-fault-019
---

# CM-LB 仮設分電盤トリップ（RA1 被覆地絡）

## 使う場面・対象条件

**CM-LB** 先行据付・**工事使用** 中に **建築仮設分電盤** がトリップするとき。Lists 19（↑高）。**症状・progress は Lists 保留**、原因・対応行はスナップショットに記載あり。

## 症状・現象

- 仮設分電盤ブレーカートリップ（Lists）
- 症状欄: 情報管理保留

## ソース要約

### Lists（list_item_id 19）

- **原因（報告）**: 受電盤～群管理盤 **RA1 動力線** が機械室ダクト内で **被覆剥け地絡**。余長折返し部がダクト蓋近く、作業員が蓋と枠で **ケーブル挟み** 推測。
- **対応**: 暫定ビニールテープ保護、恒久 **ケーブル交換**。
- 参照: 受電盤接続図（未レビュー）。
- progress: 保留。

### OneNote

- タイトル一致なし。

## 統合した回答・ノウハウ

工事期の CM-LB 現場で仮設盤トリップは **ダクト内 RA1 被覆損傷地絡** を疑う（Lists 19）。ダクト蓋付近の **余長・歩行挟み** を点検。暫定はリスト記載どおり保護、恒久は交換。

## 調査・確認手順

1. トリップ回路・RA1 経路を接続図で特定（図未レビュー）。
2. ダクト内被覆・折返し部・蓋近接を目視。
3. 地絡位置特定後、暫定保護→恒久交換計画。
4. Lists 保留解除後に症状・progress 追記。

## 関連事例と条件の違い

| テーマ | 19 CM-LB | 109 VFGLB |
| --- | --- | --- |
| 契機 | 仮設盤トリップ | TR 端子増し締め |

## KB確認に基づく追記

（未実施）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | §19 |
| OneNote | なし |
| KB | 受電盤接続図 — 未特定 |

## 未確認事項

- 症状・progress 保留内容。
- 暫定後の再発有無（draft は再発なし記載 — Lists progress 保留と突合待ち）。
