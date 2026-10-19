---
knowledge_id: KH-KE-WF-CABIN-CAMERA-FLICKER-134
kind: case_summary
status: draft
card_version: 1
title: "かご内カメラ映像 — 照度によるフリッカー"
symptoms:
  - "フリッカー"
  - "かご内カメラ"
  - "かご室照明"
  - "シャッター"
  - "映像モニタ"
model_scope:
  lists_model_label:
    - "KE-WF"
  product_lines:
    - "AXIEZ"
  model_abbreviations:
    - "KE-WF"
  machine_room:
    - "MRL"
  observed_on: []
  may_apply_to:
    - "かご室蛍光灯等とカメラ自動シャッタの組合せ"
  excludes: []
source_refs:
  - ref_type: lists_item
    list_item_id: "134"
  - ref_type: onenote_page
    onenote_id: "a75aa8fd-a447-4b0a-a6f3-29b3e023c803:1"
  - ref_type: kb_document
    document_number: "C-6-S490.1"
    kb_verify_status: pending
---

# かご内カメラ映像 — 照度によるフリッカー

## 使う場面・対象条件

**KE-WF**（Lists Model）で **かご内モニタ映像が不定期にフリッカー** する（Lists 134）。**145**（コンポジット/NTSC）と **信号方式** を混同しない。

## 症状・現象

- かご内モニタで **不定期フリッカー**（Lists）。
- カメラ付近に手をかざし **かご室照明を遮ると一時解消**、再発（Lists）。

## ソース要約

### Lists（134）

- **原因（Lists）**: かご室照明下でカメラ **自動シャッタ** が照明 **点滅より速い** → 消灯タイミングを撮影してフリッカー。
- **対応**: **フリッカー補正ケーブル** に交換 → シャッタ速度固定で解消（Lists 添付②③）。
- **progress**: **C-6-S490.1-J** トラブルシュート確認 → 製品側問題 → 先行不発・代品手配（Lists）。

### OneNote（a75aa8fd…:1）

- 技術情報リスト **索引页** — 本件タイトルへのリンク一覧。**C-6-S490.1-J**・CMH112 資料リンク（スナップショット）。詳細手順は KB 未レビュー。

## 統合した回答・ノウハウ

**照明×自動シャッタ** が疑われるときは **フリッカー補正ケーブル**（Lists 対応）。手順の正本は **C-6-S490.1**（`kb_verify_status: pending` — 断定は KB 確認後）。

## 調査・確認手順

1. フリッカーが **照明遮断で変化** するか（Lists 再現）。
2. **C-6-S490.1** トラブルシュート（KB 確認待ち）。
3. フリッカー補正ケーブル適用可否（Lists 添付）。
4. 145 と同様 **NTSC/モニタ方式** も併せ確認。

## 関連事例と条件の違い

| list | 内容 |
| --- | --- |
| **134** | **照度フリッカー**（KE-WF） |
| **145** | コンポジット/NTSC |

## KB確認に基づく追記

（C-6-S490.1 未レビュー — Lists progress のみ）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | §134 |
| OneNote | `a75aa8fd-a447-4b0a-a6f3-29b3e023c803:1`（索引） |
| KB | C-6-S490.1（pending） |

## 未確認事項

- KE-WF 以外機種への同型カメラ適用。
