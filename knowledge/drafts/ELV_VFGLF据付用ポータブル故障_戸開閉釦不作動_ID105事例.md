---
schema_version: 1
record_id: "elv-vfglf-installation-portable-fault-door-buttons-id105"
record_version: 1
title: "VFGLF据付用ポータブル故障による戸開閉釦不作動報告（ID105）"
category: "不具合対応(ELV)"
record_type: "troubleshooting_case"
product: "エレベーター"
model_type:
  - "VFGLF"
document_number: ""
revision: ""
effective_date: ""
review_status: "in_review"
publication_status: "not_published"
classification: "unknown"
cloud_approval: "not_reviewed"
keywords:
  - "戸開閉釦"
  - "釦CPU基板"
  - "据付用ポータブル"
  - "64C"
  - "VFGLF"
source_path: ""
source_filename: "技術情報リスト（協力会社展開用）.xlsx"
onenote_id: ""
related_ids: []
attachment_paths: []
reference_links: []
document_references:
  - document_number: "C-6-S1300"
    title: "トラブルシュート資料"
    locator: "原リスト記載: P.11。本文・版・適用範囲未確認。"
    source_path: ""
  - document_number: ""
    title: "類似不発ASHO29457（原リスト記載）"
    locator: "釦CPU基板交換で解消した類似例との記載。参照先未閲覧。"
    source_path: ""
evidence_sources:
  - source_id: "evidence-list-case-id105"
    source_type: "user_provided_extract"
    title: "首都工・不具合情報共有リスト Excel出力 ID105"
    source_path: ""
    s3_uri: ""
    revision: "原本リスト未照合"
    accessed_at: "2026-10-09"
    supports:
      - "VFGLFで戸開閉釦が一部の自動状態で動作しなかった症状、基板不良の調査経過、据付用ポータブル故障との原因報告、および交換後に解消したとの記載"
structured_data:
  equipment: "VFGLF エレベーター"
  symptom: "自動状態で戸開閉釦が一部動作せず、行先階床呼び、車いす操作盤の釦、かご上ステーションの戸開閉釦は動作したとの報告。エラー表示欄は64C（「sets未調整のため」と原文注記）。個々の表示と症状との関係は未確認。"
  error_codes:
    - "64C（原リスト注記: sets未調整のため。コード定義・本件との関係は未確認）"
  cause: "原リストは、据付用ポータブルの故障により信号状態に異常が生じ、かご上自動状態でかご操作盤からの戸開閉指令が取り込まれなかったと説明する。原因・機能説明は独立確認されていない。"
  verified_actions: []
  outcome: "原リストは、製品添付のポータブルへ交換した後に不具合が解消したと報告する。実施・結果の独立確認および再発有無は未確認。"
---

# VFGLF据付用ポータブル故障による戸開閉釦不作動報告（ID105）

## 症状と条件

首都工・不具合情報共有リストID105は、VFGLFで自動状態の戸開閉釦が一部動作しなかった事例を報告する。独立自動状態では戸閉釦が効かず、全自動状態では戸が閉じた後の戸開釦が効かなかった一方、行先階床呼び、車いす操作盤の釦、かご上ステーションの戸開閉釦は正常だったとの記載がある。共有日は2022-05-27。

エラー表示欄は64C（「sets未調整のため」との注記）だが、この注記が本件の症状や最終原因を示すかは確認されていない。

## 調査の経過と原因報告

原リストでは釦CPU基板の不良を疑い交換したが、症状は解消しなかった。比較確認でも釦CPU基板不良とは判断されず、かご上ステーション基板を交換しても症状が再現したと記録する。

最終的に、原リストは据付用ポータブルの故障を原因として説明する。ポータブルの信号状態により、かご上自動状態でかご操作盤からの戸開閉指令が取り込まれなくなったとの説明がある。原因・機能説明および各調査の因果は、独立確認されていない。

## 対応と結果

原リストは、製品添付のポータブルへ交換した後に不具合が解消したと報告する。交換後の継続確認や再発有無は記載されていない。

## 関連資料

- 原リストはC-6-S1300のP.11を参考資料として挙げる。本文、版、適用範囲は未確認。
- 備考の追加確認指示には電圧測定、端子・コネクタ識別、リレー状態、配線/指令異常に関する具体的な診断分岐が含まれるため、本記録には転載していない。
- 原リストは類似不発ASHO29457を挙げ、釦CPU基板交換で解消した事例と説明する。参照先未閲覧で、本件とは結論が異なるため、同一原因・同一対策とは扱わない。

## 出典・確認状態

- 出典: Excel出力のID105行にあるA列・E〜N列・O列。B/C/D列は参照していない。
- 端子/コネクタ識別、電圧・導通値、配線・リレーの確認、基板交換等の診断・作業手順は転載していない。
- 技術資料本文、参照先ASHO29457、原因・交換後結果の独立確認、現行性、技術レビューは未確認。
- 本記録はレビュー中・未公開であり、故障診断・交換・運転の手順や判定基準を示すものではない。
