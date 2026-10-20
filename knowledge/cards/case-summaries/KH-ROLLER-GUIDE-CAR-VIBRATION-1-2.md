---
knowledge_id: KH-ROLLER-GUIDE-CAR-VIBRATION-1-2
kind: case_summary
status: draft
card_version: 2
title: "ローラーガイド系 かご内振動（ガイドローラー周波数と PMT 一致）"
symptoms:
  - "かご内振動"
  - "PMT"
  - "ローラーガイド"
  - "ガイドローラー"
  - "ガイドシュー"
  - "4.25Hz"
  - "5.25Hz"
  - "8.5Hz"
  - "バランスウェイト"
  - "振動抑制回路"
  - "CM-MA"
  - "VFGH"
  - "高速"
model_scope:
  lists_model_label:
    - "CM-MA"
  product_lines:
    - "Nexcube"
  machine_room:
    - "MR"
  model_abbreviations:
    - "CM-MA"
  control_methods:
    - "VFGH"
  guide_systems:
    - "roller_guide"
  observed_on:
    - "CM-MA（Lists §1・§2 のみ。他機種の同型事象は未記載）"
  may_apply_to:
    - "ローラーガイド（ガイドローラー／ガイドシュー）を用いる走行系一般"
    - "Nexcube 高速系（CM-MA 等 MR 側、ME-CH / ME-CM — ローラーガイド適用時）"
  excludes:
    - "Lists 上、非ローラーガイド機種への適用は記載根拠なし（機種略称だけで判断しない）"
  scope_note: "主軸は走行系「ローラーガイド」。Lists Model=CM-MA は発生記録ラベル"
source_refs:
  - ref_type: lists_item
    list_item_id: "1"
    source_id: evidence-list-car-vibration-id1
  - ref_type: lists_item
    list_item_id: "2"
    source_id: evidence-list-car-vibration-id2
  - ref_type: kb_document
    document_number: "EA-97"
    kb_verify_status: not_in_catalog
    locator: ""
    summary_from_kb: ""
---

# ローラーガイド系 かご内振動（ガイドローラー周波数と PMT 一致）

## 使う場面・対象条件

**第一に見る軸: ローラーガイド（ガイドローラー／ガイドシュー）付き走行系** で、PMT かご内振動の主周波数が **ガイドローラー（シュー）回転周波数と一致** するとき。

- **Lists 上の記録**は **機種略称 CM-MA**（制御 **VFGH**）の §1・§2 のみ（2021・↑高）。**CM-MA 固有の電気不具合ではなく、ローラーガイド機械系の乗り心地パターン** として読む。
- **CM-MA はローラーガイド中心の構成**（現場知見）。**同じくローラーガイドを用いる他の高速機種**（catalog 上 **ME-CH / ME-CM** 等・VFGH）でも **同型の振動メカニズムが起きうる** — ただし Lists/KB では未確認。機種名だけで開かず **ガイド方式** を先に合わせる。

## 症状・現象

| list | Lists Model | 方向・周波数（報告） | ローラー周波数（報告） |
| --- | --- | --- | --- |
| **1** | CM-MA | 前後・約 **5.25Hz** | ガイドシュー **5.3Hz** |
| **2** | CM-MA | 前後左右・**4.25Hz / 8.5Hz** | カゴ側ガイドローラー **4.24Hz** |

いずれも **ローラー回転周波数 ≒ PMT ピーク** → Lists はガイドローラー（シュー）起因と記載。

## ソース要約

### Lists（list_item_id 1）

- 工事使用開始時 PMT 連続振動。**#4–#6 が同程度に収まり静観**（添付参照）。
- **progress**: ①かご上ガイドシュー BG 位置 ②振動抑制回路ゲイン **SP** ③バランスウェイト位置。
- 参照: EA-97、不発 ATHO07006。

### Lists（list_item_id 2）

- **progress**: ①バネ長 ②バランスウェイト配置 ③ガイドシュー移動 ④バランスウェイト移動。
- 不発 ATHO07047。

### OneNote / Vault（出典ではない索引）

- ガイドシュー異音・振動: `現場_ガイドシュー異音対策参照`（機種横断メモ・本文未統合）。

## 統合した回答・ノウハウ

PMT で **4–5Hz 帯（およびその倍频）がガイドローラー／シュー回転周波数と重なる** とき、原因候補の中心は **ローラーガイド機械系**（位置・バネ・BW・振動抑制 SP）。Lists は **CM-MA 現場** でそれを記録したに過ぎない。**VFGLF 機種名の事例に混同しない**。**スライディングガイドのみの機種**へそのまま転用しない（`guide_systems` 不一致）。

調整の型: ガイドシュー BG／移動、バネ長、バランスウェイト、振動抑制 SP（list 1）。バンク内他号機と同等なら静観（list 1）。

## 調査・確認手順

1. **ローラーガイド適用か** を仕様・図で確認（機種略称のみで決めない）。
2. PMT 波形・方向・主周波数を記録。
3. ガイドローラー／シュー回転周波数とピークの一致。
4. Lists progress: ガイドシュー・バネ・BW → list 1 は SP（EA-97 未レビュー）。
5. 他号機比較（静観判断の参考）。

## 関連事例と条件の違い

| 分け方 | 本カード | 混同しない例 |
| --- | --- | --- |
| **走行系** | ローラーガイド・PMT 周波数一致 | 137 巻上機ビス異音（巻上系） |
| **制御** | VFGH（Lists ラベル） | VFGLF 本スロー BK（392） |
| **現象** | かご内連続振動 | [111](./KH-AXIEZ-LINKS-ROPE-STRING-VIB-111.md) 吊り車弦振動 |
| **品質確認** | PMT の前に、防振ゴム未確認も候補 | [Nexcube QC](../practice-guides/KH-NEXCUBE-VFGH-QC-HUB.md) `:157` `:252`。未実施＝原因とは断定しない。戸振動は `:220` |

## KB確認に基づく追記

（未実施）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | §1, §2（Model=CM-MA） |
| OneNote | タイトル未一致 — [368 DGN 振動](./KH-LINKS-CAR-SWAY-DGN-368.md) / [341 測定](../practice-guides/KH-ALL-IPHONE-VIB-NOISE-APP-341.md) は別系 |
| KB | EA-97 — 未突合 |

## 未確認事項

- ME-CH / ME-CM 等ローラーガイド高速機での Lists 同型事例の有無。
- ローラーガイド vs 他ガイド方式の正式一覧（KB/catalog 未突合）。
- 添付振動データ・静観閾値。
