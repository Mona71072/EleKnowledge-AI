---
schema_version: 1
record_id: "elv-contactor-not-pulling-source-knowledge-id64"
record_version: 1
title: "#5コンタクタが吸引しない条件に関する原文知識（ID64）"
category: "不具合対応(ELV)"
record_type: "knowhow"
product: "エレベーター"
model_type: []
document_number: ""
revision: ""
effective_date: ""
review_status: "in_review"
publication_status: "not_published"
classification: "unknown"
cloud_approval: "not_reviewed"
keywords:
  - "コンタクタ"
  - "#5"
  - "安全回路"
  - "吸引"
related_ids: []
source_path: ""
source_filename: "技術情報リスト（協力会社展開用）.xlsx"
onenote_id: ""
attachment_paths: []
reference_links: []
document_references:
  - document_number: ""
    title: "制御盤標準接続図（ストレート）のコンタクトカウント表"
    locator: "原リストの確認欄に記載。資料本文・改訂・適用性未確認。"
    source_path: ""
evidence_sources:
  - source_id: "evidence-list-contactor-5-not-pulling-064"
    source_type: "user_provided_extract"
    title: "首都工・不具合情報共有リスト: 安全回路は問題ないにも関わらず#5を引かない（ID64）"
    source_path: ""
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-09"
    supports:
      - "コンタクタの吸引条件、バック接点による状態確認、制御指令がない場合の説明、4**エラー優先の注意"
structured_data:
  knowledge_items:
    - topic: "#5コンタクタが吸引しない条件"
      statement: "原文は、#5がコンタクタで、コイルを動作させる電気的条件が成立すると導通する一方、安全回路（#29）が正常でも吸引指令が出ていなければ#5は吸引しないと説明する。また、補助バック接点でON/OFF状態を確認する構成と、R1基板側に指令状態に関する確認箇所があることを記す。"
      conditions:
        - "対象範囲欄は「全エレ機種」。この適用範囲は原リストの記載であり、機種別の独立確認はしていない。"
        - "エラー表示欄は、4**のエラーがある場合はまずその対応を優先すると記載。4**の範囲・意味は原文以上に解釈しない。"
      exceptions: []
      rationale: "安全回路が正常であることだけではコンタクタ吸引指令の成立を意味しない、という原文上の説明。"
      verification_status: "source_recorded"
      evidence_source_ids:
        - "evidence-list-contactor-5-not-pulling-064"
  source_notes:
    - "原文にある端子名、機種別電圧値、R1基板上の個別確認点、電圧測定の指示は転載していない。動作原理の要約は測定・診断手順や承認済み仕様ではない。"
---

# #5コンタクタが吸引しない条件に関する原文知識（ID64）

首都工・不具合情報共有リストID64は、対象範囲欄を「全エレ機種」とし、重要度「中」、現象分類を「豆知識;#電気的;#機械的」と記載する。原文は#5をコンタクタとし、安全回路が正常な場合でも、吸引指令が出ていなければコンタクタは吸引しないという動作説明を示す。これは原リスト上の一般説明で、全機種への適用・現行性は未確認である。

## 条件と読み方

原文は補助バック接点によるON/OFF状態確認と、R1基板側の指令状態との関係を説明する。また、エラー表示欄には「4**のエラーがある場合はまずその対応を優先」とある。「4**」の具体的なコード範囲や意味は確認できないため、記載どおりに保留する。

## 適用上の注意

端子名、機種別電圧値、個別確認点、電圧測定・接続確認の具体指示は安全上の理由から転載していない。原リストの動作説明と確認欄にある図面名だけを記録しており、電気的な測定・故障切り分け・運転指示として使用しない。承認済みの機種別図面・要領書の本文と適用性は未確認である。