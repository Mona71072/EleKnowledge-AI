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
| Lists（推奨: ファイル名 + evidence の ID） | 390 | 301 | 89 | 重複一致 23 件 |
| Lists（拡張: + source_id 末尾） | 390 | 315 | 75 | 重複 33 件・要確認 |
| OneNote ページ | 1039 | 339 | 700 | 添付中心で実質空 240 件 |
| 下書き走査 | 627 | — | — | IMPORT-* を除く |

## Lists の一致ルール

各 `list_item_id` について、次のいずれかで下書きを探した。

1. ファイル名の `ID{番号}` / `_ID{番号}`
2. frontmatter の `evidence_sources` 題名中の `(ID{番号})` / `（ID{番号}）`（本文のエラーコードは対象外）
3. `evidence_sources` 内の `source_id` 末尾 `-{番号}` / `_{番号}`（拡張行。推奨行は 1–2 のみ）

機械可読な一覧:

- 一致（推奨）: [reconcile-lists-matched.tsv](./reconcile-lists-matched.tsv)
- 未整備（推奨）: [reconcile-lists-unmatched.tsv](./reconcile-lists-unmatched.tsv)
- 一致 / 未整備（拡張）: [reconcile-lists-matched-extended.tsv](./reconcile-lists-matched-extended.tsv) / [reconcile-lists-unmatched-extended.tsv](./reconcile-lists-unmatched-extended.tsv)

## OneNote の一致ルール

ページ frontmatter の `onenote_id` と、下書き frontmatter の `onenote_id` を小文字化して完全一致。

- 未一致 ID 一覧: [reconcile-onenote-unmatched-ids.txt](./reconcile-onenote-unmatched-ids.txt)

## 未整備 Lists のテーマ分布（参考）

| theme_bucket | 件数 |
| --- | ---: |
| `other` | 47 |
| `door` | 13 |
| `group_call` | 8 |
| `install_dim` | 7 |
| `power` | 6 |
| `display` | 3 |
| `comm` | 2 |
| `safety` | 2 |
| `clock_sets` | 1 |

## 優先してテーマ候補にしたい未整備（重要度 高 / 重要）

件数: **13**（原因・対策の断定はしていない）

| list_item_id | Model | 重要度 | タイトル（スナップショット） | theme_bucket |
| --- | --- | --- | --- | --- |
| 417 | VFGLF | ↑高 | I-CAN未接続により乗場バックアップできない | `group_call` |
| 416 | VFGH | ↑高 | 長周期振動感知器の短絡ジャンパについて | `other` |
| 413 | VFGH | 重要 | ピット点検口から出入り不可 | `install_dim` |
| 398 | AXIEZ-LINKS | 重要 | カゴが撓むことで照明安定化電源が地絡する件 | `power` |
| 394 | 全エレ機種 | ↑高 | ピットタラップの取付位置について | `install_dim` |
| 392 | VFGLF | ↑高 | ブレーキスイッチ設定不良で本スロー時カゴ運転不能の件 | `other` |
| 350 | VFGLF・VFGLB・VFGH | 重要 | UPS（アップピークサービス）動作しない件 | `other` |
| 345 | 全エレ機種 | ↑高 | LINKsでWOS工法に切り替える際にDL,DPコネクタが制御盤側に無い | `other` |
| 151 | VFGH | 重要 | P1基板不良によって、7SEGやWDTが点灯しなくなる | `display` |
| 137 | CM-MA | ↑高 | 首下長さの異なるビスを用い巻上機カバーを取付け、異音が発生 | `other` |
| 14 | 監視盤 | 重要 | （識別情報を含む可能性があるため情報管理確認まで保留） | `other` |
| 2 | CM-MA | ↑高 | かご内振動 | `other` |
| 1 | CM-MA | ↑高 | かご内振動 | `other` |

## 同一 list_item_id が複数下書きに付いた例（要確認）

ID 一致だけではどちらを正とするか決めない。担当者が確認する。

| list_item_id | record_ids | タイトル |
| --- | --- | --- |
| 411 | `elv-temporary-slow-issues, elv-vfglf-resolver-wiring-break-id411` | 巻上機レゾルバ線が断線しており、空回しが出来ない件 |
| 319 | `case-elv-new-axiez-first-maintenance-as-door-open-portable-unavailable-id172, elv-vfgr-manual-operation-disabled-run-state-id319` | VFGR機種かご上STのRUNトグルスイッチがOFF側に倒れており、運転ができない件 |
| 240 | `case-elv-mbs-connection-car-indicator-off-id240, catalog-elv-sensors-reference` | ＭBS接続するとカゴ内インジ消灯する件 |
| 233 | `elv-scu20-flash-rewrite-tool-compatibility-id233, elv-sw-change-reference` | SCU-20書換方法 |
| 221 | `case-elv-health-air-aircon-relay-misselection-damage-id221, catalog-elv-health-air-reference` | ヘルスエア併設エアコン動作不良の件 |
| 192 | `case-elv-emergency-junction-box-grommet-size-id192, catalog-elv3-emergency-elevator-reference` | 昇降路中間JBに取り付けるゴムブッシュサイズが不足する件 |
| 189 | `case-elv-vfglb-group-call-role-setting-id189, elv-group-operation-issues` | （識別情報を含む可能性があるため情報管理確認まで保留） |
| 187 | `case-elv-mrl-sets-position-write-direction-spec-id187, catalog-elv-sets-failure-reference` | SETS基準位置書き込みが完了しない件 |
| 179 | `case-elv-emergency-broadcast-low-volume-bgm-wiring-mismatch-id179, catalog-elv-bgm-emergency-broadcast-reference` | BGM結線ミスで非常放送の音量が小さい件 |
| 178 | `case-elv-signage-video-noise-signal-conversion-id178, catalog-elv-signage-case-reference` | デジタルサイネージ映像にノイズが発生する件 |
| 176 | `case-elv-normal-slow-unavailable-ground-connection-id176, elv-normal-slow-issues` | アースが結線されておらず、本スローがでない件 |
| 174 | `case-elv-vfglb-low-battery-meld-failure-entrapment-id174, elv-battery-issues-reference, elv-meld-operation-reference` | バッテリー電圧が低く、MELD動作に移行せず閉じ込めになってしまう。 |
| 171 | `case-elv-e-can-special-operation-hall-call-failure-id171, elv-group-operation-issues` | E-CAN通信不良によるNS動作しない件（+α＜群管理盤エラー見かた＞） |
| 167 | `case-elv-meld-contactor-damage-id167, elv-meld-operation-reference` | MELD の繋ぎ込み時、CP遮断をせずコンダクタが焼損した件 |
| 165 | `case-elv-new-axiez-loop-wire-removal-constraint-id165, catalog-elv-panel-terminal-wiring-reference` | 制御盤内ねじ式ターミナル変更でループ線が外せない件 |

## この台帳の範囲外

- 新しい Markdown 本文の生成
- 承認・公開・Bedrock KB への取り込み
- OneNote / Lists への書き戻し

次のステップ: 上記テーマ候補から **少数テーマ** を人が選び、選んだ ID だけ体系化（差分案）に進む。
