---
schema_version: 1
record_id: "catalog-elv-sets-failure-reference"
record_version: 2
title: "SETS関連不具合資料の参照記録"
category: "技術メモ【ELV】２"
record_type: "catalog"
product: "エレベーター"
model_type: []
document_number: ""
revision: ""
effective_date: ""
review_status: "in_review"
publication_status: "not_published"
classification: "unknown"
cloud_approval: "not_reviewed"
keywords: ["SETS", "エラー", "不具合"]
source_path: "技術メモ【ELV】２/ELV-付加仕様（その他）/SETS.md"
source_filename: "SETS.md"
onenote_id: "c9137220-f164-40f9-9fd1-1218289d3110:1"
related_ids:
  - "case-elv-mrl-sets-position-write-direction-spec-id187"
  - "elv-sets-position-reference-signal-open-circuit-id358"
attachment_paths: []
reference_links: []
document_references: []
evidence_sources:
  - source_id: "evidence-elv-sets-001"
    source_type: "vault_original"
    title: "SETS"
    source_path: "技術メモ【ELV】２/ELV-付加仕様（その他）/SETS.md"
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-08"
    supports: ["SETS未実施期間とエラー記録、制御盤確認事例へのリンクがあること"]
  - source_id: "evidence-list-elv-mrl-sets-position-write-187"
    source_type: "vault_original"
    title: "首都工・不具合情報共有リスト: SETS基準位置書き込みが完了しない件（ID187）"
    source_path: "首都工・不具合情報共有リスト.xlsx"
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-14"
    supports:
      - "MRLのSETS基準位置書込み不完了と方向仕様不一致との原因説明"
      - "変換部品の適用後に動作良好となったとの報告"
structured_data:
  source_notes:
    - "個別エラー/対応内容の本文や根拠資料は未閲覧。判断条件を推測していない。"
    - "一次リストID187を方向仕様不一致による基準位置書込み不完了事例として個別記録へ接続。エラー/位置値・具体方向・部品識別/取付方法は転載していない。ID358の信号断線事例とは原因報告が異なる。"
---

# SETS関連不具合資料の参照記録

原資料はSETS未実施期間とエラー記録、制御盤確認事例の情報共有先を参照する。詳細な事例本文、現行運用、故障対応手順は未確認。

一次リストID187のMRL事例は[[ELV_MRL_SETS基準位置書込み不完了_方向仕様不一致_ID187事例]]に記録した。ガバナエンコーダーの方向仕様不一致との説明と変換部品適用後の改善報告は出典記載として区別し、具体的なコード、位置値、方向、部品/接続情報は転載していない。ID358の位置基準信号断線とは原因説明が異なる。

リンク先と現行の保守要領を確認するまで、エラー診断や処置判断に使用しない。

出典: `技術メモ【ELV】２/ELV-付加仕様（その他）/SETS.md`（OneNote ID `c9137220-f164-40f9-9fd1-1218289d3110:1`）。確認日: 2026-10-08。
