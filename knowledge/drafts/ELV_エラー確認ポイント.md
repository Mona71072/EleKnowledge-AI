---
schema_version: 1
record_id: "elv-error-check-points"
record_version: 4
title: "エレベーター不具合時のエラー確認ポイント"
category: "不具合対応(ELV)"
record_type: "catalog"
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
  - "エラー確認"
  - "7SEG"
  - "制御エラー"
  - "各台管理"
  - "群管理"
source_path: "不具合対応【ELV】/エラー/エラー確認時のポイント.md"
source_filename: "エラー確認時のポイント.md"
onenote_id: "a8c15103-95f4-4d08-897a-403d412bffb5:122"
related_ids:
  - "elv-7seg-led-status"
  - "elv-vfgh-error-codes"
  - "elv-individual-control-error-codes"
  - "elv-group-control-error-codes"
attachment_paths:
attachment_paths: []
reference_links: []
document_references:
  - document_number: "C-7-C3900-J"
    title: "機械室レスエレベーター電気システム据付調整資料"
    locator: "P.45"
    source_path: ""
evidence_sources:
  - source_id: "evidence-elv-error-check-points-original"
    source_type: "vault_original"
    title: "エラー確認時のポイント（原文）"
    source_path: "不具合対応【ELV】/エラー/エラー確認時のポイント.md"
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-01"
    supports:
      - "表示・制御・各台・群管理の確認先と原文の案内"
  - source_id: "evidence-elv-error-category-index"
    source_type: "vault_original"
    title: "エラー"
    source_path: "不具合対応【ELV】/エラー.md"
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-08"
    supports:
      - "制御盤エラーと各台管理エラーを両方確認するよう促す案内"
  - source_id: "evidence-elv-error-check-short-circuit-table"
    source_type: "vault_original"
    title: "安全回路短絡ピンの図表"
    source_path: "不具合対応【ELV】/エラー/OneNote/エラー確認時のポイント image.png"
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-04"
    supports:
      - "安全回路関連の短絡ピン・電圧・用途を載せた図表があること。具体値・操作は転載しない"
  - source_id: "evidence-elv-error-check-cabin-display"
    source_type: "vault_original"
    title: "カゴ内エラー表示の参照図"
    source_path: "不具合対応【ELV】/エラー/OneNote/エラー確認時のポイント image 1.png"
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-04"
    supports:
      - "カゴ内表示器・基板7SEGの表示確認に関する参照例"
      - "画面モード・エラーコードの詳細は機種別資料の確認が必要"
  - source_id: "evidence-elv-error-check-operation-class"
    source_type: "vault_original"
    title: "7SEG動作分類表"
    source_path: "不具合対応【ELV】/エラー/OneNote/エラー確認時のポイント image 2.png"
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-04"
    supports:
      - "7SEG表示コードと動作分類の対応例。対象機の現行適用性は未確認"
  - source_id: "evidence-list-three-digit-error-view-077"
    source_type: "user_provided_extract"
    title: "首都工・不具合情報共有リスト: 3桁エラーの見分け方（ID77）"
    source_path: ""
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-09"
    supports:
      - "3桁エラーの各桁の意味、中央桁の重篤度に関する一般化、重篤エラーの優先確認を勧める原文上の見解"
