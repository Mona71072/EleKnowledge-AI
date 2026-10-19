---
knowledge_id: KH-ALL-SMOKE-FIRE-SERVICE-MELD-227
kind: practice_guide
status: draft
card_version: 1
title: "遮煙大臣認定 — 火災管制運転と MELD 必須"
symptoms:
  - "遮煙"
  - "火災管制運転"
  - "MELD"
  - "火報盤"
  - "戸閉保証"
  - "大臣認定"
model_scope:
  lists_model_label: []
  observed_on: []
  may_apply_to:
    - "遮煙乗場ドア適用現場の仕様・火報接点"
  excludes: []
  scope_note: "Lists Model 行なし — 遮煙適用全般"
source_refs:
  - ref_type: lists_item
    list_item_id: "227"
  - ref_type: kb_document
    document_number: "S-31-50.1"
    kb_verify_status: pending
  - ref_type: law_rag
    law_title: "建築基準法"
    law_id: "325AC0000000201_20260527_508AC0000000023"
    retrieval: "mode=law"
    law_rag_status: current
  - ref_type: law_rag
    law_title: "建築基準法施行令"
    law_id: "325CO0000000338_20251201_507CO0000000377"
    retrieval: "mode=law"
    law_rag_status: current
  - ref_type: law_rag
    law_title: "消防法"
    law_id: "323AC1000000186_20250601_504AC0000000068"
    retrieval: "mode=law"
    law_rag_status: current
---

# 遮煙大臣認定 — 火災管制運転と MELD 必須

## 使う場面・対象条件

**遮煙乗場ドア**（大臣認定）現場で、**火報連動の火災管制運転** や **MELD / 戸閉保証用バッテリー盤** が設計・現物と合っているか確認するとき（Lists 227）。**346**（シール）・**154**（煙感知器）とセットで見る。

## 症状・現象

- 仕様変更で **火報盤が無い** のに SW 上は火災管制あり → **接点なしで管制しない** → 認定不適合（Lists）。
- 遮煙なのに **MELD 無し** 等。

## ソース要約

### Lists（227）

- **必須**: 火報信号連動式 **火災管制運転** ＋ **MELD または戸閉保証用バッテリー盤**（大臣認定条件）。
- ロビーに火災/煙感知器 → **火災警報盤経由**で火報を ELV 制御盤へ。**自火報設置義務の無い建物でも、遮煙認定のため設ける**（Lists Notes）。
- **自家発を遮煙戸の予備電源に代用不可** — 火災時給電・3 分以内起動の保証がないため（Lists）。
- **対応例**: 営設へ申請書類変更、または現地で **認定シール撤去**（Lists）。

## 統合した回答・ノウハウ

テーマまとめ: [LAW-FREQUENT-THEMES.md §B-1](../../registry/LAW-FREQUENT-THEMES.md#b-1-遮煙ドア大臣認定シール)

SW に機能があっても **火報接点・MELD/BBUK** が認定どおりでなければ **大臣認定を満たさない**。停電時戸閉は **ELV 側 MELD 等** — 自家発・停電時管制運転の代用にしない。

## 調査・確認手順

1. 遮煙認定の有無（**346** / S-31-50.1）。
2. 火報盤・感知器 → 制御盤 **火報接点** の実配線。
3. **MELD** または戸閉保証用バッテリー盤の有無。
4. 不適合時は営設・ **シール撤去** 判断（Lists 227）。

## 関連事例と条件の違い

| list | 内容 |
| --- | --- |
| **227** | **火災管制＋MELD** 必須（本カード） |
| [KH-SMOKE-DOOR-MELD-227](./KH-SMOKE-DOOR-MELD-227.md) | 同一 Lists §227 — **BBUK/123** 混同注意 |
| [346](./KH-ALL-SMOKE-DOOR-SEAL-346.md) | 認定番号・シール色 |
| [154](./KH-MRL-SMOKE-SHAFT-DETECTOR-154.md) | シャフト内煙感知器（自火報） |
| [174](../case-summaries/KH-VFGLB-MELD-BATTERY-174.md) | MELD **残量**（VFGLB） |
| [290](./KH-ALL-EMERG-ELEV-FIRE-SERVICE-290.md) | 非常用＋リア遮煙 |
| [390](./KH-MRL-UCMP-SEISMIC-INDEX-390.md) | MR **UCMP/地震** 索引（別系統） |

## KB確認に基づく追記

（S-31-50.1 未レビュー）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | §227 |
| 法令 RAG | 建築基準法・施行令、消防法（frontmatter） |
| KB | S-31-50.1-J（pending） |

## 未確認事項

- 現行副本・認定条件の版（Lists 2023）。
