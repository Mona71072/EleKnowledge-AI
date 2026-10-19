---
schema_version: 1
---
record_id: "catalog-elv-car-indicator-floor-display-reference"
record_version: 3
title: "かご内インジケータの階床・行先表示と設定上の注意"
category: "技術メモ【ELV】２"
record_type: "knowhow"
product: "エレベーター"
model_type: []
document_number: "C-32-A303.1-J"
revision: ""
effective_date: ""
review_status: "in_review"
publication_status: "not_published"
classification: "unknown"
cloud_approval: "not_reviewed"
keywords: ["インジケータ", "階床表示", "行先予報灯", "ロータリー設定", "VFGLF"]
source_path: "技術メモ【ELV】２/ELV-一般/かご/カゴ内インジ.md"
source_filename: "カゴ内インジ.md"
onenote_id: "a44d4691-1c4e-40f7-bace-63d4dcdee299:1"
related_ids: []
attachment_paths: []
reference_links: []
document_references:
  - document_number: "C-32-A303.1-J"
    title: "液晶インジケータD3 据付・保守資料"
    locator: "原資料内社内PDFリンク。未閲覧"
    source_path: ""
evidence_sources:
  - source_id: "evidence-elv-car-indicator-001"
    source_type: "vault_original"
    title: "カゴ内インジ"
    source_path: "技術メモ【ELV】２/ELV-一般/かご/カゴ内インジ.md"
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-08"
    supports: ["特殊階床表示と階床設定に関する注意/事例が記載されていること"]
  - source_id: "evidence-list-case-id99"
    source_type: "user_provided_extract"
    title: "首都工・不具合情報共有リスト Excel出力 ID99"
    source_path: ""
    s3_uri: ""
    revision: "原本リスト未照合"
    accessed_at: "2026-10-09"
    supports:
      - "VFGLFで制御盤ソフト変更後もカゴ内行先階予約表示が変わらなかった症状、インジ基板側設定変更後の対応済み報告、特殊階床条件および改造図面への記載に関する注意"
  - source_id: "evidence-list-case-id107"
    source_type: "user_provided_extract"
    title: "首都工・不具合情報共有リスト Excel出力 ID107"
    source_path: ""
    s3_uri: ""
    revision: "原本リスト未照合"
    accessed_at: "2026-10-09"
    supports:
      - "VFGLFの行先予報灯が1階ずれて登録された症状、原リスト上の調査段階、特殊S/Wと設定変更に関する説明、ソフト書換・インジ再設定後に解消したとの報告"
structured_data:
  knowledge_items:
    - topic: "特殊階床の行先予定階表示"
      statement: "原ページは、特殊な階床構成がある場合、行先予定階表示が実際の階床と一致しない事例と、階床に応じた設定上の注意を記載する。個別の設定値・現場固有構成はここでは再掲しない。"
      conditions:
        - "原ページは液晶インジケータD3（10.1インチ）据付・保守資料を参照している。参照先本文・版・現行適用は未確認。"
        - "特殊階床がある場合の原文記載。個別物件への適用は未確認。"
      exceptions: []
      rationale: "実際の階床構成と表示設定が合わないと、行先予定階表示が一致しない事例が原ページに記録されている。"
      verification_status: "source_recorded"
      evidence_source_ids:
        - "evidence-elv-car-indicator-001"
    - topic: "VFGLFの階床表示変更と行先階予約表示"
      statement: "リストID99は、VFGLFで制御盤ソフトを書き換えて乗場・カゴ内の階床表示を変更した後も、LINKsからのカゴ内行先階予約表示が変更されなかったと報告する。原リストはカゴ内インジ基板側の階床設定を変更して対応済みと記録する。"
      conditions:
        - "対象は原リストに記載されたVFGLF。"
        - "乗場・カゴ内の階床表示変更と、LINKsからの行先階予約表示を区別する。"
        - "特殊階床がある場合、ソフトウェア変更または基板交換が発生する可能性があるとの原文記載。"
      exceptions:
        - "設定変更の実施と表示是正はリスト上の報告であり、独立確認していない。"
      rationale: "原リストは、制御盤ソフト変更だけではカゴ内行先階予約表示が変わらない場合があり、インジ基板側設定にも関係すると説明する。"
      verification_status: "source_recorded"
      evidence_source_ids:
        - "evidence-list-case-id99"
    - topic: "改造資料と現場作業の整合"
      statement: "原リストは、改造要領図にインジ基板側の設定指示がない場合、現場判断で指示外作業をせず、改造要領図への追記や改造提案を行うよう注意している。"
      conditions:
        - "ID99の備考欄に記載された注意。"
      exceptions: []
      verification_status: "source_recorded"
      evidence_source_ids:
        - "evidence-list-case-id99"
    - topic: "VFGLFの行先予報灯が1階ずれて登録された事例（ID107）"
      statement: "リストID107は、かご内呼びの登録に対して行先予報灯が1階ずれて点灯する症状を報告する（例: B1FLのかご内呼びで1FLの予報灯が点灯）。かご内釦と到着時のかご位置表示は正常との記載がある。原リストの原因欄はインジソフトのパラメータ設定ミスとする。"
      conditions:
        - "対象は原リストに記載されたVFGLF。"
        - "原リストは特殊S/Wと通常の設定対応を区別し、特殊S/W条件の例として『B3以下の階床あり、不停止階ありの場合など』を挙げる。『など』を含む原文表現であり、完全な適用条件とは扱わない。"
        - "原リストは、特殊S/Wの場合は設定変更だけでは対応できず、ソフト書換が必要だったと説明する。具体的な設定位置・値・操作は記録しない。"
      exceptions:
        - "現地でのロータリー設定変更により是正したとの進捗記載がある一方、原因/対応欄はソフト書換とインジ再設定後に解消したとする。各段階の完了範囲・関係は原文だけでは確定できない。"
        - "原因と対応後の結果はリスト記載で、独立確認されていない。"
      rationale: "ID99の階床表示変更後に予約表示が変わらなかった事例とは症状・原因説明が異なるため、同一事象にまとめず条件別に検索できるようにする。"
      verification_status: "source_recorded"
      evidence_source_ids:
        - "evidence-list-case-id107"
  source_notes:
    - "原資料は個別事例と図版を含む。現場固有の階床構成・設定値・スイッチ位置は転載していない。PDFと現行設定基準は未確認。"
