---
schema_version: 1
record_id: "catalog-elv-door-types-reference"
record_version: 3
title: "VFGLFの戸閉方式と戸閉装置型名の確認知見"
category: "技術メモ【ELV】２"
record_type: "knowhow"
product: "エレベーター"
model_type: ["VFGLF"]
document_number: ""
revision: ""
effective_date: ""
review_status: "in_review"
publication_status: "not_published"
classification: "unknown"
cloud_approval: "not_reviewed"
keywords: ["VFGLF", "戸閉方式", "戸閉装置", "型名", "副番"]
source_path: "技術メモ【ELV】２/ELV-一般/かご/戸の種類.md"
source_filename: "戸の種類.md"
onenote_id: "f21ec98f-05b1-4469-9118-e71fe031f4b6:1"
related_ids: []
attachment_paths: []
reference_links: []
document_references:
  - document_number: "C-18-A9-491.1-J"
    title: "ドア装置 据付・保守資料"
    locator: "原資料内社内PDFリンク。未閲覧"
    source_path: ""
evidence_sources:
  - source_id: "evidence-elv-door-types-001"
    source_type: "vault_original"
    title: "戸の種類"
    source_path: "技術メモ【ELV】２/ELV-一般/かご/戸の種類.md"
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-08"
    supports: ["戸閉方式とドア装置型名の確認に関する記載/図版があること"]
structured_data:
  knowledge_items:
    - topic: "原文に記載されたVFGLFのドア装置型名"
      statement: "原文は、かごの戸閉装置型名を正式名称KV4K-3（略称KV4）、乗場の戸閉装置型名を正式名称K4N-2（略称K4）として記載している。"
      conditions: ["VFGLFの参考資料内に記載された型名。現行性、対象機種/製造時期、個別設備への適用は未確認。"]
      exceptions: ["類似型名への読み替えや他機種への適用をしない。"]
      rationale: "かご側と乗場側の装置名称を混同せず、原文に記載された名称で確認できるようにする。"
      verification_status: "source_recorded"
      evidence_source_ids: ["evidence-elv-door-types-001"]
    - topic: "品番131の戸閉方式と表記CO"
      statement: "原文は品番131の戸閉方式で確認できると記載し、戸閉方式の表記としてCOを示している。COの意味や選択肢の定義は原文本文で説明されていないため展開していない。"
      conditions: ["原文にある確認案内と表記。対象設備での現行適用性は未確認。"]
      exceptions: ["品番131を資料番号や部品番号と混同しない。原文上は戸閉方式の確認に使う品番として記載。"]
      rationale: "資料番号、装置型名、品番、戸閉方式の表記を区別して扱う。"
      verification_status: "source_recorded"
      evidence_source_ids: ["evidence-elv-door-types-001"]
    - topic: "型名末尾の-2/-3は副番として扱う"
      statement: "原文は、戸閉装置型名の末尾にある-2/-3は副番であると注意している。型名照合時に副番を含む原表記を保持する。"
      conditions: ["原文に記載された当該型名に関する注意。別型式にも一般化しない。"]
      exceptions: ["副番が異なる型名を同一装置とみなさない。"]
      rationale: "基本型名だけに短縮すると、原文が区別している副番情報が失われるため。"
      verification_status: "source_recorded"
      evidence_source_ids: ["evidence-elv-door-types-001"]
  source_notes:
    - "原ノート自体の資料番号は記載されていないためdocument_numberは空欄。C-18-A9-491.1-Jは参照資料番号としてdocument_referencesに記録。"
    - "埋め込み画像1点は2026-10-09のVault全体画像名検索で実ファイルを確認できず、実在/内容とも未確認。参照PDFも未閲覧。"
    - "型名/品番/CO表記は原文に明記された情報として記録した。現行性、機種/製造時期適用、COの意味は未確認。"
---

# VFGLFの戸閉方式と戸閉装置型名の確認知見

## 原文に記載された識別情報

- 対象としてVFGLFが挙げられている。
- かご戸閉装置: 正式名称 `KV4K-3`、略称 `KV4`。
- 乗場戸閉装置: 正式名称 `K4N-2`、略称 `K4`。
- 原文は、品番 `131` の戸閉方式で確認できるとし、戸閉方式の表記 `CO` を記載している。COの定義や意味は説明されていない。
- `-2`、`-3`は副番との注意があるため、型名の原表記から省略しない。

## 適用上の注意

これらは原文に書かれた識別情報で、現在の製品体系や全VFGLF設備への適用を確認したものではない。型名の照合時には、かご側/乗場側、正式名称/略称、末尾副番、品番、戸閉方式表記を別の情報として扱う。類似型名から適用を推定したり、COを推測で展開したりしない。

## 未確認事項

- 埋め込み画像1点は2026-10-09のVault検索で実ファイルを確認できず、内容未確認。参照資料C-18-A9-491.1-Jの本文も未確認。
- 型名/戸閉方式の現行性、製造時期・仕様による差、対象設備への適用は未確認。
- 本ノートは型名・表記の読取り用知見であり、戸の調整、運転、検査、合否判定の手順ではない。

## 出典

- 原文: [[技術メモ【ELV】２/ELV-一般/かご/戸の種類]]（OneNote ID `f21ec98f-05b1-4469-9118-e71fe031f4b6:1`）
- 参照先: C-18-A9-491.1-J「VFGLF/ドア装置 LV5K-CO/2S, LV6K-CO/2S/SS 据付・保守資料」。本文未閲覧。
- 原文本文とリンク記載の確認日: 2026-10-08。添付所在の再確認日: 2026-10-09。
