schema_version: 1
record_id: "elv-temporary-power-s-phase-intermittent-connection-case"
record_version: 2
title: "仮設動力配線のS相接続不良による起動不能事例"
category: "不具合対応(ELV)"
record_type: "troubleshooting_case"
product: "エレベーター"
model_type: ["ME-CM"]
document_number: ""
revision: "首都工・不具合情報共有リスト記載。原本資料・版は未確認"
effective_date: ""
review_status: "in_review"
publication_status: "not_published"
classification: "unknown"
cloud_approval: "not_reviewed"
keywords: ["仮設動力", "S相", "接続不良", "起動不能", "B1基板", "E1基板"]
source_path: ""
source_filename: "技術情報リスト.xlsx"
onenote_id: ""
related_ids: ["elv-temporary-slow-issues"]
attachment_paths: []
reference_links: []
document_references: []
evidence_sources:
  - source_id: "evidence-elv-temporary-power-phase-case-id431"
    source_type: "user_provided_extract"
    title: "首都工・不具合情報共有リスト: 動力電源仮設配線ミスによるELV起動不能の件"
    source_path: ""
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-13"
    locator: "リストID 431（Excel出力のID欄）。資料番号ではない"
    supports:
      - "電源復旧後の起動不能と制御盤表示の記録、S相接続部の接触不安定、基板損傷の原文上の推定"
      - "初期調査、基板交換後も起動しなかった経過、後続対応後に起動可能となったとの進捗欄記載"
structured_data:
  symptom: "電源復旧後に自動/手動とも運転不能となった事例。Excelでは、制御盤7SEGのCFO、29、DN/UPコールが点灯し、D89は点灯しなかったと記録されている。"
  error_codes: []
  source_reported_error_field: "【011,012,131,631,64E】【311,312,34C,631】"
  cause: "原文は、仮設動力配線のS相接続部でジョイントスリーブが抜けかけており、S相が瞬間的に接続/未接続を繰り返した結果、過剰電流が発生してB1/E1基板を損傷したと思われる、と推定している。原因と基板損傷は独立検証されていない。"
  verified_actions: []
  outcome: "基板交換後およびS相接続部の再施工後も起動しなかったとされる。その後、モータブロワ不作動と関連保護スイッチのOFF状態が記録され、状態復帰後にELVが起動可能となったとの報告がある。報告結果、基板損傷との因果、復旧状態は独立確認されていない。"
  case_conditions:
    - "リストの機種欄はME-CM。"
    - "原文は仮設動力配線の接続不良と、S相接続部のジョイントスリーブが抜けかけていた状態を原因として記録。"
  source_notes:
    - "エラー表示、原因、過剰電流、B1/E1基板損傷はいずれもリスト記載の事例内容。エラーコードの意味、因果関係、基板損傷は未検証。"
    - "電源遮断・復旧等の実施記録は、再現・診断・作業手順として転記していない。"
    - "リストID 431は出典追跡用識別子であり、資料番号ではない。現場名・号機・共有者等は転記していない。"
---

# 仮設動力配線のS相接続不良による起動不能事例

## 事例の要点

ME-CMの事例として、電源復旧後に自動/手動とも運転できなくなった記録がある。制御盤7SEGではCFO、29、DN/UPコールが点灯し、D89は点灯しなかったと記載されている。表示の意味や判定方法は本記録では定義しない。

## 原文に記載された原因推定

原文は、仮設動力配線のS相接続部でジョイントスリーブが抜けかけ、接続/未接続を繰り返したことで過剰電流が生じ、B1/E1基板損傷に至ったと思われると説明している。これは一事例の原因推定であり、検証済みの一般原因ではない。

Excelのエラー欄には `【011,012,131,631,64E】【311,312,34C,631】` と記載されているが、コードの意味・発生順序・対象基板は未確認である。

進捗欄では、初期調査で制御盤の状態を確認し、電圧が投入後に低下したためB1/E1基板損傷を疑って手配したと記録されている。約2週間後の基板交換でも起動せず、追加調査で一次側動力電源のS相接続不良を確認したとされる。接続部の再施工後も直ちには起動しなかった。

後続調査ではモータブロワ不作動が記録され、BLWコンタクタが原因候補とされた。関連する過負荷保護スイッチがOFF状態だったこと、その状態の復帰後にELVが起動可能となったことが進捗欄に記載されている。個別の端子・測定・スイッチ操作手順は本記録に含めない。これらの調査内容・原因・対応後結果は、いずれもリスト上の報告であり独立確認されていない。

本記録は事例検索用であり、電源の遮断/復旧、配線確認、基板交換、エラー判定などの診断・作業手順ではない。設備への適用は現行の承認済み資料と責任者の確認を要する。
