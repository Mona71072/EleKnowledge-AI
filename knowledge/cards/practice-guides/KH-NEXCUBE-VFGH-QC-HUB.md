---
knowledge_id: KH-NEXCUBE-VFGH-QC-HUB
kind: practice_guide
status: draft
card_version: 1
title: "Nexcube（NEXWAY 表記）VFGH — 品質確認・調整チェックの入口"
symptoms:
  - "NEXWAY"
  - "Nexcube"
  - "NEXCUBE"
  - "VFGH"
  - "品質確認"
  - "Quality Check"
  - "防振ゴム"
  - "振動"
  - "戸当り"
  - "94D"
  - "コイン電池"
  - "CAN"
model_scope:
  lists_model_label: []
  product_lines:
    - "Nexcube"
  model_abbreviations:
    - "NEXWAY"
  control_methods:
    - "VFGH"
  observed_on: []
  may_apply_to:
    - "OneNote の NEXWAY 品質確認を、日本向けに Nexcube（制御 VFGH）として開くとき"
  excludes:
    - "NEXWAY を CM-MA だけに狭めること"
    - "長周期振動感知（416）を走行振動と同一視すること"
  scope_note: "2026-10-20。NEXWAY は NEXCUBE の海外呼称。日本向けは product_lines: Nexcube。制御が VFGH と書いてある頁は VFGH のまま。CM-MA はその機種略称の一つ。"
source_refs:
  - ref_type: onenote_page
    onenote_id: "4fd4eb57-ccb4-42ad-8733-37598686fd63:157"
    page_role: content
    note: "防振ゴムたわみ・ストッパボルト隙間"
  - ref_type: onenote_page
    onenote_id: "4fd4eb57-ccb4-42ad-8733-37598686fd63:252"
    page_role: content
    note: "防振ゴムの取付"
  - ref_type: onenote_page
    onenote_id: "4fd4eb57-ccb4-42ad-8733-37598686fd63:220"
    page_role: content
    note: "戸開閉の異音・振動、戸当りゴム"
  - ref_type: onenote_page
    onenote_id: "4fd4eb57-ccb4-42ad-8733-37598686fd63:177"
    page_role: content
    note: "P1 コイン電池と 94D"
  - ref_type: onenote_page
    onenote_id: "4fd4eb57-ccb4-42ad-8733-37598686fd63:181"
    page_role: content
    note: "CAN 終端。ringing は通信波形"
  - ref_type: onenote_page
    onenote_id: "4fd4eb57-ccb4-42ad-8733-37598686fd63:254"
    page_role: index
    note: "品質確認フォルダの索引。navigation のみ"
  - ref_type: onenote_page
    onenote_id: "ec02c9c5-cdb7-4e83-bc9a-e950a58b6a11:110"
    page_role: index
    note: "VFGH 検査試験調整要領・据付調整資料の添付索引。本文は PDF"
---

# Nexcube（NEXWAY 表記）VFGH — 品質確認・調整チェックの入口

## 使う場面・対象条件

OneNote に **NEXWAY** と書いてある品質確認・調整チェックを、日本向けに **Nexcube** として開くとき。ノート上の制御が **VFGH** なら `control_methods` は VFGH のまま。**CM-MA** は Nexcube の機種略称の一つであり、このフォルダ全体を CM-MA 専用にしない。

チェック値（隙間・トルク）はスナップショットの記載。**承認済み要領の現行値としては未確認**（画像は未コピー）。

## 症状・現象

- 走行時の振動・異音で、防振ゴムやストッパの確認が済んでいるか不明
- 戸開閉の振動・異音、戸当り
- 低速不能 **94D**（コイン電池）
- CAN の通信異常（波形の ringing。かごの機械振動とは別）

## ソース要約

### OneNote（ノート `4fd4eb57-…`、35 頁）

一覧は [nexcube-vfgh-qc-cluster.jsonl](../../registry/nexcube-vfgh-qc-cluster.jsonl)。索引 `:254` の他テーマ名はここへ写さない。

| 軸 | 頁 | スナップショットに書いてあること |
| --- | --- | --- |
| **走行・防振** | `:157` | 防振ゴムの異常なたわみ、ストッパボルト変形がないこと。無負荷の隙間目安（差動トランス荷重計あり 12±1 mm、なし 10±1 mm） |
| **走行・防振** | `:252` | 防振ゴムが正しく付いていること |
| **戸** | `:220` | 戸開閉で異常な音・振動がないこと。戸当りゴムは当たる直前まで |
| **戸** | `:223` | 乗場戸の開閉でばねから異常音がないこと |
| **94D** | `:177` | P1 コイン電池が無いと停電で磁極学習が RAM から落ち、**94D** で低速不能になりうる、という原文事例 |
| **CAN** | `:181` | 終端抵抗が無いと信号反射と **ringing**（通信波形）。機械振動と混同しない |
| **索引** | `:254` | navigation のみ |

