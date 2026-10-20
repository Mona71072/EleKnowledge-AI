---
schema_version: 1
record_id: "catalog-elv3-monitor-panel-communication-reference"
record_version: 3
title: "監視盤表示症状と原文原因仮説"
category: "技術メモ【ELV】３"
record_type: "technical_reference"
product: "エレベーター"
model_type: []
document_number: ""
revision: ""
effective_date: ""
review_status: "in_review"
publication_status: "not_published"
classification: "unknown"
cloud_approval: "not_reviewed"
keywords: ["監視盤", "通信", "表示"]
source_path: "技術メモ【ELV】３/監視盤.md"
source_filename: "監視盤.md"
onenote_id: "bb246305-5f61-4f0c-abbb-5c6ab791f2c7:1"
related_ids: []
attachment_paths: []
reference_links: []
document_references:
  - document_number: ""
    title: "通信線テレコが原因で監視盤表示がチラつく"
    locator: "技術情報リストID 241。SharePointリンク先未閲覧"
    source_path: ""
  - document_number: ""
    title: "保守ソフトの有無による監視盤表示の違い"
    locator: "SharePoint技術情報リストID 410。リンク先未閲覧"
    source_path: ""
  - document_number: ""
    title: "監視盤チェック"
    locator: "OneNote内部リンク。リンク先未確認"
    source_path: ""
evidence_sources:
  - source_id: "evidence-elv3-monitor-panel-001"
    source_type: "vault_original"
    title: "監視盤"
    source_path: "技術メモ【ELV】３/監視盤.md"
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-09"
    supports: ["監視盤表示のちらつきに対する通信結線不整合の原文仮説、結線変更後の表示保持注記、スロー時の運転灯記載"]
  - source_id: "evidence-list-monitor-panel-communication-241"
    source_type: "user_provided_extract"
    title: "協力会社展開用Excel: 通信線不整合による監視盤表示ちらつき（ID241）"
    source_path: ""
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-13"
    supports:
      - "表示ちらつきと通信配線不整合の原因報告"
      - "電気業者への手直し依頼との原リスト記載"
structured_data:
  technical_observations:
    - name: "監視盤LED表示のちらつき"
      value: "原文は通信配線の接続不整合を原因候補として挙げる"
      condition: "原文記載の原因仮説/報告。回路図・SharePoint技術情報・実機状況は未確認で、原因確定ではない"
    - name: "結線変更後の表示保持"
      value: "結線をつなぎ変えても監視盤の電源リセットまで表示が保持されると原文に記載"
      condition: "原文記載。リセット操作の手順/安全条件としては扱わない"
    - name: "スロー時の運転灯"
      value: "スローにすると運転灯が付かなくなると原文に記載"
      condition: "運転モードと表示に関する原文注記。対象機種/仕様・現行性は未確認"
  safety_warnings:
    - "原因仮説と表示記載は原文ノートだけで裏付けられていない。結線変更、電源リセット、運転状態の判断は、現行回路図と承認済み保守要領・所管者確認なしに行わない。"
  source_notes:
    - "電圧値、配線/端子の組合せ、切替/復旧方法、電源リセット手順は記録していない。"
    - "Excel行139/ID241は確認済み。SharePointリンク先、ID410およびOneNote内部リンクは未閲覧。"
---

# 監視盤表示症状と原文原因仮説

原資料本文には、監視盤LED表示のちらつきについて通信結線の不整合を可能性として挙げる記述、結線変更後も監視盤の表示が保持されるとの注記がある。また「スローにすると運転灯が付かなくなる」と記載されている。Excel行139/ID241も、表示ちらつきと通信配線不整合、電気業者への手直し依頼を報告している。

これらは原文記載の原因仮説/報告であり、SharePoint資料・回路図・対象機の状態・修理後の検証結果は未確認。原因確定や現行仕様を示すものではない。具体的な結線/復旧操作や運転状態の判断には使用せず、承認済みの現行回路図と保守要領を所管者に確認する。

出典: `技術メモ【ELV】３/監視盤.md`（OneNote ID `bb246305-5f61-4f0c-abbb-5c6ab791f2c7:1`）。本文確認日: 2026-10-09。
