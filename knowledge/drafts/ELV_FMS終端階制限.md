---
schema_version: 1
record_id: "elv-fms-terminal-floor-limit"
record_version: 2
title: "短ランバイ適用時の終端階手動運転制限に関するノウハウ"
category: "不具合対応(ELV)"
record_type: "knowhow"
product: "エレベーター"
model_type: ["VFGH（リスト機種欄の記載）"]
document_number: ""
revision: "Vault原文および首都工・不具合情報共有リスト記載。参照資料・改訂・適用性未確認"
effective_date: ""
review_status: "in_review"
publication_status: "not_published"
classification: "unknown"
cloud_approval: "not_reviewed"
keywords:
  - "短ランバイ"
  - "終端階"
  - "FMS"
  - "UL"
  - "DL"
source_path: "不具合対応【ELV】/現象（不具合対応）/仮スロー・本スロー・自動運転/FMS.md"
source_filename: "FMS.md"
onenote_id: "a8c15103-95f4-4d08-897a-403d412bffb5:152"
related_ids: []
attachment_paths:
  - "不具合対応【ELV】/現象（不具合対応）/仮スロー・本スロー・自動運転/OneNote/FMS image.png"
reference_links: []
document_references:
  - document_number: "C-7-D-C2950"
    title: "D資料（正式題名未確認）"
    locator: "Excel参考資料欄 P.33。本文未閲覧"
    source_path: ""
  - document_number: "C-7-F2900"
    title: "C資料（正式題名未確認）"
    locator: "Excel参考資料欄 P.44。本文未閲覧"
    source_path: ""
  - document_number: "H12建告1423"
    title: "告示参照（正式識別・本文未確認）"
    locator: "Excel参考資料欄"
    source_path: ""
  - document_number: "C-7-F2900.1-J"
    title: "C資料（正式題名未確認）"
    locator: "Excel備考欄。本文未閲覧"
    source_path: ""
  - document_number: ""
    title: "電気品目599"
    locator: "Excelに短ランバイ適用判定の参照として記載。資料実体未確認"
    source_path: ""
evidence_sources:
  - source_id: "evidence-elv-fms-terminal-original"
    source_type: "vault_original"
    title: "FMS（原文）"
    source_path: "不具合対応【ELV】/現象（不具合対応）/仮スロー・本スロー・自動運転/FMS.md"
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-02"
    supports:
      - "短ランバイ適用物件に関する終端階の運転制限メモ"
  - source_id: "evidence-elv-fms-terminal-extract-id428"
    source_type: "user_provided_extract"
    title: "首都工・不具合情報共有リスト: 短ランバイ適用物件における終端階運転制限"
    source_path: ""
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-09"
    locator: "リストID 428（Excel出力のID欄）。資料番号ではない"
    supports:
      - "短ランバイ適用時の終端階FLからの手動運転制限、速度区分別の記載条件、参照資料一覧"
structured_data:
  knowledge_items:
    - topic: "短ランバイ適用時の終端階FLからの手動運転制限"
      statement: "リスト記載は、短ランバイ適用時に終端階FLからUL/DLまで手動運転できない状態を仕様動作であり不具合ではないと説明している。高速機種の対象条件では手動速度4 m/min、HTOP=1の記載条件で運転可能との記録があり、低速機種は手動速度が自動的に4 m/minとなるため制御盤での対応不要とされる。"
      conditions: ["リストの機種欄はVFGH。", "高速/低速の区分は原文記載どおりだが、VFGHがどちらに該当するか、対象設備・制御版は未確認。", "高速機種の対象判定は電気品目599に記載、低速機種は現地対応記載がないとのリスト記録。"]
      exceptions: ["4 m/min、HTOP=1はExcelに記録された値であり、現行設定値・承認済み操作・一般的な適用条件として確認されていない。", "原文添付画像1点は2026-10-07時点で実体未確認。", "資料番号の本文、告示内容、機種適用、改訂は未確認。"]
      rationale: "短ランバイ条件に伴う終端階の運転制限を、故障と即断せず、対象設備の承認済み仕様と照合するため。"
      verification_status: "source_recorded"
      evidence_source_ids: ["evidence-elv-fms-terminal-original", "evidence-elv-fms-terminal-extract-id428"]
  source_notes:
    - "原文は添付画像1点を参照している。過去の目視確認記録はあるが、2026-10-07時点で指定パスに画像実体がなく再検証できない。"
    - "値・条件・参照番号はリスト記載として保持し、現行仕様/設定手順とは扱わない。参照資料本文、適用対象・改訂・技術レビューは未確認。"
    - "リストID 428は出典追跡用識別子であり、資料番号ではない。現場名・号機・共有者等は転記していない。"
---

# 短ランバイ適用時の終端階手動運転制限に関するノウハウ

原文は、短ランバイ適用物件で終端階FLから手動運転してもUL/DLまで運転できない事象を記載し、共有リストと画像を参照している。「首都工・不具合情報共有リスト」は当該状態を仕様動作とし、高速/低速区分別の条件を説明している。4 m/min、HTOP=1はリスト記載値として保存するが、現行基準や設定・操作手順として使用しない。VFGH内の適用条件、参照資料本文、現行性、解決結果は未確認。

## 出典

- 原文ノート: [[不具合対応【ELV】/現象（不具合対応）/仮スロー・本スロー・自動運転/FMS]]
- 出典: 首都工・不具合情報共有リスト、ID 428。内容照合にはリストからのExcel出力を使用。
- 原文は添付画像1点を参照。2026-10-07時点で指定パスに実ファイルを確認できず、過去の目視確認記録を再検証できない。共有リスト本文・適用機種・現行性・権限は未確認。