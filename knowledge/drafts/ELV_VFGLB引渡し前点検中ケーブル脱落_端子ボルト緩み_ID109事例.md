---
schema_version: 1
record_id: "elv-vfglb-cable-detachment-loose-terminal-id109"
record_version: 1
title: "VFGLB引渡し前点検中のケーブル脱落と端子ボルト緩み報告（ID109）"
category: "不具合対応(ELV)"
record_type: "troubleshooting_case"
product: "エレベーター"
model_type:
  - "VFGLB"
document_number: ""
revision: ""
effective_date: ""
review_status: "in_review"
publication_status: "not_published"
classification: "unknown"
cloud_approval: "not_reviewed"
keywords:
  - "VFGLB"
  - "引渡し前点検"
  - "端子ボルト緩み"
  - "ケーブル脱落"
  - "マーキング"
source_path: ""
source_filename: "技術情報リスト（協力会社展開用）.xlsx"
onenote_id: ""
related_ids: []
attachment_paths: []
reference_links: []
document_references: []
evidence_sources:
  - source_id: "evidence-list-case-id109"
    source_type: "user_provided_extract"
    title: "首都工・不具合情報共有リスト Excel出力 ID109"
    source_path: ""
    s3_uri: ""
    revision: "原本リスト未照合"
    accessed_at: "2026-10-09"
    supports:
      - "VFGLB引渡し前点検でケーブル1本が端子から外れた報告、端子ボルト緩みとの原因説明、復旧固定とマーキングを行ったとの記録、および原リスト備考の安全上の注意"
structured_data:
  equipment: "VFGLB エレベーター"
  symptom: "引渡し前点検中、電源を遮断していたとの報告がある状態で端子部の増し締め確認をしていたところ、接続されていた2本のケーブルのうち1本が端子から外れた。"
  error_codes: []
  cause: "原リストは端子部のボルト緩みを原因として記載する。緩みの発生時期・程度や原因の独立確認は未実施。"
  verified_actions: []
  outcome: "原リストは、外れたケーブルを固定し、マーキングしたと記録する。その後の導通・動作確認、引渡し可否、再発有無は記載されていない。"
---

# VFGLB引渡し前点検中のケーブル脱落と端子ボルト緩み報告（ID109）

## 発生状況

首都工・不具合情報共有リストID109は、VFGLBの引渡し前点検中に発生した作業上の事例を報告する。共有日は2022-06-15、重要度欄は「重要」、エラー表示は「未確認」。原リストは、電源を遮断していたとの記録がある状態で端子部の増し締め確認をしていたところ、接続ケーブル2本のうち1本が端子から外れたと記載する。端子・盤内の個別識別子や作業の再現手順は記録しない。

## 原因の記載と対応経過

原リストの原因欄は端子部のボルト緩みとしている。緩みの発生時期・程度や、ケーブルが外れた機序についての独立調査結果は記載されていない。

対応欄には、外れたケーブルを端子に固定し、その後マーキングを行ったと記録されている。これは原リストに実施済みとして記載された対応であり、独立確認済みの行為とは扱わない。

## 対応後の結果と注意

原リストには、対応後の導通・動作確認、引渡し可否、再発有無の記載がない。結果記載なしとして扱い、解決確認済みとはしない。

備考欄は、トランスリアクトルの増し締め確認時に制御盤電源を遮断すること、および引渡し前点検時に確認することを指示している。これは原リスト上の注意として記録するものであり、現行の承認済み手順・検査要件として確認したものではない。

## 出典・確認状態

- 出典: Excel出力のID109行にあるA列・E〜N列・O列。B/C/D列は参照していない。
- 電源遮断状態は発生時の原文記載として保持し、作業手順へ再構成していない。端子識別、締付け方法・値、配線操作、電気確認の具体手順は転載していない。
- 原本リスト、添付画像、原因の独立確認、対応後の試験・引渡し結果、現行性、技術・安全レビューは未確認。
- 本記録はレビュー中・未公開であり、増し締め、修理、検査、引渡しの手順や判定基準を示すものではない。
