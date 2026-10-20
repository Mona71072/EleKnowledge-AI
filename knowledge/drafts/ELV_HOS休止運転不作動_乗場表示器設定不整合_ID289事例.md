---
schema_version: 1
record_id: "elv-hos-service-suspension-not-triggered-indicator-configuration-id289"
record_version: 1
title: "運転休止へ移行しない事例と乗場表示器設定不整合の報告（ID289）"
category: "不具合対応【ELV】"
record_type: "failure_case"
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
  - "運転休止"
  - "HOS"
  - "乗場表示器"
  - "設定不整合"
source_path: ""
source_filename: "技術情報リスト（協力会社展開用）.xlsx"
onenote_id: ""
related_ids: []
attachment_paths: []
reference_links: []
document_references: []
evidence_sources:
  - source_id: "evidence-list-elv-hos-indicator-setting-mismatch-289"
    source_type: "user_provided_extract"
    title: "協力会社展開用Excel: 運転休止のキースイッチを休止側にしても休止動作に移行しない（ID289）"
    source_path: ""
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-13"
    supports:
      - "運転休止へ移行しない症状、乗場表示器の機器構成と設定不整合との原因説明、設定変更後の動作良好報告"
structured_data:
  symptom: "乗場の運転休止キースイッチを操作しても休止状態へ移行しないとの報告。"
  cause: "原リストは、ホールランタンの有無と乗場表示器設定の不整合を原因としている。独立確認していない。"
  result: "原リストは設定変更後に動作良好となったと報告する。独立確認していない。"
  limitations:
    - "設定値/アドレス、階床/基板/端子/コネクタ識別、電圧/導通/通信情報、短絡/測定/設定変更手順は転載しない。"
    - "原因・変更内容の適否・対象範囲・継続結果・現行性は未確認。"
    - "本記録を設定変更、電気診断、運転/復旧手順として使用しない。"
---

# 運転休止へ移行しない事例と乗場表示器設定不整合の報告（ID289）

協力会社展開用リストID289は、乗場の運転休止キースイッチを操作しても休止状態へ移行しない事象を報告する。原リストは、ホールランタンの有無と乗場表示器設定の不整合を原因とし、設定変更後に動作良好となったと報告する。原因・変更内容の適否・対象範囲・継続結果は独立確認していない。

設定値/アドレス、階床/基板/端子/コネクタ識別、電圧/導通/通信情報および短絡/測定/設定変更手順は記録しない。本記録を設定変更、電気診断、運転または復旧手順として使用しない。HOSの現行仕様は承認済み設計資料と所管者の確認による。