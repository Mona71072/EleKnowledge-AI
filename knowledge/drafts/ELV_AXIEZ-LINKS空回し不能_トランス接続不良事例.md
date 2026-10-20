---
schema_version: 1
record_id: "elv-axiez-links-no-load-run-transformer-connection-case"
record_version: 1
title: "AXIEZ-LINKSの空回し不能とトランス接続不良事例"
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
  - "空回し不能"
  - "トランス盤"
  - "接続不良"
  - "終点スイッチ"
related_ids:
  - "elv-me-ch-no-load-hoist-run-unavailable-phase-order-case"
source_path: ""
source_filename: ""
onenote_id: ""
attachment_paths: []
reference_links: []
document_references: []
evidence_sources:
  - source_id: "evidence-list-axiez-links-no-load-run-transformer-connection-050"
    source_type: "user_provided_extract"
    title: "首都工・不具合情報共有リスト: 巻上機の空回しが実施できない事例（ID50）"
    source_path: ""
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-09"
    supports:
      - "AXIEZ-LINKSの空回し不能、トランス盤接続部の損傷・接続不良との原因報告、是正後の回復報告、および後続の別の移動不能報告"
structured_data:
  equipment: "AXIEZ-LINKS"
  symptom: "制御盤とトランス盤の接続後、巻上機の空回しができず、制御盤表示器も点灯しなかったとの報告。"
  error_codes: []
  cause: "原文は現地配線接続部の導線が潰れ、接続が不十分だったことを主事象の原因としている。原因・一般適用性は独立確認していない。"
  verified_actions: []
  outcome: "原文は接続状態の是正後に制御盤表示と電源状態が正常となり、空回し不能が解消したと報告する。その後に別のかご移動不能報告があり、終点スイッチの異常が原因と思われるとするが、対処後に正常動作したとの記載の詳細は未確認。後続事象と主事象の因果関係も不明。具体的な電気測定、端子・配線識別、短絡、接続修理、スイッチ操作は記録しない。"
---

# AXIEZ-LINKSの空回し不能とトランス接続不良事例

首都工・不具合情報共有リストID50は、制御盤とトランス盤を接続した後、巻上機の空回しができず、制御盤表示器も点灯しなかったと報告する。原文は現地配線接続部の導線が潰れ、接続が不十分だったことを原因としている。具体的な端子や配線識別は記録しない。

## 調査経過と対応結果

原文では、接続部の状態を調べて是正した後、制御盤表示と電源状態が正常となり、空回し不能が解消したと報告する。電圧測定値、接続確認・修理方法は記録しない。

その後、別途かごが動かないとの連絡があり、再調査で終点スイッチの異常が原因と思われると記載されている。続く対応後に動作正常となったとの報告はあるが、原因・確認範囲・対処後の状態は独立確認していない。主事象との因果関係も不明であり、スイッチ操作や復旧方法は記録しない。

ID46も空回し不能の報告だが、対象機種と原因記載が異なるため別事例である。関連は症状上の参照であり、原因の裏付けや対処方法の共通性を示さない。本記録は事例検索用で、診断・電気作業・運転の手順ではない。