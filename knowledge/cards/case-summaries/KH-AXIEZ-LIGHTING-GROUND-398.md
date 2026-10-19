---
knowledge_id: KH-AXIEZ-LIGHTING-GROUND-398
kind: case_summary
status: draft
card_version: 3
title: "AXIEZ-LINKS かごの撓みで照明電源が地絡する"
symptoms:
  - "照明不能"
  - "安定化基板"
  - "地絡"
  - "吊天井"
  - "撓み"
  - "AXIEZ-LINKS"
  - "寝台"
  - "かご幅"
model_scope:
  lists_model_label: []
  product_lines:
    - "AXIEZ-LINKs"
  model_abbreviations: []
  control_methods:
    - "VFGLF"
  observed_on:
    - "AXIEZ-LINKS"
  may_apply_to:
    - "寝台用などかご幅が広い LINKs（Lists 記載）"
  excludes: []
source_refs:
  - ref_type: lists_item
    list_item_id: "398"
    source_id: evidence-list-axiez-links-lighting-ground-id398
  - ref_type: onenote_page
    onenote_id: "1bf5cc5f-f251-49bd-8572-eb97a9878e1b:1"
  - ref_type: draft_record
    record_id: case-elv-axiez-links-car-flex-lighting-power-ground-fault-id398
    note: "Lists 398 の draft 写し"
review_status: in_review
publication_status: not_published
cloud_approval: not_reviewed
---

# AXIEZ-LINKS かごの撓みで照明電源が地絡する

## 使う場面・対象条件

- AXIEZ-LINKS で **カゴ内照明安定化基板の地絡** → **照明不能**
- 輸送後・吊天井付近作業後に発生しやすい（Lists）
- **寝台用などかご幅が広い LINKs** で発生しやすい、との Lists 記載

## 症状・現象

- カゴ内安定化基板が地絡し、照明がつかない（Lists）
- 分類: 機械的・作業的現象（Lists）
- 重要度: 重要 / 対応済み（Lists）

## ソース要約

### Lists（list_item_id: 398）

**原因・メカニズム（Lists）**

- 基板と吊天井の隙間: 設計 **5 mm**
- 輸送で約 **3 mm** たわみ → 作業時に基板部を踏み込み → 隙間消失 → 基板が吊天井に接触 → **地絡**

**対応（Lists progress）**

- 基板交換（暫定）
- 天蓋と吊天井間に **補強** を追加（たわみ対策）

**周知（Lists）**

- 該当部に **重量物を置かない**
- 該当部を **極力踏まず** に作業
- 恒久対策品: 早くて **6 月中旬出荷** 見込み（Lists 共有時点）
- 図面改定後に **Q シート** 展開予定

### OneNote（`1bf5cc5f-f251-49bd-8572-eb97a9878e1b:1`）

- ページ種別: **リンクのみ**（`onenote-8042959ccd281b4de30b4933.md`）。**事実本文は Lists §398 が正本**
- 技術情報リスト: 本件タイトルへのリンク（先詳細ページはスナップショット **未取得**）
- 【資料】: **G1,G2 の差し間違いによる基板と配線の破損**（手配品リンク）— **照明地絡・撓みとは別不具合**

## 統合した回答・ノウハウ

設計隙間 5 mm に対し輸送たわみ約 3 mm、さらに作業踏み込みで基板—吊天井が接触し地絡 → 照明不能。暫定は基板交換＋天蓋—吊天井補強。再発防止は **重量物禁止・踏み込み回避** の周知。幅広かごで起きやすい。

## 調査・確認手順

1. 照明不能・安定化基板地絡の有無
2. 基板—吊天井隙間（設計 5 mm 対、たわみ・接触痕）
3. 輸送・作業履歴（踏み込み・重量物）
4. 暫定: 基板交換、補強の要否（Lists 事例どおり）
5. 恒久対策品・Q シート（Lists 時点の見込み。現行は KB 未確認）

## 関連事例と条件の違い

| 観点 | 本件 | G1/G2 差し間違い（OneNote 別リンク） |
| --- | --- | --- |
| 原因 | 撓み・接触地絡 | コネクタ差し間違い破損 |
| 資料 | Lists 398 | OneNote 手配品リンク |

## KB確認に基づく追記

（未実施 — Lists に Referenced materials 行なし。恒久対策品・図面は KB 後続。）

## 正式資料・元情報（参照元）

| 種別 | 識別子 | 補足 |
| --- | --- | --- |
| Lists | §398 |
| **OneNote** | `1bf5cc5f-f251-49bd-8572-eb97a9878e1b:1` | `onenote-8042959ccd281b4de30b4933.md` |
| **KB** | — | 恒久対策品・図面は後続 |

編集用写し: `record_id` `case-elv-axiez-links-car-flex-lighting-power-ground-fault-id398`

## 未確認事項

- 恒久対策品の型式・適用（Lists は時期見込みのみ）
- 地絡確認の電気手順（KB）
