---
schema_version: 1
record_id: "knowhow-elv3-group-control-mixed-model-power-review"
record_version: 1
title: "異機種群管理の電源構成: 設計時の確認ポイント"
category: "技術メモ【ELV】３"
record_type: "knowhow"
product: "エレベーター"
model_type: []
document_number: ""
revision: "原資料の現行性未確認"
effective_date: ""
review_status: "in_review"
publication_status: "not_published"
classification: "unknown"
cloud_approval: "not_reviewed"
keywords: ["群管理", "異機種接続", "バックアップ電源", "増設盤", "設計確認"]
source_path: "技術メモ【ELV】３/群管理（技術メモ）.md"
source_filename: "群管理（技術メモ）.md"
onenote_id: "cf01bae3-86fc-4307-949e-3798361c2ee3:1"
related_ids: []
attachment_paths: []
reference_links: []
document_references: []
evidence_sources:
  - source_id: "evidence-elv3-group-control-parent-001"
    source_type: "vault_original"
    title: "群管理（技術メモ）"
    source_path: "技術メモ【ELV】３/群管理（技術メモ）.md"
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-08"
    supports: ["異機種群管理構成と増設盤の給電、群管理バックアップ電源に関する記述があること"]
  - source_id: "evidence-list-group-control-miswiring-349"
    source_type: "user_provided_extract"
    title: "首都工・不具合情報共有リスト: 群管理通信系統の誤結線事例"
    source_path: ""
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-09"
    supports: ["ID349に記録された誤結線、通信系統への200V印加、火災および地震管制機能不全の報告"]
structured_data:
  knowledge_items:
    - topic: "異機種群管理ではバックアップ電源経路を個別に確認する"
      statement: "原資料はLINKsとKMの異機種群管理について、群管理盤・号機側の増設盤・制御盤からの給電と、群管理バックアップ電源の取り出しに関する制約を記録している。原資料の例ではG号機のR4/S4電源取り出し箇所が一つで、記載された構成のままではバックアップ電源を取り出せないとしている。"
      conditions: ["原資料に記載された構成例であり、現行設計や他機種・他物件に一般化できない。"]
      exceptions: ["電源端子、配線、盤構成、改造可否は承認済みの機種別図面・設計資料で確認する。"]
      rationale: "機種混在時に標準構成を前提とせず、群管理盤・各号機・増設盤間の給電とバックアップ経路のレビュー漏れを防ぐため。"
      verification_status: "source_recorded"
      evidence_source_ids: ["evidence-elv3-group-control-parent-001"]
    - topic: "群管理盤・増設盤の結線不具合を設計レビューへつなぐ"
      statement: "同じ原資料には、増設盤の誤結線による基板焼損事例への参照がある。結線や盤構成の変更を検討する際は、当該事例と承認済み図面・改造要領の照合が必要なレビュー事項として扱う。"
      conditions: ["原資料の不具合参照先、図版、技術情報リストの内容は未確認。"]
      exceptions: ["この記録は故障原因の確定、結線指示、改造手順を示さない。"]
      rationale: "過去事例を作業手順として流用せず、設計・品質の確認につなぐため。"
      verification_status: "source_recorded"
      evidence_source_ids: ["evidence-elv3-group-control-parent-001"]
    - topic: "群管理通信系統への誤給電を重大安全リスクとして設計審査する"
      statement: "首都工・不具合情報共有リストID349は、誤結線により通信系統へ200Vが印加され、火災と地震管制機能不全に至った事例を報告している。これはリスト記載の報告であり、因果関係・対象構成・影響範囲を独立確認したものではない。"
      conditions: ["個別の報告事例。機種、回路、設計改訂および他案件への適用性は未確認。"]
      exceptions: ["電圧・端子・配線識別、再現/測定、復旧方法は記載しない。実案件は承認済み図面と安全・設計担当の確認を要する。"]
      rationale: "通信系統への誤給電が安全機能へ及ぼす重大な影響を、作業手順にせず設計審査で確認するため。"
      verification_status: "source_recorded"
      evidence_source_ids: ["evidence-list-group-control-miswiring-349"]
  source_notes:
    - "原資料の単一構成例を要約した設計確認用ノウハウであり、現行仕様・個別物件への適用は未確認。"
    - "端子位置、結線、改造、部品手配の指示は含めない。"
    - "原資料が参照する系統図、添付画像、技術情報リストは未確認。"
    - "リストID349の記載は未独立検証の重大事例報告。設備識別情報、具体的配線・検査・復旧手順は転記していない。"
---

# 異機種群管理の電源構成: 設計時の確認ポイント

## 要点

異機種を組み合わせた群管理では、群管理盤・各号機の制御盤・増設I/O盤の給電と、群管理バックアップ電源の経路が標準構成どおりとは限らない。元ノートはLINKsとKMの混在構成を例に、号機側の電源取り出し箇所数がバックアップ電源経路の制約になるケースを記録している。

これは特定の原資料記載例であり、一般仕様ではない。実案件では機種・号機構成に対応した承認済み系統図、盤図、改造要領で確認する。

## 設計レビューで確認する観点

- 群管理対象の機種・制御方式が混在しているか。
- 群管理盤、各号機制御盤、増設盤の給電元とバックアップ電源経路が、承認済み図面上で整合しているか。
- 通信系統への誤給電が安全機能に影響したとのリスト報告（ID349）を踏まえ、給電系統と通信系統の設計上の分離・保護を、承認済み図面と設計/安全担当者が確認しているか。
- 過去の誤結線による基板焼損事例や、対象構成に適用される正式な改造要領がないか。
- 原資料の図面・不具合参照先を確認できていない場合、設計/品質の担当者へ照会できているか。

これらはレビュー漏れを防ぐための確認観点であり、結線方法・端子指定・部品手配・改造指示ではない。給電経路に不整合が疑われる場合、このメモだけで設計変更や作業判断を行わない。

## 出典と未確認事項

- 原資料: `技術メモ【ELV】３/群管理（技術メモ）.md`（OneNote ID `cf01bae3-86fc-4307-949e-3798361c2ee3:1`）。
- 追加出典: 首都工・不具合情報共有リストID 349。火災・地震管制機能不全を含む報告内容の独立確認、対象構成、影響範囲、現行対策は未確認。
- 元ノートには群管理系統図、増設盤の誤結線による基板焼損事例、技術情報リストへの参照があるが、図面・リンク先・添付画像の内容は未確認。
- 機種別適用、改訂、承認状態、個別物件の設計条件は未確認。設計・結線・改造・運転確認には、現行の承認済み資料と専門担当者の確認を優先する。