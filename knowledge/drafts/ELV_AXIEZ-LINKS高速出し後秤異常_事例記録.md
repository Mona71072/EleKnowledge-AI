---
schema_version: 1
record_id: "elv-axiez-links-high-speed-run-load-weigher-abnormality-case"
record_version: 2
title: "AXIEZ-LINKS高速出し後の自動運転休止と秤異常"
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
  - "高速出し"
  - "秤異常"
  - "自動運転休止"
related_ids:
  - "elv-automatic-operation-issues"
  - "elv-slow-adjustment-cases"
source_path: ""
source_filename: ""
onenote_id: ""
attachment_paths: []
reference_links: []
document_references: []
evidence_sources:
  - source_id: "evidence-list-axiez-links-high-speed-run-load-weigher-abnormality-037"
    source_type: "user_provided_extract"
    title: "首都工・不具合情報共有リスト: 高速出し実施時の秤異常（ID37）"
    source_path: ""
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-09"
    supports:
      - "高速出し後の自動運転休止、ゼロ荷重と半荷重の秤値逆転、原因仮説、初回対応の不成立、追加の秤値記録後の解消報告、別案未実施の記載"
structured_data:
  equipment: "AXIEZ-LINKS"
  symptom: "高速出し後の自動投入時に運転休止となり、秤異常を検出したとの報告。ゼロ荷重と半荷重の秤値が逆転していたと記載される。"
  error_codes: []
  cause: "高速出し前にスローFMSを実施していなかったことが原因との見解がリストに記載されている。原因および一般適用性は独立確認していない。"
  verified_actions: []
  outcome: "リストでは、最初の簡易な半荷重記録は秤異常により実施できず、その後に別の秤値記録対応を行ってから再試行し、異常が解消したと報告する。別の基準値を用いる案は未実施と記載される。これはリスト上の経過であり、具体的な値・機能コード・荷重条件・書込み/調整方法、因果関係、安全性は独立確認していない。"
---

# AXIEZ-LINKS高速出し後の自動運転休止と秤異常

首都工・不具合情報共有リストID37は、AXIEZ-LINKSで高速出し後の自動投入時に運転休止となり、秤異常を検出したと報告する。ゼロ荷重と半荷重の秤値が逆転していたとの記載があるが、個別の測定値や設定コードは転記しない。

リストは高速出し前のスローFMS未実施を原因仮説として挙げているが、独立確認されていない。

## 対応経過と状態

リストによると、最初の簡易な半荷重記録は秤異常により実施できなかった。その後、別の秤値記録対応を経て再試行し、異常が解消したと報告する。一方、基準値を変更する別案は未実施と記載されている。解消結果と原因の因果関係は独立確認しておらず、現行適用も未確認である。

具体的な値、機能コード、荷重条件、秤設定の書込み・調整方法は記録しない。本記録は事例検索用で、秤調整や運転の手順・安全判断の根拠ではない。