---
knowledge_id: KH-LINKS-DS-CONNECTOR-1D2G-304
kind: case_summary
status: draft
card_version: 1
title: "LINKs 1D2G — 最下階 DS 未接で休止"
symptoms:
  - "1D2G"
  - "休止"
  - "DS"
  - "312"
  - "電源BOX"
model_scope:
  lists_model_label: ["AXIEZ-LINKS"]
  machine_room: ["MRL"]
source_refs:
  - ref_type: lists_item
    list_item_id: "304"
  - ref_type: kb_document
    document_number: "C-18-D60.1-J"
    kb_verify_status: pending
---

# LINKs 1D2G — 最下階 DS 未接で休止

## 使う場面・対象条件

**1D2G** で **最下階着床→全開→最上階呼び→全閉→数秒後休止**（Lists 304・↑高）。ドア基板 **312** 表示例（Lists）。

## 症状・現象

- **1F リア / 2F フロント** 構成例（Lists progress）。

## ソース要約

### Lists（304）

- **原因**: **DS コネクタ**（基板短絡表記）を **最下階電源 BOX 基板** へ未接 — **フロント（ダミー）側 BOX** 差替漏れ（Lists）。
- **リア側** は DS **1 口のみ** で基板差しのみ — **フロント側も要確認**（Lists）。
- C-18-D60.1-J DOR 系（Lists — pending）。

## 統合した回答・ノウハウ

[11 BDD/電源BOX](../case-summaries/KH-LINKS-FMS-BDD-WIRING-11.md)・[12 DL](../practice-guides/KH-LINKS-DL-SHORT-12.md) と **最下階リア/フロント** の **コネクタ取違え** 同族。

## 調査・確認手順

1. **1D2G** 停止構成（リア/フロント）。
2. **最下階フロント電源 BOX** の **DS/基板短絡** コネクタ。
3. GS・位置 SW・サブ GS（Lists progress）。
4. 仍不良 → ドア基板交換前に **304** 配線（Lists progress）。

## 関連事例と条件の違い

| カード | 備考 |
| --- | --- |
| **304** | DS 未接 |
| [11](./KH-LINKS-FMS-BDD-WIRING-11.md) | BDD 短絡 |
| [12](../practice-guides/KH-LINKS-DL-SHORT-12.md) | DL 暫定 |
| [229](../practice-guides/KH-LINKS-LOWER-TERM-BOX-MOUNT-229.md) | 終点 BOX 腕 |

## KB確認に基づく追記

（C-18-D60.1-J pending）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | §304 |
| KB | C-18-D60.1-J（pending） |

## 未確認事項

- 312 エラーと DS 未接の対応関係（KB 未照合）。
