---
schema_version: 1
record_id: "elv-vfglb-jre-load-test-display-constraint-id89"
record_version: 1
title: "VFGLB JRE仕様における負荷試験時の表示制約（ID89）"
category: "不具合対応(ELV)"
record_type: "knowhow"
product: "エレベーター"
model_type:
  - "VFGLB"
document_number: ""
revision: ""
effective_date: ""
review_status: "unreviewed"
publication_status: "not_published"
classification: "unknown"
cloud_approval: "not_reviewed"
keywords:
  - "JRE仕様"
  - "負荷試験"
  - "位置表示"
  - "速度表示"
source_path: ""
source_filename: "技術情報リスト（協力会社展開用）.xlsx"
onenote_id: ""
related_ids: []
attachment_paths: []
reference_links: []
document_references:
  - document_number: "C-7-C3300.1"
    title: "原文が参照するVFGLB資料（正式表題・版未確認）"
    locator: "P.34、P.37"
    source_path: ""
evidence_sources:
  - source_id: "evidence-list-knowhow-id89"
    source_type: "user_provided_extract"
    title: "首都工・不具合情報共有リスト Excel出力 ID89"
    source_path: ""
    s3_uri: ""
    revision: "原本リスト・参照資料本文未照合"
    accessed_at: "2026-10-09"
    supports:
      - "JRE仕様時に通常の負荷試験方式が使えない条件と、位置/速度表示に関する記載"
structured_data:
  knowledge_items:
    - topic: "JRE仕様時の負荷試験における表示取得上の制約"
      statement: "リストID89は、JRE仕様ではかご内点検スイッチが入った状態で自動運転できず、通常の負荷試験方式を実施できないと記載する。また、位置情報と速度情報は同時表示できず、別々に取得する必要があるとしている。これは原リスト記載の条件・説明であり、承認済みの試験方法や実施結果を示すものではない。"
      conditions:
        - "原リスト上の対象機種はVFGLB。"
        - "JRE仕様における負荷試験の記載。"
      exceptions:
        - "具体的なコマンド、運転方向、反復回数、スイッチ操作は転記しない。"
      rationale: "原文は通常方式が使えない条件と、位置・速度表示を別々に取得する理由を説明している。"
      verification_status: "source_recorded"
      evidence_source_ids:
        - "evidence-list-knowhow-id89"
  source_notes:
    - "リストに実施状況・試験結果の記載なし。"
    - "C-7-C3300.1のP.34、P.37が参照されているが、資料本文・改訂・対象条件は未確認。"
    - "リストの具体的な操作記述は安全な作業手順に転用できる形で転載していない。"
---

# VFGLB JRE仕様における負荷試験時の表示制約（ID89）

## 概要

首都工・不具合情報共有リストID89は、VFGLBのJRE仕様における負荷試験時の制約を記録する。共有日は2022-01-21。原リストによると、かご内点検スイッチが入った状態では自動運転できず、通常の負荷試験方式が使えない。また、位置情報と速度情報を同時表示できないため、別々に取得する必要があると説明している。

## 条件と原文記載

| 項目 | 原リストの記載 | 確認状態 |
| --- | --- | --- |
| 対象 | VFGLB、JRE仕様 | 原リスト記載。個別設備への適用は未確認 |
| 制約 | かご内点検スイッチが入った状態では自動運転できず、通常方式の負荷試験を実施できない | 原リスト記載。現行仕様は未確認 |
| 表示 | 位置情報と速度情報は同時表示できず、別々に取得する必要がある | 原リスト記載。表示条件・現行性は未確認 |
| 実施状況・結果 | 記載なし | 未確認 |

## 安全・適用上の注意

原リストは具体的なリモコン入力と走行を伴う操作を記載しているが、本記録にはコマンド、運転方向、反復回数、スイッチ操作を転記していない。これは負荷試験の実施手順や許可を示すものではない。実施要否・方法は、対象設備に適用される承認済みの最新版資料と有資格担当者の確認が必要である。

## 参照資料

- 原リストが挙げる資料番号はC-7-C3300.1、参照位置はP.34およびP.37。本文・正式表題・版・適用性は未確認。

## 出典・確認状態

- 出典: Excel出力のID89行にあるA列・E〜N列・O列。B/C/D列は参照していない。
- 添付は提供・閲覧されていない。設備条件、原文の操作記載の妥当性、試験結果、現行性、専門レビューは未確認。
- 本記録は未レビューであり、試験方法・安全判断の根拠として使用しない。
