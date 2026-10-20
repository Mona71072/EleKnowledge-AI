---
schema_version: 1
record_id: "elv-vibration-case-reference"
record_version: 4
title: "エレベーター振動事例の症状分類知見"
category: "不具合対応(ELV)"
record_type: "knowhow"
product: "エレベーター"
model_type:
  - "VHGH（原文表記）"
  - "CM-MA"
document_number: ""
revision: ""
effective_date: ""
review_status: "in_review"
publication_status: "not_published"
classification: "unknown"
cloud_approval: "not_reviewed"
keywords:
  - "振動"
  - "走行状態"
  - "周波数解析"
  - "原因候補"
source_path: "不具合対応【ELV】/振動/振動例.md"
source_filename: "振動例.md"
onenote_id: "a8c15103-95f4-4d08-897a-403d412bffb5:97"
related_ids:
  - "elv-vibration-location-method"
  - "elv-vibration-diagnostic-tool"
attachment_paths: []
reference_links: []
document_references:
  - document_number: "EA-097-00-01-H"
    title: "EA-097-00-01-H"
    locator: ""
    source_path: ""
evidence_sources:
  - source_id: "evidence-elv-vibration-case-original"
    source_type: "vault_original"
    title: "振動例（原文）"
    source_path: "不具合対応【ELV】/振動/振動例.md"
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-01"
    supports:
      - "振動時の調整候補・条件に関する原文メモ"
  - source_id: "evidence-list-car-vibration-guide-roller-frequency-001-002"
    source_type: "user_provided_extract"
    title: "首都工・不具合情報共有リスト: CM-MAかご内振動の周波数事例（ID1・2）"
    source_path: ""
    s3_uri: ""
    revision: ""
    accessed_at: "2026-10-09"
    supports:
      - "リストID1の連続前後振動、約5.25Hzとガイドローラー回転周波数5.3Hzの報告、および経過観察の記載"
      - "リストID2の連続振動、4.25Hz/8.5Hz付近とガイドローラー回転周波数4.24Hzの報告"
