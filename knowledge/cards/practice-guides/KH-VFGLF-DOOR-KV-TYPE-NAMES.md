---
knowledge_id: KH-VFGLF-DOOR-KV-TYPE-NAMES
kind: practice_guide
status: draft
card_version: 1
title: "VFGLF 戸閉装置型名（KV・K4）の読み方"
symptoms:
  - "KV4K-3"
  - "KV4"
  - "K4N-2"
  - "戸閉装置"
  - "VFGLF"
  - "LV5K"
  - "door_types"
model_scope:
  lists_model_label: []
  product_lines:
    - "AXIEZ-LINKs"
  control_methods:
    - "VFGLF"
  door_families: []
  door_types:
    - "KV4K-3"
    - "K4N-2"
  model_abbreviations: []
  observed_on: []
  may_apply_to:
    - "VFGLF で品目表・資料の戸閉装置型名を LV5K/LV6K 戸型と照合するとき"
  excludes:
    - "型名だけから L型/K型（door_families）を断定すること"
  scope_note: "Vault 写し。Lists 単独事例なし"
source_refs:
  - ref_type: onenote_page
    onenote_id: "f21ec98f-05b1-4469-9118-e71fe031f4b6:1"
  - ref_type: kb_document
    document_number: "C-18-A9-491.1-J"
    kb_verify_status: pending
    locator: "LV5K-CO/2S, LV6K-CO/2S/SS"
  - ref_type: draft_record
    record_id: "catalog-elv-door-types-reference"
    note: "照合用。出典にしない"
---

# VFGLF 戸閉装置型名（KV・K4）の読み方

## 使う場面・対象条件

**制御 VFGLF** で **ドア装置の型名**（**door_types**）を品目表・据付資料から確認するとき。

**LV5K/LV6K** はドア装置 **系列名**、**KV4K-3 / K4N-2** 等は **戸閉装置の正式型名**（Vault「戸の種類」写し）。**L型/K型（door_families）** とは別フィールド。

## 症状・現象

（参照カード — 不具合単独ではない）

- かご/乗場で **戸閉装置型名** の取り違え
- 副番 **-2 / -3** の省略

## ソース要約

### OneNote（f21ec98f…:1）— Vault「戸の種類」

- **かご戸閉装置**: 正式 **KV4K-3**、略称 **KV4**。
- **乗場戸閉装置**: 正式 **K4N-2**、略称 **K4**。
- 品番 **131** の **戸閉方式 CO** で確認できる旨（CO の定義は原文未説明）。
- 末尾 **-2/-3 は副番** — 省略しない。

### Lists

- 本テーマの list_item_id なし。LV 戸型事例は **432–435** 等。

### 関連資料（未レビュー）

- C-18-A9-491.1-J — VFGLF / **LV5K-CO/2S, LV6K-CO/2S/SS** 据付・保守（OneNote リンク記載のみ）。

## 統合した回答・ノウハウ

現場の **「ドアタイプ」** 語は **LV5K-2S 等** と **KV 系戸閉型名** の両方があり得る。カードでは **LV* を door_types** に、**KV4K-3 / K4N-2** も **door_types** に原表記で載せ、**L型/K型** は Lists/OneNote が明示したときだけ **door_families** に書く。

## 調査・確認手順

1. 品目表で **ドア型名（LV 系列）** を確認。
2. かご/乗場それぞれ **戸閉装置正式名称**（KV / K4）を確認。
3. 副番付き型名をそのまま記録。
4. 調整・異常切り分けは **戸型別カード**（432/433/434）へ。

## 関連事例と条件の違い

| 識別 | 例 |
| --- | --- |
| door_types LV | 432 CLT、433 LV5K-2S |
| door_types KV/K4 | **本カード**（型名読み） |
| door_families K型 | list **72** KM-LD |

## KB確認に基づく追記

（未実施）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | なし |
| OneNote | f21ec98f…:1 |
| KB | C-18-A9-491.1-J（pending） |

## 未確認事項

- KV/LV と L型/K型の **対照表**（C-18 全文・品目表未確認）。
- 画像・PDF 未閲覧（draft 記載どおり）。