品質確認フォルダ（`4fd4eb57-…`）に **調整要領 PDF は無い**。VFGH の調整資料は別ノートの索引頁。

| 資料（索引に名前があるだけ。本文未レビュー） | 頁 |
| --- | --- |
| **EA-097** VFGH 検査試験調整要領書 | `ec02c9c5-cdb7-4e83-bc9a-e950a58b6a11:110` |
| **C-7-F2900.1-J** VFGH 方式エレベーター据付調整資料 | 同上 |
| VFGH 調整（A核）、高速運転調整、高揚程の調整機能 | 同上（添付名のみ） |
| **EA-030** VFGLB・VFGLF・**VFGH** の S/W 書込・検査試験調整要領 | `a8c15103-95f4-4d08-897a-403d412bffb5:99` |

`:179`（`89aaa87e-…`）は増し締め注意の本文で、末尾に EA-097 へのローカル PDF リンクがある。要領の本文ではない。

**NEXWAY（VFGH）：調整研修** は、このスナップショットと draft にはセクション名として無い。触れた M系 EV 調整研修（B253006、`00c793a4-…:83`）は `研修・教育/社内研修/M系エレ高速調整研修` の開催案内で、別物。

### Lists

- このフォルダ自体に Lists 節は無い。振動事例は別カード。

## 統合した回答・ノウハウ

振動の相談では、先に **品質確認が未実施でないか**を見る。防振ゴムのたわみ・取付（`:157` `:252`）と、戸の開閉振動（`:220`）は、その候補である。**未実施だから振動が起きた、とは書かない。** 周波数一致のガイドローラー（Lists §1/§2）や、長周期感知のジャンパ（§416）は別現象。

94D は QC `:177` が **VFGH / Nexcube（NEXWAY 表記）** のコイン電池。Lists **139** は **AXIEZ-LINKs / VFGLF** の同コード別事例。

## 調査・確認手順

1. 表記が NEXWAY でも、日本向けは **Nexcube**、制御記載が VFGH なら VFGH としてこの入口を開く。
2. かご内の走行振動なら `:157` と `:252` のチェック有無を確認し、周波数が出ているときは [1-2](../case-summaries/KH-ROLLER-GUIDE-CAR-VIBRATION-1-2.md)。
3. 戸の振動・異音なら `:220` / `:223`。長周期の管制運転なら [416](./KH-VFGH-VIBRATION-JUMPER-416.md)（感知器ジャンパ）。
4. 94D なら `:177` と、制御が VFGLF なら [139](../case-summaries/KH-LINKS-POLE-ALIGN-94D-139.md)。
5. 調整の手順本体は品質確認頁ではなく **`ec02c9c5-…:110`**（EA-097、C-7-F2900.1-J）。PDF は未レビュー。入口は [据付・試験・調整ハブ](./KH-ALL-INSTALL-TEST-ADJUST-HUB.md)。

## 関連事例と条件の違い

| カード | 条件 |
| --- | --- |
| [1-2 かご内振動](../case-summaries/KH-ROLLER-GUIDE-CAR-VIBRATION-1-2.md) | PMT とガイドローラー周波数。CM-MA / VFGH |
| [416 長周期](./KH-VFGH-VIBRATION-JUMPER-416.md) | 感知器ジャンパ。走行の防振ゴムではない |
| [139 94D](../case-summaries/KH-LINKS-POLE-ALIGN-94D-139.md) | LINKs / VFGLF。コイン電池は似るが制御が違う |
| [272 ARG](../case-summaries/KH-ME-CH-ARG-GAIN-VIB-272.md) | ME-CH のゲイン。本 QC フォルダではない |
| [据付・試験・調整ハブ](./KH-ALL-INSTALL-TEST-ADJUST-HUB.md) | 要領 PDF への入口 |

## KB確認に基づく追記

（未実施。隙間・トルクの数値は OneNote 記載のまま。現行要領で上書きしない。）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| OneNote | `4fd4eb57-ccb4-42ad-8733-37598686fd63` の content 頁（上表）。全 35 頁は registry |
| Lists | なし（振動事例は各 list カード） |
| KB | 未突合 |

## 未確認事項

- 各チェックの現行図面・要領版（画像未取得）。
- 防振ゴム未確認と、Lists §1/§2 の周波数一致振動が同一現場で重なる実例は未記録。
