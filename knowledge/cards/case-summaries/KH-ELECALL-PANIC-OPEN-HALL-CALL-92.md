---
knowledge_id: KH-ELECALL-PANIC-OPEN-HALL-CALL-92
kind: case_summary
status: draft
card_version: 1
title: "パニックオープンと同時に1階乗場呼びが自動登録される"
symptoms:
  - "パニックオープン"
  - "エレコール"
  - "乗場呼び"
  - "SCU"
  - "HA"
  - "接点③"
model_scope:
  lists_model_label:
    - "エレコール"
  product_lines: []
  control_methods: []
  model_abbreviations: []
  door_families: []
  door_types: []
  observed_on:
    - "エレコール"
  may_apply_to:
    - "パニックオープン連動でエントランス(HA)と EL 制御が結線された現場"
  excludes: []
source_refs:
  - ref_type: lists_item
    list_item_id: "92"
  - ref_type: onenote_page
    onenote_id: "2dbb1e7c-e6c4-4b52-87b1-9e8896eaa58b:1"
---

# パニックオープンと同時に1階乗場呼びが自動登録される

## 使う場面・対象条件

**エレコール** 系。**パニックオープン** でセキュリティ解除はするが、**1階乗場呼び自動登録・戸開待機30秒**（動作フロー接点③）も同時に動く（Lists 92）。

## 症状・現象

- パニックオープン + 不要な乗場呼び登録
- 対抗試験時（Lists）

## ソース要約

### Lists（92）

- **切り分け**: キャプチャ③ **SCU 内ターミナル短絡** → パニックオープンのみ（正常）→ **外部（HA 側）** 原因確定。
- **推察**: パニック信号が **エントランス（HA）** 経由で **EL 制御盤接点③** へ回り込み。HA 改造で完了。
- **progress**: 動作フローに PO 無くても **配線系統図に PO あれば必ず試験**（人命関連）。

### OneNote（2dbb1e7c…:1）

- 92 タイトル hit。

## 統合した回答・ノウハウ

PO 単独試験で乗場呼びが混ざる場合、**SCU 短絡** で EL 内/外を分け **HA→接点③** の回り込みを疑う（Lists 92）。

## 調査・確認手順

1. パニックオープン単独動作の期待を動作フロー/系統図で確認。
2. SCU 内該当ターミナル短絡試験（Lists ③）。
3. エントランス（HA）側 PO 配線の回り込み調査。
4. HA 改造後再試験。

## 関連事例と条件の違い

| 系統 | list |
| --- | --- |
| エレコール PO | **92** |
| VFGH DOAS | **373** |
| 群管理・SCU | [338 背後呼び](../practice-guides/KH-AXIEZ-LINKS-BACK-CALL-DISABLE-338.md) / [228 SCU索引](../practice-guides/KH-SCU20-CONN-TEST-228.md) / [286 試験発報](../practice-guides/KH-ALL-GROUP-ALARM-TRIGGER-286.md) |
| [384 3car 群管理](./KH-CM-MA-3CAR-GROUP-2C2BC-384.md) / [371 給電](./KH-MR-GROUP-PANEL-POWER-371.md) | **群管理** 横断 |

## KB確認に基づく追記

（なし）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | §92 |
| OneNote | 2dbb1e7c…:1 |
| KB | なし |

## 未確認事項

- 添付キャプチャはスナップショット未同梱。
