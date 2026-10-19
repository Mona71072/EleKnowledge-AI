---
schema_version: 1
record_id: "elv-vfgh-fire-service-relay-contact-automatic-operation-id102"
record_version: 1
title: "VFGH非常用エレベーターの消防リレー接触不良と自動運転不能報告（ID102）"
category: "不具合対応(ELV)"
record_type: "troubleshooting_case"
product: "エレベーター"
model_type:
  - "VFGH"
document_number: ""
revision: ""
effective_date: ""
review_status: "unreviewed"
publication_status: "not_published"
classification: "unknown"
cloud_approval: "not_reviewed"
keywords:
  - "非常用エレベーター"
  - "消防リレー"
  - "自動運転不能"
  - "手動運転"
  - "506"
  - "秤調整"
related_ids: []
source_path: ""
source_filename: "技術情報リスト（協力会社展開用）.xlsx"
onenote_id: ""
attachment_paths: []
reference_links: []
document_references:
  - document_number: ""
    title: "西支不具合リストの類似不具合（原リスト記載）"
    locator: "項目ID138と記載。リンク未閲覧、URLは保存していない。"
    source_path: ""
evidence_sources:
  - source_id: "evidence-list-case-id102"
    source_type: "user_provided_extract"
    title: "首都工・不具合情報共有リスト Excel出力 ID102"
    source_path: ""
    s3_uri: ""
    revision: "原本リスト未照合"
    accessed_at: "2026-10-09"
    supports:
      - "VFGH非常用エレベーターで秤調整中に自動運転できなかった症状、手動運転可能との記載、エラー表示、消防リレー接触不良との原因報告および対応後の動作報告"
structured_data:
  equipment: "VFGH 非常用エレベーター"
  symptom: "秤調整時に高速出しを試みたところ、自動運転できなかった。手動運転は可能だったとの報告。"
  error_codes:
    - "MON1/0=E/0: 302"
    - "MON1/0=E/0: 304"
    - "MON1/0=E/0: 306"
    - "MON1/0=E/0: 308"
    - "MON1/0=E/0: 506"
    - "MON1/0=1/0: 64E"
    - "MON1/0=1/0: 64F"
    - "MON1/0=1/0: A41"
    - "MON1/0=1/0: A51"
  cause: "原リストは、一次・二次消防リレーの監視接点エラーを受け、制御盤内リレーの接触不良を原因として記載する。原因・エラーとの因果は独立確認されていない。"
  verified_actions: []
  outcome: "原リストは、リレー接触への対応後に自動運転が可能になったと報告する。操作の具体内容、実施確認、再発有無は独立確認されていない。"
---

# VFGH非常用エレベーターの消防リレー接触不良と自動運転不能報告（ID102）

## 概要

首都工・不具合情報共有リストID102は、VFGH非常用エレベーターで秤調整時に高速出しを試みたところ自動運転できなかったと報告する。手動運転は可能だったとの記載がある。共有日は2022-04-11。

## エラー表示と原因報告

原リストの表示欄は、MON1/0=E/0で302、304、306、308、506、MON1/0=1/0で64E、64F、A41、A51を列挙する。調査経過では、506を一次・二次消防リレー監視用接点の故障として扱い、盤内リレーの接触不良を疑ったと記載する。原因は原文の判断であり、エラー表示との因果や機器の実状態は独立確認していない。

## 対応と結果

原リストは、盤内リレーの接触不良に対処した後、自動運転が可能になったと報告する。リレーの識別子・抜き差し等の具体的な操作、実施確認、再発有無は記録しない。対応後結果はリスト上の報告で、独立確認されていない。

## 関連参照

原リスト備考には西支不具合リストの類似不具合（項目ID138）への参照がある。参照先は未閲覧であり、内容・同一性・条件は確認していない。認証情報を含み得るURLは保存・転載しない。

## 出典・確認状態

- 出典: Excel出力のID102行にあるA列・E〜N列・O列。B/C/D列は参照していない。
- リレー個別識別子、抜き差しなどの操作、配線・端子・制御盤内部の確認手順は転載していない。
- 参照先ID138の本文、機種・現行適用、原因の独立確認、操作・復旧結果の再確認、安全レビューは未完了。
- 本記録は未レビューであり、消防運転・自動運転・電気作業の診断や操作手順を示すものではない。
