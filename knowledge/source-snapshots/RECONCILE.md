---
snapshot_type: "source_reconciliation_ledger"
generated_on: "2026-10-19"
review_status: unreviewed
publication_status: not_published
cloud_approval: not_reviewed
---

# 出典と整備済み下書きの突き合わせ台帳

> ID の一致だけを記録する。症状・原因の正誤判定、承認、RAG 公開は含まない。
> 正本の運用境界は [knowledge-markdown-foundation.md](../../docs/features/development/knowledge-markdown-foundation.md) と develop 上の [design-2026-10-01-knowhow-flywheel.md](https://github.com/yukiworkspace/EleKnowledge-AI/blob/develop/docs/design-2026-10-01-knowhow-flywheel.md)（段階A）を参照。

## 突き合わせの意味

- **一致**: 同じ `list_item_id` または `onenote_id` が、既存の `knowledge/drafts/` にすでに紐づいている。新規事例カードは作らない。
- **未整備**: スナップショット上の ID が、下書き側に見つからない。体系化候補として人がテーマを選ぶ。
- **本文比較はしない**: ファイル名・frontmatter・根拠題名の ID のみ。

## 件数サマリ

| 対象 | 総数 | 一致 | 未整備 | 備考 |
| --- | ---: | ---: | ---: | --- |
| Lists（不具合情報共有リスト） | 390 | 277 | 113 | 重複一致 18 件 |
| Lists（保守: ファイル名・`(ID)` のみ） | 390 | 207 | 183 | 参考比較 |
| OneNote ページ | 1039 | 339 | 700 | 本文ほぼ空 213 件 |
| 下書き走査 | 627 | — | — | IMPORT-* を除く |

## Lists の一致ルール

各 `list_item_id` について、次のいずれかで下書きを探した。

1. ファイル名の `ID{番号}` / `_ID{番号}`
2. frontmatter の `evidence_sources` 題名中の `(ID{番号})`
3. `source_id` 末尾の `-{番号}` / `_{番号}`（上表の保守行は 1–2 のみ）

機械可読な一覧:

- 一致: [reconcile-lists-matched.tsv](./reconcile-lists-matched.tsv)
- 未整備: [reconcile-lists-unmatched.tsv](./reconcile-lists-unmatched.tsv)

## OneNote の一致ルール

ページ frontmatter の `onenote_id` と、下書き frontmatter の `onenote_id` を小文字化して完全一致。

- 未一致 ID 一覧: [reconcile-onenote-unmatched-ids.txt](./reconcile-onenote-unmatched-ids.txt)

## 未整備 Lists のテーマ分布（参考）

| theme_bucket | 件数 |
| --- | ---: |
| `other` | 65 |
| `door` | 12 |
| `group_call` | 10 |
| `power` | 9 |
| `install_dim` | 7 |
| `safety` | 4 |
| `display` | 3 |
| `comm` | 2 |
| `clock_sets` | 1 |

## 優先してテーマ候補にしたい未整備（重要度 高 / 重要）

件数: **20**（原因・対策の断定はしていない）

| list_item_id | Model | 重要度 | タイトル（スナップショット） | theme_bucket |
| --- | --- | --- | --- | --- |
| 417 | VFGLF | ↑高 | I-CAN未接続により乗場バックアップできない | `group_call` |
| 416 | VFGH | ↑高 | 長周期振動感知器の短絡ジャンパについて | `other` |
| 413 | VFGH | 重要 | ピット点検口から出入り不可 | `install_dim` |
| 398 | AXIEZ-LINKS | 重要 | カゴが撓むことで照明安定化電源が地絡する件 | `power` |
| 394 | 全エレ機種 | ↑高 | ピットタラップの取付位置について | `install_dim` |
| 392 | VFGLF | ↑高 | ブレーキスイッチ設定不良で本スロー時カゴ運転不能の件 | `other` |
| 227 | — | ↑高 | 遮煙の大臣認定がある場合は火災管制運転とMELD（または戸閉保証用バッテリー盤）が必須！！ | `door` |
| 151 | VFGH | 重要 | P1基板不良によって、7SEGやWDTが点灯しなくなる | `display` |
| 137 | CM-MA | ↑高 | 首下長さの異なるビスを用い巻上機カバーを取付け、異音が発生 | `other` |
| 118 | — | 重要 | 書換プログラム４　エラー対応 | `other` |
| 83 | AXIEZ-LINKS | ↑高 | アース線を異なるターミナル(128番)に結線してしまい、制御回路の絶縁不良の件 | `other` |
| 54 | KM-LD | 重要 | 客先電源の相間違い{PWFH(欠相・逆相)}により運転ができない件 | `power` |
| 53 | CM-MA | ↑高 | 空回し時にM1カード焼損の件 | `other` |
| 50 | AXIEZ-LINKS | 重要 | 巻上機の空回しが実施できない件 | `other` |
| 46 | ME-CH | ↑高 | 相順の接続違いによって空回しができない件 | `other` |
| 33 | AXIEZ-LINKS | ↑高 | 映像分配器箱をレールに取り付ける腕の数について | `other` |
| 19 | CM-LB | ↑高 | 建築仮設分電盤ブレーカートリップ件 | `other` |
| 14 | 監視盤 | 重要 | （識別情報を含む可能性があるため情報管理確認まで保留） | `other` |
| 13 | VFGH | ↑高 | VIP運転時、客先タブレットで運転灯が光らない | `other` |
| 11 | AXIEZ-LINKS | 重要 | FMS実施時にかごが動かない件 | `other` |

## 同一 list_item_id が複数下書きに付いた例（要確認）

ID 一致だけではどちらを正とするか決めない。担当者が確認する。

| list_item_id | record_ids | タイトル |
| --- | --- | --- |
| 411 | `elv-temporary-slow-issues, elv-vfglf-resolver-wiring-break-id411` | 巻上機レゾルバ線が断線しており、空回しが出来ない件 |
| 240 | `case-elv-mbs-connection-car-indicator-off-id240, catalog-elv-sensors-reference` | ＭBS接続するとカゴ内インジ消灯する件 |
| 233 | `elv-scu20-flash-rewrite-tool-compatibility-id233, elv-sw-change-reference` | SCU-20書換方法 |
| 221 | `case-elv-health-air-aircon-relay-misselection-damage-id221, catalog-elv-health-air-reference` | ヘルスエア併設エアコン動作不良の件 |
| 190 | `field-work-1-rail-joint-inspection-criteria-relaxation-trial-id190, nexiez-vfglf-car-door-quality-check-english-notes` | 【情報共有】レール継ぎ目据付簡素化目的による現場試行 |
| 187 | `case-elv-mrl-sets-position-write-direction-spec-id187, catalog-elv-sets-failure-reference` | SETS基準位置書き込みが完了しない件 |
| 183 | `case-elv-construction-use-door-reversal-detection-id183, elv-e-series-mrl-supply-voltage-conditions-id84` | 工事使用中、稀にドア開閉中に戸反転する件 |
| 181 | `elv-automatic-operation-issues, nexway-vfgh-control-panel-quality-check-english-notes` | 客先電線が細くAC電源低下で、フルロードでE-STOPする件 |
| 180 | `case-elv-wos-suppression-diode-failure-id180, nexiez-vfglf-car-door-quality-check-english-notes` | コンダクタのダイオード不良により、かご運転不能になった件 |
| 179 | `case-elv-emergency-broadcast-low-volume-bgm-wiring-mismatch-id179, catalog-elv-bgm-emergency-broadcast-reference` | BGM結線ミスで非常放送の音量が小さい件 |
| 177 | `case-elv-vfglb-terminal-switch-mechanical-failure-id177, nexway-vfgh-control-panel-quality-check-english-notes` | 自動運転で最上階に着床後、起動不能になる件 |
| 171 | `case-elv-e-can-special-operation-hall-call-failure-id171, elv-group-operation-issues` | E-CAN通信不良によるNS動作しない件（+α＜群管理盤エラー見かた＞） |
| 167 | `case-elv-meld-contactor-damage-id167, elv-meld-operation-reference` | MELD の繋ぎ込み時、CP遮断をせずコンダクタが焼損した件 |
| 149 | `case-elv-vfglf-scu20-gs3-setting-mismatch-id149, elv-group-operation-issues` | エレベーターとSCU-20盤との通信ができない件 |
| 93 | `elv-vfglf-lhh-32x-display-board-procurement-id93, nexiez-vfglf-car-door-quality-check-english-notes` | 表示基板が手配される件 |

## この台帳の範囲外

- 新しい Markdown 本文の生成
- 承認・公開・Bedrock KB への取り込み
- OneNote / Lists への書き戻し

次のステップ: 上記テーマ候補から **少数テーマ** を人が選び、選んだ ID だけ体系化（差分案）に進む。
