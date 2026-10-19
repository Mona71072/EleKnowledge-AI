---
schema_version: 1
record_id: "elv-contiguous-data-reference"
record_version: 1
title: "連続データ取得領域の参照記録"
category: "不具合対応(ELV)"
record_type: "technical_reference"
product: "エレベーター"
model_type:
  - "VFGLB"
  - "VFGLF"
  - "VFGH"
document_number: ""
revision: ""
effective_date: ""
review_status: "in_review"
publication_status: "not_published"
classification: "unknown"
cloud_approval: "not_reviewed"
keywords:
  - "連続データ"
  - "メモリアドレス"
  - "VFGLB"
  - "VFGLF"
  - "VFGH"
source_path: "不具合対応【ELV】/メンテコン/各連続データ.md"
source_filename: "各連続データ.md"
onenote_id: "a8c15103-95f4-4d08-897a-403d412bffb5:102"
related_ids:
  - "elv-digital-recorder-reference"
  - "elv-trace-data-reference"
attachment_paths: []
reference_links: []
document_references: []
evidence_sources:
  - source_id: "evidence-elv-contiguous-data"
    source_type: "vault_original"
    title: "各連続データ（原文）"
    source_path: "不具合対応【ELV】/メンテコン/各連続データ.md"
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-01"
    supports:
      - "機種群ごとに異なるデータ領域についての原文記載"
structured_data:
  source_notes:
    - "原文はVFGLB/VFGLFとVFGHで制御・管理領域が異なると記載。VFGHの制御領域は一度で採取できないとの注記あり。"
    - "原文は添付画像2点を参照する。過去の内容確認記録では旧・改訂画面の差が記録されているが、2026-10-07時点でVault内に画像実体がなく、今回の会話にも画像共有がないため再検証できない。"
    - "原文と図版にある具体的アドレス、取得量、画面操作は誤操作防止のため本記録へ転載しない。"
---

# 連続データ取得領域の参照記録

原文は、メモリアドレス領域のデータ採取について、VFGLB/VFGLFとVFGHで制御・管理領域が異なること、VFGHの制御領域は一度で採取できないことを記載している。

## 図版から確認できる差異

過去の内容確認記録では、旧図版はセグメント／オフセット、新しい図版は開始アドレス／データ長による指定で、取得量の記載も異なるとされている。ただし、2026-10-07時点で画像実体を確認できず、現物と再照合できない。画面や上限を現行仕様として扱わない。

具体的なアドレス値、取得量、機種選択、採取操作は本ページに転載していない。対象機の制御方式、ソフトウェア版、調査指示と承認済み手順を照合すること。

## 出典

- 原文ノート: [[不具合対応【ELV】/メンテコン/各連続データ]]
- 原文は画像2点を参照するが、2026-10-07時点でVault内に実ファイルを確認できず、今回の会話にも画像共有がないため内容を再確認できない。具体的な取得手順・数値は転載していない。