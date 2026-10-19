---
schema_version: 1
record_id: "tech-elv-option1-event-service-functions-overview"
record_version: 1
title: "ELV付加仕様① 災害・サービス関連機能の概要"
category: "技術メモ【ELV】１"
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
keywords:
  - "サービス切離し"
  - "休止運転"
  - "停電時自動着床"
  - "冠水管制"
  - "地震管制"
  - "消防運転"
  - "火災管制"
  - "長周期振動"
source_path: "技術メモ【ELV】１/ELV-付加仕様①/"
source_filename: "複数原資料（下記evidence_sources参照）"
onenote_id: ""
related_ids: []
attachment_paths: []
reference_links: []
document_references:
  - document_number: ""
    title: "MELD適用上の制約条件について（S-1-B37.101-J.pdf）"
    locator: "原資料本文に記載された参照。未閲覧"
    source_path: ""
  - document_number: ""
    title: "長周期振動時管制運転に関する参考資料（S-1-Z06.1-J.pdf、TI-1371-_.pdf）"
    locator: "原資料本文に記載された参照。未閲覧"
    source_path: ""
evidence_sources:
  - source_id: "evidence-elv-ns-001"
    source_type: "vault_original"
    title: "サービス切離し（NS）"
    source_path: "技術メモ【ELV】１/ELV-付加仕様①/サービス切離し（NS）.md"
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-08"
    supports:
      - "サービス切離し機能に関する説明・注意事項があること"
  - source_id: "evidence-elv-hos-001"
    source_type: "vault_original"
    title: "休止運転（HOS）"
    source_path: "技術メモ【ELV】１/ELV-付加仕様①/休止運転（HOS）.md"
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-08"
    supports:
      - "休止運転に関する短い説明があること"
  - source_id: "evidence-elv-meld-001"
    source_type: "vault_original"
    title: "停電時自動着床装置（MELD）"
    source_path: "技術メモ【ELV】１/ELV-付加仕様①/停電時自動着床装置（MELD）.md"
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-08"
    supports:
      - "停電時の乗客救出を目的とする装置の概要があること"
  - source_id: "evidence-elv-flood-001"
    source_type: "vault_original"
    title: "冠水管制運転"
    source_path: "技術メモ【ELV】１/ELV-付加仕様①/冠水管制運転.md"
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-08"
    supports:
      - "冠水検知と管制に関する注意・参照があること"
  - source_id: "evidence-elv-earthquake-001"
    source_type: "vault_original"
    title: "地震管制運転"
    source_path: "技術メモ【ELV】１/ELV-付加仕様①/地震管制運転.md"
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-08"
    supports:
      - "地震検知後の管制運転に関する説明・注意があること"
  - source_id: "evidence-elv-firefighter-001"
    source_type: "vault_original"
    title: "消防夫運転"
    source_path: "技術メモ【ELV】１/ELV-付加仕様①/消防夫運転.md"
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-08"
    supports:
      - "消防運転と停電時自動着床機能の関係に関する注意があること"
  - source_id: "evidence-elv-fire-control-001"
    source_type: "vault_original"
    title: "火災管制運転"
    source_path: "技術メモ【ELV】１/ELV-付加仕様①/火災管制運転.md"
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-08"
    supports:
      - "火災信号による管制の概要・監視盤に関する記述があること"
  - source_id: "evidence-elv-long-period-001"
    source_type: "vault_original"
    title: "長周期振動時官制運転（BESR-CP）"
    source_path: "技術メモ【ELV】１/ELV-付加仕様①/長周期振動時官制運転（BESR-CP）.md"
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-08"
    supports:
      - "長周期振動時の管制運転に関する概要・参照があること"
structured_data:
  source_notes:
    - "8件の原資料本文を確認し、機能の位置づけを横断整理した。個別の設定値、信号条件、動作時間、運転・復帰操作は転記していない。"
    - "原資料の改訂、対象機種、適用条件、技術承認は未確認。現行仕様・設計条件・作業/運転指示として扱わない。"
    - "各原資料に画像埋め込みがあるが、対応する実ファイルの所在と内容を確認できていない。画像は根拠として使用していない。"
    - "SharePoint等のリンク先は未閲覧。クエリー情報を含むURLは再掲していない。"
---

# ELV付加仕様① 災害・サービス関連機能の概要

## 概要

この記録は、技術メモ【ELV】１の付加仕様①にある8件のノートから、資料が扱う機能の種類と確認範囲を整理したレビュー用ドラフトである。原資料の記述時点、機種、制御方式、改訂および適用可否は確認できていない。運転、設計、点検、試験、復旧の手順や判断基準を示すものではない。

## 資料が扱う機能

- **サービス状態の変更:** サービス切離し（NS）と休止運転（HOS）のノートがある。NSノートには不具合事例への参照、機能上の注意、図版参照が含まれる。HOSノートは短い説明と未閲覧の不具合情報リンクが中心で、適用条件を確定できない。
- **停電・冠水への対応:** MELDノートは停電時の乗客救出を目的とする装置を説明する。冠水管制ノートは冠水センサー等に関する注意と技術情報への参照を含む。詳細条件は原資料本文・参照資料ともに現行性を確認していない。
- **地震・長周期振動への対応:** 地震管制ノートと長周期振動時管制ノートがある。いずれも検知状態や管制後の挙動に触れているが、具体的な閾値、復帰条件、設備要件はこの概要に転記していない。
- **火災・消防運転:** 消防夫運転ノートと火災管制運転ノートがある。消防運転と他機能の関係、火災信号を扱う説明が記載されている。実際の設計・運転条件は所轄消防、承認済み設計資料および対象機種の確認が必要であり、この記録では判断しない。

## 読み取り上の注意

これらは別々の機能・条件を扱う原資料であり、横断要約によって機能間の優先順位や動作条件を補完していない。原資料には運転モード、信号、設定、解除に関する情報があるが、ここでは具体値・操作を再掲しない。旧メモの記述を現行の標準や仕様とみなさず、対象の承認済み資料へ戻って確認する。

## 未確認事項

- 8件すべての対象機種、制御方式、適用範囲、発行/改訂情報と現在の有効性。
- 原資料に埋め込まれた画像の実体、ノートとの対応、画像内の記載内容。
- 原資料が参照する社内共有リスト、SharePoint資料、PDFの内容・権限・現行性。
- NS、HOS、MELD、冠水・地震・火災・消防・長周期振動関連機能の個別設計条件と相互関係。
- 現行の設計/運転/点検判断に使用できる承認済み根拠。

## 関連資料

- [[技術メモ【ELV】１/ELV-付加仕様①/サービス切離し（NS）]]
- [[技術メモ【ELV】１/ELV-付加仕様①/休止運転（HOS）]]
- [[技術メモ【ELV】１/ELV-付加仕様①/停電時自動着床装置（MELD）]]
- [[技術メモ【ELV】１/ELV-付加仕様①/冠水管制運転]]
- [[技術メモ【ELV】１/ELV-付加仕様①/地震管制運転]]
- [[技術メモ【ELV】１/ELV-付加仕様①/消防夫運転]]
- [[技術メモ【ELV】１/ELV-付加仕様①/火災管制運転]]
- [[技術メモ【ELV】１/ELV-付加仕様①/長周期振動時官制運転（BESR-CP）]]

## 出典・確認履歴

- 出典はfrontmatterの `evidence_sources` に原資料ごとに登録。各ノートのOneNote IDは原ノート側で保持。
- 確認日: 2026-10-08。確認対象は上記8件のMarkdown本文。
- 添付画像の存在・内容、外部参照、技術レビュー、改訂確認は未完了。
