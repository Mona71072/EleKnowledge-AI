---
schema_version: 1
record_id: "elv-sets-state-error-64c-id418"
record_version: 1
title: "SETS状態に関連する64C表示事例（ID418）"
category: "不具合対応(ELV)"
record_type: "troubleshooting_case"
product: "エレベーター"
model_type:
  - "VFGLB"
document_number: ""
revision: ""
effective_date: ""
review_status: "in_review"
publication_status: "not_published"
classification: "unknown"
cloud_approval: "not_reviewed"
keywords:
  - "SETS"
  - "64C"
  - "バッファ速度制限"
  - "状態表示"
source_path: ""
source_filename: "技術情報リスト（協力会社展開用）.xlsx"
onenote_id: ""
related_ids: []
attachment_paths: []
reference_links: []
document_references: []
evidence_sources:
  - source_id: "evidence-list-elv-sets-state-64c-418"
    source_type: "user_provided_extract"
    title: "協力会社展開用Excel: SETS状態に関連する64C表示（ID418）"
    source_path: ""
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-13"
    supports:
      - "官検後に表示された64C、リセット操作で消えなかったこと、SETS状態に関する出典説明"
structured_data:
  equipment: "エレベーター（VFGLB）"
  symptom: "官検後の確認時に64C（原リスト表示名: SETSバッファ速制限）が表示され、電源・CPUリセット後も消えなかったとの報告。"
  source_explanation: "原リストは、64CがSETSに関する特定の中間状態・運転準備段階で検出され得ると説明し、確認時の状態によって表示される可能性を指摘する。コード定義、該当設備のSETS適用状態、表示が想定内かどうかは独立確認していない。"
  cause_assessment: "運転状態・SETS適用有無・エラーの判定条件が不明であり、当該表示の原因や故障該当性は確定できない。"
  outcome: "表示が解消したか、機器が正常と確認されたか、是正や運転確認が行われたかは記載から確認できない。"
  limitations:
    - "具体的な運転速度、モード、スイッチ/リモコン操作、終端走行、復帰・リセット条件は転載しない。"
    - "SETSや64Cの定義・適用条件は原リスト上の説明であり、現行資料による独立確認はない。"
    - "他事例の64C表示と同一原因・同一判定とは推定しない。"
---

# SETS状態に関連する64C表示事例（ID418）

首都工・不具合情報共有リストID418は、官検後の確認時に64C（原リスト表示名「SETSバッファ速制限」）が表示され、電源およびCPUのリセット後も表示が消えなかったと報告する。

原リストは、64CがSETSに関する特定の中間状態・運転準備段階で検出され得ると説明し、確認時の状態によって表示される可能性を指摘している。これは出典上の説明であり、コード定義、当該設備のSETS適用状態、表示が想定内か故障かは独立確認されていない。表示の解消、正常性確認、対応後の結果も不明である。

本リストは、SETSが一部の設備構成で緩衝器や昇降路スペースの設計に関係する装置として説明するが、適用範囲・設計値は本記録に含めない。具体的な速度、モード、スイッチ/リモコン操作、終端走行、復帰条件は転載しない。本記録をエラー判定・リセット・運転の手順として使用しない。

別事例の [[ELV_VFGLF据付用ポータブル故障_戸開閉釦不作動_ID105事例]] にも64Cの記載があるが、そちらではコード定義・症状との関係が未確認である。表示コードが共通するだけで、同一原因や同一対処とは扱わない。