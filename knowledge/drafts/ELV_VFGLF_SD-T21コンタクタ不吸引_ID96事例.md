---
schema_version: 1
record_id: "elv-vfglf-sd-t21-contactor-not-picking-up-id96"
record_version: 1
title: "VFGLFのSD-T21コンタクタ不吸引報告（ID96）"
category: "不具合対応(ELV)"
record_type: "troubleshooting_case"
product: "エレベーター"
model_type:
  - "VFGLF"
document_number: ""
revision: ""
effective_date: ""
review_status: "unreviewed"
publication_status: "not_published"
classification: "unknown"
cloud_approval: "not_reviewed"
keywords:
  - "SD-T21"
  - "コンタクタ不吸引"
  - "#5"
  - "M5"
  - "432"
  - "452"
  - "MELD運転"
related_ids:
  - "elv-contactor-not-pulling-source-knowledge-id64"
source_path: ""
source_filename: "技術情報リスト（協力会社展開用）.xlsx"
onenote_id: ""
attachment_paths: []
reference_links: []
document_references: []
evidence_sources:
  - source_id: "evidence-list-case-id96"
    source_type: "user_provided_extract"
    title: "首都工・不具合情報共有リスト Excel出力 ID96"
    source_path: ""
    s3_uri: ""
    revision: "原本リスト未照合"
    accessed_at: "2026-10-09"
    supports:
      - "VFGLFのSD-T21コンタクタ不吸引症状、エラー表示、原因不明、返却品での再現と調査中の記載、一時対応案とMELD運転への影響"
structured_data:
  equipment: "VFGLF エレベーター"
  symptom: "SD-T21の#5コンタクタがピックアップしようとするが動作しないとの報告。エラー表示欄は432、452。原文には電圧確認に関する記載があるが、端子や電圧値は転載しない。"
  error_codes:
    - "432"
    - "452"
  cause: "原リストでは原因不明とされている。"
  verified_actions: []
  outcome: "進捗欄では、不発返却品を用いた検証で再現性があり、調査中と記載する。一時対応として#5とM5のコンタクタ入替案を挙げるが、作業実施は確認できない。原文は、この入替によりMELD運転が使用できなくなると注意している。"
---

# VFGLFのSD-T21コンタクタ不吸引報告（ID96）

## 概要

首都工・不具合情報共有リストID96は、VFGLFのSD-T21コンタクタについて、#5がピックアップしようとするものの動作しない事象を報告する。エラー表示欄は432、452。共有日は2022-02-14。

## 調査状況と原因

原リストの原因欄は「不明」。進捗欄には、不発返却品を用いた検証で再現性があり、調査中と記載されている。再現検証の詳細、原因の特定、調査の完了は確認できない。

## 対応案と機能影響

原リストは一時対応として#5とM5のコンタクタを入れ替える案を記載するが、実施の有無や結果は不明である。また、同欄は入替によってMELD運転が使用できなくなると注意している。これは原文にある影響の記録であり、現行機種への適用や作業の承認を示すものではない。

電圧値・端子名、確認方法、コンタクタの入替手順や作業条件は転載しない。備考欄にも、異なる電気状態では別原因が考えられるとの原文記載があるが、具体的な診断条件には展開しない。

## 関連資料

- [[ELV_コンタクタ不吸引の原文知識_ID64]]: ID64は、#5コンタクタの吸引指令がない場合に吸引しないという一般説明。ID96はVFGLFのSD-T21に関する個別の不吸引報告で、返却品での再現、原因不明、一時対応案を記録する。一般説明は本件原因の裏付けではない。
- [[不具合対応【ELV】/索引]]: ELV整備資料の索引。

## 出典・確認状態

- 出典: Excel出力のID96行にあるA列・E〜N列・O列。B/C/D列は参照していない。
- 端子・電圧値・電気測定、遮断、コンタクタ入替の具体的な作業手順は転記していない。
- 製造元調査の完了、原因、入替実施、MELD運転への実機影響、処置後の結果は未確認。現行性と専門レビューも未確認。
- 本記録は未レビューであり、故障診断、電気測定、部品交換、運転・復旧の手順を示すものではない。
