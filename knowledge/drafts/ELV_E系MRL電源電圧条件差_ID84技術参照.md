---
schema_version: 1
record_id: "elv-e-series-mrl-supply-voltage-conditions-id84"
record_version: 1
title: "E系MRLの電源電圧条件と資料間差異（ID84）"
category: "現場担当業務"
record_type: "technical_reference"
product: "エレベーター"
model_type:
  - "KE-LG"
  - "KE-*F（原文表記）"
document_number: ""
revision: ""
effective_date: ""
review_status: "in_review"
publication_status: "not_published"
classification: "unknown"
cloud_approval: "not_reviewed"
keywords:
  - "E系MRL"
  - "電源電圧"
  - "受電電圧"
  - "製品裕度"
  - "工事試験報告書"
source_path: "現場担当業務/据付初期/本設電源への切り替え.md"
source_filename: "本設電源への切り替え.md"
onenote_id: "c3cbdf09-d13b-4aa5-9561-35eec9fc56a6:183"
related_ids: []
attachment_paths: []
reference_links: []
document_references:
  - document_number: "S-91-A-EG-A040-J"
    title: "KE-LG用資料（原文参照。本文・版・適用性未確認。）"
    locator: ""
    source_path: ""
  - document_number: "S-91-A-EF-A002-J"
    title: "AXIEZ容量拡張資料（原文参照。本文・版・適用性未確認。）"
    locator: ""
    source_path: ""
  - document_number: "S-91-A-EF-C030-J"
    title: "AXIEZ用資料（原文参照。本文・版・適用性未確認。）"
    locator: ""
    source_path: ""
  - document_number: ""
    title: "【作成中】勉強会資料_250605.pdf（原文が示すSharePoint添付参照。未閲覧。）"
    locator: ""
    source_path: ""
evidence_sources:
  - source_id: "evidence-vault-e-series-mrl-voltage-note-183"
    source_type: "vault_original"
    title: "本設電源への切り替え（OneNote由来原資料）"
    source_path: "現場担当業務/据付初期/本設電源への切り替え.md"
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-09"
    supports:
      - "E系MRLの客先要求値、製品裕度、工事試験報告書基準との差、品質保証に関する説明と対応記載"
  - source_id: "evidence-list-e-series-mrl-voltage-id84"
    source_type: "user_provided_extract"
    title: "首都工・不具合情報共有リスト: 【品質記録確認】E系MRLの電源電圧について（ID84）"
    source_path: ""
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-09"
    supports:
      - "原資料と重なる電圧条件・基準の説明、および2024-12-04付記表示"
structured_data:
  specifications:
    - name: "客先要求電圧として記載された範囲"
      value: "200V系: 200～220; 400V系: 380～440"
      unit: "V"
      condition: "原文はE系MRLのKE-LG、KE-*Fについて記載。要求の現行性・個別機種への適用は未確認。"
    - name: "電圧変動と相間不平衡に関する記載"
      value: "電圧変動 +5%～-10%以内; 相関での不平効率 5%"
      unit: "%"
      condition: "原文表記を保持。変動の基準値、相間不平衡の定義、および記載の正確性は未確認。"
    - name: "200V系の製品裕度として示された範囲"
      value: "180～231"
      unit: "V"
      condition: "原文は受電電圧の許容値として説明。製品裕度の説明であり、運転許可値・引渡し基準ではない。400V系の対応範囲は記載なし。"
    - name: "工事試験報告書に記載された基準としての引用"
      value: "定格電圧 ±5%; 相間 3%"
      unit: "%"
      condition: "原資料の引用・主張。報告書本文、定義、現行性、適用範囲は未確認。"
    - name: "IDS要求として説明された電圧条件"
      value: "200Vまたは400Vの定格電圧 ±5%"
      unit: "%"
      condition: "原文中の稲電・三菱の見解として記載。IDS本文・版・現行適用は未確認。"
  source_notes:
    - "原資料は、製品が耐え得る条件と品質を担保できる条件は異なるとの見解を紹介し、製品裕度範囲内でも使用継続により寿命が短くなる恐れを述べる。これは原文上の説明で独立確認していない。"
    - "原資料は、資料間に差異があり稲電から明確な指示がないと記録する一方、電圧が基準外と判明した場合は営設へ相談し、官検日まで待たず対応を検討するよう記載する。承認済み現行手順とは確認できていない。"
    - "Excel抜粋には2024-12-04付記表示がある。確認したVault原ノートでは当該付記を確認できず、付記の内容・作成者・原資料との対応は未確認。"
    - "SharePoint参照URLと認証付きパラメーターは複写していない。参照先資料・添付PDFは未閲覧。"
