---
schema_version: 1
record_id: "elv-axiez-links-independent-auto-ucmp-cpu-fault-id79"
record_version: 1
title: "AXIEZ-LINKS独立自動状態での電源喪失後UCMP-CPU故障検出（ID79）"
category: "不具合対応(ELV)"
record_type: "troubleshooting_case"
product: "エレベーター"
model_type:
  - "AXIEZ-LINKS"
document_number: ""
revision: ""
effective_date: ""
review_status: "in_review"
publication_status: "not_published"
classification: "unknown"
cloud_approval: "not_reviewed"
keywords:
  - "UCMP"
  - "独立UCMP-CPU故障"
  - "エラー614"
  - "独立自動"
  - "NRS"
  - "MELD"
related_ids:
  - "elv-ucmp-error-handling"
source_path: ""
source_filename: "技術情報リスト（協力会社展開用）.xlsx"
onenote_id: ""
attachment_paths: []
reference_links: []
document_references:
  - document_number: ""
    title: "原リストが今後注記予定とするC資料"
    locator: "具体的な資料番号・該当箇所は未記載。注記が実際に発行されたか未確認。"
    source_path: ""
evidence_sources:
  - source_id: "evidence-list-axiez-links-independent-auto-ucmp-079"
    source_type: "user_provided_extract"
    title: "首都工・不具合情報共有リスト: 電源入り切りによりUCMP故障を検出する件（ID79）"
    source_path: ""
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-09"
    supports:
      - "独立自動状態での電源リセット後にエラー614・NRSとなった報告、UCMP故障検出条件と運転状態差に関する原リスト説明、C資料への注記予定"
structured_data:
  equipment: "AXIEZ-LINKS"
  symptom: "独立自動状態で電源リセットを行ったところ、独立UCMP-CPU故障を検出してNRSとなったとの報告。エラー表示欄は614。"
  error_codes:
    - "614（原リストは独立UCMP-CPU故障として記載。適用するコード一覧との照合は未実施。）"
  cause: "原リストは、ランディングオープンまたは戸開リレベル動作後、ゲートスイッチが一度もONにならないまま電源を喪失すると独立UCMP-CPU故障を検出すると説明する。全自動状態では、特定のMELD成立条件により検出を回避する一方、独立自動状態では戸が開いたままになるため検出に至るとの説明。いずれも原リスト上の機構説明で、独立確認していない。"
  verified_actions: []
  outcome: "原リストは電源リセット時の運転状態条件を示すが、操作手順は転載しない。EDモードではUCMPエラーがリセットされないとの注意、今後C資料に注記する方向との記載がある。注記の発行・適用範囲、故障後の復帰結果、再発状況は未確認。"
---

# AXIEZ-LINKS独立自動状態での電源喪失後UCMP-CPU故障検出（ID79）

首都工・不具合情報共有リストID79は、共有日欄を2021-12-20（Excel値44550の換算）とするAXIEZ-LINKSの報告で、独立自動状態で電源リセット後に独立UCMP-CPU故障を検出し、NRSとなったと記録する。エラー表示欄は614。

## 原リストの検出条件説明

原リストは、ランディングオープンまたは戸開リレベル動作後、ゲートスイッチが一度もONにならないまま電源を喪失した場合に独立UCMP-CPU故障を検出すると説明する。発生階に固定の決まりはないとしつつ、最上階での発生報告が多いとも記載する。

全自動状態では、所定のMELD成立条件によりゲートスイッチがONとなり故障を検出しない一方、独立自動状態ではMELDへ切り換わっても戸が開いたままとなり故障検出に至る、という状態差も原文に記載される。これらは原リスト上の機構説明で、実機・現行仕様との照合は未実施。

## 注意・進捗

原リストは、乗場からの電源リセット時に手動状態を前提とする注意を示すが、これは未検証の原文記載であり、ここでは操作指示として扱わない。スイッチ識別、電源リセット操作、復旧手順は転載しない。EDモードではUCMPエラーがリセットされないとの注意も原文にあるが、適用条件は未確認。

今後C資料に注記する方向との記載があるものの、資料番号・発行・実施状況は不明。故障後の復帰結果も記載されていない。

## 関連資料

[[ELV_UCMP異常]]はVFGH/VFGLFのUCMP異常に関する原文記録で、コード614という共通点がある。機種、検出条件、適用範囲は本件と異なり、相互の根拠や手順として流用しない。