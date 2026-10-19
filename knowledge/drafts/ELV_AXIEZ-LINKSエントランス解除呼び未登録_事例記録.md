---
schema_version: 1
record_id: "elv-axiez-links-entrance-release-call-not-registered-case"
record_version: 2
title: "AXIEZ-LINKSのエントランス解除後に乗場呼びが登録されない事例"
category: "不具合対応(ELV)"
record_type: "troubleshooting_case"
product: "エレベーター"
model_type:
  - "AXIEZ-LINKS"
document_number: ""
revision: ""
effective_date: ""
review_status: "in_review"
publication_status: "not_published"
classification: "unknown"
cloud_approval: "not_reviewed"
keywords:
  - "エントランス解除"
  - "乗場呼び"
  - "信号インターフェース"
  - "ソフトウェア設定"
source_path: ""
source_filename: ""
onenote_id: ""
related_ids: []
attachment_paths: []
reference_links: []
document_references: []
evidence_sources:
  - source_id: "evidence-list-axiez-links-entrance-release-call-not-registered-044"
    source_type: "user_provided_extract"
    title: "首都工・不具合情報共有リスト: エントランス解除が動作しない事例（ID44）"
    source_path: ""
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-09"
    supports:
      - "初期試験で解除後の乗場呼びが自動登録されず、設定未実施と信号インターフェース仕様差が原因・対策として記載されること。最終対策後の結果は記載なし"
structured_data:
  equipment: "AXIEZ-LINKS"
  symptom: "エントランス解除操作を行っても、乗場呼びが自動登録されなかったとの報告。"
  error_codes: []
  cause: "ソフトウェア設定の未実施と、外部機器との信号インターフェース仕様差が原因として記録されている。原因・影響範囲は独立確認していない。"
  verified_actions: []
  outcome: "リストでは、初期試験で自動登録しなかった後、設定に対するソフトウェア改訂と信号インターフェース仕様への現地対応を対策として記載する。これらの対策後に再試験したか、解決したかは記載されていない。具体的な結線・電圧・改造方法は記録しない。"
---

# AXIEZ-LINKSのエントランス解除後に乗場呼びが登録されない事例

首都工・不具合情報共有リストID44は、初期試験でエントランス解除操作後に乗場呼びが自動登録されなかったと報告する。その後の調査で、ソフトウェア設定の未実施と外部機器との信号インターフェース仕様差を原因として記載し、ソフトウェア改訂と現地仕様への対応を対策として挙げている。

原文には、対策後の再試験結果や最終解決状態が記載されていない。原因・対策の妥当性も独立確認していない。具体的な端子、配線、電圧、試験、現地改造の内容は記録しない。