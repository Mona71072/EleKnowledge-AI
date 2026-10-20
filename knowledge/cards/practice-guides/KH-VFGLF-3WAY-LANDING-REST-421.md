---
knowledge_id: KH-VFGLF-3WAY-LANDING-REST-421
kind: practice_guide
status: draft
card_version: 1
title: "VFGLF/VFGLB — 三路式乗場休止スイッチ"
symptoms:
  - "三路式"
  - "乗場休止"
  - "運転"
  - "休止"
  - "キーSW"
model_scope:
  lists_model_label: ["VFGLF", "VFGLB"]
  machine_room: ["MRL"]
  control_methods: ["VFGLF", "VFGLB"]
source_refs:
  - ref_type: lists_item
    list_item_id: "421"
---

# VFGLF/VFGLB — 三路式乗場休止スイッチ

## 使う場面・対象条件

各階 **乗場休止 SW** の表示 **「●−●」** で **運転/休止** が判別できない、**捻り方向で休止向きが階ごとに違う**（Lists 421）。

## 症状・現象

- **豆知識** — 操作方法不明（Lists 症状）。

## ソース要約

### Lists（421）

- **仕様**: **三路式** — **廊下照明の多箇所 SW** と同様、**どの階からでも** 休止⇔運転を **切替**。
- **動作**: EV **運転中** → いずれか階でキー捻りで **休止**。**休止中** → いずれか階で捻りで **運転**。
- **設計**: AXIEZ 時代から **流用検討依頼** — 仕様書 **特記**「三路式乗場休止 SW 手配」で足りる指示（Lists progress）。
- **Notes**: 適用現場は **少ない** — 特記 **「三路式」** 注意。添付 **検討依頼** に適用条件。

### OneNote

- タイトル一致索引なし。

## 統合した回答・ノウハウ

[153 FCC-A](./KH-ALL-FCC-A-FLOOR-153.md) 等 **乗場制御** と別 — **421** は **休止 SW の多箇所連動**。

## 調査・確認手順

1. 仕様書 **特記「三路式」** の有無。
2. 稲電 **動作内容** 確認（Lists — 実施済み）。
3. 現場 **キー捻り** で **全階連動** を確認。
4. 添付 **検討依頼** の適用条件。

## 関連事例と条件の違い

| カード | 備考 |
| --- | --- |
| **421** | **三路式休止** |
| [308](./KH-EMERG-LANDING-NAMEPLATE-308.md) | 乗場 **名板** |
| [153](./KH-ALL-FCC-A-FLOOR-153.md) | いたずら呼び |

## KB確認に基づく追記

（Lists のみ）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | §421 |

## 未確認事項

- 添付検討依頼 PDF は Lists 添付で確認。
