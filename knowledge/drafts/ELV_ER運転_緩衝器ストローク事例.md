schema_version: 1
record_id: "knowhow-elv-er-buffer-stroke-stop-point-example"
record_version: 2
title: "ER運転の停止位置と緩衝器ストロークに関する事例"
category: "技術メモ【ELV】１"
record_type: "knowhow"
product: "エレベーター"
model_type: ["VFGH"]
document_number: ""
revision: "Vault原文および首都工・不具合情報共有リスト記載。参照資料の版・現行性未確認"
effective_date: ""
review_status: "in_review"
publication_status: "not_published"
classification: "unknown"
cloud_approval: "not_reviewed"
keywords: ["ER運転", "DL-A", "DOT-A", "緩衝器", "ストローク", "停止位置"]
source_path: "技術メモ【ELV】１/ELV-付加仕様②/ER運転.md"
source_filename: "ER運転.md; 技術情報リスト.xlsx"
onenote_id: "c551ee58-7bc9-4565-873c-7b6626d8a4e9:1"
related_ids: ["tech-elv-er-operation-reference"]
attachment_paths: []
reference_links: []
document_references: []
evidence_sources:
  - source_id: "evidence-elv-er-buffer-stroke-original-001"
    source_type: "vault_original"
    title: "ER運転"
    source_path: "技術メモ【ELV】１/ELV-付加仕様②/ER運転.md"
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-09"
    supports: ["ER適用基準の原文表記、DL-A/DOT-Aの機能区分、緩衝器全圧縮時を基準にした300mm/500mmの位置関係"]
  - source_id: "evidence-elv-er-buffer-stroke-extract-id379"
    source_type: "user_provided_extract"
    title: "首都工・不具合情報共有リスト: ER運転の動作点について"
    source_path: ""
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-09"
    locator: "リストID 379（Excel出力のID欄）。原文内リンクの題名とID=379が一致するが、リンク先自体は別途取得・閲覧していない"
    supports: ["VFGHの緩衝器ストローク424mm、緩衝器圧縮前の停止、約80mmのランバイと、原文に記録された原因説明", "電気設計へ設計思想を確認し、現状で問題ないとしたとの進捗欄記載"]
structured_data:
  knowledge_items:
    - topic: "ER運転の停止位置は緩衝器ストロークとの位置関係で確認する"
      statement: "Vault原文はER適用基準を『PD＞3000』と記し、単位は示していない。原文の説明ではDOT-Aは緩衝器全圧縮時の当たり面から300mm、DL-AはDOT-Aより200mm上側で、同じ当たり面から500mmの位置とされる。リストのVFGH事例はストローク424mmの緩衝器を使用し、緩衝器を圧縮する前に停止、ランバイ約80mmと報告している。500mm−424mm=76mmとなり、報告された約80mmと算術上整合する。"
      conditions: ["原文のPD＞3000は単位不記載のまま保持。", "リストID 379の機種欄はVFGH。", "位置寸法は参照点を『緩衝器全圧縮時の当たり面』とする原文記載。", "76mmは原文値からの算術比較で、設備の測定結果ではない。"]
      exceptions: ["原文資料・リスト事例は現行設計標準、許容差、現場設定値として独立検証されていない。", "現物の緩衝器、取付寸法、ランバイ、改訂、機種適用は未確認。", "本記録は寸法設定、ER操作、安全回路試験または合否判断の手順ではない。"]
      rationale: "緩衝器の全圧縮位置を基準にした停止位置と、緩衝器ストロークを分けて照合することで、緩衝器が圧縮される前に停止する事例の見方を共有する。"
      verification_status: "source_recorded"
      evidence_source_ids: ["evidence-elv-er-buffer-stroke-original-001", "evidence-elv-er-buffer-stroke-extract-id379"]
  source_notes:
    - "Vault原文の機能記載、原文に示された位置関係、リストID 379のVFGH事例を出典別に区別した。リスト題名/IDはVault原文のSharePointリンク題名/IDと一致するが、リンク先の本文や正式版は独立取得していない。"
    - "『PD＞3000』は原文表記のままとし、PDの展開語・単位を推定していない。300mm/500mm等は原文記載値、424mm/約80mmはリスト記載値として保持。"
    - "76mmは500mm−424mmの算術結果であり、原文が明記する規格値・安全余裕ではない。"
    - "共有リスト進捗欄は、電気設計に設計思想を確認し当該状況で問題ないと確認したと記載。回答の詳細、承認範囲、当該設備の寸法・図面は独立確認しておらず、他設備の安全判断へ一般化しない。"
    - "ER運転操作、スイッチ操作、回路・安全条件、図面/変数値の具体操作は記載していない。"
---

# ER運転の停止位置と緩衝器ストロークに関する事例

## 事例の要点

リストのVFGH事例では、緩衝器ストローク424mmの構成で、ER運転時に緩衝器が圧縮される前に停止し、ランバイが約80mmだったと報告されている。

進捗欄には、電気設計へER運転の設計思想を確認し、現状で問題ないと確認したとの記録がある。これは当該事例についてのリスト上の報告であり、設計回答の詳細や承認範囲、他設備への適用を独立確認したものではない。

Vault原文は、緩衝器全圧縮時の当たり面を基準に、DOT-Aの動作点を300mm、DL-Aの動作点を500mmと記し、両者の差を200mmとしている。リスト事例の数値を用いた算術比較では、500mm−424mm=76mmとなり、約80mmという報告に近い。ただし、これは原文の数値同士の整合を見る計算であり、個別設備の寸法測定や安全余裕の検証ではない。

## 原文条件の保持

Vault原文のER適用基準は「PD＞3000」と記されているが、単位は示されていない。PDの意味・単位を補わず、別資料で現行性と対象範囲を確認する必要がある。300mm/500mmの位置関係も原文記載であり、現行設計標準や作業基準と確認したものではない。

本記録は、停止位置と緩衝器ストロークを関連づけて過去事例を読むための知識メモである。現物の取付条件、機種適用、寸法測定、ER運転、設定変更、安全回路試験、合否判定には使用しない。
