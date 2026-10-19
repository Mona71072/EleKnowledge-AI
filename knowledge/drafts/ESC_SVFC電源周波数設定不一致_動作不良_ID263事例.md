---
schema_version: 1
record_id: "esc-svfc-frequency-configuration-mismatch-id263"
record_version: 1
title: "SVFCの電源周波数設定不一致に関する動作不良報告（ID263）"
category: "不具合対応【ESC】"
record_type: "failure_case"
product: "エスカレーター"
model_type:
  - "SVFC"
document_number: ""
revision: ""
effective_date: ""
review_status: "in_review"
publication_status: "not_published"
classification: "unknown"
cloud_approval: "not_reviewed"
keywords:
  - "SVFC"
  - "動作不良"
  - "電源周波数"
  - "設定不一致"
  - "トレースデータ"
source_path: ""
source_filename: "技術情報リスト（協力会社展開用）.xlsx"
onenote_id: ""
related_ids:
  - "elv-putty-svfc-log"
  - "esc-frequency-parameter-mismatch-id427"
attachment_paths: []
reference_links: []
document_references: []
evidence_sources:
  - source_id: "evidence-list-esc-svfc-frequency-mismatch-263"
    source_type: "user_provided_extract"
    title: "協力会社展開用Excel: エスカレーター(SVFC)のトレースデータ採取方法（ID263）"
    source_path: ""
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-13"
    supports:
      - "SVFCの動作不良、電源周波数設定に関する原因説明、トレースデータ採取案内"
structured_data:
  symptom: "SVFCで動作不良が発生し、電源位相に関する異常表示があったとの原リスト報告。表示コードは転載しない。"
  cause: "原リストは電源周波数設定の不一致を関連要因として挙げる。具体的な設定値および原因は独立確認していない。"
  outcome: "是正後の結果は原リストから確認できない。"
  trace_data: "原リストはトレースデータ採取に言及する。採取方法・通信/取得条件・操作手順は転載しない。"
  limitations:
    - "エラーコード、基板/パラメータ識別、周波数等の設定値、現場/担当者情報は転載しない。"
    - "原因・設定の適否・適用範囲・是正結果は未確認。"
    - "ID427のエスカレーター事例との同一原因は確認されていない。"
    - "本記録および参照先を設定変更、運転、診断、復旧またはトレース採取手順として使用しない。"
---

# SVFCの電源周波数設定不一致に関する動作不良報告（ID263）

協力会社展開用リストID263は、SVFCの動作不良と電源位相に関する異常表示を報告し、電源周波数設定の不一致を関連要因として挙げている。表示コード、基板/パラメータ識別、設定値は記録しない。原因・設定の適否・適用範囲および是正後の結果は独立確認していない。

原リストはトレースデータ採取にも言及するが、採取方法や通信/取得条件は記録しない。参照先の[SVFCログ採取ノート参照記録](ELV_SVFCログ採取参照)は手順の承認や利用権限を示すものではない。

ID427にもエスカレーターの周波数設定に関する別報告があるが、対象状況が異なるため同一原因とは扱わない。本記録を設定変更、運転、診断、復旧またはトレース採取手順として使用しない。