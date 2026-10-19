---
schema_version: 1
record_id: "case-elv-mrl-ns-keypad-temporary-release-setting-id184"
record_version: 1
title: "MRL乗場テンキーによるNS一時解除の不動作報告（ID184）"
category: "不具合対応(ELV)"
record_type: "troubleshooting_case"
product: "エレベーター"
model_type: ["MRL"]
document_number: ""
revision: ""
effective_date: ""
review_status: "in_review"
publication_status: "not_published"
classification: "unknown"
cloud_approval: "not_reviewed"
keywords:
  - "MRL"
  - "乗場テンキー"
  - "NS一時解除"
  - "品目表改定"
source_path: "首都工・不具合情報共有リスト.xlsx"
source_filename: "首都工・不具合情報共有リスト.xlsx"
onenote_id: ""
related_ids:
  - "elv-rear-ns-key-switch-no-response-id364"
attachment_paths: []
reference_links: []
document_references: []
evidence_sources:
  - source_id: "evidence-list-elv-mrl-ns-keypad-temporary-release-184"
    source_type: "vault_original"
    title: "首都工・不具合情報共有リスト: 乗場テンキーを入力しても、NSの一時解除ができない件（ID184）"
    source_path: "首都工・不具合情報共有リスト.xlsx"
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-14"
    supports:
      - "MRLの乗場テンキーによるNS一時解除が動作しなかったとの報告"
      - "品目表の設定改定を参照した後の設定変更と、動作良好との報告"
      - "対応状況欄は完了だが、改定版・広範な適用性・独立した再確認は未確認であること"
structured_data:
  equipment: "MRLの乗場テンキーによるNS一時解除機能"
  symptom: "乗場テンキーを用いたNS一時解除が動作せず、乗場呼びを登録できなかったとの報告。入力コードと具体的な操作は記録しない。"
  error_codes: []
  cause: "一次リストは、対象機の基板設定が品目表の改定内容と一致していなかったことを原因として説明する。具体的な設定値、基板上の設定位置、現行品目表の改訂・適用範囲は未確認。"
  verified_actions: []
  outcome: "設定変更後に動作良好となったとの報告があり、対応状況欄は完了。設定変更の具体値・方法、改定版の本文/現行性、独立した機能確認、他設備への適用は未確認。"
---

# MRL乗場テンキーによるNS一時解除の不動作報告（ID184）

## 症状と原因説明

首都工・不具合情報共有リストID184は、MRLで乗場テンキーによるNS一時解除が動作せず、乗場呼びを登録できなかったと報告する。原因欄は、対象機の設定が品目表の改定内容と一致していなかったことを挙げている。

## 対応状況と未確認事項

品目表の改定を参照した設定変更後、動作良好となったとの報告があり、対応状況欄は完了。品目表の改訂版、記載の現行性・対象範囲、設定変更後の独立確認は未確認である。これは出典上の一事例報告であり、他設備への適用を示さない。

ID364もサービス階のNS一時解除機能に関する報告だが、VFGLB/VFGLFのリア側キー入力と信号経路構成に関する別事例である。機種、入力方式、原因説明が異なるため同一案件として扱わない。

入力コード、設定値、基板/スイッチ識別、コネクタ/端子、測定方法、設定変更手順は転載していない。本記録を認証、サービス機能の設定、配線、運転操作の手順として使用しない。対象設備の責任者が承認済みの現行品目表と設計資料で確認する。

## 出典

- 首都工・不具合情報共有リスト.xlsx、ID184（sheet1 row240）。
- 入力コード、基板設定の具体値、測定・変更操作は転載していない。