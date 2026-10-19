---
schema_version: 1
record_id: "elv-km-ld-attendant-operation-mode-switch-failure-case"
record_version: 1
title: "KM-LDの専用運転切替不成立事例"
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
  - "専用運転"
  - "運転モード切替"
  - "ソフトウェア"
source_path: ""
source_filename: ""
onenote_id: ""
related_ids: []
attachment_paths: []
reference_links: []
document_references: []
evidence_sources:
  - source_id: "evidence-list-km-ld-attendant-mode-switch-failure-039"
    source_type: "user_provided_extract"
    title: "首都工・不具合情報共有リスト: 専用運転に移行しない事例（ID39）"
    source_path: ""
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-09"
    supports:
      - "専用運転への切替不成立、デモ機での再現、ソフトウェア改訂後に要求動作を満たしたとの報告"
structured_data:
  equipment: "KM-LD"
  symptom: "専用運転への切替操作をしても全自動運転のままで、専用運転に移行しなかったとの報告。"
  error_codes: []
  cause: "デモ機で同じ現象を再現し、ソフトウェアに起因する不具合として対策されたとの説明がリストにある。原因および他設備への適用性は独立確認していない。"
  verified_actions: []
  outcome: "動作フローの一部改訂とソフトウェア書換え後、要求された動作を満たしたとの報告。改訂内容、実施設備、現行ソフトへの適用性は未確認。"
---

# KM-LDの専用運転切替不成立事例

首都工・不具合情報共有リストID39は、専用運転への切替操作をしても全自動運転のままで、専用運転に移行しなかったと報告する。リストによると、デモ機で現象が再現され、ソフトウェア改訂後に要求された動作を満たした。

ソフトウェア起因との説明と改善結果はリスト上の報告であり、原因・改訂内容・他設備への適用性は独立確認していない。配線、電圧、信号、パラメータの診断情報および書換え手順は記録しない。