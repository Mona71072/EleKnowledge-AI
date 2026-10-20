---
schema_version: 1
record_id: "catalog-elv-bgm-emergency-broadcast-reference"
record_version: 3
title: "BGM・非常放送結線資料の参照記録"
category: "技術メモ【ELV】２"
record_type: "catalog"
product: "エレベーター"
model_type: []
document_number: "C-30-E6.203-J; TR24-01; 電気-591"
revision: ""
effective_date: ""
review_status: "in_review"
publication_status: "not_published"
classification: "unknown"
cloud_approval: "not_reviewed"
keywords: ["BGM", "非常放送", "結線"]
source_path: "技術メモ【ELV】２/ELV-付加仕様（その他）/BGM.md"
source_filename: "BGM.md"
onenote_id: "741d6f4a-06aa-44b5-9fab-02c5d7d98fda:1"
related_ids:
  - "case-elv-emergency-broadcast-low-volume-bgm-wiring-mismatch-id179"
attachment_paths: []
reference_links: []
document_references:
  - document_number: "C-30-E6.203-J"
    title: "BGMスピーカー接続資料"
    locator: "原資料内社内PDFリンク。未閲覧"
    source_path: ""
  - document_number: "品証-06-118"
    title: "協力会社連絡メモ"
    locator: "首都工・不具合情報共有リストID179が結線変更の根拠として記載。本文・版未確認。"
    source_path: ""
evidence_sources:
  - source_id: "evidence-elv-bgm-001"
    source_type: "vault_original"
    title: "BGM"
    source_path: "技術メモ【ELV】２/ELV-付加仕様（その他）/BGM.md"
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-08"
    supports: ["非常放送とBGMの結線/音量に関する情報共有・資料参照があること"]
  - source_id: "evidence-list-bgm-low-volume-wiring-363"
    source_type: "user_provided_extract"
    title: "協力会社展開用Excel: BGM結線誤りによる音量低下事例（ID363）"
    source_path: ""
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-13"
    supports:
      - "二線式アッテネータなしスピーカー仕様での音量低下と、結線是正後に音量が改善したとの報告"
  - source_id: "evidence-list-elv-emergency-broadcast-low-volume-bgm-mismatch-179"
    source_type: "vault_original"
    title: "首都工・不具合情報共有リスト: BGM結線ミスで非常放送の音量が小さい件（ID179）"
    source_path: "首都工・不具合情報共有リスト.xlsx"
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-14"
    supports:
      - "非常放送のみの環境での音量低下、アッテネーター設定に問題なしとの報告"
      - "入線構成と放送設備側の結線方式の不一致を原因とする説明、変更後に音量が大きくなったとの報告"
      - "品証-06-118の本文・現行適用、変更・音量結果の独立確認が未完了であること"
structured_data:
  source_notes:
    - "原文に電圧/容量/電流等の値、結線図、非常放送影響が含まれる。数値・結線条件は転載していない。"
    - "協力会社展開用Excel ID363は、二線式アッテネータなしスピーカーのBGM音量低下について、盤内の結線誤りと是正後の音量改善を報告する。具体的な端子名・信号割当は記録しない。"
    - "首都工・不具合情報共有リストID179を個別事例記録へ接続。非常放送のみの環境における入線構成と放送設備側の結線方式の不一致との説明、変更後の音量増加報告を記録。ID363はVFGLB/VFGLFのかご上スピーカーに関する別事例であり、条件・配線を混同しない。端子/線番/信号割当・結線変更/試験手順は転載していない。"
---

# BGM・非常放送結線資料の参照記録

原資料はBGMと非常放送の結線、音量低下事例、関連する社内情報共有と図版を含む。具体的な電圧・負荷・結線条件は記録していない。非常放送設備への影響を含むため、現行の防災/電気設計資料と承認を確認するまで配線・試験判断に使用しない。

## 共有リストの個別事例

協力会社展開用ExcelのリストID363は、二線式アッテネータなしスピーカー仕様でBGM結線後の音量が小さく、盤内結線の誤りを是正した後に音量が改善したと報告する。個別事例の報告であり、具体的な端子名・信号割当、結線図、配線変更手順は本記録に含めない。対象仕様への適用は承認済みの現行資料で確認する。

首都工・不具合情報共有リストID179は、非常放送のみの環境で音量が小さく、アッテネーター設定ではなく入線構成と放送設備側の結線方式の不一致が原因と説明する。連絡メモに基づく変更後に音量が大きくなったとの報告がある。詳細は[[ELV_非常放送音量低下_BGM系統結線不一致_ID179事例]]を参照。ID363とは対象・条件の異なる報告として分け、具体的な端子/配線割当と変更手順は示さない。

出典: `技術メモ【ELV】２/ELV-付加仕様（その他）/BGM.md`（OneNote ID `741d6f4a-06aa-44b5-9fab-02c5d7d98fda:1`）。確認日: 2026-10-08。
