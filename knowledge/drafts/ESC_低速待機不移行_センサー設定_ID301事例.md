---
schema_version: 1
record_id: "esc-low-speed-standby-not-entered-sensor-setting-id301"
record_version: 1
title: "低速待機に移行しない事象とセンサー設定報告（ID301）"
category: "不具合対応【ESC】"
record_type: "failure_case"
product: "エスカレーター"
model_type: []
document_number: ""
revision: ""
effective_date: ""
review_status: "in_review"
publication_status: "not_published"
classification: "unknown"
cloud_approval: "not_reviewed"
keywords:
  - "低速待機"
  - "センサー設定"
  - "検出距離"
source_path: ""
source_filename: "技術情報リスト（協力会社展開用）.xlsx"
onenote_id: ""
related_ids:
  - "esc-svfc-post-photoelectric-sensor-standby-id103"
attachment_paths: []
reference_links: []
document_references: []
evidence_sources:
  - source_id: "evidence-list-esc-low-speed-standby-sensor-setting-301"
    source_type: "user_provided_extract"
    title: "協力会社展開用Excel: エスが低速待機に移行しない（ID301）"
    source_path: ""
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-13"
    supports:
      - "自動運転中に低速待機へ移行しなかったとの報告"
      - "センサー設定が原因との説明と設定変更後の動作良好報告"
structured_data:
  symptom: "自動運転中に低速待機へ移行しなかったとの報告。"
  cause: "原リストはセンサーの検出距離設定が原因と説明する。原因の独立確認はしていない。"
  action: "設定変更後に正常動作したとの原リスト報告。具体的な設定値・調整方法は転載しない。"
  result: "設定変更後の動作良好との報告。継続性・再発有無は未確認。"
  limitations:
    - "現場識別、基板/センサー識別、設定値、LED判定、調整/確認手順は転載しない。"
    - "ID103の停止待機不移行報告とは関連テーマだが、同一事象・同一原因とは確認できない。"
    - "本記録をセンサー調整、運転、点検の手順として使用しない。"
---

# 低速待機に移行しない事象とセンサー設定報告（ID301）

協力会社展開用リストID301は、自動運転中に低速待機へ移行しなかった事例を報告し、センサーの検出距離設定を原因として挙げている。設定変更後に正常動作したとの記載があるが、原因、対応後の継続性、再発有無は独立確認していない。

ID103にも待機移行とセンサーに関する報告があるが、ID103は停止待機不移行の別記録であり、同一事象・同一原因とは確認できない。現場識別、基板/センサー識別、設定値、LED判定、調整・確認手順は記録しない。本記録をセンサー調整、運転、点検の手順として使用しない。