structured_data:
  items:
    - item: "状態表示"
      detail: "P1基板上の7SEGで安全回路、自動/手動、コンバータ異常、戸開閉、UP/DN指令を確認する案内。"
    - item: "制御エラー"
      detail: "機種別制御エラー一覧と、コンバータ基板状態表示への参照。"
    - item: "各台管理エラー"
      detail: "カゴ通信、カゴドア、センサー、通信、管制運転等に関係する場合の確認先として記載。"
    - item: "群管理エラー"
      detail: "群管理、管制運転、監視盤に関係する場合の確認先として記載。"
    - item: "3桁エラーの見方（原文説明・適用未確認）"
      detail: "リストID77と原文ノートは、百の位を大分類、十の位を重篤度、一の位を小分類と説明する。十の位が小さいほど重症で、3以下なら自動で動かない状態と認識するよう記載。また自動でかごが動かない場合、4/5系より1/3系の原因を先に確認する案を述べる。機種共通の体系・閾値・優先順位として独立確認していない。"
  source_notes:
    - "原文は制御エラーと各台エラーの双方を確認するよう案内。承認済み故障診断手順との照合は未実施。"
    - "3桁エラーの重篤度等に関する説明は原文記載であり、画像・外部リストを含む最新版の確認は未実施。"
    - "原文は添付画像3点を参照している。過去の内容確認記録ではカゴ内表示例、7SEG動作分類表、安全回路短絡ピン表を含むが、2026-10-07時点で指定パスに画像実体がなく再検証できない。"
    - "原文は添付画像3点を参照している。過去の確認記録にはカゴ内表示例、7SEG動作分類表、安全回路短絡ピン表の内容記録がある。2026-10-09の指定フォルダー・カテゴリ共通OneNoteフォルダー・添付画像フォルダー・Vault画像名検索では該当ファイルを確認できず、現在の再照合はできないためattachment_pathsには登録しない。"
    - "安全回路短絡表には具体的なピン番号・電圧・用途があるが、短絡操作への転用を避けるため参照MDへ転載しない。"
    - "画像中の表示コード・分類表は対象機の承認済み最新版で適用を確認する。"
    - "リストID77は原文ノートの3桁エラー説明と対応する追加入力。桁の意味・重篤度・自動運転可否・原因確認の優先案は、共有リスト上の説明/見解であり、全機種共通の公式ルールや承認済み診断優先順位として独立確認していない。"
  safety_warnings:
    - "添付画像に安全回路を短絡するピン・電圧表がある。画像や本参照MDを短絡操作の指示に使用しない。安全回路の確認は承認済み手順と有資格担当者に従う。"
---

# エレベーター不具合時のエラー確認ポイント

## 原文の案内

- P1基板の7SEG表示から、安全回路、自動/手動、コンバータ異常、戸開閉、UP/DN指令等の状態を確認する。
- 親ページ「エラー」と子ページ「エラー確認時のポイント」の双方が、制御エラーと各台管理エラーを併せて確認するよう案内している。
- ドア駆動、コンバータ、群管理・監視盤等に関係する場合の個別確認資料を案内している。
- カゴ内リモコンでエラーを確認する記述があり、参照資料としてC-7-C3900-J P.45を挙げている。
- 原文ノートおよび共有リストID77は、百の位を大分類、十の位を重篤度、一の位を小分類と説明し、十の位が小さいほど重症で3以下なら自動で動かない状態と認識するよう記載する。さらに、自動でかごが動かない場合に4/5系より1/3系の原因を先に確認する案を示す。これらは共有元の説明・見解で、コード体系、閾値、全機種への適用、診断優先順位は未確認。
- 添付図版はカゴ内表示器・基板7SEGの確認方法や動作分類表を含む。表示コードの適用は対象機の最新版資料で確認する。

## 概略確認フロー（診断手順ではない）

対象機と発生時の表示を特定し、カゴ内表示・基板7SEG・制御エラー・各台管理エラーなど目的に合う確認先を選ぶ。原文は制御エラーと各台エラーを併せて確認するよう案内している。コードの意味と重篤度は対象機に適用する承認済み一覧で照合し、回路操作は行わず担当者へ確認する。

共有リストID77の重篤度と優先確認に関する説明は、未検証の一般論である。対象機の承認済みエラー一覧や正式な診断優先順位の代用にしない。

## 出典・確認履歴

- 原文ノート: [[不具合対応【ELV】/エラー/エラー確認時のポイント]]
- 原文は添付画像3点を参照。2026-10-09の指定フォルダー・カテゴリ共通OneNoteフォルダー・添付画像フォルダー・Vault画像名検索では実ファイルを確認できず、過去の画像内容確認を再検証できない。短絡ピン表の具体値は転載していない。
- 診断の正式手順ではない。安全・技術レビュー前のドラフト。