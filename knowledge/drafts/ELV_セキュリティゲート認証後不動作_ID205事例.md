---
schema_version: 1
record_id: "case-elv-security-gate-card-authentication-assignment-failure-id205"
record_version: 1
title: "カード認証後のセキュリティゲート・号機割当不動作報告（ID205）"
category: "不具合対応【ELV】"
record_type: "troubleshooting_case"
product: "エレナビ"
model_type: []
document_number: ""
revision: ""
effective_date: ""
review_status: "in_review"
publication_status: "not_published"
classification: "unknown"
cloud_approval: "not_reviewed"
keywords:
  - "カード認証"
  - "セキュリティゲート"
  - "号機割当"
  - "非常解除状態"
source_path: "首都工・不具合情報共有リスト.xlsx"
source_filename: "首都工・不具合情報共有リスト.xlsx"
onenote_id: ""
related_ids: []
attachment_paths: []
reference_links: []
document_references: []
evidence_sources:
  - source_id: "evidence-list-elv-security-gate-card-authentication-assignment-failure-205"
    source_type: "vault_original"
    title: "首都工・不具合情報共有リスト: カード認証後のセキュリティゲート・号機割当不動作（ID205）"
    source_path: "首都工・不具合情報共有リスト.xlsx"
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-14"
    supports:
      - "認証応答後にゲートが動作せず、割当号機表示と呼びが変化しなかったとの報告"
      - "非常解除状態が残っていたとの原因説明と、復旧後に正常動作を確認したとの報告"
structured_data:
  equipment: "エレナビ、カード認証設備、セキュリティゲート、割当号機表示器"
  symptom: "5台中1台で、カード認証応答の後に認証エラーとなり、ゲートが動作せず、割当号機表示器も変化しなかったとの報告。"
  error_codes: []
  cause: "連動試験後にセキュリティゲートの非常解除状態が残っていたことが原因との一次リスト記載。独立確認していない。"
  verified_actions: []
  outcome: "一次リストは、所管側の復旧対応後に正常動作を確認したと報告する。独立確認・継続確認はしていない。"
  limitations:
    - "現場名、号機識別、担当者等の個別情報は記録しない。"
    - "強制解錠、非常解除からの復帰、電源操作の具体的な手順・順序、認証設定および詳細な監査ログ情報は記録しない。"
    - "認証・ゲートの状態、原因、復旧結果は一次リスト上の報告であり、独立確認していない。"
    - "本記録を認証設定、ゲート操作、復旧、入退場制御、セキュリティ判断の手順として使用しない。"
---

# カード認証後のセキュリティゲート・号機割当不動作報告（ID205）

## 事象と調査所見

首都工・不具合情報共有リストID205は、5台中1台でカード認証応答の後にエラーとなり、セキュリティゲートが動作せず、割当号機表示器が変化しなかったと報告する。原リストの調査記載では、カード情報は認証装置側に届いていた一方、認証は不成立で、群管理側へ号機割当情報が渡っていないと判断された。これらは原リスト上の観察・推定であり、設備ログや試験記録による独立確認はしていない。

## 原リスト上の原因と結果

原リストは、連動試験後にセキュリティゲートの非常解除状態が残っていたことを原因として挙げる。所管側の復旧対応後に正常動作を確認したとの報告があるが、具体的な復帰操作・電源操作の手順と順序は記録しない。原因との因果関係、復旧確認、再発有無は独立確認していない。

現場・個人情報、強制解錠や復帰の手順、認証設定、詳細な監査ログ情報は記録しない。本記録をゲート操作、認証設定、復旧、入退場制御の手順として使用しない。