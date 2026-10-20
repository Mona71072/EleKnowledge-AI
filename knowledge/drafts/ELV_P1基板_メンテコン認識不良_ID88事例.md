---
schema_version: 1
record_id: "elv-p1-board-maintenance-console-recognition-id88"
record_version: 1
title: "P1基板がメンテコンに認識されない報告（ID88）"
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
  - "P1基板"
  - "メンテコン"
  - "USBシリアル変換"
related_ids:
  - "elv-p1-board-replacement"
source_path: ""
source_filename: "技術情報リスト（協力会社展開用）.xlsx"
onenote_id: ""
attachment_paths: []
reference_links: []
document_references: []
evidence_sources:
  - source_id: "evidence-list-case-id88"
    source_type: "user_provided_extract"
    title: "首都工・不具合情報共有リスト Excel出力 ID88"
    source_path: ""
    s3_uri: ""
    revision: "原本リスト・添付未照合"
    accessed_at: "2026-10-09"
    supports:
      - "P1基板がメンテコンに認識されない症状、原文記載の確認観点と記述差、対応後結果の記載有無"
structured_data:
  equipment: "P1基板とメンテコン"
  symptom: "メンテコンをP1基板へ接続した際に、メンテコンが基板を認識しなかったとの報告。接続位置の詳細は記録しない。"
  cause: "確定原因は記載されていない。原文は基板側スイッチ状態とUSBシリアルポートの設定を確認観点として挙げ、追記ではPC側のポート割当て競合を疑う説明をしている。各状態の実測・是正実施・改善確認は記載されていない。設定説明には文面上の不一致があり、正しい値や変更方法は未解決。"
  verified_actions: []
  outcome: "確認・設定を促す記載はあるが、誰が確認・変更したか、認識が回復したか、最終結果は記載なし。"
---

# P1基板がメンテコンに認識されない報告（ID88）

## 概要

首都工・不具合情報共有リストID88は、メンテコン接続時にP1基板を認識しなかった事例を記録する。共有日は2022-01-21。機種、エラー表示、確認実施者、確認・変更後の結果は記載されていない。

## 症状と確認経過

- メンテコンをP1基板へ接続した際、基板を認識しなかったとの報告。
- 原文は基板側スイッチ状態とUSBシリアルポート設定を確認観点に挙げている。
- 追記ではPC側のポート割当て競合を疑う説明がある。ただし、実際に競合が確認されたか、割当て変更を実施したかは記載されていない。

## 原文上の不一致と結果

初回記載と追記では、USBシリアルポートに関する指示の方向が一致していない。どの設定が正しいか、対象PC・ドライバー・機器構成が何かは確認できず、原文が参照する添付も未閲覧である。このため具体的な設定値、画面操作、変更手順は転記していない。原文の確認観点を現行の設定指示として使用しないこと。

対応の実施や認識回復の結果は記載なし。原因を確定したり、解決済みと判断したりできない。

## 関連資料

- [[ELV_P1基板交換記録]]: P1基板交換に関する別の原資料記録。本件は交換ではなくメンテコンの認識不良であり、原因・作業は共通と確認されていない。
- [[不具合対応【ELV】/索引]]: ELV不具合資料の索引。

## 出典・確認状態

- 出典: Excel出力のID88行にあるA列・E〜N列・O列。B/C/D列は参照していない。
- 原本リスト、添付、PC・ケーブル・基板の実構成は未照合。設定の妥当性、原因、是正、結果、現行性は未確認。
- 具体的なスイッチ位置、ポート値、PC画面操作、変更手順は転記していない。
- 本記録は未レビューであり、メンテコン接続や設定変更の手順を示すものではない。
