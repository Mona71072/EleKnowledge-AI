---
schema_version: 1
record_id: "case-elv-vfglf-brake-switch-stroke-id392"
list_item_id: "392"
record_version: 1
title: "VFGLF 本スロー時ブレーキSW設定不良による運転不能"
category: "不具合対応(ELV)"
record_type: "troubleshooting_case"
product: "エレベーター"
model_type:
  - "VFGLF"
document_number: ""
revision: ""
effective_date: ""
review_status: "in_review"
publication_status: "not_published"
classification: "unknown"
cloud_approval: "not_reviewed"
keywords:
  - "本スロー"
  - "ブレーキスイッチ"
  - "BK1"
  - "438"
  - "614"
  - "932"
related_ids: []
source_path: ""
source_filename: ""
onenote_id: ""
attachment_paths: []
reference_links: []
document_references: []
evidence_sources:
  - source_id: "evidence-list-vfglf-brake-switch-id392"
    source_type: "lists_csv_snapshot"
    title: "首都工・不具合情報共有リスト: ブレーキスイッチ設定不良で本スロー時カゴ運転不能の件"
    source_path: ""
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-19"
    supports:
      - "WOS→本スロー後上部終点SW調整後にスロー不能、438/614/932、BK1解放信号なし、スイッチストローク調整で解消"
structured_data:
  equipment: "VFGLF"
  symptom: "本スロー運転不能、ブレーキ解放後すぐ閉じる、稀に走行後緩停止しB・K・↓表示、などリスト記載。"
  error_codes:
    - "438"
    - "614"
    - "932"
  cause: "P1基板でBK1解放信号がなく、スキミゲージでBK1未動作、ストローク調整ボルト再調整で解消、とリスト。"
  verified_actions:
    - "リスト記載の調査手順（UP/DN取込、終点SW、磁極学習、レゾルバ電圧、BK/BC電圧導通、シーケンス表示でBK1確認）"
  outcome: "リスト上は対応済み。"
---

# VFGLF 本スロー時ブレーキSW設定不良による運転不能

共有リスト上の記録 は、WOS から本スロー切替後、上部終点 SW 調整後にスロー運転不能となり、エラー 438・614・932 が出る事例を報告する。

## リスト上の調査の流れ（報告ベース）

1. P1 基板で UP/DN 信号取込確認
2. 終点 SW 挟み込み確認（問題なし、とリスト）
3. 磁極学習・レゾルバ電圧等（リスト進捗記載）
4. ブレーキ BK/BC の電圧・導通
5. mon1/0 2/6 シーケンス表示で **BK1 解放信号なし** を確認
6. スキミゲージで BK1 未動作 → **ストローク調整ボルト再調整** で解消

参照資料名としてリストは「VFGLF据付調整資料抜粋_シーケンス表示」を挙げる。本文・版は未確認。

## 未確認事項

- エラーコード 438/614/932 の現行定義
- 調整手順の正式資料該当頁
- 上部終点 SW 調整と BK1 未動作の因果（リスト説明の独立確認なし）

本記録は事例索引であり、復旧手順の正本ではない。
