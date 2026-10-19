---
schema_version: 1
record_id: "catalog-elv-hall-chime-reference"
record_version: 2
title: "乗場チャイム資料の参照記録"
category: "技術メモ【ELV】２"
record_type: "catalog"
product: "エレベーター"
model_type: []
document_number: "C-6-S1300-K7-J; C-6-S1300-K5.1-J"
revision: ""
effective_date: ""
review_status: "in_review"
publication_status: "not_published"
classification: "unknown"
cloud_approval: "not_reviewed"
keywords: ["乗場チャイム", "電子音", "ソフトウェア"]
source_path: "技術メモ【ELV】２/ELV-付加仕様（その他）/乗場チャイム（電子音チャイム）.md"
source_filename: "乗場チャイム（電子音チャイム）.md"
onenote_id: "ec7a020a-b61b-4b31-8097-a76e0583aecd:1"
related_ids: []
attachment_paths: []
reference_links: []
document_references:
  - document_number: "C-6-S1300-K7-J; C-6-S1300-K5.1-J"
    title: "電子音チャイム関連資料"
    locator: "原資料内社内PDFリンク。未閲覧"
    source_path: ""
evidence_sources:
  - source_id: "evidence-list-hall-chime-unintended-tone-399"
    source_type: "user_provided_extract"
    title: "首都工・不具合情報共有リスト: 電子音チャイム誤鳴動事例"
    source_path: ""
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-09"
    supports:
      - "AECHとAIL併用時の意図しない音、ソフト処理漏れの原因説明と500ms/400msの個別例"
  - source_id: "evidence-elv-hall-chime-001"
    source_type: "vault_original"
    title: "乗場チャイム（電子音チャイム）"
    source_path: "技術メモ【ELV】２/ELV-付加仕様（その他）/乗場チャイム（電子音チャイム）.md"
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-08"
    supports: ["チャイム鳴動パターン/不具合事例と関連資料があること"]
structured_data:
  knowledge_items:
    - topic: "到着予報音と方向チャイムの出力更新が重なった誤鳴動事例"
      statement: "首都工・不具合情報共有リストID 399とVault原資料には、AECHとAILの併用時、かごがいる階で上呼びを作ると意図しない下方向音が鳴った事例が記載されている。原資料はチャイム出力が500ms継続する仕様とし、400ms後に次の要求へ更新する例で旧出力の解除処理が漏れ、出力が重なったことをソフトウェア不具合の原因として説明する。数値は原資料の個別例で、現行仕様・一般的なしきい値ではない。"
      conditions: ["AECHとAILの併用として記録された過去事例", "原資料とリスト項目が同一案件かは独立確認していない"]
      exceptions: ["信号ビット列、現場情報、動画、ソフト改修内容・適用版は転載/確認していない。", "500ms/400msを現行タイミング仕様や試験条件として使用しない。"]
      rationale: "時間差を伴う連続出力で前状態の解除が欠けると、複合した出力が別の音として解釈されるという個別不具合の説明を残すため。"
      verification_status: "source_recorded"
      evidence_source_ids: ["evidence-elv-hall-chime-001", "evidence-list-hall-chime-unintended-tone-399"]
  source_notes:
    - "原文に信号シーケンス、タイミング、個別現場動画/資料が含まれる。電気/ソフト条件と案件情報は転載していない。"
---

# 乗場チャイム資料の参照記録

原資料は電子音チャイムの鳴動パターン、信号処理に関する過去不具合、機種資料と個別事例動画への参照を含む。信号状態、タイミング、原因解析、現場情報は複写していない。

首都工・不具合情報共有リストID 399にも、AECHとAIL併用時の意図しない音とソフト処理漏れの説明がある。原資料にある500ms保持/400ms更新は一つの説明例として記録し、現行仕様や試験条件とは扱わない。原資料とリスト項目の案件同一性は未確認。

現行ソフトウェア版・機種仕様・承認済み不具合情報を確認するまで、信号解析や改修判断に使用しない。

出典: `技術メモ【ELV】２/ELV-付加仕様（その他）/乗場チャイム（電子音チャイム）.md`（OneNote ID `ec7a020a-b61b-4b31-8097-a76e0583aecd:1`）。確認日: 2026-10-08。
