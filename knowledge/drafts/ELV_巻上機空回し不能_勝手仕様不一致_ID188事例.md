---
schema_version: 1
record_id: "case-elv-hoist-free-run-direction-spec-mismatch-id188"
record_version: 1
title: "巻上機の仕様方向不一致による空回し不能事例（ID188）"
category: "不具合対応(ELV)"
record_type: "troubleshooting_case"
product: "エレベーター"
model_type: ["全エレ機種（一次リスト欄の表記。適用範囲未確認）"]
document_number: ""
revision: ""
effective_date: ""
review_status: "in_review"
publication_status: "not_published"
classification: "unknown"
cloud_approval: "not_reviewed"
keywords:
  - "巻上機"
  - "空回し"
  - "仕様不一致"
  - "ソフトウェア"
source_path: "首都工・不具合情報共有リスト.xlsx"
source_filename: "首都工・不具合情報共有リスト.xlsx"
onenote_id: ""
related_ids: []
attachment_paths: []
reference_links: []
document_references: []
evidence_sources:
  - source_id: "evidence-list-elv-hoist-direction-spec-mismatch-188"
    source_type: "vault_original"
    title: "首都工・不具合情報共有リスト: 巻上機の勝手方向の違いで、空回しができない件（ID188）"
    source_path: "首都工・不具合情報共有リスト.xlsx"
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-14"
    supports:
      - "巻上機の空回し運転不能と、ハードウェアとソフトウェアの方向仕様不一致との原因説明"
      - "対応済み欄に対し具体的な是正内容と是正後動作確認が記載されていないこと"
structured_data:
  equipment: "巻上機"
  symptom: "巻上機の空回し運転ができなかったとの報告。指令と動作の方向別詳細は記録しない。"
  error_codes: []
  cause: "一次リストは、仕様決定時の巻上機方向とソフトウェア作成時の方向仕様が、巻上機ハードウェアの仕様と一致していなかったと説明する。機器型式や方向の具体値は記録しない。"
  verified_actions: []
  outcome: "対応状況欄は対応済み。原リストには制御盤からの配線確認で問題がなかったとの記載と、ソフトウェア確認で方向仕様の不一致が判明したとの記載があるが、是正内容および是正後の動作確認は記載されていない。"
---

# 巻上機の仕様方向不一致による空回し不能事例（ID188）

## 事例の概要

首都工・不具合情報共有リストID188は、巻上機の空回し運転ができなかった事例を報告する。一次リストは、巻上機ハードウェアの仕様と、仕様決定およびソフトウェア作成時の方向仕様との不一致を原因として説明している。

原リストには配線確認で異常がなかったとの記載があるが、具体的なピン配置、配線、運転指令、方向別の動作は再現可能な情報となるため転載しない。原因の独立確認も行っていない。

## 対応状況と未確認事項

対応状況欄は完了扱いだが、ソフトウェアの是正内容、実施状況、是正後の動作確認は記載されていない。設備の復旧状態、原因の独立検証、リスト欄にある広い機種適用、現行の設計・ソフトウェア管理要件は未確認。

本記録は事例の検索・確認用であり、空回し運転、回転方向確認、配線・設定変更、復旧判断の手順ではない。

## 出典

- 首都工・不具合情報共有リスト.xlsx、ID188（sheet1 row236）。
- 設備・現場・担当者、巻上機型式、具体的な方向、ピン/配線、運転操作は転載していない。