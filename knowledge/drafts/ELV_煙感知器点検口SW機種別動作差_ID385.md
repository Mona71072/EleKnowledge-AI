---
schema_version: 1
record_id: "elv-smoke-detector-access-switch-model-behavior-id385"
record_version: 1
title: "煙感知器点検口スイッチの機種別動作差（ID385）"
category: "不具合対応(ELV)"
record_type: "technical_reference"
product: "エレベーター"
model_type:
  - "VFGLB"
  - "VFGLF"
document_number: ""
revision: ""
effective_date: ""
review_status: "in_review"
publication_status: "not_published"
classification: "unknown"
cloud_approval: "not_reviewed"
keywords:
  - "煙感知器点検口"
  - "点検口スイッチ"
  - "制御方式"
  - "戸回路"
source_path: ""
source_filename: "技術情報リスト（協力会社展開用）.xlsx"
onenote_id: ""
related_ids: []
attachment_paths: []
reference_links: []
document_references: []
evidence_sources:
  - source_id: "evidence-list-elv-smoke-detector-access-switch-385"
    source_type: "user_provided_extract"
    title: "協力会社展開用Excel: 煙感知器点検口SWの機種別動作差（ID385）"
    source_path: ""
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-13"
    supports:
      - "VFGLBとVFGLFについて煙感知器点検口SWに関する異なる動作説明が記載されていること"
structured_data:
  source_explanation: "原リストは制御方式の違いに関連づけ、点検口スイッチが開状態になった場合の制御動作がVFGLBとVFGLFで異なると説明する。"
  reported_difference: "原リスト上、VFGLBでは安全回路に関わる動作、VFGLFでは戸状態判定に関わる動作として記載され、それぞれ運転可否の現れ方が異なる。回路構成・現行機種適用は独立確認していない。"
  limitations:
    - "記載内容は共有リスト上の説明であり、機種別回路図、制御ソフト版、個別設備仕様との照合は未実施。"
    - "回路番号、端子/信号名、短絡・ジャンパー、運転操作、復帰/試験手順は転載しない。"
    - "本記録は安全回路や扉回路の判断、点検口スイッチの無効化、運転可否判断に使用しない。"
---

# 煙感知器点検口スイッチの機種別動作差（ID385）

首都工・不具合情報共有リストID385は、煙感知器点検口スイッチの開状態に対する制御動作がVFGLBとVFGLFで異なると説明している。原リストは、制御方式の違いに関連づけて、安全回路に関わる動作と戸状態判定に関わる動作を区別し、運転可否の現れ方が異なるとしている。

これは原リスト上の説明であり、機種別回路図、ソフトウェア版、物件仕様、現行設計との照合は未実施である。回路番号、端子/信号名、短絡による確認・復帰、運転操作などの手順は本記録に含めない。

本記録を安全回路・扉回路の診断、点検口スイッチの無効化、運転判断に使用しない。作業・判断には対象機種の承認済み現行図書と所管技術者の確認を要する。