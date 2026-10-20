---
schema_version: 1
record_id: "elv-axiez-links-no-load-rotation-temporary-connector-state-id309"
record_version: 1
title: "仮設コネクタ状態に関連した巻上機空回し不能（ID309）"
category: "不具合対応(ELV)"
record_type: "failure_case"
product: "エレベーター"
model_type:
  - "AXIEZ-LINKs"
document_number: ""
revision: ""
effective_date: ""
review_status: "in_review"
publication_status: "not_published"
classification: "unknown"
cloud_approval: "not_reviewed"
keywords:
  - "巻上機"
  - "空回し不能"
  - "仮設コネクタ"
  - "接続状態"
source_path: ""
source_filename: "技術情報リスト（協力会社展開用）.xlsx"
onenote_id: ""
related_ids:
  - "ID317"
  - "ID362"
attachment_paths: []
reference_links: []
document_references: []
evidence_sources:
  - source_id: "evidence-list-elv-no-load-rotation-connector-state-309"
    source_type: "user_provided_extract"
    title: "協力会社展開用Excel: コネクタの抜き忘れで巻上機空回しできない件（ID309）"
    source_path: ""
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-13"
    supports:
      - "巻上機空回し不能と仮設コネクタの状態との関連報告、状態変更後の動作良好報告"
structured_data:
  symptom: "制御盤単独の確認では問題がなかった一方、据付後の巻上機空回しができなかったとの報告。"
  cause: "仮設コネクタが所定の状態で残っていたことを原因として原リストが説明する。独立確認していない。"
  result: "原リストは本設接続後に動作が良好となったと報告する。独立確認していない。"
  limitations:
    - "現場識別情報、診断コード、コネクタ識別、短絡状態、図面位置は転載しない。"
    - "電気確認、短絡/開放、接続変更、運転/復旧の手順は転載しない。"
    - "ID317のソフトウェア書込み不備、ID362のブレーキ内部結線誤りとは別の原因報告。原因・結果・適用性は未確認。"
    - "本記録を電気作業、診断、運転、復旧手順として使用しない。"
---

# 仮設コネクタ状態に関連した巻上機空回し不能（ID309）

協力会社展開用リストID309は、制御盤単独の確認では問題がなかった一方、据付後に巻上機の空回しができなかった事例を報告している。原リストは仮設コネクタが所定の状態で残っていたことを原因とし、本設接続後に動作が良好となったと説明するが、原因・結果・適用範囲は独立確認していない。

ID317のソフトウェア書込み不備、ID362のブレーキ内部結線誤りとは原因の報告が異なる別事例である。現場識別情報、診断コード、コネクタ識別、電気確認・短絡/開放・接続変更・運転/復旧の手順は記録しない。本記録を電気作業、診断、運転、復旧の手順として使用しない。