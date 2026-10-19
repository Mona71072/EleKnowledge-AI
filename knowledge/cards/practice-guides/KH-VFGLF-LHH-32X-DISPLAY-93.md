---
knowledge_id: KH-VFGLF-LHH-32X-DISPLAY-93
kind: practice_guide
status: draft
card_version: 1
title: "VFGLF 表示基板 LHH-32X の手配と現地取扱"
symptoms:
  - "表示基板"
  - "LHH-32X"
  - "VFGLF"
  - "乗場インジ"
  - "電気品目266"
  - "最上階"
  - "LEDインジ"
  - "液晶インジ"
  - "調整"
model_scope:
  observed_on:
    - "VFGLF"
  may_apply_to:
    - "最上階乗場インジが LED 以外・無し・液晶等で表示基板が付く構成"
  excludes: []
source_refs:
  - ref_type: lists_item
    list_item_id: "93"
    source_id: evidence-list-knowledge-id93
  - ref_type: kb_document
    document_number: "C-32-B36.1-J"
    kb_verify_status: filename_in_catalog
    locator: "C-32-B36.1-J-B.pdf"
    summary_from_kb: ""
  - ref_type: kb_document
    document_number: "C-7-C3900-J"
    kb_verify_status: filename_in_catalog
    locator: "C-7-C3900-J-E.pdf"
    summary_from_kb: ""
---

# VFGLF 表示基板 LHH-32X の手配と現地取扱

## 使う場面・対象条件

**VFGLF** で **小箱（A220）に未知の基板** が入っている、または **最上階乗場インジ条件** で **LHH-32X** が手配されている現場。Lists は豆知識・重要、対応不要。

## 症状・現象

- 現場から「LINKs 手配品で用途不明」の問合せ（Lists）
- エラー表示: 未確認

## ソース要約

### Lists（list_item_id 93）

- **手配条件**: **最上階乗場インジが LED インジ以外** のとき **電気品目 266** で **表示基板 LHH-32X** 手配。例: 乗場インジ無し、液晶インジ。
- **出荷**: 品名は乗場切替 SW。**梱番 A220**（最小段ボール）に **組立品を帯電防止袋** 入りで出荷。
- **用途**: **各種調整時に乗場インジの代わりに表示** する基板 → **現地で捨てない**。
- **展開**: 2 月度技連で協力会社展開予定（Lists 時点）。
- **KB 参照（Lists）**: C-32-B36.1-J 取付、C-7-C3900-J 設定。

### OneNote

- list タイトル **一致页なし**（「表示基板」一般言及は別文脈のみ）。

## 統合した回答・ノウハウ

LHH-32X は故障部品ではなく **調整用の仮表示**。**LED 以外・無し・液晶** 等の最上階条件で 266 手配され、**A220 小箱** で届くため問合せが来やすい。廃棄せず、取付・設定は Lists 指定の **C-32-B36.1-J / C-7-C3900-J**（PDF 本文は未レビュー）。

## 調査・確認手順

1. 最上階乗場インジ形式（LED / 液晶 / 無し）を確認。
2. 手配品が LHH-32X・品目 266 か梱包ラベル・品名で確認。
3. 調整工程で乗場インジ代替表示として使用予定か関係者に共有。
4. 取付・設定は KB PDF を `content_reviewed` 後に手順化（現時点は Lists 参照のみ）。

## 関連事例と条件の違い

| 条件 | LHH-32X 手配 |
| --- | --- |
| 最上階 LED インジ | Lists 記載の標準手配外 |
| 液晶・無し等 | 266 / LHH-32X |

## KB確認に基づく追記

（未実施）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | §93 |
| OneNote | なし |
| KB | C-32-B36.1-J-B.pdf, C-7-C3900-J-E.pdf（カタログ突合） |

## 未確認事項

- 現行 VFGLF 仕様での手配条件の継続有無。
- 技連展開後の協力会社向け正本の所在。
