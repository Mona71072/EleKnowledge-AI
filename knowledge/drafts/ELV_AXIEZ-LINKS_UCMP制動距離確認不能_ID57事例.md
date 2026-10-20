---
schema_version: 1
record_id: "elv-axiez-links-ucmp-braking-distance-unavailable-id57"
record_version: 1
title: "AXIEZ-LINKSのUCMP制動距離を確認できなかった事例（ID57）"
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
  - "制動距離"
  - "赤外線リモコン"
  - "UOT"
related_ids:
  - "elv-ucmp-error-handling"
source_path: ""
source_filename: "技術情報リスト（協力会社展開用）.xlsx"
onenote_id: ""
attachment_paths: []
reference_links: []
document_references:
  - document_number: "C-7-C3900-J"
    title: "技評資料（原リスト記載）"
    locator: "P.44、P.81～83"
    source_path: ""
evidence_sources:
  - source_id: "evidence-list-axiez-links-ucmp-braking-distance-057"
    source_type: "user_provided_extract"
    title: "首都工・不具合情報共有リスト: 赤外線リモコンのコマンド間違いによりUCMP制動距離が確認できない件（ID57）"
    source_path: ""
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-09"
    supports:
      - "UCMP制動距離の表示不成立と走行挙動の報告、確認モードの取り違えとの原因説明、技評記載の修正予定"
structured_data:
  equipment: "AXIEZ-LINKS（原リストの機種欄。個別設備への適用は未確認。）"
  symptom: "UCMP制動距離の確認時にインジケーターへ数値が表示されず、かごが急停止しなかったとの報告。ETP接続状態でかご内手動運転した場合はULを越えてUOTまで走行し、ETPを外した状態ではULで停止したと記載。ETPの状態表記は原文どおり「nomal側」。この記載は事例の症状であり、試験・運転方法ではない。"
  cause: "調整作業員が確認モードを取り違えたとの原文説明。リストはLINKsのUCMP制動確認に「Bモード5/C」を用いるところ、現地ではAXIEZ用の「Bモード0/A」で確認していたとする。そのため制動距離を確認できず、LINKsのBモード0/AはUOT動作点測定用のためUOTまで走行した可能性があると推定する。詳細動作は原文でも未確認。モード識別子は原因報告の記録であり、設定・操作指示ではない。"
  verified_actions: []
  outcome: "進捗欄には実施状態と対応手順を確認したとあるが、確認結果の具体的な回答は記載されていない。技評のUCMP制動距離項目にBモード0/Aと記載されていたため修正予定との報告がある。修正実施・修正後の試験結果は記載されていない。"
---

# AXIEZ-LINKSのUCMP制動距離を確認できなかった事例（ID57）

首都工・不具合情報共有リストID57は、共有日欄を2021-11-11（Excel値44511の換算）とするAXIEZ-LINKSの事例である。重要度は「重要」、エラー表示は「なし」。UCMP制動距離確認時に数値が表示されず、かごが急停止しなかったと報告する。ETP接続状態ではULを越えてUOTまで走行し、ETPを外した状態ではULで停止したとの条件差も記載される。ETP状態の「nomal」は原文表記を保持した。

## 調査・原因の記載

進捗欄には、実施状態と対応手順を確認したとある。原因欄は、LINKsのUCMP制動確認に用いるモードと、現地でAXIEZ用として選択されたモードの取り違えを原因としている。さらにLINKsのBモード0/AはUOT動作点測定用であるためUOTまで走行した可能性を示すが、詳細動作は原文でも未確認である。これらのモード識別子は出典の原因説明を特定するために限って記載し、確認・運転手順にはしない。

## 対応状況と未確認事項

技評のUCMP制動距離項目にBモード0/Aと記載されていたため修正予定との記載がある。修正済みか、修正後に制動距離を確認できたかは不明であり、完了とは扱わない。参考資料欄はC-7-C3900-J P.44、P.81～83を挙げるが、資料本文・版・当該ページの内容は未確認である。

既存の[[ELV_UCMP異常]]はVFGH/VFGLFの異常表示に関する別資料で、モデル範囲と現象が異なる。UCMPという共通テーマの参照先として関連付けるが、ID57の事例原因やモードを裏付ける根拠とはしない。本記録をUCMP試験・運転・安全判定の手順として使用しない。