structured_data:
  knowledge_items:
    - topic: "起動ショックと走行中/着床前後の振動を分けて記録する"
      statement: "原文の『調整』欄は、かご内無負荷でのUP走行着床間際またはDN走行起動直後に、起動ショックとは異なる振動が目立つ事例を記載する。原文表現は『加速度は計上5~10数Hz』『10gal以上』で、別にモーター電流周波数の2倍の周期のかご振動にも触れている。"
      conditions: ["かご内無負荷", "UP走行の着床間際、またはDN走行の起動直後。測定方法・対象量・対象機種の現行適用は未確認。"]
      exceptions: ["症状の一致だけで原因・部品・調整対象を決定しない。周波数表現を推定で補正しない。"]
      rationale: "起動時のショックと走行状態に依存する別の振動を一括りにせず、観測条件を明確にして担当者へ引き継ぐため。"
      verification_status: "source_recorded"
      evidence_source_ids: ["evidence-elv-vibration-case-original"]
    - topic: "モーター電流周波数との関係は原因確定ではなく観測事項として扱う"
      statement: "原文は、モーター電流周波数の2倍周期に対応するかご振動も事例として記載している。個別設備での測定根拠・再現性・因果関係は確認されていないため、観測した周波数関係として記録し、原因確定には使わない。"
      conditions: ["原文にある振動事例の記述。測定条件と機種適用は未確認。"]
      exceptions: ["ゲイン調整などの設定変更は本記録から指示しない。"]
      rationale: "相関に見える特徴を、検証されていない原因説明へ読み替えないため。"
      verification_status: "source_recorded"
      evidence_source_ids: ["evidence-elv-vibration-case-original"]
    - topic: "CM-MAの連続前後振動とガイドローラー周波数の近似（リストID1）"
      statement: "リストID1は、工事使用開始時のPMT測定で、UP/DN共に約5.25Hzの連続前後振動があったと報告する。かご側ローラーガイドシューの回転周波数を5.3Hzとし、ガイドローラーが起因すると推察している。後段には、振動が同程度に収まったため静観したとの記載がある。"
      conditions: ["機種はCM-MA。工事使用開始時、かご前後方向、UP/DN。測定条件の詳細・現行適用は未確認。"]
      exceptions: ["周波数の近似と原因説明はリスト上の報告であり、因果関係・再現性を独立検証していない。静観の記載を判断基準や推奨として扱わない。"]
      rationale: "症状・運転方向・報告された周波数関係を、推定原因や対応状態と区別して保持するため。"
      verification_status: "source_recorded"
      evidence_source_ids: ["evidence-list-car-vibration-guide-roller-frequency-001-002"]
    - topic: "CM-MAの連続振動とガイドローラー周波数の近似（リストID2）"
      statement: "リストID2は、PMT測定でかご前後左右方向に連続振動があり、4.25Hzおよび8.5Hz付近の成分を確認したと報告する。かご側ガイドローラーの回転周波数を4.24Hzとし、ガイドローラーが起因すると考えている。"
      conditions: ["機種はCM-MA。前後左右方向の連続振動。測定条件の詳細・現行適用は未確認。"]
      exceptions: ["周波数の近似と原因説明はリスト上の報告であり、因果関係・再現性を独立検証していない。調整作業欄は手順として転載しない。"]
      rationale: "周波数成分と原文の原因推定を、承認済み診断や調整手順と混同しないため。"
      verification_status: "source_recorded"
      evidence_source_ids: ["evidence-list-car-vibration-guide-roller-frequency-001-002"]
    - topic: "コンペンずれ補償に関する原文の調整候補と条件"
      statement: "原文は、コンペンレスの場合、または起動秤調整後も中間階以外で起動ショックが許容値を超え、終端階に近づくほど大きくなる場合に、コンペンずれ補償の調整を挙げている。あわせて、本運転により昇降路ロス補正も自動で設定されると記載している。"
      conditions:
        - "コンペンレスの場合。"
        - "起動秤調整後、中間階以外で起動ショックが原文上の許容値を超える場合。"
        - "原文では終端階に近いほど起動ショックが大きくなる傾向を条件に含む。"
      exceptions: ["許容値の数値・測定方法、対象機種、現行性は未確認。設定変更の指示ではない。"]
      rationale: "原文が特定の起動ショック条件に対する調整候補として記載。"
      verification_status: "source_recorded"
      evidence_source_ids: ["evidence-elv-vibration-case-original"]
    - topic: "起動ショックが残る場合の原文記載"
      statement: "原文は、起動ショック調整とコンペンずれ補償を行っても起動ショックが取り切れない場合に、起動秤ゲインの微調整を挙げている。"
      conditions: ["原文に記載された調整後の状態。現行手順・設定値・適用機種は未確認。"]
      exceptions: ["微調整の方法・量を本記録から推定しない。"]
      rationale: "原文に記載された候補と前提条件を保持するため。"
      verification_status: "source_recorded"
      evidence_source_ids: ["evidence-elv-vibration-case-original"]
    - topic: "VHGH自動運転速度変更モードの原文注記"
      statement: "原文の注意欄は、VHGHの全自動運転速度変更モードをMON1/0=9/D（VTOP）と記し、速度変更で状況が変わるか確認してもよいかもしれない、という提案を記載している。"
      conditions: ["VHGHは原文表記。対象機種・モード定義・現行適用は未確認。"]
      exceptions: ["操作・設定の実施を指示するものではなく、本記録から変更しない。"]
      rationale: "原文の提案と不確実な語尾を、確定手順・推奨へ変換せず保持するため。"
      verification_status: "source_recorded"
      evidence_source_ids: ["evidence-elv-vibration-case-original"]
  source_notes:
    - "原文の5~10数Hz、10gal以上、MON1/0=9/Dと調整候補は、条件付きの旧メモ記載として保持。測定定義、許容値、機種適用、設定方法は未確認。"
    - "原文にある調整候補と条件の関係は記録するが、具体的な設定変更・測定・調整の手順へ再構成しない。"
    - "『VHGH』は原文表記。VFGHへの修正・同一視はしていない。"
    - "原文は画像2点とEA-097-00-01-H.pdfを参照する。2026-10-09時点でVault内に画像実体を確認できず、PDF本文も照合していない。"
    - "リストID1・2のローラー周波数と振動周波数の近似は、出典に記載された観測・推定として追記。測定条件、因果関係、現行性は未確認。"
    - "リストID1の結果欄には同程度に収まったため静観との記載があるが、判断基準・推奨として扱わない。調整作業欄は手順として転載していない。"
    - "リストの参考資料欄にあるEA-97、ATHO07006、ATHO07047は資料種別・実体・本文・現行性を未確認のため、内容根拠として登録していない。"
