---
schema_version: 1
record_id: "elv-breaker-grounding-safety-review-hold"
record_version: 2
title: "ブレーカー種別・接地記述の安全レビュー保留"
category: "技術メモ【ELV】２"
record_type: "catalog"
product: "エレベーター"
model_type: []
document_number: ""
revision: ""
effective_date: ""
review_status: "in_review"
publication_status: "not_published"
classification: "unknown"
cloud_approval: "not_reviewed"
keywords: ["MCCB", "MCB", "ELCB", "ELB", "NF", "NV", "接地", "地絡", "漏電警報", "KM-LD", "ID116", "安全レビュー"]
source_path: "技術メモ【ELV】２/ELV-一般/ブレーカー（技術メモ）.md"
source_filename: "ブレーカー（技術メモ）.md"
onenote_id: "2fd509b2-87aa-4e26-8cd6-6d51680accc1:1"
related_ids:
  - "elv-customer-breaker-capacity-relationship-id214"
attachment_paths: []
reference_links: []
document_references:
  - document_number: ""
    title: "負荷試験の電流値がMCBブレーカー定格電流を超えてしまう件"
    locator: "SharePoint技術共有リストID 391。未閲覧"
    source_path: ""
  - document_number: ""
    title: "MCBブレーカーのトリップ接点について"
    locator: "SharePoint技術共有リストID 405。未閲覧"
    source_path: ""
  - document_number: ""
    title: "100Vラインが地絡し客先漏電警報機が異常発報する件"
    locator: "首都工・不具合情報共有リスト.xlsx ID116。一次リストを照合済み。記載内容・添付の適用性と現行性は未確認。"
    source_path: ""
  - document_number: ""
    title: "三菱電機関西適塾20150605資料.ppt"
    locator: "原資料内SharePointリンク。未閲覧"
    source_path: ""
  - document_number: ""
    title: "内線規程 1350-13"
    locator: "原資料が引用。版・条文本文・例外条件は未確認"
    source_path: ""
evidence_sources:
  - source_id: "evidence-elv-breaker-grounding-hold-20261009"
    source_type: "vault_original"
    title: "ブレーカー（技術メモ）"
    source_path: "技術メモ【ELV】２/ELV-一般/ブレーカー（技術メモ）.md"
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-09"
    supports: ["用語説明、機種別ブレーカー適用の主張、客先保護協調、接地規程引用と未解決質問、外部資料参照が原文にあること"]
  - source_id: "evidence-elv-ground-fault-alarm-id116-20261014"
    source_type: "vault_original"
    title: "首都工・不具合情報共有リスト: 100Vライン地絡・漏電警報（ID116）"
    source_path: "首都工・不具合情報共有リスト.xlsx"
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-14"
    supports: ["KM-LDの客先漏電警報異常、地絡を確認したとの報告、配線の挟み込みを確認したとの報告。原因確定・復旧・安全確認は裏付けない"]
structured_data:
  safety_warnings:
    - "本記録は、原文に安全・電気・法令上の主張が含まれるためのレビュー保留であり、記載内容を承認済み仕様/法令解釈として確認したものではない。選定、施工、結線、接地、測定、遮断器操作、停電/運転判断に使用しない。"
    - "原文の機種別NF/NV適用理由、非常用エレベーターに関する説明、客先遮断器との保護協調、接地共用の禁止/例外引用は、正式な現行機種別資料・規程本文・設計責任者による確認が必要。"
  source_notes:
    - "原文はMCCB/MCB、ELCB/ELB、NFB/NF、NVの名称/役割を説明するが、略語・商標・機能説明の正確性は独立確認していない。"
    - "原文はMRL/MR/非常用エレベーターごとのNF/NV適用理由を記すが、現行設計基準・対象機種・契約条件は未確認。"
    - "内線規程1350-13と例外条件を引用しているが、規程の版、正確な条文、法的解釈・適用条件を確認していない。"
    - "原文末尾にMRLの接地線が1本の場合の扱いを所管部門へ確認する旨の未解決質問がある。回答・承認は記録されていない。"
    - "埋め込み画像1点およびSharePoint参照3件・PowerPoint資料は未確認。認証付きリンク先を閲覧していない。"
    - "一次リストID116では、KM-LDで客先の漏電警報が異常発報した初期状況、地絡を確認したとの報告、配線の挟み込みを確認したとの記載を確認。詳細添付の存在に言及があるが、添付実体・内容は未確認。"
    - "ID116の電圧測定、遮断、絶縁測定、コネクタ操作による切り分けの具体的方法・識別情報は転載していない。挟み込みとの因果、処置、復旧/安全確認、再発有無は未確認。"
---

# ブレーカー種別・接地記述の安全レビュー保留

原資料には、MCCB/MCB・ELCB/ELBの用語と機能、NF/NVの機種別適用、客先遮断器との動作、接地共用に関する規程引用が含まれる。これらは安全・設計・規程上の主張であり、原資料本文だけでは正確性、現行性、対象機種、契約/物件条件を確認できないため、整備済みの技術知識として承認していない。

## レビュー待ち事項

ID214の客先側・エレベーター側ブレーカー容量関係、1台1回線との記載、および品目表の容量例は、別記録[[ELV_客先ブレーカー容量関係_ID214]]に出典記載として分離した。現行設計資料・品目表との照合前に選定基準として扱わない。

- 遮断器の名称、略語、商標および保護機能の正式な定義
- MRL/MR/非常用エレベーターごとの選定理由と、現行の設計・製品適用条件
- エレベーター側と客先側の保護協調、地絡時の遮断/警報挙動
- 原資料が引用する内線規程1350-13の適用版、正確な条文、例外と設計上の扱い
- MRLで接地線が1本の場合の扱いについて、原文中の未解決質問に対する所管部門の正式回答

SharePointの事例資料、PowerPoint、埋め込み画像は未確認。上記の所管レビューと根拠資料照合が完了するまで、本記録を選定・施工・結線・接地・検査・運転判断に使用しない。

## ID116の一次リスト記載

KM-LDの客先漏電警報が異常発報した初期状況と、地絡および配線の挟み込みを確認したとの報告がある。これは一次リストの記載内容であり、原因の独立確認や因果関係の確定を意味しない。処置後の復旧・安全確認・再発有無は確認できていない。詳細添付があるとの記載はあるが、添付実体と内容は未確認。電気測定・遮断・切り分けの具体的手順や配線/コネクタ識別情報は転載していない。

出典: `技術メモ【ELV】２/ELV-一般/ブレーカー（技術メモ）.md`（OneNote ID `2fd509b2-87aa-4e26-8cd6-6d51680accc1:1`）。本文確認日: 2026-10-09。