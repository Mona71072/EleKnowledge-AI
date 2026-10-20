---
schema_version: 1
record_id: "knowhow-axiez-links-rear-call-disable-display-conditions-20261009"
record_version: 2
title: "AXIEZ-LINKs背後呼び登録無効機能の液晶仕様条件"
category: "技術メモ【ELV】２"
record_type: "knowhow"
product: "エレベーター"
model_type:
  - "AXIEZ-LINKs"
document_number: ""
revision: "リスト記載。現行性未確認"
effective_date: ""
review_status: "in_review"
publication_status: "not_published"
classification: "unknown"
cloud_approval: "not_reviewed"
keywords:
  - "背後呼び"
  - "登録無効機能"
  - "液晶仕様"
source_path: ""
source_filename: ""
onenote_id: ""
related_ids: []
attachment_paths: []
reference_links: []
document_references: []
evidence_sources:
  - source_id: "evidence-list-axiez-links-rear-call-display-338"
    source_type: "user_provided_extract"
    title: "首都工・不具合情報共有リスト: 背後呼び登録無効機能の適用条件"
    source_path: ""
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-09"
    supports:
      - "AXIEZ-LINKsの背後呼び登録無効機能について、液晶仕様別の適用差が報告されていること"
      - "背後呼びの用語説明"
structured_data:
  knowledge_items:
    - topic: "背後呼びの用語説明"
      statement: "原リストの説明では、背後呼びは、かごの運転方向と反対側にある自かごより後方の階の呼びを指す。"
      conditions:
        - "原リストの用語説明を一般化したもの。"
      exceptions:
        - "個別設備の階床情報や呼び登録の操作方法は含めない。"
      rationale: "機能説明中の用語を個別設備情報なしで明確化するため。"
      verification_status: "source_recorded"
      evidence_source_ids:
        - "evidence-list-axiez-links-rear-call-display-338"
    - topic: "背後呼び登録無効機能は液晶仕様により適用差があるとの報告"
      statement: "首都工・不具合情報共有リストID338は、AXIEZ-LINKsで5.7インチ液晶CID-Sの場合は背後呼び登録無効機能が適用されず、10.1インチ液晶CID-SAの場合は適用されると報告している。これはリスト記載であり、現行仕様との独立照合は未実施。"
      conditions:
        - "AXIEZ-LINKsの個別報告。機種・仕様の別構成へ一般化しない。"
        - "液晶仕様・機能の組合せと対象設備への適用は承認済み現行資料で未確認。"
      exceptions:
        - "設定変更、機能解除、運転操作の手順は含まない。"
      rationale: "機種名だけで機能適用を一律判断せず、液晶仕様と承認済み機種別資料の照合を促すため。"
      verification_status: "source_recorded"
      evidence_source_ids:
        - "evidence-list-axiez-links-rear-call-display-338"
  source_notes:
    - "出典リストの内容を記録したもので、機能の現行性・適用範囲・表示仕様との対応は未確認。"
    - "現場名・号機・共有者情報は転記していない。機能設定や運転判断に使用しない。AWS/S3送信なし。"
---

# AXIEZ-LINKs背後呼び登録無効機能の液晶仕様条件

首都工・不具合情報共有リストID338は、AXIEZ-LINKsの背後呼び登録無効機能について、液晶仕様による適用差を報告している。リスト記載では、CID-Sの場合は適用されず、CID-SAの場合は適用される。

原リストの説明では、「背後呼び」は、かごの運転方向と反対側にある自かごより後方の階の呼びを指す。

この対応関係はリスト上の報告であり、現行仕様、個別設備の構成、機種別適用は未確認である。機種名だけで適用を判断せず、承認済み現行資料で照合する。設定変更・解除・運転手順は含めない。