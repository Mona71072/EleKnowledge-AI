---
schema_version: 1
record_id: "elv-meld-battery-polarity-m1-card-damage-id101"
record_version: 1
title: "MELDバッテリーの極性誤接続とM1カード損傷の報告（ID101）"
category: "不具合対応(ELV)"
record_type: "troubleshooting_case"
product: "エレベーター"
model_type: []
document_number: ""
revision: ""
effective_date: ""
review_status: "unreviewed"
publication_status: "not_published"
classification: "unknown"
cloud_approval: "not_reviewed"
keywords:
  - "MELDバッテリー"
  - "極性誤接続"
  - "M1カード"
  - "E84"
  - "PWD"
  - "停電移行"
related_ids:
  - "elv-cm-ma-no-load-run-m1-card-terminal-label-case"
  - "elv-axiez-links-boon-grounding-misconnection-id69"
source_path: ""
source_filename: "技術情報リスト（協力会社展開用）.xlsx"
onenote_id: ""
attachment_paths: []
reference_links: []
document_references:
  - document_number: "EA-11-F"
    title: "VFGR検査試験調整要領"
    locator: "ブレーキトルク確認（原リスト記載。本文未確認）"
    source_path: ""
  - document_number: "C-54-B203-54a"
    title: "原リスト記載の動的ブレーキトルク確認資料"
    locator: "原リスト記載。本文未確認"
    source_path: ""
  - document_number: "ASHA19108"
    title: "類似不発（原リスト記載）"
    locator: "参考資料欄"
    source_path: ""
evidence_sources:
  - source_id: "evidence-list-case-id101"
    source_type: "user_provided_extract"
    title: "首都工・不具合情報共有リスト Excel出力 ID101"
    source_path: ""
    s3_uri: ""
    revision: "原本リスト未照合"
    accessed_at: "2026-10-09"
    supports:
      - "全自動運転中の停電移行・一時復帰の症状、E84表示、MELDバッテリー極性誤接続によるM1カード損傷との原文説明、カード交換記載"
structured_data:
  equipment: "エレベーター"
  symptom: "全自動運転中に停電状態へ移行し、原文にある電源リセット後はいったん復帰するものの、再び停電状態へ移行するとの報告。エラー表示欄はE84（PWD、停電検出）。"
  error_codes:
    - "E84"
  cause: "原リストは、MELDバッテリーのプラス・マイナスを逆に接続したため、IPU基板内のM1カードにあるダイオードが損傷したと説明する。極性誤接続と損傷の因果は独立確認されていない。"
  verified_actions: []
  outcome: "原因・対応欄はM1カードを交換したと記録する。交換の独立確認、交換後の運転状態、再発有無は記載されていない。"
---

# MELDバッテリーの極性誤接続とM1カード損傷の報告（ID101）

## 概要

首都工・不具合情報共有リストID101は、全自動運転中に停電状態へ移行し、電源リセット後はいったん復帰するものの再発したと報告する。エラー表示はE84（PWD、停電検出）。共有日は2022-03-15。対象機種欄は空欄である。

## 原文の原因説明

原リストは、MELDバッテリーの極性を逆に接続したことにより、IPU基板内のM1カードのダイオードが損傷したと説明する。これは原文上の原因記載であり、現物・損傷部位・因果関係は独立確認されていない。

## 対応と結果

原因・対応欄にはM1カードを交換したとの記載がある。ただし、交換の独立確認、交換後の運転状態、再発有無は記載されていない。

進捗欄には複数の電気・制御・ブレーキ関連確認項目が列挙されているが、具体的な点検・測定・運転手順や確認点は転載しない。備考欄には動的ブレーキトルク確認の具体的な運転操作が含まれるため、手順・順序・設定・運転状態は一切転記していない。参照資料の本文も未確認である。

## 関連資料

- [[ELV_CM-MA空回し不能_M1カード損傷事例]]: ID53もM1カード損傷を報告するが、CM-MAでの空回し時の事例であり、端子表示誤貼付との原因報告。機種・発生状況・原因・経過が異なる別報告で、本件の裏付けではない。
- [[ELV_AXIEZ-LINKS_BOON線誤結線_絶縁不良_ID69事例]]: ID69/83はMELDバッテリー負極線を接地線と誤認したとの絶縁不良報告。ID101の極性逆接続によるM1カード損傷とは原因説明・症状・結果が異なる別事例で、相互の根拠ではない。
- [[不具合対応【ELV】/索引]]: ELV整備資料の索引。

## 出典・確認状態

- 出典: Excel出力のID101行にあるA列・E〜N列・O列。B/C/D列は参照していない。
- 逆極性の電気接続、端子・配線、電源リセット、診断・測定、動的ブレーキトルク試験の具体手順は転記していない。
- 損傷箇所、原因の独立確認、カード交換の実施確認、交換後の運転・再発、対象機種、参照資料本文、現行性、安全レビューは未確認。
- 本記録は未レビューであり、停電・非常運転・ブレーキ試験・電気作業・復旧の手順や判断根拠を示すものではない。
