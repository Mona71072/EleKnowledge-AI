---
schema_version: 1
record_id: "knowhow-elv-axiez-links-short-oh-cwt-runby-id163"
record_version: 1
title: "AXIEZ-LINKsの短OH条件とCWTランバイ区分に関する注意（ID163）"
category: "技術メモ【ELV】２"
record_type: "knowhow"
product: "エレベーター"
model_type: ["AXIEZ-LINKS"]
document_number: ""
revision: ""
effective_date: ""
review_status: "in_review"
publication_status: "not_published"
classification: "unknown"
cloud_approval: "not_reviewed"
keywords:
  - "AXIEZ-LINKS"
  - "短OH"
  - "CWTランバイ"
  - "MIN.OH"
  - "品目表"
source_path: "首都工・不具合情報共有リスト.xlsx"
source_filename: "首都工・不具合情報共有リスト.xlsx"
onenote_id: ""
related_ids: []
attachment_paths: []
reference_links: []
document_references:
  - document_number: "S-91-A-EG-D30"
    title: "営業設計資料（原リスト表記。正式題名未確認）"
    locator: "必要オーバーヘッドMIN.OHの参照資料としてID163に記載。本文・版未確認"
    source_path: ""
evidence_sources:
  - source_id: "evidence-list-elv-axiez-short-oh-cwt-runby-163"
    source_type: "vault_original"
    title: "首都工・不具合情報共有リスト: AXIEZ-LINKs 短OH対応によるおもりランバイ基準外（ID163）"
    source_path: "首都工・不具合情報共有リスト.xlsx"
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-14"
    supports:
      - "MIN.OHの記載を通常OH条件と解釈した後、技評で短OH対応と分かりCWTランバイが基準外とされた経緯"
      - "MIN.OHの導出条件により品目表の同一表記が異なる意味を持つとの説明"
      - "対応状況欄が完了である一方、変更内容と変更後確認が記載されていないこと"
  - source_id: "evidence-vfglf-pit-runby-original"
    source_type: "vault_original"
    title: "総点（VFGLB・VFGLF）/ピット/ランバイ（原文）"
    source_path: "総点（VFGLB・VFGLF）/ピット/ランバイ.md"
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-14"
    supports:
      - "VFGLF向け総点原文に短OH時の注意が記載されていること。ID163のAXIEZ-LINKSへの適用根拠ではない"
structured_data:
  knowledge_items:
    - topic: "MIN.OHの導出条件とCWTランバイ区分"
      statement: "ID163では、品目表のMIN.OH表記だけから通常OH条件と判断したところ、技評確認で別の短OH対応条件と分かり、CWTランバイが基準外とされた経緯を報告する。原リストの説明では、品目表のMIN.OHが示す値は、標準資料の必要値がそのまま記載されたものか、必要値を満たせない条件で個別計算されたものかにより意味が異なる。"
      conditions:
        - "本記録はID163のAXIEZ-LINKSに関する出典記載であり、個別現場の設計条件を示すものではない。"
        - "原リストは、必要オーバーヘッドを確保できず詳細計算が行われる場合に、品目表のMIN.OH欄が計算値を示すことがあると説明する。"
      exceptions:
        - "寸法閾値、ランバイ値、許容差、個別設定値は記録しない。"
        - "現行の適用条件、設計承認、是正内容、設定後の確認結果は未確認。"
      rationale: "原リストは、重りバッファ接触時にかごが昇降路天井へ衝突する危険を避ける目的で短OH対応を説明している。"
      verification_status: "source_recorded"
      evidence_source_ids:
        - "evidence-list-elv-axiez-short-oh-cwt-runby-163"
  source_notes:
    - "ID163の対応状況欄は完了だが、具体的な是正内容および是正後のランバイ確認は記載されていない。"
    - "総点（VFGLB・VFGLF）/ピット/ランバイ.mdにも短OH注意があるがVFGLF向けであり、機種範囲が異なるためID163の適用根拠としていない。"
    - "参照先S-91-A-EG-D30の本文・版・現行性は未確認。本記録は設計・設定・施工・検査の判断や作業指示に使用しない。"
---

# AXIEZ-LINKsの短OH条件とCWTランバイ区分に関する注意（ID163）

## 出典記載の要点

首都工・不具合情報共有リストID163は、品目表のMIN.OH表記を通常OH条件と判断してCWTランバイを設定した後、技評確認で短OH対応と判明し、設定が基準外だった事例を報告する。原リストは、必要オーバーヘッドを満たせず個別計算する条件では、品目表のMIN.OH欄に計算値が記載される場合があり、標準資料の値がそのまま記載される場合と同じ意味ではないと説明している。

原リストは短OH対応の理由として、重りバッファ接触時にかごが昇降路天井へ衝突する危険の回避を挙げる。これは出典の説明であり、現行の設計根拠や個別設備の安全確認を裏付けるものではない。寸法閾値、ランバイ値、許容差、具体設定、確認操作は掲載しない。

## 対応状況と適用上の注意

対応状況欄は完了だが、設定是正の具体的内容と是正後確認は記載されていない。参照資料S-91-A-EG-D30の本文・版・現行性、設計承認、個別設備への適用も未確認であり、本記録を設計・設定・施工・検査判断や作業指示に使わない。

既存の「総点（VFGLB・VFGLF）/ピット/ランバイ.md」にも短OH時の注意があるが、VFGLF向けで対象機種が異なるため、本件の根拠や適用指示には扱わない。

## 出典

- 首都工・不具合情報共有リスト.xlsx、ID163（sheet1 row260）。
- `総点（VFGLB・VFGLF）/ピット/ランバイ.md` は別機種範囲の既存原文として照合。ID163の根拠には用いていない。