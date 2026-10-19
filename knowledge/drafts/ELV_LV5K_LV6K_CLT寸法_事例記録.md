schema_version: 1
record_id: "elv-lv5k-lv6k-clt-dimension-acceleration-case"
record_version: 1
title: "LV5K/LV6KのCLT寸法と戸閉終端の挙動に関する事例"
category: "不具合対応(ELV)"
record_type: "troubleshooting_case"
product: "エレベーター"
model_type: ["LV5K-CO/2S", "LV6K-CO/2S/SS/2CO"]
document_number: ""
revision: "首都工・不具合情報共有リスト記載。原本資料・版は未確認"
effective_date: ""
review_status: "in_review"
publication_status: "not_published"
classification: "unknown"
cloud_approval: "not_reviewed"
keywords: ["CLT", "OLT", "戸閉終端", "LV5K", "LV6K", "加速様挙動"]
source_path: ""
source_filename: "技術情報リスト.xlsx"
onenote_id: ""
related_ids: ["catalog-elv-olt-clt-position-adjustment-reference", "catalog-elv-car-door-failures-reference"]
attachment_paths: []
reference_links: []
document_references: []
evidence_sources:
  - source_id: "evidence-elv-clt-dimension-spreadsheet-id432"
    source_type: "user_provided_extract"
    title: "首都工・不具合情報共有リスト: LV5K/LV6Kドア適用現場におけるCLT寸法の設定基準について"
    source_path: ""
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-09"
    locator: "リストID 432（Excel出力のID欄）。資料番号ではない"
    supports:
      - "戸閉終端付近の加速様挙動、CLT寸法に関する記載、原文に記された制御説明と発生条件"
structured_data:
  symptom: "LV5K/LV6Kの対象戸型に関する事例として、CLTを全閉位置から5 mmとした状態で、戸閉終端付近に一時的に加速したように見える挙動が記録されている。"
  error_codes: []
  case_conditions:
    - "リスト本文に記載された対象: LV5K-CO/2S、LV6K-CO/2S/SS/2CO。"
    - "リストの機種欄は『全エレ機種』だが、本文の適用範囲は上記戸型に限られるため、全機種へ一般化しない。"
    - "戸閉力、クローザー力、ドアレール走行抵抗等の条件により発生し、CLTが5 mmでも必ず発生するとは限らないと記載。"
  cause: "リスト記載は、CLT検知後約2 mmの位置で速度制御から位置制御へ切り替わり、CLTを5 mmとした場合は切替えが早まるため、制御上のブレーキ力が小さくなりクローザーの戸閉力が優位になることが、終端付近で加速したように見える挙動につながり得ると説明している。機械・制御上の因果は独立検証していない。"
  source_reported_dimensions:
    - name: "CLT"
      value: "全閉位置から3～4 mm"
      condition: "リスト本文に記載された対象戸型の基準値。現行仕様・測定基準・許容差として未確認"
    - name: "OLT"
      value: "全開位置から5±1 mm"
      condition: "リスト本文に記載された対象戸型の値。現行仕様・測定基準として未確認"
    - name: "ゲートスイッチ形状によるCLT寸法の違い"
      value: "通常型、アクチュエーター型（DS-131）のいずれもCLTは全閉位置から3～4 mmと記載"
      condition: "リスト本文の記載。対象戸型・現行仕様の独立確認は未実施"
  verified_actions: []
  outcome: "リスト事例ではCLT寸法を全閉位置から3～4 mmへ是正後に不自然な挙動が解消したと報告されている。独立検証済みの結果ではない。"
  source_notes:
    - "数値、制御説明、是正後の結果は首都工・不具合情報共有リストの一事例に由来し、現行の承認済み調整基準・作業手順・合否基準として使用しない。"
    - "戸型名とリストの機種欄に適用範囲の不一致がある。本文に明記された戸型を記録し、『全エレ機種』とは扱わない。"
    - "Excelの参考資料欄は空欄。類似するVault内共有リストのリンク先や、資料番号C-18-A9-491.1-Jの本文を本事例の根拠としていない。"
---

# LV5K/LV6KのCLT寸法と戸閉終端の挙動に関する事例

## 事例の要点

首都工・不具合情報共有リストから出力されたExcelには、LV5K/LV6Kの対象戸型でCLTを全閉位置から5 mmとしていた際、戸閉終端付近に一時的な加速のように見える挙動が発生した例が記録されている。CLTを3～4 mmへ是正した後に解消したと報告されているが、これは独立検証済みの手順・結果ではない。

## 原文に記載された説明と寸法

原文は、CLT検知から約2 mmの位置で制御モードが切り替わること、CLTを5 mmとした場合に切替えが早まり、制御上のブレーキ力よりクローザーの戸閉力が優位となる場合があることを原因説明としている。この説明の技術的妥当性や適用条件は独立確認していない。

| 項目 | リスト本文の記載 | 留意点 |
| --- | --- | --- |
| CLT | 全閉位置から3～4 mm | 対象戸型に関する原文値。現行仕様・測定方法・許容差は未確認 |
| OLT | 全開位置から5±1 mm | 対象戸型に関する原文値。現行仕様・測定方法は未確認 |
| ゲートスイッチ形状 | 通常型とアクチュエーター型（DS-131）のいずれもCLT 3～4 mmと記載 | 本文に記載された適用範囲に限定 |

原文はクローザー戸閉力やドアレール走行抵抗等により発生条件が異なり、CLTが5 mmでも必ず発生するわけではないとしている。

## 適用範囲と出典上の不一致

リストの機種欄は「全エレ機種」だが、本文で挙げる戸型はLV5K-CO/2SおよびLV6K-CO/2S/SS/2COである。本記録では本文の具体的な戸型を保持し、全機種へ適用を拡張しない。リストID 432はExcel出力のID欄にある出典追跡用識別子であり、資料番号ではない。

本記録は事例の検索・照合用であり、調整方法、測定方法、許容差、故障判定、現行の作業指示を示さない。実設備への適用は、対象機種・戸型の現行承認済み資料と責任者の確認を要する。
