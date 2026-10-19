---
schema_version: 1
record_id: "elv-axiez-links-car-top-up-restriction-id87"
record_version: 1
title: "AXIEZ-LINKS 本スロー後のかご上UP運転制限とコネクタ未装着報告（ID87）"
category: "不具合対応(ELV)"
record_type: "troubleshooting_case"
product: "エレベーター"
model_type:
  - "AXIEZ-LINKS"
document_number: ""
revision: ""
effective_date: ""
review_status: "unreviewed"
publication_status: "not_published"
classification: "unknown"
cloud_approval: "not_reviewed"
keywords:
  - "本スロー"
  - "かご上UP運転"
  - "着床プレート"
  - "終点検出"
related_ids:
  - "elv-normal-slow-issues"
source_path: ""
source_filename: "技術情報リスト（協力会社展開用）.xlsx"
onenote_id: ""
attachment_paths: []
reference_links: []
document_references: []
evidence_sources:
  - source_id: "evidence-list-case-id87"
    source_type: "user_provided_extract"
    title: "首都工・不具合情報共有リスト Excel出力 ID87"
    source_path: ""
    s3_uri: ""
    revision: "原文行の記載。原本リスト・添付は未照合。"
    accessed_at: "2026-10-09"
    supports:
      - "共有日、機種、症状、調査経過、原因説明、エラー表示、対応後結果の記載有無"
structured_data:
  equipment: "AXIEZ-LINKS"
  symptom: "本スロー出し後、着床装置を取り付けた状態で、かご上UP運転中に着床プレートを検出すると停止し、その後かご上からUP運転できなくなったとの報告。"
  error_codes:
    - "845"
    - "847"
    - "854"
    - "856"
    - "85E"
    - "95D"
    - "A43"
    - "E32"
    - "E39"
    - "E42"
    - "E49"
    - "64E"
    - "64F"
  cause: "原リストは、出荷時装着とされる部品の未装着により終点検出状態が想定と異なり、着床プレート検出時に制御が異常状態と判定してかご上UP運転を制限したと説明する。これは原リスト上の原因説明であり、独立確認していない。"
  verified_actions: []
  outcome: "コネクタ未装着の発見までの経過は記載されているが、装着等の対応実施、対応後の運転確認および最終結果は記載なし。"
---

# AXIEZ-LINKS 本スロー後のかご上UP運転制限とコネクタ未装着報告（ID87）

## 概要

首都工・不具合情報共有リストID87は、AXIEZ-LINKSで本スロー出し後に着床装置を取り付けた状態において、着床プレート検出を契機にかご上UP運転が制限された事例を報告する。原文上の原因説明は、出荷時装着とされる部品の未装着により終点検出状態が想定と異なったというもの。原因と因果関係は独立確認されていない。

## 発生条件と症状

- 原文の共有日は2022-01-20。
- 本スロー出し後、着床装置を取り付けた状態で、かご上UP運転中に着床プレートを検出すると停止し、その後UP運転できなくなったとの記載。
- エラー表示欄には845、847、854、856、85E、95D、A43、E32、E39、E42、E49、64E、64Fが列挙されている。各コードの意味、発生順序、診断上の意味は未確認。

## 調査の経過と原因説明

現場ではR1基板の不良を疑い、別現場の基板を流用する案が出たが、調査中に部品の未装着に気づいた、とリストは記録する。リストは、この未装着が終点検出状態に影響し、着床プレート検出時の制御判定とUP運転制限につながったと説明している。信号経路や部品の具体的位置・識別情報は、作業への転用を避けるため記載しない。

この原因説明はリスト記載の主張であり、実機・図面・正式資料による独立確認はしていない。エラーコードの定義、対象ソフトウェア版、機種適用範囲も未確認である。

## 対応・結果

未装着の発見後に行った是正内容、実施者による確認、かご上UP運転の再確認結果は記載されていない。したがって、対応済み・復旧済みとは判断できない。

## 関連資料

- [[ELV_本スロー不具合一覧]]: 本スロー関連報告を検索する一覧。本件はID7・27等と分類上は近いが、条件と原因説明が異なる別報告。
- [[不具合対応【ELV】/現象（不具合対応）/仮スロー・本スロー・自動運転/本スロー（不具合）]]: 原資料分類索引。認証付きURLや原文のアクセス情報は転載していない。

## 出典・確認状態

- 出典: Excel出力のID87行にあるA列・E〜N列・O列。B/C/D列は参照していない。
- 原本Excel行の内容と添付は未照合。原因、コード定義、復旧結果、現行性、他設備への適用は未確認。
- 部品/端子の識別、信号経路の詳細、運転・確認・復旧手順、現場名・個人情報は転記していない。
- 本記録は未レビューであり、現行の診断・運転・作業手順を示すものではない。
