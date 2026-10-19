---
schema_version: 1
record_id: "case-elv-meld-contactor-damage-id167"
record_version: 1
title: "MELD接続時のコンタクタ焼損報告（ID167）"
category: "不具合対応(ELV)"
record_type: "troubleshooting_case"
product: "エレベーター"
model_type: ["MR機種"]
document_number: ""
revision: ""
effective_date: ""
review_status: "in_review"
publication_status: "not_published"
classification: "unknown"
cloud_approval: "not_reviewed"
keywords:
  - "MELD"
  - "コンタクタ損傷"
  - "地絡"
  - "活線作業リスク"
source_path: "首都工・不具合情報共有リスト.xlsx"
source_filename: "首都工・不具合情報共有リスト.xlsx"
onenote_id: ""
related_ids:
  - "elv-meld-operation-reference"
attachment_paths: []
reference_links: []
document_references: []
evidence_sources:
  - source_id: "evidence-list-elv-meld-contactor-damage-167"
    source_type: "vault_original"
    title: "首都工・不具合情報共有リスト: MELD の繋ぎ込み時、CP遮断をせずコンダクタが焼損した件（ID167）"
    source_path: "首都工・不具合情報共有リスト.xlsx"
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-14"
    supports:
      - "MELD関連接続時の地絡とコンタクタ損傷に関する原リストの説明"
      - "盤内作業を活線で行わないよう警告していること"
      - "対応状況欄と詳細記述の復旧状況が一致しないこと"
structured_data:
  equipment: "エレベーター"
  symptom: "MELD関連設備のコンタクタ損傷、制御表示の異常、およびリレーの断続動作があったとの報告。表示・動作の意味や原因は独立確認されていない。"
  error_codes: []
  cause: "一次リストは、MELD関連の接続時に地絡が発生し、コンタクタが損傷したと説明する。電源が遮断されていない状態だったとの記載もあるが、回路詳細・端子・電圧・因果関係は独立確認されていない。"
  verified_actions: []
  outcome: "対応状況欄は部品を手配し納品後に取り付け予定とする一方、詳細欄は別設備の部品と交換して不具合が解消したと記載する。実施時期、最終復旧状態、因果関係は不一致を解消できず未確認。"
---

# MELD接続時のコンタクタ焼損報告（ID167）

## 報告内容

首都工・不具合情報共有リストのID167は、MELD関連の接続時に地絡が発生し、コンタクタが損傷したと報告する。損傷後は制御表示の異常とリレーの断続動作があったとの記載がある。原因、表示の意味、設備状態はいずれも独立確認されていない。

対応状況欄には部品を手配し納品後に取り付ける予定とある一方、詳細欄には別設備の部品と交換して不具合が解消したと記載されている。実施時期と最終復旧状態は一致せず、確定できない。

## 安全上の注意

原リストは盤内作業を活線で行わないよう警告している。本記録は具体的な回路・端子・電圧・遮断箇所や接続/交換手順を示さない。盤内作業には所管部門の承認済み安全手順を適用し、原リストや本記録を作業指示・復旧判断に使用しない。

## 関連資料

- [[ELV_MELD動作参照]]: MELD関連の共有情報をまとめた参照記録。本件の原因や復旧結果を裏付ける資料ではない。

## 出典・確認状態

- 出典: `首都工・不具合情報共有リスト.xlsx`（ID167、sheet1 row256）。
- 原リストに画像添付の記載があるが、添付実体・内容・本文との対応は未確認。
- 地絡原因、損傷部位、作業状態、部品交換の実施/結果、設備の安全状態、現行適用性は未確認。電気・端子・測定・交換等の詳細は転載していない。
- 技術・電気・安全レビュー前の下書きであり、施工・検査・運転・復旧判断には使用しない。