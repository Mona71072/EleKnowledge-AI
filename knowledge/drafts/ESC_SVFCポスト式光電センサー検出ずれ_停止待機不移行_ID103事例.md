---
schema_version: 1
record_id: "esc-svfc-post-photoelectric-sensor-standby-id103"
record_version: 1
title: "SVFCポスト式光電センサーの検出ずれによる停止待機不移行報告（ID103）"
category: "不具合対応【ESC】"
record_type: "troubleshooting_case"
product: "エスカレーター"
model_type:
  - "SVFC"
document_number: ""
revision: ""
effective_date: ""
review_status: "in_review"
publication_status: "not_published"
classification: "unknown"
cloud_approval: "not_reviewed"
keywords:
  - "ポスト式光電センサー"
  - "光軸ずれ"
  - "停止待機"
  - "自動運転"
  - "SVFC"
source_path: ""
source_filename: "技術情報リスト（協力会社展開用）.xlsx"
onenote_id: ""
related_ids:
  - "esc-low-speed-standby-not-entered-sensor-setting-id301"
attachment_paths: []
reference_links: []
document_references:
  - document_number: "C-60-631-VF30.4-J"
    title: "原リストID103に記載された参考資料"
    locator: "本文未閲覧。版・適用範囲未確認。"
    source_path: ""
  - document_number: ""
    title: "エスが低速待機に移行しない（原リスト備考の関連事例）"
    locator: "リストID301を確認済み。低速待機不移行の別報告で、同一案件/共通原因か未確認。"
    source_path: ""
evidence_sources:
  - source_id: "evidence-list-case-id103"
    source_type: "user_provided_extract"
    title: "首都工・不具合情報共有リスト Excel出力 ID103"
    source_path: ""
    s3_uri: ""
    revision: "原本リスト未照合"
    accessed_at: "2026-10-09"
    supports:
      - "SVFC自動運転で停止待機へ移行しなかった症状、原文記載のセンサー検出状態、原因説明、センサー調整後に停止待機へ移行したとの報告"
structured_data:
  equipment: "SVFC エスカレーター"
  symptom: "自動運転中、所定時間が経過しても停止待機へ移行しなかった。エラー表示はなしとの報告。"
  error_codes: []
  cause: "原リストは、ポスト上部右側の受光センサーのずれを原因として記載する。原因の独立確認および他要因の除外は未確認。"
  verified_actions: []
  outcome: "原リストは、受光センサーの角度を調整した後、自動運転で所定時間後に停止待機へ移行したと報告する。作業の独立確認、継続性、再発有無は未確認。"
---

# SVFCポスト式光電センサーの検出ずれによる停止待機不移行報告（ID103）

## 概要

首都工・不具合情報共有リストID103は、SVFCエスカレーターの自動運転で、所定時間が経過しても停止待機へ移行しなかった事例を報告する。共有日は2022-04-13、エラー表示は「なし」と記載されている。

## 調査時の所見と原因報告

原リストは、ポスト各所のセンサー検出状態を確認した経過を記録し、上部右側の受光センサーが検出状態だったこと、同センサーのずれを原因として判断したことを記載する。表示器の具体的な確認モード・LED操作や設定値は転載しない。センサー状態と停止待機不移行との因果、他要因の有無は独立確認されていない。

## 対応と結果

原リストは、受光センサーの角度を調整した後、自動運転で所定時間後に停止待機へ移行したと報告する。具体的な調整方法や確認操作は記録しない。作業実施・結果の独立確認、継続性、再発有無は未確認。

## 関連資料

- 参考資料として「C-60-631-VF30.4-J」の記載がある。本文・版・適用範囲は未確認。
- 備考にリストID301「エスが低速待機に移行しない」への参照がある。ID301は内容確認済みだが、ID103の停止待機不移行とは異なる症状の報告であり、同一案件か、原因・条件・結果が共通するかは判断していない。
- 不具合対応【ESC】の「停止距離」原資料にもC-60-631-VF30.4-Jの記載があるが、同資料はモニター値と基準値の説明であり、ID103のセンサー不具合を裏付ける資料として扱わない。

## 出典・確認状態

- 出典: Excel出力のID103行にあるA列・E〜N列・O列。B/C/D列は参照していない。
- 具体的な確認モード、LED操作、センサー調整操作・手順は転載していない。
- 参考資料本文、ID301との事象関係、原因の独立確認、対策後の継続性、現行性、技術・安全レビューは未確認。
- 本記録はレビュー中・未公開であり、点検・調整・運転の手順や判定基準を示すものではない。
