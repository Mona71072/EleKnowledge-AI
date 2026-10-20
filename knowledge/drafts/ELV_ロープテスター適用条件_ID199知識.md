---
schema_version: 1
record_id: "knowhow-elv-rope-tester-applicability-id199"
record_version: 1
title: "ロープテスター点検の適用条件（ID199）"
category: "技術メモ【ELV】２"
record_type: "knowhow"
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
  - "ロープテスター"
  - "ラング撚り"
  - "普通ロープA種"
  - "普通ロープE種"
  - "MRL"
  - "WOS工法"
  - "GAW工法"
source_path: "首都工・不具合情報共有リスト.xlsx"
source_filename: "首都工・不具合情報共有リスト.xlsx"
onenote_id: ""
related_ids: []
attachment_paths: []
reference_links: []
document_references:
  - document_number: ""
    title: "ワイヤロープの概要｜ワイヤロープ｜製品情報｜ジェイ-ワイテックス株式会社"
    locator: "ID199の参考欄に表示。リンク先未閲覧。Excel出力にURLターゲットなし"
    source_path: ""
  - document_number: ""
    title: "ロープテスター確認方法の添付資料"
    locator: "ID199の備考に言及。資料名・番号・版・実体未確認"
    source_path: ""
  - document_number: ""
    title: "各種呼び方と表示記号.PNG"
    locator: "ID199のサムネイル欄にファイル名あり。ファイル実体・本文との対応・内容未確認"
    source_path: ""
evidence_sources:
  - source_id: "evidence-list-elv-rope-tester-applicability-199"
    source_type: "vault_original"
    title: "首都工・不具合情報共有リスト: 高速機種におけるロープテスター実施について（ID199）"
    source_path: "首都工・不具合情報共有リスト.xlsx"
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-14"
    supports:
      - "ロープ種別・撚り・設計時期ごとの適用記載と部内対応の説明"
      - "MRL用ロープテスターのTR/WOS条件とGAW工法の適用外記載"
      - "過去の首都圏限定点検実施の背景記載"
structured_data:
  knowledge_items:
    - topic: "ラング撚りロープの点検適用"
      statement: "一次リストは、普通ロープA種・合成繊維芯ロープ・sfleX-ropeを適用なし、普通ロープE種を一部適用ありと記載する。E種は22/1/A以降の設計から適用なしとの注記があり、現状の適用はほとんどないとも述べる。A種/E種は素線の引張強さの種類で、A種の方がE種より大きいとの説明もある。"
      conditions:
        - "22/1/Aは原文の設計時期表記であり、暦日や改訂番号への読み替えはしていない。"
        - "一次リストのタイトルは高速機種、E列は全エレ機種。対象範囲の不一致は未解決。"
      exceptions:
        - "普通ロープの点検はE種のラング撚り以外は不要との部内説明があるが、客先要望がある場合を除く。"
      rationale: "過去に首都圏物件でラング撚りロープの早期破断が散発したため、首都圏地区で同ロープを対象に点検していたとの背景説明がある。現在の適用根拠とは確認されていない。"
      verification_status: "source_recorded"
      evidence_source_ids:
        - "evidence-list-elv-rope-tester-applicability-199"
    - topic: "MRL用ロープテスターの適用条件"
      statement: "一次リストはMRL用ロープテスターの実施条件をMRL（TR≧40m）かつWOS工法とし、GAW工法は適用外と記載する。"
      conditions:
        - "MRLであること。"
        - "TRが40m以上であること。"
        - "WOS工法であること。"
      exceptions:
        - "GAW工法は適用外との一次リスト記載。"
      rationale: "記載の背景・承認根拠は一次リストに示されていない。"
      verification_status: "source_recorded"
      evidence_source_ids:
        - "evidence-list-elv-rope-tester-applicability-199"
  specifications:
    - name: "MRL用ロープテスターのTR条件"
      value: "40以上"
      unit: "m"
      condition: "一次リスト記載のMRL・WOS工法条件。現行適用未確認。"
  source_notes:
    - "原リストの過去の首都圏限定点検、課内対応、MRL条件は別の記載として整理した。現行の地域/機種共通ルールと断定しない。"
    - "ロープ品目表で種別・撚りを確認するとの記載があるが、品目表・版・判定方法は未確認。試験手順・測定値・合否基準は記録していない。"
    - "『現状の適用はほとんどない』は原リストの記載時点に関する主張であり、記載日・現行性は未確認。"
    - "ロープテスター確認方法の添付とサムネイル画像は実体/内容未確認。添付として登録していない。"
    - "メーカーWeb資料名は参考欄にあるが、URLターゲットを一次リストExcelから取得できず、リンク先本文は未閲覧。"
---

# ロープテスター点検の適用条件（ID199）

## 過去の点検背景

首都工・不具合情報共有リストID199は、過去に首都圏物件でラング撚りロープの早期破断が散発したため、首都圏地区でラング撚りロープを対象にロープテスター点検を実施していたと説明する。これは過去の実施背景であり、現行の地域限定運用とは確認されていない。

## ロープ種別と設計時期

一次リストの記載は次のとおり。いずれも現行の設計・点検基準として独立確認していない。

- 普通ロープA種: 適用なし
- 普通ロープE種: 一部適用あり。22/1/A以降の設計から適用なしとの注記
- 合成繊維芯ロープ: 適用なし
- sfleX-rope: 適用なし

リストはA種/E種を素線の引張強さの種類として説明し、A種の方がE種より大きいとしている。また「現状の適用はほとんどない」と記載するが、その記載時点と現行性は未確認。「22/1/A」は原文表記のまま保持し、日付や改訂番号と解釈していない。タイトルは「高速機種」、機種欄は「全エレ機種」となっており、適用範囲は未解決。

課内対応の説明では、普通ロープはE種のラング撚り以外は点検不要とし、客先要望を例外としている。E種への切換えが最近との記載に基づき、ロープ種別・撚りを品目表で確認するよう述べるが、品目表の版と確認方法は未確認。

## MRL用ロープテスター

一次リストは、MRL用ロープテスターの条件を「MRL（TR≧40m）＋WOS工法」とし、GAW工法は適用外としている。40mは出典記載の条件であり、現行の対象・根拠・承認状態は未確認。

試験方法、測定値、合否基準は本記録に含めない。原文は確認方法の添付に言及するが、資料の実体・版・内容は未確認である。参考欄のメーカーWeb資料はタイトルのみ確認でき、Excel出力にリンク先URLは含まれていなかった。現行のロープ仕様・承認済み点検資料を確認するまで、試験の要否や実施判断に使用しない。