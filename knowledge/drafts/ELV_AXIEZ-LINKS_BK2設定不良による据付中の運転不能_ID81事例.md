---
schema_version: 1
record_id: "elv-axiez-links-bk2-setting-installation-stop-id81"
record_version: 2
title: "AXIEZ-LINKSのBK2設定不良による据付中の運転不能報告（ID81）"
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
  - "BK2"
  - "ブレーキスイッチ"
  - "設定不良"
  - "据付中運転不能"
related_ids:
  - "elv-axiez-links-bk2-brake-contact-setting-id63"
  - "elv-axiez-links-brake-circuit-reinstatement-mismatch-id82"
source_path: ""
source_filename: "技術情報リスト（協力会社展開用）.xlsx"
onenote_id: ""
attachment_paths: []
reference_links: []
document_references:
  - document_number: ""
    title: "原リスト記載のC資料"
    locator: "確認方法の参照。具体資料名・番号、本文、版、適用性は未確認。"
    source_path: ""
evidence_sources:
  - source_id: "evidence-list-axiez-links-bk2-setting-081"
    source_type: "user_provided_extract"
    title: "首都工・不具合情報共有リスト: ブレーキスイッチ設定不良によるエレベーター運転不能の件（ID81）"
    source_path: ""
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-09"
    supports:
      - "据付中の1階運転不能、BK表示、調査段階ごとの所見、BK2設定不良との原因報告、調整後の解消報告"
structured_data:
  equipment: "AXIEZ-LINKS（原リストの機種欄。個別設備への適用は未確認。）"
  symptom: "据付中に1階でスロー・自動とも運転できなくなった。電源リセット後も復帰せず、エラー表示はなかった一方、乗場インジケーターに「BK」の点滅があったとの報告。"
  cause: "原リストはブレーキスイッチBK2側の設定不良を原因とする。ストッパーボルトのマーキングずれはなかったとの記載。原因・機構は独立確認していない。"
  verified_actions: []
  outcome: "原リストは、C資料記載の確認方法で設定不良を確認して調整し、不具合が解消したと報告する。実施・結果は原リスト上の報告であり独立確認していない。"
---

# AXIEZ-LINKSのBK2設定不良による据付中の運転不能報告（ID81）

首都工・不具合情報共有リストID81は、共有日欄を2021-12-22とするAXIEZ-LINKSの報告で、据付中に1階でスロー・自動とも運転できなくなったとしている。エラー表示はなかったが、乗場インジケーターに「BK」の点滅があったとの記載がある。

## 調査経過

原リストは、機器間の接続状態等の確認では問題が見つからず、基板交換で電気的な所見に変化があっても運転不能は解消しなかったと記録する。その後、ブレーキスイッチの取込み状態を確認した際、ブレーキ開放状態でBK2が取り込まれていなかったとの所見を記載している。個別のコネクタ・ピン・端子・電圧確認やブレーキ開放などの操作詳細は転載しない。

## 原因報告と結果

原因欄はブレーキスイッチBK2側の設定不良とし、ストッパーボルトのマーキングずれはなかったと記載する。C資料に記載された確認方法で設定不良を確認して調整し、不具合が解消したとの報告がある。原因・調整内容・結果は原リスト上の説明で、独立確認していない。C資料の具体名・番号・本文・版・対象適用性も未確認であり、本記録は診断・調整・運転復旧の手順ではない。

## ID63との関係

[[ELV_AXIEZ-LINKS_BK2接点設定不良_ID63事例]]もAXIEZ-LINKSのBK2設定不良と運転不能を扱うが、共有日と発生状況・調査経過が異なる別報告である。同一設備・同一発生事象とは確認できない。ID63には電圧説明の内部不整合があるが、ID81の記録へ混ぜず、それぞれの原文上の所見として保持する。共通するテーマの参照であり、原因・適用・是正方法の裏付けを意味しない。

[[ELV_AXIEZ-LINKS基板復帰後のブレーキ回路不一致_ID82事例]]も同じ機種・共有日でブレーキ関連の運転不能を扱うため、検索上の関連として参照する。ただしID82は基板復帰後のブレーキ回路対応誤りとの原因報告であり、本件のBK2設定不良とは異なる。同一設備・同一発生事象、共通原因、共通是正方法とは確認できない。

## 出典・確認履歴

- 原資料: 首都工・不具合情報共有リスト Excel出力のID81（A列・E〜N列・O列を確認。B/C/D列は参照していない）
- 確認状態: 原リスト抜粋に基づく内容整理。原本資料・C資料・現行適用・技術レビューは未確認。
- 安全上の制約: 配線・端子・コネクタ識別、電圧測定、ブレーキ開放、設定・調整・復旧の手順は含めない。