---

# かご内インジケータの階床・行先表示と設定上の注意

## 特殊階床の行先予定階表示

原ページは、特殊な階床構成がある場合に行先予定階表示が実際の階床と一致しない事例と、階床に応じた設定上の注意を記載する。参照されている液晶インジケータD3（10.1インチ）据付・保守資料の本文・版・現行適用は未確認。現場固有の階床構成・設定値・スイッチ位置は複写せず、個別事例を他現場へ一般化しない。

## VFGLFの表示変更事例（リストID99）

リストID99は、VFGLFで制御盤ソフトを書き換えて乗場・カゴ内の階床表示を変更した後も、LINKsからのカゴ内行先階予約表示が変更されなかったと報告する。原リストは、カゴ内インジ基板側の階床設定を変更して対応済みと記録し、特殊階床がある場合にはソフトウェア変更または基板交換が発生する可能性にも触れている。対応と表示是正はリスト上の報告で、独立確認していない。具体的な設定値・スイッチ位置・変更手順は記録しない。

同リストの備考は、改造要領図に設定指示がない場合、現場判断で指示外作業をせず、図面への追記や改造提案を行うよう注意している。これはID99の原文上の注意であり、現行の承認済み手順は別途確認が必要。

## VFGLFの行先予報灯1階ずれ事例（リストID107）

リストID107は、VFGLFでかご内呼びを登録すると、行先予報灯が1階ずれて点灯する症状を報告する。原文例はB1FLのかご内呼びに対して1FLの予報灯が点灯するというもの。かご内釦と到着時のかご位置インジ表示は良好と記載されている。原因欄はインジソフトのパラメータ設定ミスとするが、独立確認はされていない。

進捗欄では、電気設計経由で開発にソフト作成を依頼した後、現地でインジ基板側の設定を変更して表示不具合を是正したと記録する。同じ進捗欄と原因/対応欄は、対象が特殊S/W指定で設定変更だけでは対応できず、6月13日にソフト書換とインジ再設定を行い解消したとも記載する。このため、設定変更とソフト書換がそれぞれどの状態を是正したか、作業の前後関係・完了範囲は記載だけでは確定できない。

原文は通常のS/Wと特殊S/Wで対応が異なると説明し、特殊S/W条件の例として「B3以下の階床あり、不停止階ありの場合など」を挙げる。「など」を含む例示で、適用条件全体・現行仕様として確認されたものではない。設定位置・値・ソフト書換手順は記録しない。ID99は階床表示変更後にLINKsの行先予約表示が変更されなかった事例であり、ID107の1階ずれとは症状・原因説明が異なる。

## 出典と確認状態

- 原資料: `技術メモ【ELV】２/ELV-一般/かご/カゴ内インジ.md`（OneNote ID `a44d4691-1c4e-40f7-bace-63d4dcdee299:1`）。確認日: 2026-10-08。
- 追加出典: Excel出力ID99のA列・E〜N列・O列。B/C/D列は参照していない。
- 追加出典: Excel出力ID107のA列・E〜N列・O列。B/C/D列は参照していない。共有日は2022-06-13。SharePoint上の類似事例ID99は未閲覧で、同一性・補足内容は確認していない。
- C-32-A303.1-Jの本文・版・現行設定基準、原資料の図版の再確認、ID99の改造要領図・対応後の独立確認、現行適用、専門レビューは未完了。
- ID107の原因・各対応段階・解消結果の独立確認、現行適用、技術レビューは未完了。

出典: `技術メモ【ELV】２/ELV-一般/かご/カゴ内インジ.md`（OneNote ID `a44d4691-1c4e-40f7-bace-63d4dcdee299:1`）。確認日: 2026-10-08。
