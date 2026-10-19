---
knowledge_id: KH-VFGLF-BRAKE-SW-392
kind: case_summary
status: draft
card_version: 3
title: "VFGLF 本スロー時ブレーキSW設定不良による運転不能"
symptoms:
  - "本スロー"
  - "WOS"
  - "ブレーキスイッチ"
  - "BK1"
  - "438"
  - "614"
  - "932"
  - "B・K・↓"
  - "終点SW"
  - "シーケンス表示"
  - "VFGLF"
model_scope:
  lists_model_label:
    - "VFGLF"
  product_lines:
    - "AXIEZ-LINKs"
  model_abbreviations: []
  control_methods:
    - "VFGLF"
  observed_on:
    - "VFGLF"
  may_apply_to: []
  excludes: []
source_refs:
  - ref_type: lists_item
    list_item_id: "392"
    source_id: evidence-list-vfglf-brake-switch-id392
  - ref_type: onenote_page
    onenote_id: "a8c15103-95f4-4d08-897a-403d412bffb5:156"
    note: "不具合リスト索引（392 タイトルリンク）"
  - ref_type: kb_document
    document_number: "VFGLF据付調整資料抜粋_シーケンス表示"
    kb_filename: "C-7-C3900-J-E.pdf"
    kb_category: "C資料"
    kb_verify_status: catalog_matched
    locator: ""
    summary_from_kb: ""
    note: "Lists 通称 → カタログ上 VFGLF 電気システム据付調整資料"
  - ref_type: draft_record
    record_id: case-elv-vfglf-brake-switch-stroke-id392
    note: "Lists 392 の draft 写し"
review_status: in_review
publication_status: not_published
cloud_approval: not_reviewed
---

# VFGLF 本スロー時ブレーキSW設定不良による運転不能

## 使う場面・対象条件

- **WOS → 本スロー**切替後、**上部終点 SW 調整（動作点）** のあと **スロー運転不能**（VFGLF）
- ブレーキ解放後すぐ閉じる、**438 / 614 / 932**、**B・K・↓** 表示（Lists）

## 症状・現象

- 本スロー切替後しばらく動作 → 上部終点 SW 調整後にスロー不能（Lists）
- CPU リセット後: ブレーキ解放まで行くが **すぐ閉じる**
- 約 3 回運転後 UP/DN 操作でも **ブレーキ解放しない**（438/614/932）
- 稀にスロー可能 → 一定距離後 **緩やか停止**、最上階乗場インジ **B・K・↓**（Lists）
- エラー表示: **438、614、932**（Lists）

## ソース要約

### Lists（list_item_id: 392）

**確定原因（Lists）**

- P1 基板 **mon1/0 2/6 シーケンス 1 表示**で BK 信号確認 → **BK1 解放信号なし**
- スキミゲージで BK1 不動 → **ストローク調整ボルト再調整** → 解消

**調査経過（Lists progress、実施順）**

1. P1 で UP/DN 信号取込み → 確認
2. 終点 SW 挟み込み → 問題なし
3. かご上ポータブル **磁極学習** → 動かず（調整屋判断）
4. レゾルバ線電圧（挿抜状態）→ 異常なし
5. ブレーキ BK1/2: 48 V・導通 → 問題なし
6. ブレーキ BC1/2: 200 V・導通 → 問題なし
7. B・K・↓ 表示時 BK 取込み → **BK1 のみ解放信号なし**

**参照（Lists）**

- VFGLF 据付調整資料抜粋_シーケンス表示（→ KB **`C-7-C3900-J-E.pdf`** 候補）

### OneNote（navigation のみ）

- **索引頁** `a8c15103-95f4-4d08-897a-403d412bffb5:156`（`onenote-1ce36975e184ab075d978bd7.md`）— 本件は **BK 接点不良** 配下リンク。**他テーマタイトルは §6 の関連カード** へ（索引転記しない）。

## 統合した回答・ノウハウ

上部終点調整後のスロー不能は、P1 シーケンス表示で **BK1 解放信号が無い**状態。BK 電圧・導通が正常でも **BK1 スイッチストローク**不良があり、調整ボルト再調整で解消。磁極学習・レゾルバ電圧・終点 SW 挟み込みは本事例では除外済み。

## 調査・確認手順

Lists progress の順を推奨:

1. P1: UP/DN 取込み
2. 終点 SW 挟み込み
3. 磁極学習（必要時）
4. レゾルバ線電圧
5. BK1/2 48 V、BC1/2 200 V・導通
6. **mon1/0 2/6 シーケンス 1** で BK1/BK2 解放信号
7. スキミゲージで BK1 動作 → **ストローク調整ボルト**

## 関連事例と条件の違い

| カード / 論点 | 備考 |
| --- | --- |
| **392 本件** | 本スロー・終点 SW 調整後 **BK1 ストローク**（Lists §392） |
| [27](./KH-LINKS-BLOCKING-DEVICE-G6-27.md) | G6 固定装置・本スロー |
| [7](./KH-LINKS-TERM-BOX-S2A-7.md) | S1A/S2A 嵌合・終点箱 |
| [63](./KH-LINKS-BK2-SETTING-63.md) / [81](./KH-LINKS-BK-SW-SETTING-81.md) | BK2 / BK SW — 同 **`:156`** 索引 |
| [176](./KH-ALL-GROUND-N00-NORMAL-SLOW-176.md) | N00 アース・本スロー不出 |
| [87](./KH-LINKS-RHQ-CONNECTOR-87.md) | RHQ 忘れ |
| [90](../practice-guides/KH-AXIEZ-WOS-SHORT-CONNECTOR-90.md) | WOS 短絡コネクタ |
| [55](./KH-LINKS-PSL-PIN-55.md) / [342](./KH-LINKS-PSL-PIN-S21-342.md) | PSL ピン・本スロー DN |
| [139](./KH-LINKS-POLE-ALIGN-94D-139.md) | 94D 磁極 |
| [414](./KH-VFGLF-LINE-LED-GROUND-414.md) | ライン LED / 421 |
| [407](./KH-ALL-KEIAIN-DOOR-WIRING-407.md) | 気配り U-CAN |
| [283](./KH-VFGLF-BRAKE-OVERCURRENT-932-283.md) | 932/941 過電流 |
| [235](./KH-VFGLF-EMERG-STOP-RAIL-235.md) | 非常止め |
| [据付・試験・調整ハブ](../practice-guides/KH-ALL-INSTALL-TEST-ADJUST-HUB.md) | **横断入口** |

## KB確認に基づく追記

（未実施 — `C-7-C3900-J-E.pdf` で mon1/0 2/6 シーケンス表示節を確認後追記。）

## 正式資料・元情報（参照元）

| 種別 | 識別子 | 補足 |
| --- | --- | --- |
| Lists | §392 |
| **OneNote** | `a8c15103-95f4-4d08-897a-403d412bffb5:156` | `onenote-1ce36975e184ab075d978bd7.md` |
| **KB** | Lists 通称 → **`C-7-C3900-J-E.pdf`** | C資料 / AXIEZ-LINKs |

編集用写し: `record_id` `case-elv-vfglf-brake-switch-stroke-id392`

## 未確認事項

- C-7-C3900 内のシーケンス表示手順（KB 本文）
- 438/614/932 の現行定義（KB）
