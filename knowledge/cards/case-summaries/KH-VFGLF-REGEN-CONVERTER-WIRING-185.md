---
knowledge_id: KH-VFGLF-REGEN-CONVERTER-WIRING-185
kind: case_summary
status: draft
card_version: 1
title: "回生コンバータ中継未配線 — 磁極補正 141"
symptoms:
  - "磁極補正"
  - "141"
  - "回生コンバータ"
  - "空回し"
  - "VFGLB"
  - "VFGLF"
model_scope:
  lists_model_label:
    - "VFGLB・VFGLF"
  machine_room:
    - "MRL"
  control_methods:
    - "VFGLB"
    - "VFGLF"
  observed_on:
    - "VFGLB"
    - "VFGLF"
  may_apply_to:
    - "回生コンバータ現場で磁極補正が数秒で止まる"
  excludes: []
source_refs:
  - ref_type: lists_item
    list_item_id: "185"
---

# 回生コンバータ中継未配線 — 磁極補正 141

## 使う場面・対象条件

**VFGLB/VFGLF** **回生コンバータ付** で **磁極補正・空回し** が **2〜3 秒で停止** を繰返し、最終的に巻上が動かなくなる（Lists 185）。

## 症状・現象

- SET1/0=0/d モード、ポータブルで **2〜3 秒停止** → リセットで再発。
- エラー **141**（コンバータ電圧 FB コネクタ抜け）（Lists progress）。

## ソース要約

### Lists（185）

- **原因**: **制御盤～回生コンバータ中継 BOX 配線未実施**。
- **Notes（据付）**: 出荷は **故障運転モード**（ダイオード CV、スロー 15→MELD 8 m/min 制限）。中継 BOX で入替で **PWM 回生** を生かす。**NVA 短絡コネクタ** 取外し **KC10 NVA** 接続等（Lists 詳細）。
- **298** は **エス SVFC UVW** — 機種・現象が異なる。

### OneNote

- タイトル一致索引なし。

## 統合した回答・ノウハウ

**141** + **回生現場** なら **中継配線完了** を Lists 185 Notes どおり確認してから磁極補正。

## 調査・確認手順

1. 回生コンバータ **中継 BOX 配線**（PP14/CP14、NVA/CVA、NVB/CVB、NVC/CVC、PWFH）。
2. **NVA 短絡** vs **KC10** 接続。
3. エラー 141 確認。
4. 配線後 **磁極補正** 再試行。

## 関連事例と条件の違い

| list | 機種/原因 |
| --- | --- |
| **185** | エレ **回生未配線** |
| **298** | エス **UVW** |

## KB確認に基づく追記

（該当なし）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | §185 |
| OneNote | なし |
| KB | なし |

## 未確認事項

- PWFH 据付ミス多発（Lists Notes）— 個別 KB 未照合。
