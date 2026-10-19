---
schema_version: 1
record_id: "case-vfglf-m14-meld-pin-assignment-id429"
record_version: 1
title: "VFGLF・M14コネクタの接続誤りによる345エラー事例"
category: "不具合対応(ELV)"
record_type: "troubleshooting_case"
product: "エレベーター"
model_type: ["VFGLF"]
document_number: ""
revision: "首都工・不具合情報共有リスト記載。原資料・版は未確認"
effective_date: ""
review_status: "in_review"
publication_status: "not_published"
classification: "unknown"
cloud_approval: "not_reviewed"
keywords: ["VFGLF", "M14コネクタ", "MELDEN", "MCB(MP)", "345"]
source_path: ""
source_filename: "技術情報リスト（協力会社展開用）.xlsx"
onenote_id: ""
related_ids:
  - "elv-meld-operation-reference"
  - "elv-vfglf-error-codes"
attachment_paths: []
reference_links: []
document_references:
  - document_number: "YE317C142"
    title: "制御盤接続図（原文記載）"
    locator: ""
    source_path: ""
  - document_number: ""
    title: "C資料（エラー名称の確認先として原文記載）"
    locator: "本文・正式名称・番号未確認"
    source_path: ""
  - document_number: ""
    title: "菱技ノート3201『ＶＦＧＬＦエレベーター技術研修資料』"
    locator: "MELDEN接点信号の監視説明として原文記載"
    source_path: ""
evidence_sources:
  - source_id: "evidence-elv-vfglf-m14-pin-assignment-id429"
    source_type: "user_provided_extract"
    title: "首都工・不具合情報共有リスト: M14コネクタ ピンアサイン間違い"
    source_path: ""
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-13"
    locator: "リストID429（Excel出力のID欄、ワークシート行6）"
    supports:
      - "高速調整後の345表示、原文上のM14接続誤りとMELDEN信号不達の原因説明"
      - "現地で配線是正を行ったとの進捗記載と、復旧結果の記載有無"
structured_data:
  equipment: "VFGLF"
  symptom: "高速調整完了後、MON=1/0のエラー表示で345が表示されたとの報告。"
  error_codes: ["345"]
  cause: "リストは、M14コネクタ（MPスイッチ側）の接続が図面上の指定と異なり、MELDEN接点信号を受信できずにエラー表示となったと説明する。原因、信号経路、参照図面の適用性は独立確認されていない。"
  verified_actions: []
  outcome: "進捗欄は現地で配線是正を行い、フィードバック資料を作成したと記載する。是正後のエラー消失、運転回復、再発確認は記載されていない。"
  case_conditions:
    - "リストの機種欄はVFGLF。"
    - "345の名称は、リスト作成者がC資料で確認したとの記載。C資料本文は未確認。"
  source_notes:
    - "表示値、原因説明、調査所見、現地対応は共有リスト上の報告。エラーコードの意味、原因、因果関係、対応後結果は独立確認されていない。"
    - "図面番号YE317C142、C資料、菱技ノート3201の本文・改訂・適用範囲は未確認。"
    - "進捗欄には『不発を作成（ASYO50193）』とある。文書種別、正式番号としての位置づけ、本文は未確認。"
    - "ピン位置、端子識別、電圧値、短絡確認、具体的な配線変更・接続操作は記録していない。"
    - "関連IDは参照導線であり、本事例の事実を裏付けるものではない。"
---

# VFGLF・M14コネクタの接続誤りによる345エラー事例

## 事例の要点

首都工・不具合情報共有リストID429は、VFGLFで高速調整完了後にMON=1/0表示のエラー345が出た事例を記録している。345を「MCB(MP)遮断検出」とする名称は、リスト作成者がC資料で確認したとの説明であり、エラー表やC資料の本文は本記録では照合していない。

## 原文上の原因説明

リストは、M14コネクタのMPスイッチ側接続が図面上の指定と異なり、MELDEN接点信号が取り込まれなかったことをエラー原因として説明する。これは共有リスト上の説明であり、接続図、信号経路、対象設備での原因は独立確認されていない。

## 対応と結果

進捗欄には現地で配線是正を行ったことと、フィードバック資料「不発」を作成したことが記載されている。是正後にエラーが消えたか、エレベーターが運転可能になったか、再発確認が行われたかは記載されていない。

## 注意事項

本記録は事例検索用であり、電気診断、ピン判定、測定、短絡、配線変更、運転・復旧の手順ではない。原文にある具体的な接続位置・測定値・操作は転載していない。現行性、図面改訂、技術・安全レビューは未確認。

## 関連資料

- [[ELV_MELD動作参照]]: MELD関連共有情報の索引。ID429の詳細は本記録へ接続。ID132はコネクタ差し忘れによるMELD不動作の別報告であり、個別記録[[ELV_VFGLFコネクタ差し忘れ_MELD不動作_ID132事例]]を参照。
- [[ELV_VFGLF制御エラー]]: VFGLF制御エラー表示の技術参照。エラー表画像の内容と345の独立照合は未確認。

## 出典・確認状態

- 出典: 首都工・不具合情報共有リストのExcel出力、リストID429。
- 現場名、号機、共有者名は転記していない。参照資料本文、図面、適用性、対応後結果は未確認。