---
schema_version: 1
record_id: "esc-frequency-parameter-mismatch-id427"
record_version: 1
title: "ESC周波数設定不一致による運転不能事例（ID427）"
category: "不具合対応(ESC)"
record_type: "troubleshooting_case"
product: "エスカレーター"
model_type:
  - "全エス機種（原文記載。対象範囲未確認）"
document_number: ""
revision: ""
effective_date: ""
review_status: "in_review"
publication_status: "not_published"
classification: "unknown"
cloud_approval: "not_reviewed"
keywords:
  - "周波数設定"
  - "パラメータ不一致"
  - "運転不能"
  - "異常コード"
source_path: ""
source_filename: "技術情報リスト（協力会社展開用）.xlsx"
onenote_id: ""
related_ids: []
attachment_paths: []
reference_links: []
document_references:
  - document_number: "C-60-631-VF31.1-J"
    title: "エスカレーター故障対応資料"
    locator: "Excel記載の参照資料。本文・版・適用範囲未確認"
    source_path: ""
evidence_sources:
  - source_id: "evidence-list-esc-frequency-mismatch-427"
    source_type: "user_provided_extract"
    title: "協力会社展開用Excel: 周波数設定違いによる運転不能（ID427）"
    source_path: ""
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-13"
    supports:
      - "本設電源接続後の運転不能、異常コード、周波数・制御パラメータ不一致に関する記載"
structured_data:
  equipment: "エスカレーター（原文は全エス機種と記載。具体的な対象範囲は未確認）"
  symptom: "後工程の初回号機で本設電源へ接続後、運転できなかったとの報告。"
  error_codes:
    - code: "E-1 001"
      source_description: "インバータ異常"
    - code: "E-1 121"
      source_description: "サブCPU異常"
    - code: "E-3 126"
      source_description: "サブCPU RSW設定異常"
    - code: "E-1 305"
      source_description: "電源位相異常PLL"
  cause: "稲電回答は、E-3 126をRSW設定とソフトウェアパラメータの不一致、E-1 305を電源周波数とソフトウェアパラメータの不一致として説明し、E-1 001とE-1 121はこれらに付随して検出するとしている。原リストは、工場試験時に周波数関連の設定を一時変更し、出荷検査後の処理で初期化できなかった可能性を原因として挙げる。いずれも当該号機での独立検証はない。"
  verified_actions: []
  outcome: "対応後に運転可能となったかは記載から確認できない。回答欄には、参照資料へESC側の周波数設定確認を追記する方向で検討する旨があるが、資料改訂の実施・承認は未確認。"
  limitations:
    - "確認・初期化・リセットなどの具体操作、設定値、スイッチ位置、コネクタ操作は転載しない。"
    - "参照資料C-60-631-VF31.1-Jの本文、版、適用機種、改訂実施状況は未確認。"
    - "全エス機種という原文表現の適用範囲、原因および復旧結果は独立確認していない。"
---

# ESC周波数設定不一致による運転不能事例（ID427）

## 症状と記録された調査

首都工・不具合情報共有リストID427は、後工程の初回号機で本設電源へ接続後、運転できなかったと報告する。P1基板でE-1 001、E-1 121、E-3 126、E-1 305が確認されたとの記載がある。エラー名称はExcel記載を保持しており、現行定義との照合はしていない。

原リストはC-60-631-VF31.1-Jを参照して調査したとする。稲電回答は、E-3 126をRSW設定とソフトウェアパラメータの不一致、E-1 305を電源周波数とソフトウェアパラメータの不一致として説明し、E-1 001とE-1 121はこれらに付随して検出するとしている。この説明は出典上の回答であり、対象機で独立確認した診断結果ではない。

## 原因推定と対応状況

原リストは、工場試験時に周波数関連設定を一時変更し、出荷検査後に行う処理でパラメータを初期化できなかった可能性を原因として挙げる。確定原因としては扱わない。

回答欄には、C-60-631-VF31.1のE-1 305にESC側の周波数設定確認を追記する方向で検討する旨が記載されている。資料改訂の実施・承認、対象機の復旧、再発状況は未確認である。具体的な確認・初期化・リセット操作、設定値、スイッチ位置、配線・コネクタ作業は本記録に含めない。

## 適用上の注意

Excelは対象を「全エス機種」と記載するが、具体的な対象範囲や参照資料の適用機種は未確認。C-60-631-VF31.1-Jの本文・版も未確認であるため、本記録を運転可否判断や設定変更の手順として使用しない。適用判断は承認済み最新版の資料と所管担当の確認による。