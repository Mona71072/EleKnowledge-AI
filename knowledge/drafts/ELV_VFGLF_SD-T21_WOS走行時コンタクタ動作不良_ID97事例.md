---
schema_version: 1
record_id: "elv-vfglf-sd-t21-wos-contactor-operation-failure-id97"
record_version: 1
title: "VFGLFのWOS運転時にSD-T21コンタクタ動作不良で走行できない報告（ID97）"
category: "不具合対応(ELV)"
record_type: "troubleshooting_case"
product: "エレベーター"
model_type:
  - "VFGLF"
document_number: ""
revision: ""
effective_date: ""
review_status: "unreviewed"
publication_status: "not_published"
classification: "unknown"
cloud_approval: "not_reviewed"
keywords:
  - "SD-T21"
  - "WOS運転"
  - "コンタクタ動作不良"
  - "#5"
  - "M5"
  - "432"
  - "452"
related_ids:
  - "elv-vfglf-sd-t21-contactor-not-picking-up-id96"
source_path: ""
source_filename: "技術情報リスト（協力会社展開用）.xlsx"
onenote_id: ""
attachment_paths: []
reference_links: []
document_references:
  - document_number: "ASHO29423"
    title: "原リスト記載の参考資料"
    locator: ""
    source_path: ""
evidence_sources:
  - source_id: "evidence-list-case-id97"
    source_type: "user_provided_extract"
    title: "首都工・不具合情報共有リスト Excel出力 ID97"
    source_path: ""
    s3_uri: ""
    revision: "原本リスト未照合"
    accessed_at: "2026-10-09"
    supports:
      - "VFGLFのWOS運転時症状、表示コードの記載と不記載、原文の調査状況、対応報告と結果"
structured_data:
  equipment: "VFGLF エレベーター"
  symptom: "WOS運転時にUP/DN操作で走行できず、まれに走行できても操作から走行までが通常より遅いとの報告。SD-T21の#5コンタクタ可動部が動こうとするが、十分に動かない状態も記載されている。エラー表示欄に複数コードが記載される一方、432および452は本事象で確認されなかったと記録される。"
  error_codes:
    - "855"
    - "856"
    - "95D"
    - "A48"
    - "43A"
    - "614"
    - "631"
    - "64C"
    - "64E"
    - "64F"
    - "66D"
    - "66F"
    - "845"
    - "E2F"
    - "E32"
    - "E34"
    - "E35"
    - "E36"
    - "E39"
    - "E3F"
    - "E42"
    - "E44"
    - "E45"
    - "E46"
    - "E49"
    - "E4F"
    - "437"
  cause: "原因欄は「#5コンタクタ不良？」と疑問形で記載され、確定原因は示されていない。"
  verified_actions: []
  outcome: "進捗欄では、原文に記載された電気的確認では問題が示されず、#5とM5を入れ替えたところ動作良好になったと報告する。不発返却品は製造元で確認中。確認・入替の詳細は転載せず、行為・結果はリスト上の報告で独立確認していない。"
---

# VFGLFのWOS運転時にSD-T21コンタクタ動作不良で走行できない報告（ID97）

## 概要

首都工・不具合情報共有リストID97は、VFGLFのWOS運転時にUP/DN操作で走行できないことがあり、まれに走行できても操作から走行まで通常より時間がかかると報告する。SD-T21の#5コンタクタ可動部が動こうとするが十分に動かない状態も記載されている。共有日は2022-02-16。

原リストには多数の表示コードが列挙される一方、432と452は本事象で確認されなかったと明記されている。表示コード一覧の意味や症状との因果関係は確認されていない。

## 調査・原因の記載

進捗欄では、原文記載の電気的確認では問題が示されず、#5とM5を入れ替えたところ動作良好になったと報告する。原因欄は「#5コンタクタ不良？」と疑問形であり、確定原因とは扱わない。不発返却品は製造元で確認中と記載されている。

測定値、端子・測定点、電気確認方法、コンタクタの入替手順は記録しない。動作良好との記載はリスト上の結果で、独立確認されたものではない。

## ID96との関係

ID96もVFGLFのSD-T21・#5コンタクタ不吸引とM5入替案を扱うため、同系統の関連報告として参照する。ID96は返却品で再現し調査中、一時対応の提案段階であるのに対し、ID97は入替後に動作良好との記載がある。同一現場・同一機器・同一返却品の続報かは確認できないため、別記録として保持する。ID96には入替後にMELD運転が使えなくなるとの注意もあるが、これはID96の記載であり、ID97の結果・適用を裏付けない。

## 参照資料

原リストの参考資料欄にASHO29423が記載されている。資料本文、版、適用範囲は未確認。

## 出典・確認状態

- 出典: Excel出力のID97行にあるA列・E〜N列・O列。B/C/D列は参照していない。
- 測定値、端子・測定点、測定手順およびコンタクタ入替の具体的な電気作業は転載していない。
- 同一案件か、原因、調査完了、製造元の確認結果、対応後の継続状態、表示コードの意味、参考資料ASHO29423の内容と現行性は未確認。専門レビューも未実施。
- 本記録は未レビューであり、電気測定、部品交換、運転・復旧手順を示すものではない。
