---
schema_version: 1
record_id: "esc-zj-safety-circuit-status-mismatch-buzzer-case"
record_version: 2
title: "ZJ型ESCの安全回路異常表示と運転不能事例"
category: "不具合対応(ESC)"
record_type: "troubleshooting_case"
product: "エスカレーター"
model_type:
  - "ZJ型ESC"
document_number: ""
revision: ""
effective_date: ""
review_status: "in_review"
publication_status: "not_published"
classification: "unknown"
cloud_approval: "not_reviewed"
keywords:
  - "安全回路"
  - "SD＿SAFL"
  - "運転不能"
  - "ブザー"
related_ids:
  - "esc-zj2s-dc1-dc2-relay-seating-id65"
source_path: ""
source_filename: ""
onenote_id: ""
attachment_paths: []
reference_links: []
document_references: []
evidence_sources:
  - source_id: "evidence-list-zj-esc-safety-circuit-status-mismatch-052"
    source_type: "user_provided_extract"
    title: "首都工・不具合情報共有リスト: ESC突然運転できない事例（ID52）"
    source_path: ""
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-09"
    supports:
      - "安全スイッチの確認中にブザーが継続し運転できなくなった症状、SD＿SAFL表示、下部安全回路側への絞り込み、後続介入後に正常化したとの記載"
structured_data:
  equipment: "ZJ型ESC"
  symptom: "安全スイッチの動作確認中、スイッチを作動させていないにもかかわらずブザーが鳴り続け、ESCが運転できなくなったとの報告。"
  error_codes:
    - "SD＿SAFL（原リストは安全回路SAFL切断中と説明。現行コード定義は未確認。）"
  cause: "制御盤では該当するA接点表示や通常のエラー表示を確認できなかった一方、別の状態表示では安全回路切断中と表示されたとする。原リストは下部安全回路側に原因箇所を絞り込んだが、コネクタ・ピンに異常は見られなかったと記載する。原因部品・因果関係は独立確認していない。"
  verified_actions: []
  outcome: "コネクタ周辺への介入後に正常状態へ戻ったとの報告。具体的な安全回路短絡による切り分け、対象スイッチ/コネクタ識別、接続操作は記録しない。復旧原因・再発状況・現行適用は未確認。"
---

# ZJ型ESCの安全回路異常表示と運転不能事例

首都工・不具合情報共有リストID52は、安全スイッチの動作確認中、スイッチを作動させていないにもかかわらずブザーが鳴り続け、ESCが運転できなくなったと報告する。制御盤では該当する接点表示や通常のエラー表示を確認できなかった一方、別の状態表示には `SD＿SAFL` が現れ、リストは安全回路SAFL切断中を示すと説明している。このコードの現行定義は未確認である。

## 調査経過と対応結果

リストは調査の結果、下部安全回路側に原因箇所を絞り込んだとするが、コネクタやピンに異常は見られなかったと記載する。その後のコネクタ周辺への介入後、正常状態に戻ったとの報告がある。原因部品、介入内容、復旧との因果関係は独立確認していない。

安全回路を意図的に短絡して箇所を絞る操作、対象スイッチ/コネクタの識別、接続操作、サービス機器の使用方法は記録しない。本記録は事例検索用であり、安全回路の試験・診断・復旧手順ではない。

[[ESC_ZJ2S_DC1_DC2リレー不完全嵌合_ID65事例]]も安全回路遮断による運転不能報告だが、ZJ2Sのリレー不完全嵌合に関する別事例であり、本件とは症状・原因・機種範囲が異なる。