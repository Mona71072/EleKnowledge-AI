---
schema_version: 1
record_id: "elv-variable-speed-anomaly"
record_version: 1
title: "エレベーター可変速時の速度差に関する不具合メモ"
category: "不具合対応(ELV)"
record_type: "troubleshooting_case"
product: "エレベーター"
model_type:
  - "LINKs"
document_number: ""
revision: ""
effective_date: ""
review_status: "in_review"
publication_status: "not_published"
classification: "unknown"
cloud_approval: "not_reviewed"
keywords:
  - "可変速"
  - "NL"
  - "BL"
  - "FMS"
  - "秤値"
source_path: "不具合対応【ELV】/現象（不具合対応）/可変速 (不具合).md"
source_filename: "可変速 (不具合).md"
onenote_id: "a8c15103-95f4-4d08-897a-403d412bffb5:159"
related_ids: []
attachment_paths:
  - "不具合対応【ELV】/現象（不具合対応）/OneNote/可変速 (不具合) image.png"
  - "不具合対応【ELV】/現象（不具合対応）/OneNote/可変速 (不具合) image 1.png"
reference_links: []
document_references: []
evidence_sources:
  - source_id: "evidence-elv-variable-speed-original"
    source_type: "vault_original"
    title: "可変速（不具合）（原文）"
    source_path: "不具合対応【ELV】/現象（不具合対応）/可変速 (不具合).md"
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-01"
    supports:
      - "UP/DN時の速度差、秤値に関する原因仮説、FMS後の原文記録"
  - source_id: "evidence-elv-variable-speed-weighing-offset"
    source_type: "vault_original"
    title: "秤自動オフセット補正の説明図"
    source_path: "不具合対応【ELV】/現象（不具合対応）/OneNote/可変速 (不具合) image.png"
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-04"
    supports:
      - "秤出力とパラメータ書込み値の差、低速階高書込み運転時の自動オフセット補正の説明"
      - "個別事例の原因確定や現行FMS適用条件は裏付けない"
  - source_id: "evidence-elv-variable-speed-manual-display"
    source_type: "vault_original"
    title: "手動優先モード表示例"
    source_path: "不具合対応【ELV】/現象（不具合対応）/OneNote/可変速 (不具合) image 1.png"
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-04"
    supports:
      - "中間位置で速度・位置等を確認する表示モードの画面項目例"
      - "スイッチ値や操作手順の現行適用性は裏付けない"
structured_data:
  equipment: "LINKs エレベーター（原文記載）"
  symptom: "NLで可変速の設計速度値に達しない事象。DNでは設計速度値、UPでは基準値より大きい値を測定したと記載。"
  cause: "秤値の差による負荷誤認識の可能性を原文が仮説として提示。"
  verified_actions: []
  outcome: "スローFMS後、UP/DNの無負荷時に設計速度値で動作良好と原文に記載。"
  source_notes:
    - "秤装置の勝手、ロープアンバランス、傾斜センサーばらつき等は原文中の推測・疑問で、原因確定ではない。"
    - "FMSの適用条件、測定値、承認記録は未確認。"
    - "原文は添付画像2点を参照している。過去の内容確認記録では秤自動オフセット補正の説明と手動優先モードの表示例を含むが、2026-10-07時点で指定パスに画像実体がなく再検証できない。"
---

# エレベーター可変速時の速度差に関する不具合メモ

## 事象

原文は、負荷試験時にNLで可変速の設計速度値に達せず、DNでは設計速度値、UPでは基準値より大きい値を測定したと記録している。

## 原文の原因仮説と結果

原文は、UP/DN間で秤値に差が生じ、負荷を誤認識した可能性を仮説としている。原因候補としてロープアンバランス、秤装置の勝手、傾斜センサーのばらつき等を挙げるが、確定原因ではない。

スローFMSの秤オフセット機能を使用した後は、UP/DNの無負荷時に設計速度値で動作良好と記載されている。適用条件と正式な作業記録は未確認。

添付図版は、秤出力値がパラメータ書込み値と異なる可能性と、スローでの階高書込み時に秤のオフセット補正を行う説明を示す。原因仮説を裏付ける一般法則ではなく、当該事例の説明として扱う。もう1点は、中間位置で速度・位置などを確認する手動優先モードの表示例であり、現行の測定手順を示すものではない。

## 概略確認フロー（調整手順ではない）

対象機・運転方向・負荷条件を記録し、速度差と秤値差の関係を承認済み資料で確認する。FMSの適用条件と測定方法を担当者に照合し、画像の表示例や原因仮説だけで秤設定・速度調整を行わない。

## 出典

- 原文ノート: [[不具合対応【ELV】/現象（不具合対応）/可変速 (不具合)]]
- 原文は添付画像2点を参照。2026-10-07時点で指定パスに実ファイルを確認できず、過去の内容確認記録を再検証できない。設定値・測定手順は転載していない。
- レビュー前の事例メモであり調整手順ではない。