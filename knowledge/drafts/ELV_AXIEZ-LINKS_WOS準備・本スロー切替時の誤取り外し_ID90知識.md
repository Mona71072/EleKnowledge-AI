---
schema_version: 1
record_id: "elv-axiez-links-wos-transition-removal-confusion-id90"
record_version: 1
title: "AXIEZ-LINKS WOS準備・本スロー切替時の誤取り外し報告（ID90）"
category: "不具合対応(ELV)"
record_type: "knowhow"
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
  - "WOS"
  - "本スロー"
  - "誤取り外し"
  - "走行不能"
related_ids:
  - "elv-normal-slow-issues"
  - "elv-axiez-links-car-top-up-restriction-id87"
source_path: ""
source_filename: "技術情報リスト（協力会社展開用）.xlsx"
onenote_id: ""
attachment_paths: []
reference_links: []
document_references:
  - document_number: ""
    title: "原リストが参照するPowerPoint資料（題名・本文・版未確認）"
    locator: ""
    source_path: ""
evidence_sources:
  - source_id: "evidence-list-knowhow-id90"
    source_type: "user_provided_extract"
    title: "首都工・不具合情報共有リスト Excel出力 ID90"
    source_path: ""
    s3_uri: ""
    revision: "原本リスト・参照PowerPoint未照合"
    accessed_at: "2026-10-09"
    supports:
      - "WOS準備および本スロー切替時に発生した二つの誤取り外し事例の条件・症状・原文上の原因説明"
structured_data:
  knowledge_items:
    - topic: "WOS準備中に工場装着状態を誤って変更した事例"
      statement: "原リストは、煙感知器点検口がない条件でのWOS準備中、同梱品を使う過程で工場出荷時に装着されていた別の部品を誤って取り外し廃棄し、その後に走行できなくなった事例を記録する。詳細な部品識別・取り外し方法は記録しない。"
      conditions:
        - "AXIEZ-LINKS。"
        - "原リスト記載の条件は煙感知器点検口がない場合。"
      exceptions: []
      rationale: "原リストは、工場装着状態の部品を誤って取り外したことを走行不能の原因としている。因果関係・復旧状況は独立確認されていない。"
      verification_status: "source_recorded"
      evidence_source_ids:
        - "evidence-list-knowhow-id90"
    - topic: "WOSから本スローへの切替時に誤取り外しが生じた事例"
      statement: "原リストは、WOSから本スローへ切り替える際、切替用の同梱品とともに工場出荷時の別部品まで取り外した事例を記録する。その結果、着床プレート検出時にかご上UP運転が制限されたと説明する。ID87にも着床プレート検出後のUP運転制限があるが、ID87は未装着の発見までを記録し、取り外し経緯や復旧結果は確認されていないため、別報告として扱う。"
      conditions:
        - "AXIEZ-LINKS。"
        - "原リスト記載の条件はWOSから本スローへの切替時。"
      exceptions:
        - "具体的な部品識別、配線・端子、取り外し対象や手順は転記しない。"
      rationale: "原リストは切替時の不要な取り外しを原因として挙げる。因果関係・復旧状況は独立確認されていない。"
      verification_status: "source_recorded"
      evidence_source_ids:
        - "evidence-list-knowhow-id90"
  source_notes:
    - "共有日は2022-01-31。進捗欄、エラー表示、是正実施、復旧結果の記載なし。"
    - "同じリスト行に二つの異なる発生状況が記されているため、症状と条件を分けて保持した。"
    - "原リストが参照するPowerPointは未閲覧。題名、版、閲覧権限、内容は未確認。"
    - "安全上、部品識別、電気的機能、配線、端子、取り外し・切替の具体手順は転載していない。"
---

# AXIEZ-LINKS WOS準備・本スロー切替時の誤取り外し報告（ID90）

## 概要

首都工・不具合情報共有リストID90は、AXIEZ-LINKSでWOS関連の準備およびWOSから本スローへの切替時に起きた、二つの異なる誤取り外し事例をまとめている。共有日は2022-01-31。部品の識別・取り外し方法を示さず、原リスト上の条件、症状、原因説明を区別して記録する。

## 事例A: WOS準備時の走行不能報告

原リストは、煙感知器点検口がない条件で、同梱品を使用する過程において工場出荷時に装着されていた別の部品を誤って取り外し廃棄し、その後に走行できなくなった事例を記録する。原因は原リスト上の説明であり、因果関係、是正内容、復旧結果は確認されていない。

## 事例B: WOSから本スローへの切替時のUP運転制限

原リストは、WOSから本スローへ切り替える際、切替用の同梱品とともに工場出荷時の別部品まで取り外し、着床プレート検出時にかご上UP運転が制限された事例を記録する。これも原リスト上の原因説明であり、是正内容と復旧結果は記載されていない。

同じ症状の一部はID87にも記録されているが、ID87は未装着の発見までを記し、取り外し経緯は特定していない。ID90の事例Bは原因説明が異なるため、同一案件・同一原因とは扱わない。

## 注意事項・未確認事項

原リストの具体的な部品識別、接続先、電気的機能、取り外し対象および切替手順は転記していない。個別の現場で適用可能な判断や作業指示として利用しないこと。

原リストが参照するPowerPointの本文、版、閲覧権限、現行性は未確認。進捗欄、エラー表示、是正実施、復旧結果も記載されていない。

## 関連資料

- [[ELV_本スロー不具合一覧]]: 本スロー関連の報告一覧。ID90の二つの発生状況を区別して追記。
- [[ELV_AXIEZ-LINKSかご上UP運転制限_本スロー後コネクタ未装着_ID87事例]]: 着床プレート検出後のUP運転制限という症状は共通するが、ID87は未装着を発見した経過、ID90はWOSからの切替時に取り外したとの別の原因説明。

## 出典・確認状態

- 出典: Excel出力のID90行にあるA列・E〜N列・O列。B/C/D列は参照していない。
- 原本リストと参照PowerPointは未照合。原因の独立確認、是正・復旧、対象設備への適用、現行性、専門レビューは未了。
- 本記録は未レビューであり、運転・切替・電気作業手順ではない。
