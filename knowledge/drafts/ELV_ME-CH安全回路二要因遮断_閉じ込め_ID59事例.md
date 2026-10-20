---
schema_version: 1
record_id: "elv-me-ch-dual-safety-circuit-interruption-entrapment-id59"
record_version: 1
title: "ME-CHの安全回路二要因遮断による閉じ込め報告（ID59）"
category: "不具合対応(ELV)"
record_type: "troubleshooting_case"
product: "エレベーター"
model_type:
  - "ME-CH"
document_number: ""
revision: ""
effective_date: ""
review_status: "in_review"
publication_status: "not_published"
classification: "unknown"
cloud_approval: "not_reviewed"
keywords:
  - "安全回路"
  - "閉じ込め"
  - "CWT"
  - "ガバナ張り車スイッチ"
  - "二要因"
related_ids: []
source_path: ""
source_filename: "技術情報リスト（協力会社展開用）.xlsx"
onenote_id: ""
attachment_paths: []
reference_links: []
document_references:
  - document_number: ""
    title: "EA97_短絡ピンの使用例抜粋"
    locator: "原リストの原因+対応欄に記載。本文未確認。"
    source_path: ""
evidence_sources:
  - source_id: "evidence-list-me-ch-dual-safety-circuit-interruption-059"
    source_type: "user_provided_extract"
    title: "首都工・不具合情報共有リスト: 二つの要因による安全回路遮断によりカゴが動かない件（ID59）"
    source_path: ""
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-09"
    supports:
      - "昇降路最上部での停止時に生じた閉じ込め、二つの安全回路遮断要因との原因報告、調査の振り返り、CWT側スイッチ復帰後の動作回復報告"
structured_data:
  equipment: "ME-CH（原リストの機種欄。個別設備への適用は未確認。）"
  symptom: "かご上UP運転時に昇降路最上部でULを検出して停止した際の振動で、CWT側GOV張り車スイッチが誤作動し、閉じ込めに至ったとの報告。工事使用中にガバナロープが伸びることを考慮して張り車位置を高く設定しており、張り車「予報」スイッチ検出用ボルトが近接して張り車「本」スイッチを作動させたと説明する。エラー表示は未確認。"
  cause: "原因欄は、かご上RUNスイッチOFFとCWT側張り車スイッチ遮断の二つを記録する。現象説明では、上部停止時の振動、工事使用中のロープ伸びを考慮した張り車位置、検出用ボルトの近接によるスイッチ誤作動を挙げる。これらはリスト上の原因説明で、構造・因果関係は独立確認していない。"
  verified_actions: []
  outcome: "調査欄では安全回路の区分を切り分けたと記録するが、短絡操作の箇所・順序・識別情報は転記しない。ゲート周りは電気的に問題なしとの報告後、ピットでCWT側張り車スイッチの遮断を確認し、復帰後にかごが動くようになったとする。これは原リストの結果報告であり、恒久的な位置調整・再発防止・対策後確認は記載されていない。"
---

# ME-CHの安全回路二要因遮断による閉じ込め報告（ID59）

首都工・不具合情報共有リストID59は、共有日欄を2021-11-30（Excel値44530の換算）とするME-CHの報告で、重要度は「中」、エラー表示は「未確認」。かご上UP運転時に昇降路最上部でULを検出して停止した際、振動によりCWT側GOV張り車スイッチが誤作動し、閉じ込めに至ったと記録する。

## 原因の報告

原文は、工事使用中のガバナロープ伸びを考慮して張り車位置を高く設定していたこと、張り車「予報」スイッチ用の検出ボルトが近接して張り車「本」スイッチを作動させたことを説明する。原因欄には別途、かご上RUNスイッチOFFとCWT側張り車スイッチ遮断の二要因を挙げる。いずれもリスト上の説明であり、独立した原因検証ではない。

## 調査経過と結果

進捗欄には、制御盤表示で安全回路が成立していないことを確認し、回路を区分して切り分けたとの記載がある。短絡操作の箇所・順序・端子識別は記録しない。調査時には単一原因と思い込んだこと、回路図を確認せずゲート側を原因と判断したことを問題点として挙げている。ゲート周りは電気的に問題なしとの報告後、ピットでCWT側張り車スイッチの遮断を確認し、復帰後にかごが動くようになったとする。

この結果はリスト上の一時的な動作回復報告である。張り車位置・検出部の是正、再発防止、対策後の確認結果は記載がなく、恒久対策完了とは判断できない。参考欄にEA97_短絡ピンの使用例抜粋が挙げられているが、内容は未確認であり、短絡による確認・復旧手順は本記録に含めない。本記録を安全回路の診断・運転・復旧手順として使用しない。