---

# E系MRLの電源電圧条件と資料間差異（ID84）

## 概要・適用範囲

首都工・不具合情報共有リストID84とOneNote由来の「本設電源への切り替え」には、E系MRL（KE-LG、KE-*Fと原文表記）の電源電圧について、客先要求値、製品裕度、工事試験報告書の基準、品質保証上の見解が記載されている。本記録は資料上の記述と相違を整理したもので、現行仕様、受電設備の判定、引渡し可否を決める基準や実作業指示ではない。

## 原文に記載された数値

| 項目 | 原文記載 | 条件・確認状態 |
|---|---|---|
| 客先要求電圧 | 200V系: 200～220V、400V系: 380～440V | E系MRLのKE-LG、KE-*Fについての記載。現行性・個別適用未確認。 |
| 電圧変動 | +5%～-10%以内 | 基準電圧や適用条件は原文だけでは確定できない。 |
| 相間不平衡 | 「相関での不平効率は5%」 | 原文の表記を保持。用語の意味・定義は要確認。 |
| 200V系の製品裕度 | 180～231V | 原文は受電電圧の許容範囲として説明するが、製品裕度の説明であり、運転許可値や引渡し基準とはしていない。400V系の裕度範囲は記載されていない。 |
| 工事試験報告書の基準として引用 | 定格電圧±5%、相間3% | 報告書本文・現行性・適用範囲は未確認。 |
| IDS要求としての説明 | 200Vまたは400Vの定格電圧±5% | 原資料中の見解。IDS本文・版・現行適用は未確認。 |

## 資料間の差と見解

原資料は、客先に要求する電圧、製品が耐え得る裕度、品質を担保できる範囲を区別している。製品裕度として示された値を、要求値や検査基準の代わりに使わないよう説明し、裕度上限付近での継続使用には製品寿命への懸念があるとの見解を記録している。これらは原資料上の主張で、独立した技術確認ではない。

同じノートは「定格±5%・相間3%」を守る必要があると述べる一方、資料間に差があり、明確な指示がないとも記録する。電圧基準外が判明した際に営設へ相談し、官検日まで待たず対応を検討するとの記載もあるが、現行の承認済み手順かは未確認である。本記録だけで数値の優先順位、合否、継続使用、引渡し判断を決めない。

## 参照資料と未確認事項

原資料はS-91-A-EG-A040-J（KE-LG用）、S-91-A-EF-A002-J（AXIEZ容量拡張）、S-91-A-EF-C030-J（AXIEZ用）および作成中の勉強会PDFを参照する。各資料の本文・改訂・対象機適用性は未確認であり、根拠確認済み資料とは扱わない。元ノートに含まれるSharePoint URLはアクセス情報を含むため転載していない。

Excel抜粋には2024-12-04付記表示があるが、確認したVault原ノートでは同付記を確認できず、その内容・作成者・反映範囲は未確認である。原ノートとExcelの差異を解消済みとは扱わない。

## 出典・確認履歴

- 原資料: [[現場担当業務/据付初期/本設電源への切り替え]]（OneNote ID `c3cbdf09-d13b-4aa5-9561-35eec9fc56a6:183`）および首都工・不具合情報共有リストExcel出力ID84
- 確認状態: Vault原ノート本文とExcel指定列を確認。参照資料本文、数値の定義、改訂、現行適用、技術・品質レビューは未確認。
- 原本変更・AWS/S3送信: なし。
