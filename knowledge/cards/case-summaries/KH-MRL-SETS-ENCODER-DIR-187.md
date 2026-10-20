---
knowledge_id: KH-MRL-SETS-ENCODER-DIR-187
kind: case_summary
status: draft
card_version: 1
title: "SETS 基準書込み — ガバナエンコーダ回転方向・9999"
symptoms:
  - "SETS"
  - "基準位置"
  - "9999"
  - "ガバナエンコーダ"
  - "64C"
  - "可変速"
  - "MRL"
model_scope:
  lists_model_label:
    - "MRL機種"
  machine_room:
    - "MRL"
  observed_on: []
  may_apply_to:
    - "SETS 書込み OK 表示でも UP1/UP2 が 9999・可変速にならない"
  excludes: []
  scope_note: "duplicate primary: case-elv-mrl-sets-position-write-direction-spec-id187"
source_refs:
  - ref_type: lists_item
    list_item_id: "187"
---

# SETS 基準書込み — ガバナエンコーダ回転方向・9999

## 使う場面・対象条件

**MRL** **高速調整** で **SETS 基準書込み** が完了しない／**可変速にならない** とき。

## 症状・現象

- 乗場インジ **UP1/2 DN1/2 OK** 表示も **可変速にならない**
- 制御盤位置 **UP1/UP2=9999**（Lists）
- エラー例: **64C**、SETS **42/43**（Lists）

## ソース要約

### Lists（187）

- **9999 要因（Lists）**: ① **ガバナエンコーダ回転方向逆** ② **終点 SW 取り込み逆**
- **本件**: 回転方向設計誤り — **品目115 KUN=LF/RB** 時 **変換コネクタ** 必要（EA-98 p.45）→ 取付で **良好**。
- **Notes**: **KUN 指定は品目確認**（変換コネクタは **電気図面に無い** ことがある）。

### OneNote

- タイトル一致索引なし。

## 統合した回答・ノウハウ

[177 UP1 バネ](./KH-VFGLB-UP1-SPRING-177.md) は **終点 SW 物理** — **187** は **ガバナエンコーダ/KUN**。**9999** 表示は両方の切り口。

SETS **9999** はエンコーダ/SW 系を Lists 187 の二系統で切る。**436**（SETS 664/665 未実施）とは別エラー群。

## 調査・確認手順

1. SETS エラー 42/43/64C（Lists）。
2. 位置表示 **9999** パターン。
3. **品目 KUN** → 変換コネクタ要否（EA-98 — pending）。
4. 終点 SW 取り込み（Lists ②）。

## 関連事例と条件の違い

| list | 内容 |
| --- | --- |
| **187** | エンコーダ **方向** |
| **436** | SETS **検査未実施** 664/665 |

## KB確認に基づく追記

（該当なし）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | §187 |
| OneNote | なし |
| KB | EA-98（pending） |

## 未確認事項

- 個別機種略称（Lists=MRL機種のみ）。
