---
knowledge_id: KH-ESC-FREQ-PARAM-427
kind: case_summary
status: draft
card_version: 1
title: "エスカ周波数/RSW 不一致で運転不能（E-1 305 等）"
symptoms:
  - "周波数"
  - "RSW"
  - "E-1 305"
  - "E-3 126"
  - "パラメータ"
  - "SVFC"
  - "エスカレーター"
model_scope:
  lists_model_label: ["全エス機種"]
  product_lines: ["escalator"]
  control_methods: ["SVFC"]
  observed_on: []
  may_apply_to: ["本設受電後エスカ運転不能・60Hz 現場で PSF=60 表示"]
  excludes: []
source_refs:
  - ref_type: lists_item
    list_item_id: "427"
  - ref_type: onenote_page
    onenote_id: "3514df2a-e4b1-44a9-9ee6-691cb8491d2e:31"
  - ref_type: kb_document
    document_number: "C-60-631-VF31.1-J"
    kb_verify_status: pending
---

# エスカ周波数/RSW 不一致で運転不能（E-1 305 等）

## 使う場面・対象条件

**エスカ** 本設後 **運転不能**。P1 **E-1 001/121、E-3 126、E-1 305** 等（Lists 427）。症状原文 **保留** — progress/原因主。

## 症状・現象

- 複数インバータ/PLL 系エラー（Lists progress）
- **PSF 表示 60** → 50Hz 現場なら **パラメータ初期化** 要（Lists 対処法）

## ソース要約

### Lists（427）

- **原因（Lists）**: 出荷試験 **60Hz 用 RSW/S/W 一時変更** が **E90 操作等でリセットされず** 残存の可能性。
- **確認**: P2 **RSW=E** → 7seg **PSF** 後の設定値。
- **初期化**: 運転阻止抜き、RSW 2/1/0 → E/9/0、SW2 UP → Π9n→Π9y→End → ACB/CPU reset（Lists）。
- **稲電**: E-3 126＝RSW と S/W パラメアンマッチ、E-1 305＝電源周波数と S/W アンマッチ（Notes）。

## 統合した回答・ノウハウ

エスカ運転不能は **周波数表示（PSF）** と **VF31.1 エラーコード表** から 427 経路を開く。エレ VFGLF とは別 product。

## 調査・確認手順

1. P1 エラーコード記録。
2. C-60-631-VF31.1 各コード手順。
3. **PSF/RSW3** 確認（Lists）。
4. 60 表示なら **パラメータ初期化**（Lists 手順）。
5. 客先電源周波数・IVFO 配線（progress 項）。

## 関連事例と条件の違い

| list | 内容 |
| --- | --- |
| **427** | 周波数/RSW |
| **103** | 光電待機 |

## KB確認に基づく追記

（VF31.1 追記検討 Notes 2026/05）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | §427 |
| OneNote | 3514df2a…:31 |
| KB | C-60-631-VF31.1-J |

## 未確認事項

- 症状原文（情報管理保留）。
