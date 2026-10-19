---
schema_version: 1
record_id: "elv-km-ld-regenerative-converter-run-phase-order-case"
record_version: 2
title: "KM-LDの回生コンバーター運転不能と相順差の事例"
category: "不具合対応(ELV)"
record_type: "troubleshooting_case"
product: "エレベーター"
model_type:
  - "KM-LD"
document_number: ""
revision: ""
effective_date: ""
review_status: "in_review"
publication_status: "not_published"
classification: "unknown"
cloud_approval: "not_reviewed"
keywords:
  - "回生コンバーター"
  - "相順"
  - "PWFH"
  - "LFOH"
related_ids:
  - "elv-me-ch-no-load-hoist-run-unavailable-phase-order-case"
  - "elv-km-ld-regenerative-converter-not-operating-control-power-id80"
source_path: ""
source_filename: ""
onenote_id: ""
attachment_paths: []
reference_links: []
document_references:
  - document_number: "C-7-C3700"
    title: "VFGLBのEA（参考資料欄記載。対象設備への適用未確認）"
    locator: ""
    source_path: ""
  - document_number: "YE310C814"
    title: "PT.14（参考資料欄記載。本文未確認）"
    locator: ""
    source_path: ""
evidence_sources:
  - source_id: "evidence-list-km-ld-regenerative-converter-phase-order-054"
    source_type: "user_provided_extract"
    title: "首都工・不具合情報共有リスト: 客先電源相間違いによる回生コンバーター運転不能（ID54）"
    source_path: ""
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-09"
    supports:
      - "回生コンバーター使用時と非使用時の低速運転可否・速度条件、C1カードの表示欄と現地確認時のLED状態、客先電源相順差との原因報告および是正後の運転報告"
structured_data:
  equipment: "KM-LD"
  symptom: "WOS開始時、回生コンバーター使用時は15 m/minの低速運転ができず、非使用時は8 m/minで運転できたとの一事例報告。これらはリスト記載の条件であり、推奨速度や試験条件ではない。"
  error_codes:
    - "PWFH"
    - "LFOH"
  cause: "リストは客先電源の相順誤り（欠相・逆相関連）を原因としている。原因・コードとの関係は独立確認していない。"
  verified_actions: []
  outcome: "初期の運転・配線確認では解消せず、現地確認時のC1カード表示ではPWFH・LFOHのLEDが点灯しなかったと記録される。客先電源の相順是正後、回生コンバーターを使用した運転が可能になったとの報告。具体的な相、遮断器、端子、配線変更、測定値、確認手順は記録しない。原因・結果・現行適用は未確認。"
---

# KM-LDの回生コンバーター運転不能と相順差の事例

首都工・不具合情報共有リストID54は、KM-LDのWOS開始時、回生コンバーター使用時には15 m/minの低速運転ができず、非使用時には8 m/minで運転できたと報告する。これらは単一事例の記録値であり、推奨速度や試験条件ではない。

## 調査経過と原因報告

リストのエラー表示欄にはC1カードのPWFH・LFOHが記載される一方、現地確認欄ではハードウェアエラー確認時に該当LEDが点灯しなかったと記録される。表示の発生条件や意味は独立確認していない。初期の運転・配線確認では解消せず、原文は客先電源の相順誤りを原因としている。

## 対応結果

原文によると、客先電源の相順を是正した後、回生コンバーターを使用した運転が可能になった。具体的な相、遮断器、端子、配線変更、電圧測定値、確認・是正手順は記録しない。原因・結果・現行適用は独立確認していない。

ID46も相順差を原因とする空回し不能の報告だが、対象機種と電源の状況が異なる。関連付けは事例検索のためであり、同一原因や是正方法の共通性を示さない。本記録は事例検索用で、運転・電気作業の手順ではない。

[[ELV_KM-LD回生コンバーター運転不能_CCP未投入報告_ID80事例]]（ID80）も同じKM-LD・WOS・コンバーター使用時の運転不能を記録するが、制御電源未投入との別原因報告である。共通条件だけを示す関連であり、同一案件・共通是正を意味しない。