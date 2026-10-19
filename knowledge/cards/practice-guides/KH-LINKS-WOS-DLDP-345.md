---

knowledge_id: KH-LINKS-WOS-DLDP-345
kind: practice_guide
status: draft
card_version: 3
title: "GAWからWOSへの切替でDL・DPコネクタが無い"
symptoms:
  - "WOS工法"
  - "GAW工法"
  - "工法切替"
  - "DLコネクタ"
  - "DPコネクタ"
  - "100V"
  - "ブザー"
  - "コンセント"
  - "KB3AB3500"
  - "LINKs"
  - "NMOP"
model_scope:
  observed_on:
    - "AXIEZ-LINKS"
  may_apply_to:
    - "LINKs 制御盤で GAW→WOS 切替する現場（Lists 機種欄は全エレだが LINKs 本体）"
  excludes:
    - "足場工法・WOS単体のみ（DL/DP 不使用で問題にならない）"
source_refs:
  - ref_type: lists_item
    list_item_id: "345"
    source_id: evidence-list-links-wos-dldp-id345
  - ref_type: onenote_page
    onenote_id: "a8c15103-95f4-4d08-897a-403d412bffb5:154"
    note: "WOS/GAW 回路図索引＋Lists 345 リンク"
  - ref_type: kb_document
    document_number: "TI-1335"
    kb_filename: "TI-1335.pdf"
    kb_category: "テクニカルインフォメーション"
    kb_verify_status: catalog_matched
    locator: ""
    summary_from_kb: ""
  - ref_type: draft_record
    record_id: knowhow-elv-links-wos-switch-dldp-connector-id345
    note: "Lists 345 の draft 写し"
review_status: in_review
publication_status: not_published
cloud_approval: not_reviewed
---
# GAWからWOSへの切替でDL・DPコネクタが無い

## 使う場面・対象条件

- **GAW 工法** から **WOS 工法**へ切り替える LINKs 制御盤現場
- 盤側に **DL・DP コネクタが無い**／100 V 系（カゴ上 JB **ブザー・コンセント**）が動かない
- **23 年度/4A 生産以降** DL/DP 抹消の影響（Lists）

## 症状・現象

- GAW→WOS 切替時に DL/DP が盤に無く接続できない（Lists）
- 100 V 未供給 → **ブザーが鳴らない**、**コンセントが使えない**（Lists: 「仕様出来ない」＝使用不可の意）
- 足場・WOS のみでは DL/DP を使わないため **問題にならない**（Lists）

## ソース要約

### Lists（list_item_id: 345）

| 項目 | 内容 |
| --- | --- |
| 展開資料 | **TI-1335**（AXIEZ-LINKs GAW→WOS 切替注意） |
| 100 V 引込 | 制御盤ケーブル **KB3AB3500 G02** を接続し、DL/DP コネクタから 100 V をカゴ上 JB へ |
| 恒久対策 | 支社予算で変わる。**東日本**: アタッチメント **KB3AB428 G01** を治工具センターで付けて出荷 |
| 注意 | 治工具センター **付け忘れ**あり。NMOP の **ダミーコネクタ** を無くさず保管・復帰。盤側 NMOP は **袋入りで分かりにくい** |
| ステータス | 対応済み / 重要度 高 / 2024/06/10 |

### OneNote（`a8c15103-95f4-4d08-897a-403d412bffb5:154`）

- **参考資料**: WOS 工法回路図（LINKs）、GAW 工法回路図（LINKs）、S2-GAW 工法回路図（索引。個別 PDF はリンク未解決）
- **技術情報リスト**「コネクタ間違い」配下に **Lists 345 と同一タイトル**へのリンク
- 注記: **「正常時の制御盤エラーです。」**（OneNote 冒頭。文脈は索引ページ全体）


## 統合した回答・ノウハウ

23 年度/4A 以降、盤から DL/DP が無い場合、GAW→WOS 切替では **KB3AB3500 G02** 経由の 100 V 引込が前提。DL/DP に繋げられないと 100 V が来ず **ブザー・コンセント不具合**になる。足場/WOS 単体は DL/DP 非使用のため該当しない。東日本恒久策は **KB3AB428 G01** 事前取付出荷（付け忘れ注意、NMOP ダミー管理）。

## 調査・確認手順

1. 工法: GAW 切替か、足場/WOS のみか
2. 生産時期（23 年度/4A 以降の DL/DP 抹消の該当有無）
3. DL/DP または **KB3AB3500 G02** による 100 V 引込状態
4. ブザー・コンセントの 100 V 供給
5. 東日本: **KB3AB428 G01** 取付有無、NMOP ダミーコネクタ
6. 詳細手順・図: **TI-1335**（KB `TI-1335.pdf` 索引済・本文未読）

## 関連事例と条件の違い

| 条件 | DL/DP・100 V | 備考 |
| --- | --- | --- |
| GAW→WOS 切替 | 必要（Lists） | 本カード |
| 足場 / WOS のみ | DL/DP 不使用 | 問題にならない |
| 相順・電源誤結線 | 別症状 | OneNote 同页の別リンク |

## KB確認に基づく追記

（未実施 — TI-1335 本文確認後に §4 を補強。）

## 正式資料・元情報（参照元）

| 種別 | 識別子 | 補足 |
| --- | --- | --- |
| Lists | §345 |
| **OneNote** | `a8c15103-95f4-4d08-897a-403d412bffb5:154` | `onenote-0f576759bbdaf38b98d75037.md` |
| **KB** | TI-1335 → `TI-1335.pdf` | カタログ確認済 |

部品参照（Lists 本文）: KB3AB3500 G02、KB3AB428 G01（KB 突合は後続）

編集用写し: `record_id` `knowhow-elv-links-wos-switch-dldp-connector-id345`

## 未確認事項

- TI-1335 該当節（KB 本文）
- 他支社の恒久対策（Lists は東日本例）
- OneNote 回路図 PDF の解決先
