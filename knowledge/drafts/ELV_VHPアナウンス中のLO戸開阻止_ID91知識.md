---
schema_version: 1
record_id: "elv-vhp-announcement-landing-open-inhibit-id91"
record_version: 1
title: "VHP仕様でアナウンス中にランディングオープンしない動作（ID91）"
category: "不具合対応(ELV)"
record_type: "knowhow"
product: "エレベーター"
model_type:
  - "VFGLF"
  - "VFGLB"
  - "VFGH"
document_number: ""
revision: ""
effective_date: ""
review_status: "unreviewed"
publication_status: "not_published"
classification: "unknown"
cloud_approval: "not_reviewed"
keywords:
  - "VHP"
  - "視覚障害者仕様"
  - "ランディングオープン"
  - "戸開阻止"
  - "アナウンス"
related_ids:
  - "catalog-elv-relevel-landing-open-reference"
source_path: ""
source_filename: "技術情報リスト（協力会社展開用）.xlsx"
onenote_id: ""
attachment_paths: []
reference_links: []
document_references:
  - document_number: "JEAS-515E"
    title: "原リストが到着階床名の報知について引用する規格"
    locator: ""
    source_path: ""
evidence_sources:
  - source_id: "evidence-list-knowhow-id91"
    source_type: "user_provided_extract"
    title: "首都工・不具合情報共有リスト Excel出力 ID91"
    source_path: ""
    s3_uri: ""
    revision: "原本リスト・要目資料・規格本文未照合"
    accessed_at: "2026-10-09"
    supports:
      - "VHP仕様でのアナウンス中の戸開阻止、ランディングオープンへの影響、原文上の理由と適用注意"
structured_data:
  knowledge_items:
    - topic: "VHP仕様におけるアナウンス中の戸開阻止とランディングオープン"
      statement: "リストID91は、VHP仕様で全自動運転中にランディングオープンしない場合があると説明する。戸開・到着階床のアナウンスが発報中は戸開を阻止するため、アナウンスの完了前にはランディングオープンしないことがあるという原文上の機能説明である。"
      conditions:
        - "原リストの対象機種欄はVFGLF、VFGLB、VFGH。個別機種の仕様差・適用範囲は未確認。"
        - "原リストは、アナウンス発報中の戸開阻止を説明している。"
      exceptions:
        - "原文にはLINKsではランディングオープンが標準仕様との注記があるが、対象機種欄との対応関係は示されていない。"
        - "二か国語アナウンス等で発報時間が長い場合、戸開待ち時間が長くなる可能性を原文が注意している。"
      rationale: "原文は、戸開アナウンス完了前の戸開を防ぐ危険防止と、到着階床名の報知を到着前に完了するというJEAS-515Eへの言及を理由に挙げる。規格本文・適用条件は未確認。"
      verification_status: "source_recorded"
      evidence_source_ids:
        - "evidence-list-knowhow-id91"
  source_notes:
    - "共有日は2022-02-04。進捗欄、エラー表示、個別現場の動作確認記録はない。"
    - "設計思想の確認先として営業設計への照会を案内する記載があるが、照会実施・回答は記載されていない。"
    - "リスト記載は原文上の仕様説明であり、個別設備の故障診断や現行仕様の保証ではない。"
    - "参照された要目資料とJEAS-515E本文、版、現行適用は未確認。"
---

# VHP仕様でアナウンス中にランディングオープンしない動作（ID91）

## 概要

首都工・不具合情報共有リストID91は、VHP（視覚障害者仕様）適用時に、全自動運転でランディングオープン（LO）が行われない場合があると記録する。これはリスト上では不具合原因ではなく、アナウンス発報中に戸開を阻止する機能による動作として説明されている。

## 原文上の動作説明

リストは、戸開アナウンスまたは到着階床アナウンスが鳴動中は、その順序にかかわらず戸開を阻止すると説明する。戸開アナウンスについては、案内完了前の戸開を危険防止の理由として挙げる。到着階床アナウンスについては、到着前に案内を完了する趣旨でJEAS-515Eを引用し、その完了を待つため戸開を阻止すると説明している。

この説明によれば、アナウンスが完了するまでLOしないことがあり、二か国語アナウンス等で発報時間が長い場合は戸開待ち時間も長くなる可能性がある。これは原リスト記載の機能説明であり、現行仕様・個別設備の動作確認済み事実とは区別する。

## 適用範囲・例外

- Excelの機種欄はVFGLF・VFGLB・VFGH。
- 同じ行には「LINKsはLO標準仕様」との注記があるが、機種欄との対応や条件は示されていない。各機種へ一律に適用しない。
- JEAS-515Eおよび参照要目資料の本文・版・現行性は未確認。
- 設計思想について営業設計へ確認するよう記載されているが、照会・回答の実施記録はない。

## 関連資料

- [[ELV_リレベル_LO_参照記録]]: リレベルおよびランディングオープンに関する原資料の所在・概要を示すcatalog。本記録のVHP条件や戸開阻止理由を裏付けるものではない。
- [[不具合対応【ELV】/索引]]: ELV整備資料の索引。

## 出典・確認状態

- 出典: Excel出力のID91行にあるA列・E〜N列・O列。B/C/D列は参照していない。
- 原本リスト、要目資料、JEAS-515E本文、各機種への適用差、現行性は未確認。
- 本記録は未レビューであり、実機の故障判断、戸開タイミングの調整、仕様説明の対外回答根拠として使用しない。