---

# エレベーター振動事例の症状分類知見

原文の「調整」欄は、かご内無負荷、UP走行の着床間際またはDN走行起動直後に目立つ振動として「加速度は計上5~10数Hz」「10gal以上」と記載し、モーター電流周波数の2倍周期のかご振動にも触れている。語句・数値は原文の表記を保持しており、測定方法・対象量・許容基準・現行適用性は未確認である。

## 原文にある調整候補と条件

| 原文の候補 | 原文に記載された条件・補足 |
| --- | --- |
| コンペンずれ補償の調整 | コンペンレスの場合、または起動秤調整後も中間階以外で起動ショックが許容値を超え、終端階に近づくほど大きくなる場合。原文には本運転で昇降路ロス補正も自動設定されるとの補足がある。 |
| 起動秤ゲイン微調整 | 起動ショック調整・コンペンずれ補償後も起動ショックが取り切れない場合。 |
| 全自動運転速度変更モードの確認 | 注意欄に「VHGH」「MON1/0=9/D（VTOP）」と、速度変更で状況が変わるか確認してもよいかもしれない旨がある。原文の提案表現を保持。 |
| DC-CTゲイン調整に関する記載 | かご内無負荷でUP走行着床間際/DN走行起動直後に、原文表現の周波数・gal値の振動、またはモーター電流周波数の2倍周期の振動がある場合に記載。 |

これらは過去メモが候補として挙げた関係の記録であり、現行の設定指示や作業手順ではない。症状・測定法・許容値・機種適用は承認済み資料と所管担当者で確認する。

症状を比較・引継ぎする際は、走行状態、方向、位置、負荷条件、起動ショックとの区別、測定条件を分ける。原文にない測定方法や因果関係は補わない。

## 首都工・不具合情報共有リストの振動事例

### ID1: CM-MAの連続前後振動

工事使用開始時にPMTで測定した事例として、UP/DN共に約5.25Hzの連続前後振動が報告されている。リストはローラーガイドシューの回転周波数を5.3Hzと記し、ガイドローラー起因と推察する。結果欄には振動が同程度に収まったため静観したとの記載がある。これらはリスト上の観測・推定・対応状態であり、因果関係や判断の妥当性を確認したものではない。

### ID2: CM-MAの連続振動

PMT測定の報告では、かご前後左右方向に連続振動があり、4.25Hzと8.5Hz付近の成分が記されている。ガイドローラーの回転周波数は4.24Hzとされ、リストはローラー起因と考えている。周波数関係は出典上の記載であり、測定条件・因果関係・再現性・現行適用は未確認である。調整作業欄の内容は作業手順として転記しない。

両事例の周波数の近さだけで原因を確定したり、別機種・設備へ一般化したりしない。測定条件と現行仕様は承認済み資料および所管担当者で確認する。

この記録は過去メモにある症状条件と調整候補を検索・照合するための知識である。特定設備の原因確定、設定変更、部品調整や作業判断を単独で支えるものではない。機種・現場に適用できる測定方法や対処は、現行の承認済み資料と専門担当者に確認する。原文に記載された機種表記は未照合のため、そのまま保持している。

## 出典

- 原文ノート: [[不具合対応【ELV】/振動/振動例]]
- 原文は画像2点とEA-097-00-01-H.pdfを参照するが、2026-10-07時点で指定パスに実ファイルを確認できない。過去の画像確認記録は再検証できず、PDF本文・原文の機種適用性・現行性も未確認。