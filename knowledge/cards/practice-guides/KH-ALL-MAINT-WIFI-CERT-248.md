---
knowledge_id: KH-ALL-MAINT-WIFI-CERT-248
kind: practice_guide
status: draft
card_version: 1
title: "メンテコン 8 世代 — 事務所 Wi-Fi とコンピュータ証明書"
symptoms:
  - "メンテコン"
  - "wifi"
  - "8世代"
  - "コンピュータ証明書"
  - "ZERO申請"
model_scope:
  lists_model_label: ["全エレ機種"]
  guide_systems: ["メンテコン"]
source_refs:
  - ref_type: lists_item
    list_item_id: "248"
---

# メンテコン 8 世代 — 事務所 Wi-Fi とコンピュータ証明書

## 使う場面・対象条件

**新メンテコン（8 世代）** セットアップ後、**事務所 Wi-Fi に接続できない** とき（Lists 248）。

## 症状・現象

- Wi-Fi 接続不可（Lists 症状）。

## ソース要約

### Lists（248）

- **手順要旨**: 社内 **無線 LAN 利用申請** → メール URL → **Edge 管理者モード** で **Import**（詳細 URL は Lists 添付 — スナップショットでは省略）。
- **Notes**: 配布メンテコンは **ZERO 申請済み** — 本手順で接続可。他 PC で証明書だけ取得しても不可の場合は **Wi-Fi MAC の ZERO 申請** を確認。
- **Referenced materials**: 無線 LAN PC セットアップ手順 Ver.1.8。
- **progress**: イントラ個人メニュー → メール・スマートカード → 無線 LAN 利用方法にも記載。

### OneNote

- タイトル一致索引なし。

## 統合した回答・ノウハウ

[118 FwCard McEnv](./KH-ALL-FWCARD-MCENV-DEBUG-118.md) 等 **メンテ作業** と同桶 — **248** は **Wi-Fi 証明書** のみ。

## 調査・確認手順

1. メンテコン世代（8 世代か）。
2. **ZERO 申請**（MAC）済みか。
3. Lists／イントラ手順で **証明書 Import**。
4. 仍不可なら **MAC 申請** と **Edge 管理者** 起動を再確認。

## 関連事例と条件の違い

| カード | 備考 |
| --- | --- |
| **248** | Wi-Fi 証明書 |
| [233](./KH-SCU20-FLASH-REWRITE-233.md) | SCU-20 書換ツール |

## KB確認に基づく追記

（Lists のみ — URL 未転載）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | §248 |

## 未確認事項

- 社内 URL・手順書の最新版は Lists 添付／イントラで確認。
