---
schema_version: 1
record_id: "elv-ucmp-error-handling"
record_version: 4
title: "エレベーターUCMP異常に関する原文記述"
category: "不具合対応(ELV)"
record_type: "troubleshooting_case"
product: "エレベーター"
model_type:
  - "VFGH"
  - "VFGLF"
document_number: ""
revision: ""
effective_date: ""
review_status: "in_review"
publication_status: "not_published"
classification: "unknown"
cloud_approval: "not_reviewed"
keywords:
  - "UCMP"
  - "戸開走行保護装置"
  - "SS_DKC"
  - "712"
  - "C11"
source_path: "不具合対応【ELV】/エラー/戸開走行保護装置（UCMP）に関するエラー.md"
source_filename: "戸開走行保護装置（UCMP）に関するエラー.md"
onenote_id: "a8c15103-95f4-4d08-897a-403d412bffb5:131"
related_ids:
  - "elv-axiez-links-ucmp-braking-distance-unavailable-id57"
  - "elv-axiez-links-independent-auto-ucmp-cpu-fault-id79"
attachment_paths:
  - "不具合対応【ELV】/エラー/OneNote/戸開走行保護装置（UCMP）に関するエラー image.png"
  - "不具合対応【ELV】/エラー/OneNote/戸開走行保護装置（UCMP）に関するエラー image 1.png"
  - "不具合対応【ELV】/エラー/OneNote/戸開走行保護装置（UCMP）に関するエラー image 2.png"
reference_links: []
document_references:
  - document_number: "C-7-F2900.1-J"
    title: "VFGH方式エレベーター据付調整資料"
    locator: ""
    source_path: ""
  - document_number: "C-7-C3900-J"
    title: "機械室レスエレベーター電気システム据付調整資料"
    locator: ""
    source_path: ""
  - document_number: "菱技ノート第3201号"
    title: "VFGLFエレベーター技術研修資料"
    locator: "ID204がCPU/UCMPリセット情報の参照先として記載。本文・版未確認"
    source_path: ""
evidence_sources:
  - source_id: "evidence-elv-ucmp-original"
    source_type: "vault_original"
    title: "戸開走行保護装置（UCMP）に関するエラー（原文）"
    source_path: "不具合対応【ELV】/エラー/戸開走行保護装置（UCMP）に関するエラー.md"
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-01"
    supports:
      - "UCMP異常時の原文説明と参照資料"
  - source_id: "evidence-elv-ucmp-reset-vfgh"
    source_type: "vault_original"
    title: "VFGH資料のUCMP関連図版"
    source_path: "不具合対応【ELV】/エラー/OneNote/戸開走行保護装置（UCMP）に関するエラー image.png"
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-04"
    supports:
      - "VFGH資料図版にHANDモードでのCPU電源リセットの記載があること"
      - "図版にUCMP関連を含むエラーコード表があること"
  - source_id: "evidence-elv-ucmp-reset-vfglf"
    source_type: "vault_original"
    title: "VFGLF資料のUCMP関連図版"
    source_path: "不具合対応【ELV】/エラー/OneNote/戸開走行保護装置（UCMP）に関するエラー image 2.png"
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-04"
    supports:
      - "VFGLF参照資料の図版にHAND/ED保持時間とリセット前の故障確認条件が記載されていること"
      - "独立UCMP-CPU異常検出コード614の記載と関連条件"
  - source_id: "evidence-list-vfglf-cpu-ucmp-reset-id204"
    source_type: "vault_original"
    title: "首都工・不具合情報共有リスト: VFGLFのCPU/UCMPリセットに関する記載（ID204）"
    source_path: "首都工・不具合情報共有リスト.xlsx"
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-14"
    supports:
      - "VFGLFのCPU電源状態とUCMPエラーラッチ復帰条件に関する原リスト記載があること"
      - "菱技ノート第3201号が参照されていること"
structured_data:
  error_codes:
    - code: "712,C11"
      meaning: "原文はSS_DKCとして記載"
      condition: "ドアゾーン外で停止中に#29がOFFになった場合の説明"
    - code: "614"
      meaning: "独立UCMP-CPU異常検出（添付図版記載）"
      condition: "添付図版に関連条件の説明がある。対象機への適用は参照資料で要確認"
  verified_actions: []
  source_notes:
    - "原文はUCMP異常がエラーラッチすると記載し、HAND/EDモードでのリセットに言及。手順・適用条件は承認済み資料で未照合。"
    - "#29と#41回路の接続に関する説明は原文記載。添付画像と参照資料本文は未確認。"
    - "原文は添付3点を参照している。過去の内容確認記録ではVFGHとVFGLFの条件差が記録されているが、2026-10-07時点で指定パスに画像実体がなく再検証できない。"
    - "VFGLF図版にはHAND/EDを10秒超継続する条件、該当機器故障がないことの確認、およびコード614の説明がある。具体操作の指示としては使用しない。"
    - "一次リストID204は、かごへアクセスできない場合のVFGLF CPU電源状態とUCMPエラーラッチ復帰条件を記載する。状態遷移、具体操作、時間値は転載せず、現行手順として扱わない。"
---

# エレベーターUCMP異常に関する原文記述

## 原文の記述

- VFGH方式・VFGLF方式の資料を参照先として記載。
- UCMP異常処理プログラムにより、対象エラーがラッチすると説明している。
- 原文は保守点検による復帰が必要との説明、HAND/EDモードでのリセットに言及している。
- ドアゾーン外で停止中に#29がOFFとなる場合、SS_DKC（コード712,C11）が検出される仕組みを説明している。
- 過去の内容確認記録では、添付図版にVFGHとVFGLFの条件差および独立UCMP-CPU異常検出コード614が記録されている。2026-10-07時点で画像実体を再確認できないため、条件・コードの現物照合が必要。

## CPU/UCMPリセットに関する別出典（リストID204）

一次リストID204は、かごへアクセスできない状況でのVFGLF CPU電源状態とUCMPエラーラッチの復帰条件を記載し、「菱技ノート第3201号」を参照先として挙げる。モード間の状態遷移、操作順序、接続部・スイッチ操作および時間値は転載しない。参照資料本文・版、条件の正確性、現行適用は未確認であり、リセット・運転・安全装置の作業手順には使用しない。

## 重大な注意

### 概略確認フロー（操作手順ではない）

対象機種と適用資料を特定し、検出コード・発生条件・現在の故障状態を確認する。該当資料に記載された復帰前提を確認し、復帰操作は承認済み最新版と有資格担当者の指示に従う。VFGHとVFGLFの条件を相互に流用しない。

これは原文と図版の要点整理であり、リセット操作や回路操作の手順ではない。UCMP・安全回路に関する判断は承認済み最新版と有資格担当者の指示で確認すること。

## 出典

- 原文ノート: [[不具合対応【ELV】/エラー/戸開走行保護装置（UCMP）に関するエラー]]
- 原文は添付3点を参照。2026-10-07時点で指定パスに実ファイルを確認できず、過去の内容確認記録を再検証できない。具体的なリセット操作は転載していない。
- [[ELV_AXIEZ-LINKS_UCMP制動距離確認不能_ID57事例]]はAXIEZ-LINKSの別個の制動距離確認事例。UCMPという共通テーマで関連付けるが、本記録のVFGH/VFGLFのエラー説明とはモデル範囲・事象が異なる。
- [[ELV_AXIEZ-LINKS独立自動時UCMP故障検出_ID79事例]]はAXIEZ-LINKSの電源喪失後の独立UCMP-CPU故障検出報告。コード614に共通点があるが、本記録のVFGH/VFGLFとは検出条件・適用範囲が異なる。