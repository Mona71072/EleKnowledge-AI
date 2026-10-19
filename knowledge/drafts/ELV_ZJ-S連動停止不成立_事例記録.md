---
schema_version: 1
record_id: "elv-zj-s-coupled-stop-failure-label-mismatch-case"
record_version: 1
title: "ZJ-Sの複数台連動停止不成立事例"
category: "不具合対応(ELV)"
record_type: "troubleshooting_case"
product: "エレベーター"
model_type:
  - "ZJ-S(SVFBM)"
document_number: ""
revision: ""
effective_date: ""
review_status: "in_review"
publication_status: "not_published"
classification: "unknown"
cloud_approval: "not_reviewed"
keywords:
  - "複数台連動"
  - "連動停止"
  - "接続漏れ"
  - "線札"
related_ids: []
source_path: ""
source_filename: ""
onenote_id: ""
attachment_paths: []
reference_links: []
document_references:
  - document_number: "YS152C135"
    title: "特殊工事連絡票"
    locator: ""
    source_path: ""
evidence_sources:
  - source_id: "evidence-list-zj-s-coupled-stop-failure-label-mismatch-051"
    source_type: "user_provided_extract"
    title: "首都工・不具合情報共有リスト: 連動停止動作ができない事例（ID51）"
    source_path: ""
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-09"
    supports:
      - "複数台連動停止の症状、接続図との照合後に見つかった接続漏れ、名称と線札の不一致との原因報告、是正後の動作確認結果"
      - "進捗欄の完了状態と、不具合票作成・添付に関する備考記載"
structured_data:
  equipment: "ZJ-S(SVFBM)"
  symptom: "特定の複数台構成で連動停止を確認する際、同方向への運転を試みても一部の組合せで想定方向の運転ができず、連動停止動作を確認できなかったとの報告。"
  error_codes: []
  cause: "接続図と現地状態の照合で盤間の接続漏れが見つかり、端子台名称と線札の不一致により接続されていなかったことが原因と記録されている。原因はリスト上の報告であり、独立確認していない。"
  verified_actions: []
  outcome: "リストでは、現地是正後に対象の同方向運転と連動停止が良好となり、進捗欄は完了としている。備考には不具合票を作成し添付したとの記載があるが、添付実体・内容は未確認。"
---

# ZJ-Sの複数台連動停止不成立事例

首都工・不具合情報共有リストID51は、ZJ-S(SVFBM)の特定の複数台構成で、同方向への運転を試みた際に一部の組合せで想定方向の運転ができず、連動停止を確認できなかったと報告する。号機配置や現地固有の識別情報は記録しない。

## 調査経過と対応結果

リストでは、指定された連動用の盤間配線は施工済みとされた一方、接続図と現地状態の照合で受電盤とI/O盤間に接続漏れが見つかったとしている。端子台名称と線札の不一致が原因との報告であり、現地是正後は対象の同方向運転と連動停止が良好となった。進捗欄は「完了」である。

備考には不具合票を作成し添付したとの記載があるが、添付実体・内容は確認していない。参照資料YS152C135の本文・改訂も未確認である。端子・線札の識別、配線経路、導通試験、具体的な結線・是正方法は記録しない。原因・結果の独立確認および現行適用確認は未実施。