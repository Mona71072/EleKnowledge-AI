# scope-review queue

> 自動生成ファイルです。直接編集せず、次のコマンドで再生成します。
>
> `python scripts/knowledge/build_scope_review_queue.py`

Senpai の機種フィルタ（UI「機種（任意）」）は、**人が適用範囲を確認したカード**（`scope_status: verified`）だけを除外対象にします。Lists の機種欄は信頼できないため、未検証のカードは除外されません。このキューは未検証カードを確認の優先度順に並べたものです。

## 訂正の手順

1. 一覧のカードを開き、Lists・OneNote・KB の原文で実際の適用範囲を確認する。
2. `model_scope` を正しい内容に直す（例: VFGH と書かれていても全エレベーターに当てはまるなら `lists_model_label: ["全エレ機種"]` にし、機種名のみの `product_lines` を外す）。
3. 確認できたら `model_scope` に次の 3 行を足す（`verified` は確認者と確認日が必須。欠けるとビルドが失敗する）。

```yaml
model_scope:
  scope_status: verified
  scope_verified_by: <確認した人の名前>
  scope_verified_at: YYYY-MM-DD
```

詳細は [CONTRACT.md](../../CONTRACT.md) と [APPLICABILITY-TAXONOMY.md](../../registry/APPLICABILITY-TAXONOMY.md) を参照。

## 件数

| 区分 | 件数 |
| --- | ---: |
| P1 矛盾の疑い（機種名があるのに適用範囲が広いと読める） | 2 |
| P2 機種を名指し・未検証（検証すれば機種フィルタで除外対象になる） | 95 |
| P3 制御方式・略称のみ・未検証 | 194 |
| P4 汎用ラベル／空（対応不要の情報） | 107 |
| 検証済み（キュー対象外） | 0 |
| 読み込み不可 | 0 |

## P1 矛盾の疑い（機種名があるのに適用範囲が広いと読める）（2 件）

| カード | タイトル | product_lines | lists_model_label | control_methods | 理由 | 推奨対応 |
| --- | --- | --- | --- | --- | --- | --- |
| [KH-LINKS-WOS-DLDP-345](../../cards/practice-guides/KH-LINKS-WOS-DLDP-345.md) | GAWからWOSへの切替でDL・DPコネクタが無い | — | — | — | エレベーター機種名あり、かつ may_apply_to に「全エレ」 | 適用範囲を確認する。全機種対応なら product_lines / lists_model_label を全エレ機種へ直し、特定機種のみなら may_apply_to / scope_note を直して、検証済みにする |
| [KH-ROLLER-GUIDE-CAR-VIBRATION-1-2](../../cards/case-summaries/KH-ROLLER-GUIDE-CAR-VIBRATION-1-2.md) | ローラーガイド系 かご内振動（ガイドローラー周波数と PMT 一致） | Nexcube | CM-MA | VFGH | エレベーター機種名あり、かつ may_apply_to に「一般」 | 適用範囲を確認する。全機種対応なら product_lines / lists_model_label を全エレ機種へ直し、特定機種のみなら may_apply_to / scope_note を直して、検証済みにする |

## P2 機種を名指し・未検証（検証すれば機種フィルタで除外対象になる）（95 件）

| カード | タイトル | product_lines | lists_model_label | control_methods | 理由 | 推奨対応 |
| --- | --- | --- | --- | --- | --- | --- |
| [KH-ALL-NSHR-TOUCHLESS-329](../../cards/practice-guides/KH-ALL-NSHR-TOUCHLESS-329.md) | NSHR 時 — 他社 CR とタッチレス併用 | AXIEZ-LINKs | AXIEZ-LINKS | — | 機種名あり（AXIEZ-LINKs） | product_lines が正しければ検証済みにする（以後、他機種を選んだときに除外される） |
| [KH-AXIEZ-LIGHTING-GROUND-398](../../cards/case-summaries/KH-AXIEZ-LIGHTING-GROUND-398.md) | AXIEZ-LINKS かごの撓みで照明電源が地絡する | AXIEZ-LINKs | — | VFGLF | 機種名あり（AXIEZ-LINKs） | product_lines が正しければ検証済みにする（以後、他機種を選んだときに除外される） |
| [KH-AXIEZ-LINKS-BACK-CALL-DISABLE-338](../../cards/practice-guides/KH-AXIEZ-LINKS-BACK-CALL-DISABLE-338.md) | AXIEZ-LINKs 背後呼び登録無効（CID-S / CID-SA） | AXIEZ-LINKs | AXIEZ-LINKS | VFGLF | 機種名あり（AXIEZ-LINKs） | product_lines が正しければ検証済みにする（以後、他機種を選んだときに除外される） |
| [KH-AXIEZ-LINKS-DOOR-DRIVE-31-434](../../cards/case-summaries/KH-AXIEZ-LINKS-DOOR-DRIVE-31-434.md) | ドア駆動基板エラー31と CLT/OLT（基板上表示確認） | AXIEZ-LINKs | AXIEZ-LINKS | VFGLF | 機種名あり（AXIEZ-LINKs） | product_lines が正しければ検証済みにする（以後、他機種を選んだときに除外される） |
| [KH-AXIEZ-LINKS-ROPE-STRING-VIB-111](../../cards/case-summaries/KH-AXIEZ-LINKS-ROPE-STRING-VIB-111.md) | かご吊り車 — 弦振動による微振動・騒音 | — | AXIEZ-LINKS | LINKS | 機種名あり（） | product_lines が正しければ検証済みにする（以後、他機種を選んだときに除外される） |
| [KH-AXIEZ-WOS-SHORT-CONNECTOR-90](../../cards/practice-guides/KH-AXIEZ-WOS-SHORT-CONNECTOR-90.md) | AXIEZ-LINKS WOS用短絡コネクタの取外し誤り（本スロー後） | — | — | — | 機種名あり（） | product_lines が正しければ検証済みにする（以後、他機種を選んだときに除外される） |
| [KH-CM-LB-DOOR-SHORT-LATCH](../../cards/practice-guides/KH-CM-LB-DOOR-SHORT-LATCH.md) | CM-LB 戸短検出（ラッチあり）の注意 | Nexcube | — | VFGLB-K | 機種名あり（Nexcube） | product_lines が正しければ検証済みにする（以後、他機種を選んだときに除外される） |
| [KH-CM-LB-TEMP-POWER-TRIP-19](../../cards/case-summaries/KH-CM-LB-TEMP-POWER-TRIP-19.md) | CM-LB 仮設分電盤トリップ（RA1 被覆地絡） | Nexcube | CM-LB | VFGLB-K | 機種名あり（Nexcube） | product_lines が正しければ検証済みにする（以後、他機種を選んだときに除外される） |
| [KH-CM-MA-3CAR-GROUP-2C2BC-384](../../cards/case-summaries/KH-CM-MA-3CAR-GROUP-2C2BC-384.md) | 3台群管理が 2C-2BC 状態になる（CM-MA） | Nexcube | CM-MA | VFGH | 機種名あり（Nexcube） | product_lines が正しければ検証済みにする（以後、他機種を選んだときに除外される） |
| [KH-ESC-ALL-B-SENSOR-SLOW-STANDBY-301](../../cards/case-summaries/KH-ESC-ALL-B-SENSOR-SLOW-STANDBY-301.md) | エス B センサ — 低速待機に移行しない | escalator | 全エス機種 | — | 機種名あり（escalator） | product_lines が正しければ検証済みにする（以後、他機種を選んだときに除外される） |
| [KH-ESC-FREQ-PARAM-427](../../cards/case-summaries/KH-ESC-FREQ-PARAM-427.md) | エスカ周波数/RSW 不一致で運転不能（E-1 305 等） | escalator | 全エス機種 | SVFC | 機種名あり（escalator） | product_lines が正しければ検証済みにする（以後、他機種を選んだときに除外される） |
| [KH-ESC-SVFC-ECO-SPEED-SW-339](../../cards/practice-guides/KH-ESC-SVFC-ECO-SPEED-SW-339.md) | SVFC 省エネ — 速度切替 LOW/HIGH の速度 | escalator | SVFC | SVFC | 機種名あり（escalator） | product_lines が正しければ検証済みにする（以後、他機種を選んだときに除外される） |
| [KH-ESC-SVFC-P2-FWR-TOGGLE-325](../../cards/case-summaries/KH-ESC-SVFC-P2-FWR-TOGGLE-325.md) | SVFC P2 FWR トグル — E-1 001 / P1P2 通信 | escalator | SVFC | SVFC | 機種名あり（escalator） | product_lines が正しければ検証済みにする（以後、他機種を選んだときに除外される） |
| [KH-ESC-SVFC-PHOTO-STANDBY-103](../../cards/case-summaries/KH-ESC-SVFC-PHOTO-STANDBY-103.md) | SVFC ポスト式光電ずれ — 停止待機に移行しない | escalator | SVFC | SVFC | 機種名あり（escalator） | product_lines が正しければ検証済みにする（以後、他機種を選んだときに除外される） |
| [KH-ESC-SVFC-STEP-CHAIN-GAP-326](../../cards/case-summaries/KH-ESC-SVFC-STEP-CHAIN-GAP-326.md) | SVFC チェーン隙間 — DN 異音ゴンゴン | escalator | SVFC | SVFC | 機種名あり（escalator） | product_lines が正しければ検証済みにする（以後、他機種を選んだときに除外される） |
| [KH-ESC-SVFC-TRACE-PUTTY-263](../../cards/practice-guides/KH-ESC-SVFC-TRACE-PUTTY-263.md) | SVFC — トレースデータ採取（PuTTY） | escalator | SVFC | SVFC | 機種名あり（escalator） | product_lines が正しければ検証済みにする（以後、他機種を選んだときに除外される） |
| [KH-ESC-SVFC-UVW-WIRING-298](../../cards/case-summaries/KH-ESC-SVFC-UVW-WIRING-298.md) | SVFC UVW 結線ミス — E-1 001 / E-2 061 | escalator | SVFC | SVFC | 機種名あり（escalator） | product_lines が正しければ検証済みにする（以後、他機種を選んだときに除外される） |
| [KH-ESC-U-HANDRAIL-TENSION-430](../../cards/case-summaries/KH-ESC-U-HANDRAIL-TENSION-430.md) | u形 — 弓ローラー手摺テンション調整手順 | escalator | u形 | — | 機種名あり（escalator） | product_lines が正しければ検証済みにする（以後、他機種を選んだときに除外される） |
| [KH-ESC-U-MODEL-CATALOG](../../cards/practice-guides/KH-ESC-U-MODEL-CATALOG.md) | u形エスカレーター機種略称（索引） | escalator | — | SVFC | 機種名あり（escalator） | product_lines が正しければ検証済みにする（以後、他機種を選んだときに除外される） |
| [KH-ESC-ZJ2-BLOCK-WELD-136](../../cards/case-summaries/KH-ESC-ZJ2-BLOCK-WELD-136.md) | ZJ2 エストラス上ブロック浮上り防止溶接忘れ | escalator | ZJ2 | — | 機種名あり（escalator） | product_lines が正しければ検証済みにする（以後、他機種を選んだときに除外される） |
| [KH-ESC-ZJ2S-DC-RELAY-65](../../cards/case-summaries/KH-ESC-ZJ2S-DC-RELAY-65.md) | ZJ2S DC1/DC2 リレー嵌合不良 — E.0.0 | escalator | ZJ2S | — | 機種名あり（escalator） | product_lines が正しければ検証済みにする（以後、他機種を選んだときに除外される） |
| [KH-HEALTH-AIR-AC-TIMER-221](../../cards/case-summaries/KH-HEALTH-AIR-AC-TIMER-221.md) | ヘルスエア併設 — タイマーリレー 24V 誤品と AC 基板 | — | AXIEZ-LINKS | AXIEZ-LINKS | 機種名あり（） | product_lines が正しければ検証済みにする（以後、他機種を選んだときに除外される） |
| [KH-HOIST-SCREW-LENGTH-137](../../cards/case-summaries/KH-HOIST-SCREW-LENGTH-137.md) | 巻上機ロープカバー取付ビスの首下長さ違いによる異音 | Nexcube | CM-MA | VFGH | 機種名あり（Nexcube） | product_lines が正しければ検証済みにする（以後、他機種を選んだときに除外される） |
| [KH-KE-WF-CABIN-CAMERA-FLICKER-134](../../cards/case-summaries/KH-KE-WF-CABIN-CAMERA-FLICKER-134.md) | かご内カメラ映像 — 照度によるフリッカー | AXIEZ | KE-WF | — | 機種名あり（AXIEZ） | product_lines が正しければ検証済みにする（以後、他機種を選んだときに除外される） |
| [KH-KM-LD-K-DOOR-ROLLER-72](../../cards/case-summaries/KH-KM-LD-K-DOOR-ROLLER-72.md) | K型ドア ドライブローラー取付金向き不良（KM-LD） | Nexcube | KM-LD | VFGLB-WB | 機種名あり（Nexcube） | product_lines が正しければ検証済みにする（以後、他機種を選んだときに除外される） |
| [KH-LINKS-BK-SW-SETTING-81](../../cards/case-summaries/KH-LINKS-BK-SW-SETTING-81.md) | LINKs — ブレーキスイッチ設定不良で運転不能 | — | AXIEZ-LINKS | — | 機種名あり（） | product_lines が正しければ検証済みにする（以後、他機種を選んだときに除外される） |
| [KH-LINKS-BK2-SETTING-63](../../cards/case-summaries/KH-LINKS-BK2-SETTING-63.md) | LINKs — BK2 設定不良で B・K 表示・不走 | — | AXIEZ-LINKS | — | 機種名あり（） | product_lines が正しければ検証済みにする（以後、他機種を選んだときに除外される） |
| [KH-LINKS-BLOCKING-DEVICE-G6-27](../../cards/case-summaries/KH-LINKS-BLOCKING-DEVICE-G6-27.md) | LINKs — カゴ固定装置未接続で本スロー不可 | — | AXIEZ-LINKS | — | 機種名あり（） | product_lines が正しければ検証済みにする（以後、他機種を選んだときに除外される） |
| [KH-LINKS-BPS-SWITCH-335](../../cards/practice-guides/KH-LINKS-BPS-SWITCH-335.md) | AXIEZ-LINKs — BPS スイッチ適用（索引） | — | AXIEZ-LINKS | — | 機種名あり（） | product_lines が正しければ検証済みにする（以後、他機種を選んだときに除外される） |
| [KH-LINKS-BRAKE-DRUM-RUST-299](../../cards/practice-guides/KH-LINKS-BRAKE-DRUM-RUST-299.md) | LINKs — 巻上ブレーキドラム発錆対応 | — | AXIEZ-LINKS | — | 機種名あり（） | product_lines が正しければ検証済みにする（以後、他機種を選んだときに除外される） |
| [KH-LINKS-CAR-SWAY-DGN-368](../../cards/case-summaries/KH-LINKS-CAR-SWAY-DGN-368.md) | LINKs — 長時間停止後 UP でかご揺すり（DGN 調整） | — | AXIEZ-LINKS | — | 機種名あり（） | product_lines が正しければ検証済みにする（以後、他機種を選んだときに除外される） |
| [KH-LINKS-CAR-TOP-G4-HAND-16](../../cards/case-summaries/KH-LINKS-CAR-TOP-G4-HAND-16.md) | LINKs — G4 誤挿でかご上 HAND スロー不可 | — | AXIEZ-LINKS | — | 機種名あり（） | product_lines が正しければ検証済みにする（以後、他機種を選んだときに除外される） |
| [KH-LINKS-CID-DS-DUAL-142](../../cards/case-summaries/KH-LINKS-CID-DS-DUAL-142.md) | CID-DS — かご内インジ 2 画面にならない | — | AXIEZ-LINKS | AXIEZ-LINKS | 機種名あり（） | product_lines が正しければ検証済みにする（以後、他機種を選んだときに除外される） |
| [KH-LINKS-CL1-CABLE-RISE-8](../../cards/case-summaries/KH-LINKS-CL1-CABLE-RISE-8.md) | LINKs — CL1 天蓋ケーブル立上げ不足 | — | AXIEZ-LINKS | — | 機種名あり（） | product_lines が正しければ検証済みにする（以後、他機種を選んだときに除外される） |
| [KH-LINKS-CPDK-INTERCOM-RESET-328](../../cards/case-summaries/KH-LINKS-CPDK-INTERCOM-RESET-328.md) | LINKs — CPD-K+S と多階インターホンリセット結線 | AXIEZ-LINKs | AXIEZ-LINKS | — | 機種名あり（AXIEZ-LINKs） | product_lines が正しければ検証済みにする（以後、他機種を選んだときに除外される） |
| [KH-LINKS-DL-SHORT-12](../../cards/practice-guides/KH-LINKS-DL-SHORT-12.md) | LINKs — DL 短絡暫定手順（S2A・ED モード） | AXIEZ-LINKs | AXIEZ-LINKS | VFGLF | 機種名あり（AXIEZ-LINKs） | product_lines が正しければ検証済みにする（以後、他機種を選んだときに除外される） |
| [KH-LINKS-DS-CONNECTOR-1D2G-304](../../cards/case-summaries/KH-LINKS-DS-CONNECTOR-1D2G-304.md) | LINKs 1D2G — 最下階 DS 未接で休止 | — | AXIEZ-LINKS | — | 機種名あり（） | product_lines が正しければ検証済みにする（以後、他機種を選んだときに除外される） |
| [KH-LINKS-END-SW-USL-CWL-209](../../cards/practice-guides/KH-LINKS-END-SW-USL-CWL-209.md) | LINKs 終点 — USL/PSL/CWL/USR 名称と取付 | AXIEZ-LINKs | AXIEZ-LINKS | VFGLF | 機種名あり（AXIEZ-LINKs） | product_lines が正しければ検証済みにする（以後、他機種を選んだときに除外される） |
| [KH-LINKS-ENTRANCE-RELEASE-44](../../cards/case-summaries/KH-LINKS-ENTRANCE-RELEASE-44.md) | LINKs — エントランス解除・パラメータ | — | AXIEZ-LINKS | LINKS | 機種名あり（） | product_lines が正しければ検証済みにする（以後、他機種を選んだときに除外される） |
| [KH-LINKS-FACTORY-100V-200V-140](../../cards/case-summaries/KH-LINKS-FACTORY-100V-200V-140.md) | 工場誤結線 — 100V/200V 混供（原因・progress 保留） | AXIEZ-LINKs | AXIEZ-LINKS | VFGLF | 機種名あり（AXIEZ-LINKs） | product_lines が正しければ検証済みにする（以後、他機種を選んだときに除外される） |
| [KH-LINKS-FMS-BDD-WIRING-11](../../cards/case-summaries/KH-LINKS-FMS-BDD-WIRING-11.md) | LINKs — FMS 前 BDD 短絡誤結で不走 | — | AXIEZ-LINKS | — | 機種名あり（） | product_lines が正しければ検証済みにする（以後、他機種を選んだときに除外される） |
| [KH-LINKS-HEALTH-AIR-CONNECTOR-320](../../cards/case-summaries/KH-LINKS-HEALTH-AIR-CONNECTOR-320.md) | LINKs — ヘルスエア 8極コネクタピン抜け | — | AXIEZ-LINKS | — | 機種名あり（） | product_lines が正しければ検証済みにする（以後、他機種を選んだときに除外される） |
| [KH-LINKS-HOIST-WALL-GAP-29](../../cards/practice-guides/KH-LINKS-HOIST-WALL-GAP-29.md) | 巻上機・機械台と躯体隙間 — 設計見解（Lists 29 保留） | AXIEZ-LINKs | AXIEZ-LINKS | VFGLF | 機種名あり（AXIEZ-LINKs） | product_lines が正しければ検証済みにする（以後、他機種を選んだときに除外される） |
| [KH-LINKS-IPU-DCL-SUBSTITUTE-353](../../cards/practice-guides/KH-LINKS-IPU-DCL-SUBSTITUTE-353.md) | LINKs — IPU 代品 G33 で G36–G38 代替 | AXIEZ-LINKs | AXIEZ-LINKS | — | 機種名あり（AXIEZ-LINKs） | product_lines が正しければ検証済みにする（以後、他機種を選んだときに除外される） |
| [KH-LINKS-LIMIT-SW-SLOTTED-223](../../cards/practice-guides/KH-LINKS-LIMIT-SW-SLOTTED-223.md) | LINKs — 制限スイッチ長穴固定と検査指摘 | AXIEZ-LINKs | AXIEZ-LINKS | VFGLF | 機種名あり（AXIEZ-LINKs） | product_lines が正しければ検証済みにする（以後、他機種を選んだときに除外される） |
| [KH-LINKS-LOWER-TERM-BOX-MOUNT-229](../../cards/practice-guides/KH-LINKS-LOWER-TERM-BOX-MOUNT-229.md) | LINKs — 下部終点 BOX 2 個時の取付腕位置 | — | AXIEZ-LINKS | — | 機種名あり（） | product_lines が正しければ検証済みにする（以後、他機種を選んだときに除外される） |
| [KH-LINKS-LV5K-DOOR-CLT-VIB-310](../../cards/case-summaries/KH-LINKS-LV5K-DOOR-CLT-VIB-310.md) | LINKs LV5K — 戸閉反動・CLT 調整 | — | AXIEZ-LINKS | — | 機種名あり（） | product_lines が正しければ検証済みにする（以後、他機種を選んだときに除外される） |
| [KH-LINKS-MBS-800-RECEIVER-4](../../cards/case-summaries/KH-LINKS-MBS-800-RECEIVER-4.md) | MBS-800 受光側 — 緑点滅・戸当り 100mm | AXIEZ-LINKs | AXIEZ-LINKS | VFGLF | 機種名あり（AXIEZ-LINKs） | product_lines が正しければ検証済みにする（以後、他機種を選んだときに除外される） |
| [KH-LINKS-MONITOR-JB-MOUNT-211](../../cards/practice-guides/KH-LINKS-MONITOR-JB-MOUNT-211.md) | 監視盤 JB — 設置階と取付高さ | AXIEZ-LINKs | AXIEZ-LINKS | VFGLF | 機種名あり（AXIEZ-LINKs） | product_lines が正しければ検証済みにする（以後、他機種を選んだときに除外される） |
| [KH-LINKS-NORDLOCK-WASHER-LV6K-246](../../cards/practice-guides/KH-LINKS-NORDLOCK-WASHER-LV6K-246.md) | LINKs LV6K — ノルトロックワッシャー取付 | — | AXIEZ-LINKS | — | 機種名あり（） | product_lines が正しければ検証済みにする（以後、他機種を選んだときに除外される） |
| [KH-LINKS-NS-TEMP-RELEASE-BLINK-315](../../cards/practice-guides/KH-LINKS-NS-TEMP-RELEASE-BLINK-315.md) | NS 一時解除 — ボタン点滅（22/2 生産以降） | AXIEZ-LINKs | AXIEZ-LINKS | VFGLF | 機種名あり（AXIEZ-LINKs） | product_lines が正しければ検証済みにする（以後、他機種を選んだときに除外される） |
| [KH-LINKS-POLE-ALIGN-94D-139](../../cards/case-summaries/KH-LINKS-POLE-ALIGN-94D-139.md) | 磁極未学習 94D — コイン電池と HAND 運転 | AXIEZ-LINKs | AXIEZ-LINKS | VFGLF | 機種名あり（AXIEZ-LINKs） | product_lines が正しければ検証済みにする（以後、他機種を選んだときに除外される） |
| [KH-LINKS-PSL-PIN-55](../../cards/case-summaries/KH-LINKS-PSL-PIN-55.md) | LINKs — PSL ピン抜けで DN リレベル停止 | — | AXIEZ-LINKS | — | 機種名あり（） | product_lines が正しければ検証済みにする（以後、他機種を選んだときに除外される） |
| [KH-LINKS-PSL-PIN-S21-342](../../cards/case-summaries/KH-LINKS-PSL-PIN-S21-342.md) | LINKs — PSL ピン抜け（S21・342②） | — | AXIEZ-LINKS | — | 機種名あり（） | product_lines が正しければ検証済みにする（以後、他機種を選んだときに除外される） |
| [KH-LINKS-QB1-REVERSAL-82](../../cards/case-summaries/KH-LINKS-QB1-REVERSAL-82.md) | LINKs — QB1 復帰ミスで BK テレコ・437 | — | AXIEZ-LINKS | — | 機種名あり（） | product_lines が正しければ検証済みにする（以後、他機種を選んだときに除外される） |
| [KH-LINKS-RAIL-MAT-TEST-CERT-366](../../cards/practice-guides/KH-LINKS-RAIL-MAT-TEST-CERT-366.md) | 副本「ガイドレール材料試験成績書」の意味 | — | AXIEZ-LINKS | — | 機種名あり（） | product_lines が正しければ検証済みにする（以後、他機種を選んだときに除外される） |
| [KH-LINKS-RDB-RSLV-EMPTY-RUN-309](../../cards/case-summaries/KH-LINKS-RDB-RSLV-EMPTY-RUN-309.md) | LINKs — RDB/RSLV 短絡残で空回し巻上不动 | — | AXIEZ-LINKS | — | 機種名あり（） | product_lines が正しければ検証済みにする（以後、他機種を選んだときに除外される） |
| [KH-LINKS-RDU-RDF-SWAP-31](../../cards/case-summaries/KH-LINKS-RDU-RDF-SWAP-31.md) | LINKs — RDU/RDF と DRU/DRF 誤結（UP 不入） | — | AXIEZ-LINKS | — | 機種名あり（） | product_lines が正しければ検証済みにする（以後、他機種を選んだときに除外される） |
| [KH-LINKS-RHQ-CONNECTOR-87](../../cards/case-summaries/KH-LINKS-RHQ-CONNECTOR-87.md) | RHQ コネクタ忘れ — USL ON 故障でかご上 UP 不可 | AXIEZ-LINKs | AXIEZ-LINKS | VFGLF | 機種名あり（AXIEZ-LINKs） | product_lines が正しければ検証済みにする（以後、他機種を選んだときに除外される） |
| [KH-LINKS-ROPE-COVER-NOISE-75](../../cards/case-summaries/KH-LINKS-ROPE-COVER-NOISE-75.md) | LINKs — ロープカバー設定で最上階前異音 | — | AXIEZ-LINKS | — | 機種名あり（） | product_lines が正しければ検証済みにする（以後、他機種を選んだときに除外される） |
| [KH-LINKS-SCALE-FMS-37](../../cards/case-summaries/KH-LINKS-SCALE-FMS-37.md) | LINKs — 高速出し後の秤逆転・FMS | — | AXIEZ-LINKS | — | 機種名あり（） | product_lines が正しければ検証済みにする（以後、他機種を選んだときに除外される） |
| [KH-LINKS-SHORT-OH-RUNBY-163](../../cards/practice-guides/KH-LINKS-SHORT-OH-RUNBY-163.md) | LINKs 短 OH — おもりランバイ 145 vs 180 | AXIEZ-LINKs | AXIEZ-LINKS | VFGLF | 機種名あり（AXIEZ-LINKs） | product_lines が正しければ検証済みにする（以後、他機種を選んだときに除外される） |
| [KH-LINKS-TERM-BOX-S2A-7](../../cards/case-summaries/KH-LINKS-TERM-BOX-S2A-7.md) | LINKs — 終点 S2A/S1A 嵌合で本スロー不出 | — | AXIEZ-LINKS | — | 機種名あり（） | product_lines が正しければ検証済みにする（以後、他機種を選んだときに除外される） |
| [KH-LINKS-TERM128-EARTH-69](../../cards/case-summaries/KH-LINKS-TERM128-EARTH-69.md) | LINKs — 128番 BOON 誤アース（69） | — | AXIEZ-LINKS | — | 機種名あり（） | product_lines が正しければ検証済みにする（以後、他機種を選んだときに除外される） |
| [KH-LINKS-TERM128-EARTH-83](../../cards/case-summaries/KH-LINKS-TERM128-EARTH-83.md) | LINKs — 128番 BOON 誤アースで絶縁不良 | — | AXIEZ-LINKS | — | 機種名あり（） | product_lines が正しければ検証済みにする（以後、他機種を選んだときに除外される） |
| [KH-LINKS-TRANS-CRIMP-50](../../cards/case-summaries/KH-LINKS-TRANS-CRIMP-50.md) | LINKs — トランス結線不良で空回し不可 | — | AXIEZ-LINKS | — | 機種名あり（） | product_lines が正しければ検証済みにする（以後、他機種を選んだときに除外される） |
| [KH-LINKS-UCAN-MMS-CABLE-222](../../cards/case-summaries/KH-LINKS-UCAN-MMS-CABLE-222.md) | U-CAN 異常 — ドア MMS コネクタ線噛みで起動不能 | AXIEZ-LINKs | AXIEZ-LINKS | VFGLF | 機種名あり（AXIEZ-LINKs） | product_lines が正しければ検証済みにする（以後、他機種を選んだときに除外される） |
| [KH-LINKS-UCMP-BMODE-57](../../cards/case-summaries/KH-LINKS-UCMP-BMODE-57.md) | LINKs — UCMP 制動距離と B モード取違え | — | AXIEZ-LINKS | LINKS | 機種名あり（） | product_lines が正しければ検証済みにする（以後、他機種を選んだときに除外される） |
| [KH-LINKS-UCMP-RESET-POWER-79](../../cards/practice-guides/KH-LINKS-UCMP-RESET-POWER-79.md) | 独立 UCMP — 電源入切り時の故障検出 | — | AXIEZ-LINKS | LINKS | 機種名あり（） | product_lines が正しければ検証済みにする（以後、他機種を選んだときに除外される） |
| [KH-LINKS-UV-PHASE-FREE-RUN-10](../../cards/case-summaries/KH-LINKS-UV-PHASE-FREE-RUN-10.md) | LINKs — 制御盤 U/V 逆相で空回し不可 | — | AXIEZ-LINKS | — | 機種名あり（） | product_lines が正しければ検証済みにする（以後、他機種を選んだときに除外される） |
| [KH-LINKS-VDA-CAMERA-SPLIT-334](../../cards/practice-guides/KH-LINKS-VDA-CAMERA-SPLIT-334.md) | ITV — 分配器2台・VDA-106B スイッチ | — | AXIEZ-LINKS | — | 機種名あり（） | product_lines が正しければ検証済みにする（以後、他機種を選んだときに除外される） |
| [KH-LINKS-VIDEO-DIST-ARM-33](../../cards/practice-guides/KH-LINKS-VIDEO-DIST-ARM-33.md) | 映像分配器 — 取付腕本数（箱長） | — | AXIEZ-LINKS | — | 機種名あり（） | product_lines が正しければ検証済みにする（以後、他機種を選んだときに除外される） |
| [KH-LINKS-Z-CARD-SW-306-212](../../cards/case-summaries/KH-LINKS-Z-CARD-SW-306-212.md) | 306 Z 系カード重故障 — SW Z11 設定不一致 | AXIEZ-LINKs | AXIEZ-LINKS | VFGLF | 機種名あり（AXIEZ-LINKs） | product_lines が正しければ検証済みにする（以後、他機種を選んだときに除外される） |
| [KH-LV5K-2S-DOOR-NOISE-433](../../cards/case-summaries/KH-LV5K-2S-DOOR-NOISE-433.md) | LV5K-2S かごドア開閉時のキュルキュル異音（G寸法・STSベルト） | AXIEZ-LINKs | VFGLF | VFGLF | 機種名あり（AXIEZ-LINKs） | product_lines が正しければ検証済みにする（以後、他機種を選んだときに除外される） |
| [KH-LV5K-LV6K-CAP-COVER-BAND-435](../../cards/practice-guides/KH-LV5K-LV6K-CAP-COVER-BAND-435.md) | LV5K/LV6K かごドア カプラカバー入口の結束バンド | AXIEZ-LINKs | VFGLF | VFGLF | 機種名あり（AXIEZ-LINKs） | product_lines が正しければ検証済みにする（以後、他機種を選んだときに除外される） |
| [KH-NEXCUBE-VFGH-QC-HUB](../../cards/practice-guides/KH-NEXCUBE-VFGH-QC-HUB.md) | Nexcube（NEXWAY 表記）VFGH — 品質確認・調整チェックの入口 | Nexcube | — | VFGH | 機種名あり（Nexcube） | product_lines が正しければ検証済みにする（以後、他機種を選んだときに除外される） |
| [KH-TRB-S0-TERMINAL-109](../../cards/case-summaries/KH-TRB-S0-TERMINAL-109.md) | トランスリアクトル S0 端子増し締めでケーブル脱落 | AXIEZ | VFGLB | VFGLB | 機種名あり（AXIEZ） | product_lines が正しければ検証済みにする（以後、他機種を選んだときに除外される） |
| [KH-VFGH-DOAS-CONSTRUCTION-373](../../cards/case-summaries/KH-VFGH-DOAS-CONSTRUCTION-373.md) | 工事使用時の行先階制限（DOAS）でカゴ呼びが登録できない | Nexcube | VFGH | VFGH | 機種名あり（Nexcube） | product_lines が正しければ検証済みにする（以後、他機種を選んだときに除外される） |
| [KH-VFGH-KEIAIN-HMS-DOOR-408](../../cards/case-summaries/KH-VFGH-KEIAIN-HMS-DOOR-408.md) | 戸閉時の気配りドアセンサーとHMS動作不良 | Nexcube | VFGH | VFGH | 機種名あり（Nexcube） | product_lines が正しければ検証済みにする（以後、他機種を選んだときに除外される） |
| [KH-VFGH-VIBRATION-JUMPER-416](../../cards/practice-guides/KH-VFGH-VIBRATION-JUMPER-416.md) | 長周期振動感知器の短絡ジャンパとBSER/BSER-CP | Nexcube | VFGH | VFGH | 機種名あり（Nexcube） | product_lines が正しければ検証済みにする（以後、他機種を選んだときに除外される） |
| [KH-VFGLF-ACTUATOR-HANGER-400](../../cards/case-summaries/KH-VFGLF-ACTUATOR-HANGER-400.md) | アクチュエータ外し後のハンガー接触でドア重い（高速戸） | AXIEZ-LINKs | VFGLF | VFGLF | 機種名あり（AXIEZ-LINKs） | product_lines が正しければ検証済みにする（以後、他機種を選んだときに除外される） |
| [KH-VFGLF-BRAKE-SW-392](../../cards/case-summaries/KH-VFGLF-BRAKE-SW-392.md) | VFGLF 本スロー時ブレーキSW設定不良による運転不能 | AXIEZ-LINKs | VFGLF | VFGLF | 機種名あり（AXIEZ-LINKs） | product_lines が正しければ検証済みにする（以後、他機種を選んだときに除外される） |
| [KH-VFGLF-CAR-IND-DEST-FLOOR-99](../../cards/case-summaries/KH-VFGLF-CAR-IND-DEST-FLOOR-99.md) | 階床 S/W 変更後もかご内行先階予約表示が変わらない（LHC-1132） | AXIEZ-LINKs | VFGLF | VFGLF | 機種名あり（AXIEZ-LINKs） | product_lines が正しければ検証済みにする（以後、他機種を選んだときに除外される） |
| [KH-VFGLF-DOB-CPU-PORTABLE-105](../../cards/case-summaries/KH-VFGLF-DOB-CPU-PORTABLE-105.md) | かご内戸開閉釦无效 — 釦CPU・60A・据付ポータブル（DOB/DCB） | AXIEZ-LINKs | VFGLF | VFGLF | 機種名あり（AXIEZ-LINKs） | product_lines が正しければ検証済みにする（以後、他機種を選んだときに除外される） |
| [KH-VFGLF-DOOR-KV-TYPE-NAMES](../../cards/practice-guides/KH-VFGLF-DOOR-KV-TYPE-NAMES.md) | VFGLF 戸閉装置型名（KV・K4）の読み方 | AXIEZ-LINKs | — | VFGLF | 機種名あり（AXIEZ-LINKs） | product_lines が正しければ検証済みにする（以後、他機種を選んだときに除外される） |
| [KH-VFGLF-DOR-DOB-403](../../cards/case-summaries/KH-VFGLF-DOR-DOB-403.md) | ドア開閉釦が効かない（DOR-1280D・D14 DCB/DOB） | AXIEZ-LINKs | VFGLF | VFGLF | 機種名あり（AXIEZ-LINKs） | product_lines が正しければ検証済みにする（以後、他機種を選んだときに除外される） |
| [KH-VFGLF-HOIST-RESOLVER-WIRE-411](../../cards/case-summaries/KH-VFGLF-HOIST-RESOLVER-WIRE-411.md) | 巻上機レゾルバ配線断線で空回し不能 | AXIEZ-LINKs | VFGLF | VFGLF | 機種名あり（AXIEZ-LINKs） | product_lines が正しければ検証済みにする（以後、他機種を選んだときに除外される） |
| [KH-VFGLF-ICAN-HALL-BACKUP-417](../../cards/case-summaries/KH-VFGLF-ICAN-HALL-BACKUP-417.md) | VFGLFで乗場バックアップができない | AXIEZ-LINKs | VFGLF | VFGLF | 機種名あり（AXIEZ-LINKs） | product_lines が正しければ検証済みにする（以後、他機種を選んだときに除外される） |
| [KH-VFGLF-LINKS-FLOOD-SENSOR-395](../../cards/practice-guides/KH-VFGLF-LINKS-FLOOD-SENSOR-395.md) | 冠水 PER — Lists 395 保留・Notes のみ | AXIEZ-LINKs | VFGLB・VFGLF | VFGLF | 機種名あり（AXIEZ-LINKs） | product_lines が正しければ検証済みにする（以後、他機種を選んだときに除外される） |
| [KH-VFGLF-LINKS-MACHINE-DIM-128](../../cards/practice-guides/KH-VFGLF-LINKS-MACHINE-DIM-128.md) | LINKs 機械台 — イーイ断面寸法の見方 | AXIEZ-LINKs | VFGLF | VFGLF | 機種名あり（AXIEZ-LINKs） | product_lines が正しければ検証済みにする（以後、他機種を選んだときに除外される） |
| [KH-VFGLF-MELD-RHY-CONNECTOR-132](../../cards/case-summaries/KH-VFGLF-MELD-RHY-CONNECTOR-132.md) | RHY コネクタ未挿 — 64D と MELD 実動作しない | AXIEZ-LINKs | VFGLF | VFGLF | 機種名あり（AXIEZ-LINKs） | product_lines が正しければ検証済みにする（以後、他機種を選んだときに除外される） |
| [KH-VFGLF-RAIL-SPACER-389](../../cards/practice-guides/KH-VFGLF-RAIL-SPACER-389.md) | 昇降路全高不足 — 緩衝器台スペーサ調整 | AXIEZ-LINKs | VFGLF | VFGLF | 機種名あり（AXIEZ-LINKs） | product_lines が正しければ検証済みにする（以後、他機種を選んだときに除外される） |
| [KH-VFGLF-SD-T21-WOS-97](../../cards/case-summaries/KH-VFGLF-SD-T21-WOS-97.md) | WOS 時 SD-T21 #5 コンタクタ動作不良（M5 交換） | AXIEZ-LINKs | VFGLF | VFGLF | 機種名あり（AXIEZ-LINKs） | product_lines が正しければ検証済みにする（以後、他機種を選んだときに除外される） |
| [KH-VFGLF-TERMINAL-M8-343](../../cards/practice-guides/KH-VFGLF-TERMINAL-M8-343.md) | VFGLF 制御盤 — 繋ぎ込み端子 M8（X17AT-44） | — | VFGLF、AXIEZ-LINKS | VFGLF | 機種名あり（） | product_lines が正しければ検証済みにする（以後、他機種を選んだときに除外される） |
| [KH-VFGLF-VIRTUAL-FLOOR-PLATE-401](../../cards/practice-guides/KH-VFGLF-VIRTUAL-FLOOR-PLATE-401.md) | 仮想階用着床プレート — 品目余剰の見方 | AXIEZ-LINKs | VFGLF | VFGLF | 機種名あり（AXIEZ-LINKs） | product_lines が正しければ検証済みにする（以後、他機種を選んだときに除外される） |

## P3 制御方式・略称のみ・未検証（194 件）

| カード | タイトル | product_lines | lists_model_label | control_methods | 理由 | 推奨対応 |
| --- | --- | --- | --- | --- | --- | --- |
| [KH-ALL-E-MRL-SUPPLY-VOLTAGE-84](../../cards/practice-guides/KH-ALL-E-MRL-SUPPLY-VOLTAGE-84.md) | E系 MRL — 受電電圧許容と品質記録 | — | （Lists 機種空） | — | 制御方式・略称のみ | 機種フィルタ対象外。全機種対応なら lists_model_label を全エレ機種へ |
| [KH-ALL-MD20B-MI4-FORCED-AC-112](../../cards/practice-guides/KH-ALL-MD20B-MI4-FORCED-AC-112.md) | 小型エアコン MD-20B-MI4 — 強制運転（豆知識） | — | （Lists 機種空） | — | 制御方式・略称のみ | 機種フィルタ対象外。全機種対応なら lists_model_label を全エレ機種へ |
| [KH-ALL-MONITOR-CRT-TELECO-241](../../cards/case-summaries/KH-ALL-MONITOR-CRT-TELECO-241.md) | 監視盤 — CRT 通信線テレコで表示チラつき | — | 監視盤 | — | 制御方式・略称のみ | 機種フィルタ対象外。全機種対応なら lists_model_label を全エレ機種へ |
| [KH-ALL-MONITOR-FIRE-GEN-LAMP-14](../../cards/practice-guides/KH-ALL-MONITOR-FIRE-GEN-LAMP-14.md) | 監視盤 — 火災停電時の非常電源と自家発ランプ | — | 監視盤 | — | 制御方式・略称のみ | 機種フィルタ対象外。全機種対応なら lists_model_label を全エレ機種へ |
| [KH-ALL-PHOTO-POST-FOB-DISPLAY-296](../../cards/practice-guides/KH-ALL-PHOTO-POST-FOB-DISPLAY-296.md) | 光電ポスト — 自動運転時インジ（FOB/制御方式別） | — | トラベーター | — | 制御方式・略称のみ | 機種フィルタ対象外。全機種対応なら lists_model_label を全エレ機種へ |
| [KH-ALL-SILL-GAP-10MM-LINKS-MRL-281](../../cards/practice-guides/KH-ALL-SILL-GAP-10MM-LINKS-MRL-281.md) | 敷居 10 mm ver — LINKs と MRL 追加敷居差 | — | VFGLB・VFGLF | — | 制御方式・略称のみ | 機種フィルタ対象外。全機種対応なら lists_model_label を全エレ機種へ |
| [KH-ALL-VHP-LANDING-OPEN-91](../../cards/practice-guides/KH-ALL-VHP-LANDING-OPEN-91.md) | VHP 仕様 — ランディングオープン（LO）しない | — | VFGLF・VFGLB・VFGH | VFGLF、VFGLB、VFGH | 制御方式・略称のみ | 機種フィルタ対象外。全機種対応なら lists_model_label を全エレ機種へ |
| [KH-AXIEZ-INSTALL-FLAG-85](../../cards/practice-guides/KH-AXIEZ-INSTALL-FLAG-85.md) | 据付完了フラグ — AXIEZ（100930CF）を未完了へ戻す | — | 新AXIEZ | AXIEZ | 制御方式・略称のみ | 機種フィルタ対象外。全機種対応なら lists_model_label を全エレ機種へ |
| [KH-CM-LB-GATE-EARTH-36](../../cards/case-summaries/KH-CM-LB-GATE-EARTH-36.md) | CM-LB — ゲート SW G3/EARTH 取違えと D41 | — | CM-LB | VFGLB-K | 制御方式・略称のみ | 機種フィルタ対象外。全機種対応なら lists_model_label を全エレ機種へ |
| [KH-CM-LB-PMF020MB-SPACER-238](../../cards/practice-guides/KH-CM-LB-PMF020MB-SPACER-238.md) | CM-LB — PMF020MB 嵩上げ台と揚重図 | — | CM-LB | — | 制御方式・略称のみ | 機種フィルタ対象外。全機種対応なら lists_model_label を全エレ機種へ |
| [KH-CM-LB-PRIMARY-FIRE-SDE-288](../../cards/case-summaries/KH-CM-LB-PRIMARY-FIRE-SDE-288.md) | CM-LB — 一次消防 #FE2 渡線抜け 727 | — | CM-LB | — | 制御方式・略称のみ | 機種フィルタ対象外。全機種対応なら lists_model_label を全エレ機種へ |
| [KH-CM-LB-RA1-CABLE-DUCT-19](../../cards/case-summaries/KH-CM-LB-RA1-CABLE-DUCT-19.md) | CM-LB — RA1 被覆剥け・仮設分電トリップ | — | CM-LB | — | 制御方式・略称のみ | 機種フィルタ対象外。全機種対応なら lists_model_label を全エレ機種へ |
| [KH-CM-MA-AC-NOISE-271](../../cards/practice-guides/KH-CM-MA-AC-NOISE-271.md) | CM-MA — カゴ内エアコン動作音（基準超過） | — | CM-MA | — | 制御方式・略称のみ | 機種フィルタ対象外。全機種対応なら lists_model_label を全エレ機種へ |
| [KH-CM-MA-CHEM-ANCHOR-DEPTH-114](../../cards/case-summaries/KH-CM-MA-CHEM-ANCHOR-DEPTH-114.md) | M12 ケミカルアンカー — 埋込115mmの判断 | — | CM-MA | CM-MA | 制御方式・略称のみ | 機種フィルタ対象外。全機種対応なら lists_model_label を全エレ機種へ |
| [KH-CM-MA-DOOR-SHOE-MISSING-56](../../cards/case-summaries/KH-CM-MA-DOOR-SHOE-MISSING-56.md) | CM-MA — カゴドアシュー類手配漏れ | — | CM-MA | — | 制御方式・略称のみ | 機種フィルタ対象外。全機種対応なら lists_model_label を全エレ機種へ |
| [KH-CM-MA-FIN-THERMO-MGMT-218](../../cards/case-summaries/KH-CM-MA-FIN-THERMO-MGMT-218.md) | CM-MA — 養生・室温でフィンサーモ管理外 | — | CM-MA | CM-MA | 制御方式・略称のみ | 機種フィルタ対象外。全機種対応なら lists_model_label を全エレ機種へ |
| [KH-CM-MA-GOV-PLAY-71](../../cards/case-summaries/KH-CM-MA-GOV-PLAY-71.md) | CM-MA — シンダーレス GOV 台ガタツキ | — | CM-MA | — | 制御方式・略称のみ | 機種フィルタ対象外。全機種対応なら lists_model_label を全エレ機種へ |
| [KH-CM-MA-LHC1130-ANNOUNCE-BUSY-22](../../cards/case-summaries/KH-CM-MA-LHC1130-ANNOUNCE-BUSY-22.md) | CM-MA — LHC-1130 COP アナウンス基板 E225/227 | — | CM-MA | — | 制御方式・略称のみ | 機種フィルタ対象外。全機種対応なら lists_model_label を全エレ機種へ |
| [KH-CM-MA-M1-CARD-BURN-53](../../cards/case-summaries/KH-CM-MA-M1-CARD-BURN-53.md) | CM-MA — 空回し前 M1 カード焼損 | — | CM-MA | — | 制御方式・略称のみ | 機種フィルタ対象外。全機種対応なら lists_model_label を全エレ機種へ |
| [KH-CM-MA-POLE-CORRECT-ENC-234](../../cards/case-summaries/KH-CM-MA-POLE-CORRECT-ENC-234.md) | CM-MA — 空回し磁極補正が止まらない（ENC/GND接触） | — | CM-MA | — | 制御方式・略称のみ | 機種フィルタ対象外。全機種対応なら lists_model_label を全エレ機種へ |
| [KH-CM-MA-WCHAIR-PANEL-OPENING-30](../../cards/case-summaries/KH-CM-MA-WCHAIR-PANEL-OPENING-30.md) | CM-MA — 車椅子操作盤と枠開口不一致 | — | CM-MA | — | 制御方式・略称のみ | 機種フィルタ対象外。全機種対応なら lists_model_label を全エレ機種へ |
| [KH-ELECALL-FACE-AUTH-SCU-412](../../cards/practice-guides/KH-ELECALL-FACE-AUTH-SCU-412.md) | エレコール — 顔認証複数台の SCU RS-422 ポート | — | エレコール | — | 制御方式・略称のみ | 機種フィルタ対象外。全機種対応なら lists_model_label を全エレ機種へ |
| [KH-ELECALL-GATE-NO-INTERCOM-143](../../cards/case-summaries/KH-ELECALL-GATE-NO-INTERCOM-143.md) | エレコール — ゲート番号不一致と監理者キー | — | エレコール | — | 制御方式・略称のみ | 機種フィルタ対象外。全機種対応なら lists_model_label を全エレ機種へ |
| [KH-ELECALL-HA-SECOM-26](../../cards/case-summaries/KH-ELECALL-HA-SECOM-26.md) | エレコール — HA メーカー取違え（E,0） | — | エレコール | — | 制御方式・略称のみ | 機種フィルタ対象外。全機種対応なら lists_model_label を全エレ機種へ |
| [KH-ELECALL-MOCK-RPE-RNE-17](../../cards/practice-guides/KH-ELECALL-MOCK-RPE-RNE-17.md) | エレコール — 模擬試験と RPE/RNE テレコ | — | エレコール | — | 制御方式・略称のみ | 機種フィルタ対象外。全機種対応なら lists_model_label を全エレ機種へ |
| [KH-ELECALL-PANIC-OPEN-HALL-CALL-92](../../cards/case-summaries/KH-ELECALL-PANIC-OPEN-HALL-CALL-92.md) | パニックオープンと同時に1階乗場呼びが自動登録される | — | エレコール | — | 制御方式・略称のみ | 機種フィルタ対象外。全機種対応なら lists_model_label を全エレ機種へ |
| [KH-ELECALL-PUTTY-INSTALL-130](../../cards/practice-guides/KH-ELECALL-PUTTY-INSTALL-130.md) | SCU-20 保守 — Putty インストール | elecall | エレコール | — | 制御方式・略称のみ | 機種フィルタ対象外。全機種対応なら lists_model_label を全エレ機種へ |
| [KH-ELECALL-PUTTY-LOG-ADMIN-119](../../cards/practice-guides/KH-ELECALL-PUTTY-LOG-ADMIN-119.md) | Putty — ログが保存されない（管理者実行） | elecall | エレコール | — | 制御方式・略称のみ | 機種フィルタ対象外。全機種対応なら lists_model_label を全エレ機種へ |
| [KH-ELECALL-SCU-TOOL-DOWNLOAD-297](../../cards/practice-guides/KH-ELECALL-SCU-TOOL-DOWNLOAD-297.md) | エレコール — SCU 保守ツールの入手場所 | — | エレコール | — | 制御方式・略称のみ | 機種フィルタ対象外。全機種対応なら lists_model_label を全エレ機種へ |
| [KH-ELENAVI-ELSGW-PUTTY-NET-415](../../cards/practice-guides/KH-ELENAVI-ELSGW-PUTTY-NET-415.md) | ELSGW — PuTTY ログ採取と IP 設定 | — | エレナビ | — | 制御方式・略称のみ | 機種フィルタ対象外。全機種対応なら lists_model_label を全エレ機種へ |
| [KH-ELENAVI-ISSUES-INDEX-336](../../cards/practice-guides/KH-ELENAVI-ISSUES-INDEX-336.md) | エレナビ不具合対応まとめ（添付索引） | — | エレナビ | — | 制御方式・略称のみ | 機種フィルタ対象外。全機種対応なら lists_model_label を全エレ機種へ |
| [KH-ELENAVI-MELSAFETY-GATE-RESET-205](../../cards/practice-guides/KH-ELENAVI-MELSAFETY-GATE-RESET-205.md) | エレナビ — MELSAFTY ゲート非常解除状態の復帰 | — | エレナビ | — | 制御方式・略称のみ | 機種フィルタ対象外。全機種対応なら lists_model_label を全エレ機種へ |
| [KH-EMER-JB-GROMMET-192](../../cards/practice-guides/KH-EMER-JB-GROMMET-192.md) | 非常エレ中間 JB — ゴムブッシュサイズ不足 | — | 非常エレ | — | 制御方式・略称のみ | 機種フィルタ対象外。全機種対応なら lists_model_label を全エレ機種へ |
| [KH-EMERG-LANDING-NAMEPLATE-308](../../cards/practice-guides/KH-EMERG-LANDING-NAMEPLATE-308.md) | 非常用 — 乗場名板貼付け要領 | — | 非常用エレ | — | 制御方式・略称のみ | 機種フィルタ対象外。全機種対応なら lists_model_label を全エレ機種へ |
| [KH-ESC-SVFBM-INTERLOCK-STOP-51](../../cards/case-summaries/KH-ESC-SVFBM-INTERLOCK-STOP-51.md) | ZJ-S — 連動停止不可（端子名称と線色不一致） | — | ZJ-S(SVFBM) | — | 制御方式・略称のみ | 機種フィルタ対象外。全機種対応なら lists_model_label を全エレ機種へ |
| [KH-ESC-SVFC-ANNOUNCE-RSW-78](../../cards/practice-guides/KH-ESC-SVFC-ANNOUNCE-RSW-78.md) | SVFC — 標準アナウンス RSW 設定 | — | SVFC | — | 制御方式・略称のみ | 機種フィルタ対象外。全機種対応なら lists_model_label を全エレ機種へ |
| [KH-ESC-ZJ-SAFL-HGS-52](../../cards/case-summaries/KH-ESC-ZJ-SAFL-HGS-52.md) | ZJ ESC — SD_SAFL と HGS-R コネクタ | — | ZJ型ESC | — | 制御方式・略称のみ | 機種フィルタ対象外。全機種対応なら lists_model_label を全エレ機種へ |
| [KH-GROUP-ECAN-MAG-171](../../cards/case-summaries/KH-GROUP-ECAN-MAG-171.md) | E-CAN MAG 未接続 — NS 不能と群管理 GC エラー読取 | — | 群管理盤 | — | 制御方式・略称のみ | 機種フィルタ対象外。全機種対応なら lists_model_label を全エレ機種へ |
| [KH-GS3-PART-NO-SCU20-422](../../cards/case-summaries/KH-GS3-PART-NO-SCU20-422.md) | GS3 品番 -24/-03 と LM2B — SCU-20 通信不成立 | — | 群管理盤 | — | 制御方式・略称のみ | 機種フィルタ対象外。全機種対応なら lists_model_label を全エレ機種へ |
| [KH-HA-PANEL-ELECALL-158](../../cards/case-summaries/KH-HA-PANEL-ELECALL-158.md) | HA 制御盤内部エラー — エレコール連動停止 | — | エレコール | — | 制御方式・略称のみ | 機種フィルタ対象外。全機種対応なら lists_model_label を全エレ機種へ |
| [KH-KE-BF-AC-SAG-E-STOP-181](../../cards/case-summaries/KH-KE-BF-AC-SAG-E-STOP-181.md) | 客先電線細径 — フルロード AC 低下 E-STOP | — | KE-BF | — | 制御方式・略称のみ | 機種フィルタ対象外。全機種対応なら lists_model_label を全エレ機種へ |
| [KH-KE-RFM-SEAL-WASHER-356](../../cards/practice-guides/KH-KE-RFM-SEAL-WASHER-356.md) | KE-RFM — 機械台シールワッシャー取付位置 | — | KE-RFM | — | 制御方式・略称のみ | 機種フィルタ対象外。全機種対応なら lists_model_label を全エレ機種へ |
| [KH-KF-MTC-DV5K-DOOR-NOISE-327](../../cards/practice-guides/KH-KF-MTC-DV5K-DOOR-NOISE-327.md) | 荷物用 DV5K — 戸反転騒音（不具合ではない） | — | KF-MTC | — | 制御方式・略称のみ | 機種フィルタ対象外。全機種対応なら lists_model_label を全エレ機種へ |
| [KH-KM-LB-VESTA-DZ-DN-62](../../cards/case-summaries/KH-KM-LB-VESTA-DZ-DN-62.md) | KM-LB — 最上階 DN で DZ 抜け E-stop | — | KM-LB | — | 制御方式・略称のみ | 機種フィルタ対象外。全機種対応なら lists_model_label を全エレ機種へ |
| [KH-KM-LD-CCP-REGEN-80](../../cards/case-summaries/KH-KM-LD-CCP-REGEN-80.md) | KM-LD — CCP 未投入で回生スロー不可 | — | KM-LD | — | 制御方式・略称のみ | 機種フィルタ対象外。全機種対応なら lists_model_label を全エレ機種へ |
| [KH-KM-LD-DEDICATED-MODE-39](../../cards/case-summaries/KH-KM-LD-DEDICATED-MODE-39.md) | KM-LD — 専用運転に切替わらない（S/W） | — | KM-LD | — | 制御方式・略称のみ | 機種フィルタ対象外。全機種対応なら lists_model_label を全エレ機種へ |
| [KH-KM-LD-DOOR-TRANSPORT-BRACKET-264](../../cards/practice-guides/KH-KM-LD-DOOR-TRANSPORT-BRACKET-264.md) | KM-LD M系2S/2CO — 輸送金具は取外し | — | KM-LD | — | 制御方式・略称のみ | 機種フィルタ対象外。全機種対応なら lists_model_label を全エレ機種へ |
| [KH-KM-LD-DOR1280-REV-370](../../cards/case-summaries/KH-KM-LD-DOR1280-REV-370.md) | DOR-1280 C/D 副番 — J9 短絡プラグ | — | KM-LD | VFGLB-WB | 制御方式・略称のみ | 機種フィルタ対象外。全機種対応なら lists_model_label を全エレ機種へ |
| [KH-KM-LD-FSHFT-LANDING-20](../../cards/case-summaries/KH-KM-LD-FSHFT-LANDING-20.md) | KM-LD — 着床レベル差・FSHFT 追加 | — | KM-LD | — | 制御方式・略称のみ | 機種フィルタ対象外。全機種対応なら lists_model_label を全エレ機種へ |
| [KH-KM-LD-GANTRY-BRACKET-404](../../cards/practice-guides/KH-KM-LD-GANTRY-BRACKET-404.md) | KM-LD — 門形共用ブラケットと CWT ツナギ | — | KM-LD | — | 制御方式・略称のみ | 機種フィルタ対象外。全機種対応なら lists_model_label を全エレ機種へ |
| [KH-KM-LD-HOP-LANDING-POWER-21](../../cards/practice-guides/KH-KM-LD-HOP-LANDING-POWER-21.md) | KM-LD — 乗場押釦と HOP の電源系統 | — | KM-LD | — | 制御方式・略称のみ | 機種フィルタ対象外。全機種対応なら lists_model_label を全エレ機種へ |
| [KH-KM-LD-KETA-BRACE-INTERFERENCE-244](../../cards/case-summaries/KH-KM-LD-KETA-BRACE-INTERFERENCE-244.md) | KM-LD — 斜め筋交いとドアモーターカバー干渉 | — | KM-LD | — | 制御方式・略称のみ | 機種フィルタ対象外。全機種対応なら lists_model_label を全エレ機種へ |
| [KH-KM-LD-L20A-GROUND-116](../../cards/case-summaries/KH-KM-LD-L20A-GROUND-116.md) | 100V 地絡 — L20A 挟み込み（KM-LD） | — | KM-LD | — | 制御方式・略称のみ | 機種フィルタ対象外。全機種対応なら lists_model_label を全エレ機種へ |
| [KH-KM-LD-MED-HARNESS-E35-261](../../cards/case-summaries/KH-KM-LD-MED-HARNESS-E35-261.md) | KM-LD — MED ハーネス違いで E35/E36/E45 | — | KM-LD | — | 制御方式・略称のみ | 機種フィルタ対象外。全機種対応なら lists_model_label を全エレ機種へ |
| [KH-KM-LD-PC-MOUNT-PLATE-259](../../cards/case-summaries/KH-KM-LD-PC-MOUNT-PLATE-259.md) | KM-LD 増設盤 — パソコン取付板干渉 | — | KM-LD | — | 制御方式・略称のみ | 機種フィルタ対象外。全機種対応なら lists_model_label を全エレ機種へ |
| [KH-KM-LD-PWFH-PHASE-54](../../cards/case-summaries/KH-KM-LD-PWFH-PHASE-54.md) | KM-LD — PWFH 逆相で回生スロー不可 | — | KM-LD | — | 制御方式・略称のみ | 機種フィルタ対象外。全機種対応なら lists_model_label を全エレ機種へ |
| [KH-KM-LD-REGEN-LID-SW-NVA-287](../../cards/case-summaries/KH-KM-LD-REGEN-LID-SW-NVA-287.md) | KM-LD — 回生盤フタ SW 不足で NVA 後起動不可 | — | KM-LD | — | 制御方式・略称のみ | 機種フィルタ対象外。全機種対応なら lists_model_label を全エレ機種へ |
| [KH-KM-LD-SEISMIC-HARNESS-155](../../cards/case-summaries/KH-KM-LD-SEISMIC-HARNESS-155.md) | 変換ハーネス誤品 — 呼戻し中低ガル遠隔解除不可 | — | KM-LD | KM-LD | 制御方式・略称のみ | 機種フィルタ対象外。全機種対応なら lists_model_label を全エレ機種へ |
| [KH-KM-LD-YBO-YBI-CONNECTOR-70](../../cards/case-summaries/KH-KM-LD-YBO-YBI-CONNECTOR-70.md) | KM-LD — YBO/YBI 誤結で戸閉遅延 | — | KM-LD | — | 制御方式・略称のみ | 機種フィルタ対象外。全機種対応なら lists_model_label を全エレ機種へ |
| [KH-KM-SA-DOOR-RATTLE-SW-200](../../cards/case-summaries/KH-KM-SA-DOOR-RATTLE-SW-200.md) | KM-SA — 一般戸閉ボタンでドアガタつき | — | KM-SA | KM-SA | 制御方式・略称のみ | 機種フィルタ対象外。全機種対応なら lists_model_label を全エレ機種へ |
| [KH-LINKS-NSCR-REAR-KEY-364](../../cards/practice-guides/KH-LINKS-NSCR-REAR-KEY-364.md) | LINKs — リア NSCR-XR キーSW（フロント CPU 経由） | — | VFGLB、VFGLF | — | 制御方式・略称のみ | 機種フィルタ対象外。全機種対応なら lists_model_label を全エレ機種へ |
| [KH-LINKS-R9-LATERAL-WIRE-DRAW-257](../../cards/practice-guides/KH-LINKS-R9-LATERAL-WIRE-DRAW-257.md) | LINKs R9 — 横保護線施工図条件（正本） | — | VFGLF | — | 制御方式・略称のみ | 機種フィルタ対象外。全機種対応なら lists_model_label を全エレ機種へ |
| [KH-LV0K-7-2S-DOOR-RESOLVER-328-439](../../cards/case-summaries/KH-LV0K-7-2S-DOOR-RESOLVER-328-439.md) | LV0K-7-2S ドア駆動基板レゾルバ異常（328） | — | MRL機種 | — | 制御方式・略称のみ | 機種フィルタ対象外。全機種対応なら lists_model_label を全エレ機種へ |
| [KH-MBS-F4B-PIN-240](../../cards/case-summaries/KH-MBS-F4B-PIN-240.md) | MBS F4B ピン逆 — カゴ内 12V 消失・インジ消灯 | — | VFGLF・VFGLB・VFGH | VFGLF、VFGLB、VFGH | 制御方式・略称のみ | 機種フィルタ対象外。全機種対応なら lists_model_label を全エレ機種へ |
| [KH-ME-BL-2ND-PIT-SWITCH-393](../../cards/practice-guides/KH-ME-BL-2ND-PIT-SWITCH-393.md) | 2nd ピットスイッチ — 深さ 1600 超と SUE-3-19 改定 | — | ME-BL | — | 制御方式・略称のみ | 機種フィルタ対象外。全機種対応なら lists_model_label を全エレ機種へ |
| [KH-ME-CH-ARG-GAIN-VIB-272](../../cards/case-summaries/KH-ME-CH-ARG-GAIN-VIB-272.md) | ME-CH — ARG ゲイン調整で振動低減 | — | ME-CH | — | 制御方式・略称のみ | 機種フィルタ対象外。全機種対応なら lists_model_label を全エレ機種へ |
| [KH-ME-CH-GOV-DUAL-SAFETY-59](../../cards/case-summaries/KH-ME-CH-GOV-DUAL-SAFETY-59.md) | ME-CH — 張車 SW と RUN OFF の二重安全遮断 | — | ME-CH | — | 制御方式・略称のみ | 機種フィルタ対象外。全機種対応なら lists_model_label を全エレ機種へ |
| [KH-ME-CH-PHASE-89M-46](../../cards/case-summaries/KH-ME-CH-PHASE-89M-46.md) | ME-CH — 逆相で 89M 振動・空回し不可 | — | ME-CH | — | 制御方式・略称のみ | 機種フィルタ対象外。全機種対応なら lists_model_label を全エレ機種へ |
| [KH-ME-CM-CURTAIN-HOOK-WASHER-6](../../cards/case-summaries/KH-ME-CM-CURTAIN-HOOK-WASHER-6.md) | ME-CM — カーテンフック座金欠品 | — | ME-CM | — | 制御方式・略称のみ | 機種フィルタ対象外。全機種対応なら lists_model_label を全エレ機種へ |
| [KH-ME-CM-TEMP-POWER-S-431](../../cards/case-summaries/KH-ME-CM-TEMP-POWER-S-431.md) | 仮設動力 S 相不良 — B1/E1 焼損のあと OCR-BL OFF | — | ME-CM | — | 制御方式・略称のみ | 機種フィルタ対象外。全機種対応なら lists_model_label を全エレ機種へ |
| [KH-MEBL-SCALE-LOCK-PIN-340](../../cards/practice-guides/KH-MEBL-SCALE-LOCK-PIN-340.md) | ME-BL — 秤固定金（シャックル後に取外） | — | ME-BL | — | 制御方式・略称のみ | 機種フィルタ対象外。全機種対応なら lists_model_label を全エレ機種へ |
| [KH-MR-2ND-PIT-SW-HEIGHT-166](../../cards/practice-guides/KH-MR-2ND-PIT-SW-HEIGHT-166.md) | MR — 2nd ピットスイッチ取付高さ | — | MR機種 | — | 制御方式・略称のみ | 機種フィルタ対象外。全機種対応なら lists_model_label を全エレ機種へ |
| [KH-MR-BRAKE-TORQUE-DOC-275](../../cards/practice-guides/KH-MR-BRAKE-TORQUE-DOC-275.md) | MR ブレーキ — C-4 トルクボルト改定 | — | MR機種 | — | 制御方式・略称のみ | 機種フィルタ対象外。全機種対応なら lists_model_label を全エレ機種へ |
| [KH-MR-CAGE-CP-PROTECTOR-201](../../cards/practice-guides/KH-MR-CAGE-CP-PROTECTOR-201.md) | MR — かご側制御ケーブル立上げとプロテクター同時取付 | — | MR機種 | — | 制御方式・略称のみ | 機種フィルタ対象外。全機種対応なら lists_model_label を全エレ機種へ |
| [KH-MR-CONTROL-CABLE-HANG-420](../../cards/practice-guides/KH-MR-CONTROL-CABLE-HANG-420.md) | MR — 制御ケーブル吊り高さ（据付ノート・C-10-C5.3） | — | MR機種 | — | 制御方式・略称のみ | 機種フィルタ対象外。全機種対応なら lists_model_label を全エレ機種へ |
| [KH-MR-EMER-PIT-STATION-HEIGHT-159](../../cards/practice-guides/KH-MR-EMER-PIT-STATION-HEIGHT-159.md) | 非常用エレ — ピットステーション取付高さ | — | MR機種 | — | 制御方式・略称のみ | 機種フィルタ対象外。全機種対応なら lists_model_label を全エレ機種へ |
| [KH-MR-ER-EXTRA-DL-DOT-348](../../cards/practice-guides/KH-MR-ER-EXTRA-DL-DOT-348.md) | MR — 深ピット ER 運転時の DL-1/DOT-1 追加手配 | — | MR機種 | — | 制御方式・略称のみ | 機種フィルタ対象外。全機種対応なら lists_model_label を全エレ機種へ |
| [KH-MR-GROUP-PANEL-POWER-371](../../cards/case-summaries/KH-MR-GROUP-PANEL-POWER-371.md) | 群管理盤への電源線抜けで乗場釦のみ失效 | — | MR機種 | — | 制御方式・略称のみ | 機種フィルタ対象外。全機種対応なら lists_model_label を全エレ機種へ |
| [KH-MR-HOIST-WELD-SITE-276](../../cards/practice-guides/KH-MR-HOIST-WELD-SITE-276.md) | MR 巻上機 — 現地溶接箇所の確認 | — | MR機種 | — | 制御方式・略称のみ | 機種フィルタ対象外。全機種対応なら lists_model_label を全エレ機種へ |
| [KH-MR-IMV-LV1-RESET-357](../../cards/case-summaries/KH-MR-IMV-LV1-RESET-357.md) | MR — IMV 長周期振動感知 Lv1 リセット結線訂正 | — | MR機種 | — | 制御方式・略称のみ | 機種フィルタ対象外。全機種対応なら lists_model_label を全エレ機種へ |
| [KH-MR-L-DOOR-COTTON-UNLOCK-242](../../cards/practice-guides/KH-MR-L-DOOR-COTTON-UNLOCK-242.md) | MR L型戸 — 錠引き外し装置廃止・コットン解錠 | — | MR機種 | — | 制御方式・略称のみ | 機種フィルタ対象外。全機種対応なら lists_model_label を全エレ機種へ |
| [KH-MR-MELD-CP-LIVE-WORK-167](../../cards/case-summaries/KH-MR-MELD-CP-LIVE-WORK-167.md) | MELD R4-S4-T4 結線時 CP 活線 — コンダクタ焼損（↑高） | — | MR機種 | — | 制御方式・略称のみ | 機種フィルタ対象外。全機種対応なら lists_model_label を全エレ機種へ |
| [KH-MR-METAL-DUCT-GROUND-252](../../cards/practice-guides/KH-MR-METAL-DUCT-GROUND-252.md) | MR — 金属ダクト・可とう管アース（内線規程） | — | MR機種 | — | 制御方式・略称のみ | 機種フィルタ対象外。全機種対応なら lists_model_label を全エレ機種へ |
| [KH-MR-NL-DIFF-TRANS-ESTOP-306](../../cards/practice-guides/KH-MR-NL-DIFF-TRANS-ESTOP-306.md) | MR 高速 — NL 差動トランス調整後 E-STOP 確認 | — | MR機種 | — | 制御方式・略称のみ | 機種フィルタ対象外。全機種対応なら lists_model_label を全エレ機種へ |
| [KH-MR-PIANO-WIRE-SPACING-396](../../cards/practice-guides/KH-MR-PIANO-WIRE-SPACING-396.md) | 型板設定 — ピアノ線間寸法（IN-EL-08-111 / Excel） | — | MR機種 | — | 制御方式・略称のみ | 機種フィルタ対象外。全機種対応なら lists_model_label を全エレ機種へ |
| [KH-MR-S14-CWT-GUIDE-BRACKET-376](../../cards/practice-guides/KH-MR-S14-CWT-GUIDE-BRACKET-376.md) | MR S14耐震 — CWT 上部ガイド取付台二重手配 | — | MR機種 | — | 制御方式・略称のみ | 機種フィルタ対象外。全機種対応なら lists_model_label を全エレ機種へ |
| [KH-MR-SEISMIC-SW-ELEQUICK-157](../../cards/practice-guides/KH-MR-SEISMIC-SW-ELEQUICK-157.md) | MR 地震感知器 — 同時リセット SW と ELE-QUICK | — | MR機種 | — | 制御方式・略称のみ | 機種フィルタ対象外。全機種対応なら lists_model_label を全エレ機種へ |
| [KH-MR-SFLEX-ROPE-SOCKET-278](../../cards/practice-guides/KH-MR-SFLEX-ROPE-SOCKET-278.md) | SfleX-rope と非対称ソケット — 労基・構造規格 | — | MR機種 | — | 制御方式・略称のみ | 機種フィルタ対象外。全機種対応なら lists_model_label を全エレ機種へ |
| [KH-MRL-BRAKE-WIRING-REVERSE-362](../../cards/case-summaries/KH-MRL-BRAKE-WIRING-REVERSE-362.md) | MRL — 制御盤内ブレーキ結線逆で空回し不能 | — | MRL機種 | — | 制御方式・略称のみ | 機種フィルタ対象外。全機種対応なら lists_model_label を全エレ機種へ |
| [KH-MRL-CAR-PANEL-B3-SW-438](../../cards/case-summaries/KH-MRL-CAR-PANEL-B3-SW-438.md) | 操作盤フロント/リア取違え — 平常-独立・ドア-切 SW 无效 | — | MRL機種 | — | 制御方式・略称のみ | 機種フィルタ対象外。全機種対応なら lists_model_label を全エレ機種へ |
| [KH-MRL-HALL-IND-PART-NO-232](../../cards/practice-guides/KH-MRL-HALL-IND-PART-NO-232.md) | MRL — 乗場位置表示器の図番（T-366） | — | MRL機種 | — | 制御方式・略称のみ | 機種フィルタ対象外。全機種対応なら lists_model_label を全エレ機種へ |
| [KH-MRL-HALL-IND-WRONG-BOARD-318](../../cards/case-summaries/KH-MRL-HALL-IND-WRONG-BOARD-318.md) | 乗場位置表示 — LHH-1230E で G14/G24 取違え | — | MRL機種 | — | 制御方式・略称のみ | 機種フィルタ対象外。全機種対応なら lists_model_label を全エレ機種へ |
| [KH-MRL-HEALTH-AIR-MED-VERSION-266](../../cards/practice-guides/KH-MRL-HEALTH-AIR-MED-VERSION-266.md) | ヘルスエア — MED-2 / 2.1 / 2.2 / 3 の違い | — | MRL機種 | — | 制御方式・略称のみ | 機種フィルタ対象外。全機種対応なら lists_model_label を全エレ機種へ |
| [KH-MRL-HMS-SUNLIGHT-316](../../cards/case-summaries/KH-MRL-HMS-SUNLIGHT-316.md) | MRL — HMS 日光差込で扉開きっぱなし | — | MRL機種 | — | 制御方式・略称のみ | 機種フィルタ対象外。全機種対応なら lists_model_label を全エレ機種へ |
| [KH-MRL-HYD-BRAKE-OLS-250](../../cards/case-summaries/KH-MRL-HYD-BRAKE-OLS-250.md) | 油圧ブレーキ — OPC/OLS 緩み（939/948） | — | MRL機種 | — | 制御方式・略称のみ | 機種フィルタ対象外。全機種対応なら lists_model_label を全エレ機種へ |
| [KH-MRL-IR-REMOTE-CHANNEL-164](../../cards/practice-guides/KH-MRL-IR-REMOTE-CHANNEL-164.md) | 赤外線リモコン — チャンネル初期化と海外モード | — | MRL機種 | — | 制御方式・略称のみ | 機種フィルタ対象外。全機種対応なら lists_model_label を全エレ機種へ |
| [KH-MRL-ISO-TRANS-CST-HST-260](../../cards/practice-guides/KH-MRL-ISO-TRANS-CST-HST-260.md) | 絶縁トランス — CST/HST 停止時電圧上振れ | — | MRL機種 | — | 制御方式・略称のみ | 機種フィルタ対象外。全機種対応なら lists_model_label を全エレ機種へ |
| [KH-MRL-LANDING-NS-RSW-FW-184](../../cards/case-summaries/KH-MRL-LANDING-NS-RSW-FW-184.md) | 乗場 NS テンキー — インジ CPU RSW FW=1 | — | MRL機種 | — | 制御方式・略称のみ | 機種フィルタ対象外。全機種対応なら lists_model_label を全エレ機種へ |
| [KH-MRL-LOAD-TEST-ESTOP-437](../../cards/case-summaries/KH-MRL-LOAD-TEST-ESTOP-437.md) | 負荷試験 110% で E-stop — トランス容量・SW_ACFST | — | MRL機種 | — | 制御方式・略称のみ | 機種フィルタ対象外。全機種対応なら lists_model_label を全エレ機種へ |
| [KH-MRL-MOVABLE-VANE-CAM-359](../../cards/case-summaries/KH-MRL-MOVABLE-VANE-CAM-359.md) | 可動ベーン動作カムずれで戸全閉しない（ガガガ） | — | MRL機種 | — | 制御方式・略称のみ | 機種フィルタ対象外。全機種対応なら lists_model_label を全エレ機種へ |
| [KH-MRL-OBC-RUBBER-CAP-127](../../cards/practice-guides/KH-MRL-OBC-RUBBER-CAP-127.md) | OBC 緩衝器 — ラバーキャップ外れ | — | MRL機種 | — | 制御方式・略称のみ | 機種フィルタ対象外。全機種対応なら lists_model_label を全エレ機種へ |
| [KH-MRL-POWER-CABLE-IR-307](../../cards/case-summaries/KH-MRL-POWER-CABLE-IR-307.md) | MRL — 動力線絶縁抵抗不良（配線整理） | — | MRL機種 | — | 制御方式・略称のみ | 機種フィルタ対象外。全機種対応なら lists_model_label を全エレ機種へ |
| [KH-MRL-PRECISION-S-WAVE-TEST-138](../../cards/practice-guides/KH-MRL-PRECISION-S-WAVE-TEST-138.md) | MRL — 精密級 S 波地震感知器の点検 | — | MRL機種 | — | 制御方式・略称のみ | 機種フィルタ対象外。全機種対応なら lists_model_label を全エレ機種へ |
| [KH-MRL-RUNBY-SPACER-347](../../cards/practice-guides/KH-MRL-RUNBY-SPACER-347.md) | MRL — かご下調整板なしのランバイ調整（6t スペーサ） | — | MRL機種 | — | 制御方式・略称のみ | 機種フィルタ対象外。全機種対応なら lists_model_label を全エレ機種へ |
| [KH-MRL-SETS-664-665-436](../../cards/practice-guides/KH-MRL-SETS-664-665-436.md) | SETS 664/665 — 11 か月未実施（据付で検出） | — | MRL機種 | — | 制御方式・略称のみ | 機種フィルタ対象外。全機種対応なら lists_model_label を全エレ機種へ |
| [KH-MRL-SETS-DN1-BREAK-358](../../cards/case-summaries/KH-MRL-SETS-DN1-BREAK-358.md) | MRL — SETS DN1/DN2 断線で 62D 最寄階停止 | — | MRL機種 | — | 制御方式・略称のみ | 機種フィルタ対象外。全機種対応なら lists_model_label を全エレ機種へ |
| [KH-MRL-SETS-ENCODER-DIR-187](../../cards/case-summaries/KH-MRL-SETS-ENCODER-DIR-187.md) | SETS 基準書込み — ガバナエンコーダ回転方向・9999 | — | MRL機種 | — | 制御方式・略称のみ | 機種フィルタ対象外。全機種対応なら lists_model_label を全エレ機種へ |
| [KH-MRL-SHACKLE-SPRING-355](../../cards/case-summaries/KH-MRL-SHACKLE-SPRING-355.md) | MRL — シャックルばね取付間違いで秤ワイヤー余り | — | MRL機種 | — | 制御方式・略称のみ | 機種フィルタ対象外。全機種対応なら lists_model_label を全エレ機種へ |
| [KH-MRL-SMOKE-INSPECT-SW-DIFF-385](../../cards/practice-guides/KH-MRL-SMOKE-INSPECT-SW-DIFF-385.md) | VFGLB vs VFGLF — 煙感知器点検口 SW 動作差 | — | MRL機種 | — | 制御方式・略称のみ | 機種フィルタ対象外。全機種対応なら lists_model_label を全エレ機種へ |
| [KH-MRL-SMOKE-SHAFT-DETECTOR-154](../../cards/practice-guides/KH-MRL-SMOKE-SHAFT-DETECTOR-154.md) | 遮煙現場 — 昇降路内煙感知器の要否 | — | MRL機種 | — | 制御方式・略称のみ | 機種フィルタ対象外。全機種対応なら lists_model_label を全エレ機種へ |
| [KH-MRL-SMOKE-SHAFT-SENSOR-154](../../cards/practice-guides/KH-MRL-SMOKE-SHAFT-SENSOR-154.md) | 遮煙現場 — シャフト内煙感知器と防火区画 | — | MRL機種 | — | 制御方式・略称のみ | 機種フィルタ対象外。全機種対応なら lists_model_label を全エレ機種へ |
| [KH-MRL-SOFT-MNT-170](../../cards/practice-guides/KH-MRL-SOFT-MNT-170.md) | ソフト MNT — 投入・解除と発報回避 | — | MRL機種 | — | 制御方式・略称のみ | 機種フィルタ対象外。全機種対応なら lists_model_label を全エレ機種へ |
| [KH-MRL-TYRE-BRACKET-ORIENTATION-372](../../cards/practice-guides/KH-MRL-TYRE-BRACKET-ORIENTATION-372.md) | MRL — タイブラケット取付向き（逆付け静観） | — | MRL機種 | — | 制御方式・略称のみ | 機種フィルタ対象外。全機種対応なら lists_model_label を全エレ機種へ |
| [KH-MRL-UCMP-SEISMIC-INDEX-390](../../cards/practice-guides/KH-MRL-UCMP-SEISMIC-INDEX-390.md) | MR — UCMP・地震管制（Lists 390 索引） | — | MR機種 | — | 制御方式・略称のみ | 機種フィルタ対象外。全機種対応なら lists_model_label を全エレ機種へ |
| [KH-NEW-AXIEZ-100V-200V-LEAK-32](../../cards/case-summaries/KH-NEW-AXIEZ-100V-200V-LEAK-32.md) | 新 AXIEZ — 動力から 100V 系への漏えい（YE315C379） | — | 新AXIEZ | — | 制御方式・略称のみ | 機種フィルタ対象外。全機種対応なら lists_model_label を全エレ機種へ |
| [KH-NEW-AXIEZ-JR-SMOKE-29-LATCH-141](../../cards/practice-guides/KH-NEW-AXIEZ-JR-SMOKE-29-LATCH-141.md) | JR 仕様 — 煙感知 29 切りラッチ | — | 新AXIEZ | — | 制御方式・略称のみ | 機種フィルタ対象外。全機種対応なら lists_model_label を全エレ機種へ |
| [KH-NEW-AXIEZ-RDK-120-1-172](../../cards/practice-guides/KH-NEW-AXIEZ-RDK-120-1-172.md) | RDK 120-1 切断 — 1F 扉開・乗場ポータブル不可 | — | 新AXIEZ | — | 制御方式・略称のみ | 機種フィルタ対象外。全機種対応なら lists_model_label を全エレ機種へ |
| [KH-NEW-AXIEZ-ROPE-WELD-28](../../cards/case-summaries/KH-NEW-AXIEZ-ROPE-WELD-28.md) | 主ロープ素線切れ — 溶接加熱脆化 | — | 新AXIEZ | — | 制御方式・略称のみ | 機種フィルタ対象外。全機種対応なら lists_model_label を全エレ機種へ |
| [KH-NEW-AXIEZ-WAGO-TERMINAL-165](../../cards/practice-guides/KH-NEW-AXIEZ-WAGO-TERMINAL-165.md) | ねじ式ターミナル — WAGO ドライバと官検ループ線 | — | 新AXIEZ | AXIEZ | 制御方式・略称のみ | 機種フィルタ対象外。全機種対応なら lists_model_label を全エレ機種へ |
| [KH-NEWAXIEZ-WEDGE-SOCKET-MARK-121](../../cards/practice-guides/KH-NEWAXIEZ-WEDGE-SOCKET-MARK-121.md) | くさび式端末ソケット — 鋳出し番号の意味 | — | 新AXIEZ | — | 制御方式・略称のみ | 機種フィルタ対象外。全機種対応なら lists_model_label を全エレ機種へ |
| [KH-P1-7SEG-WDT-151](../../cards/case-summaries/KH-P1-7SEG-WDT-151.md) | P1基板不良で7SEG・WDTが点灯しない | — | — | — | 制御方式・略称のみ | 機種フィルタ対象外。全機種対応なら lists_model_label を全エレ機種へ |
| [KH-RS-SV-FALL-PROTECTION-NOT-243](../../cards/practice-guides/KH-RS-SV-FALL-PROTECTION-NOT-243.md) | RS-SV — 脱落防止 vs ウエサポート（据付図誤記） | — | RS-SV | — | 制御方式・略称のみ | 機種フィルタ対象外。全機種対応なら lists_model_label を全エレ機種へ |
| [KH-SCU20-CONN-TEST-228](../../cards/practice-guides/KH-SCU20-CONN-TEST-228.md) | SCU-20 接続テスト — 現地仕様は反映されず自動登録 | — | エレコール | — | 制御方式・略称のみ | 機種フィルタ対象外。全機種対応なら lists_model_label を全エレ機種へ |
| [KH-SCU20-FLASH-REWRITE-233](../../cards/practice-guides/KH-SCU20-FLASH-REWRITE-233.md) | SCU-20 フラッシュ書換 — CN37・メンテコン ver4（duplicate primary） | — | エレコール | — | 制御方式・略称のみ | 機種フィルタ対象外。全機種対応なら lists_model_label を全エレ機種へ |
| [KH-UPS-PEAK-SERVICE-350](../../cards/practice-guides/KH-UPS-PEAK-SERVICE-350.md) | UPS（アップピーク）不作動と監視盤・群管理の制御優先 | — | — | — | 制御方式・略称のみ | 機種フィルタ対象外。全機種対応なら lists_model_label を全エレ機種へ |
| [KH-VFEL-DZ-PLATE-SHORT-RUN-182](../../cards/practice-guides/KH-VFEL-DZ-PLATE-SHORT-RUN-182.md) | VFEL — 短ランバイ時 DZ プレート停止（Notes のみ） | — | VFEL | — | 制御方式・略称のみ | 機種フィルタ対象外。全機種対応なら lists_model_label を全エレ機種へ |
| [KH-VFGH-CWT-MID-STOPPER-402](../../cards/practice-guides/KH-VFGH-CWT-MID-STOPPER-402.md) | 中間免震 — CWT 枠中間ストッパーなし | — | VFGH | VFGH | 制御方式・略称のみ | 機種フィルタ対象外。全機種対応なら lists_model_label を全エレ機種へ |
| [KH-VFGH-ER-OPERATION-DL-A-379](../../cards/case-summaries/KH-VFGH-ER-OPERATION-DL-A-379.md) | ER 運転 — DL-A/DOT-A と緩衝器前停止 | — | VFGH | VFGH | 制御方式・略称のみ | 機種フィルタ対象外。全機種対応なら lists_model_label を全エレ機種へ |
| [KH-VFGH-FE-FIRE-RELAY-102](../../cards/case-summaries/KH-VFGH-FE-FIRE-RELAY-102.md) | FE1S/FE2S 接触不良 — 506 と自動運転不能 | — | VFGH | VFGH | 制御方式・略称のみ | 機種フィルタ対象外。全機種対応なら lists_model_label を全エレ機種へ |
| [KH-VFGH-FORCED-SINGLE-CAR-129](../../cards/practice-guides/KH-VFGH-FORCED-SINGLE-CAR-129.md) | VFGH — 強制シングルカーモード設定 | — | VFGH | VFGH | 制御方式・略称のみ | 機種フィルタ対象外。全機種対応なら lists_model_label を全エレ機種へ |
| [KH-VFGH-HALL-BUTTON-ZONE-15](../../cards/case-summaries/KH-VFGH-HALL-BUTTON-ZONE-15.md) | VFGH — 乗場ボタン一部階不可 | — | VFGH | — | 制御方式・略称のみ | 機種フィルタ対象外。全機種対応なら lists_model_label を全エレ機種へ |
| [KH-VFGH-HALL-LANTERN-PINCH-147](../../cards/case-summaries/KH-VFGH-HALL-LANTERN-PINCH-147.md) | ホールランタン施工で N5A 621A 挟み込み — 乗場釦失效 | — | VFGH | VFGH | 制御方式・略称のみ | 機種フィルタ対象外。全機種対応なら lists_model_label を全エレ機種へ |
| [KH-VFGH-HMS-MBS-T2T3-352](../../cards/case-summaries/KH-VFGH-HMS-MBS-T2T3-352.md) | VFGH — HMS/MBS I/F ユニット T2/T3 誤結線 | — | VFGH | VFGH | 制御方式・略称のみ | 機種フィルタ対象外。全機種対応なら lists_model_label を全エレ機種へ |
| [KH-VFGH-LOCKDOWN-Y-GAP-388](../../cards/case-summaries/KH-VFGH-LOCKDOWN-Y-GAP-388.md) | ロックダウン — Y 寸法は目安・隙間あれば可 | — | VFGH | VFGH | 制御方式・略称のみ | 機種フィルタ対象外。全機種対応なら lists_model_label を全エレ機種へ |
| [KH-VFGH-MDU-BACKUP-BATTERY-123](../../cards/practice-guides/KH-VFGH-MDU-BACKUP-BATTERY-123.md) | MELD なし — 受電盤バックアップバッテリー | — | VFGH | VFGH | 制御方式・略称のみ | 機種フィルタ対象外。全機種対応なら lists_model_label を全エレ機種へ |
| [KH-VFGH-PIT-ACCESS-GOV-413](../../cards/practice-guides/KH-VFGH-PIT-ACCESS-GOV-413.md) | VFGH — ピット点検口と GOV 張車（出入り不可） | — | VFGH | VFGH | 制御方式・略称のみ | 機種フィルタ対象外。全機種対応なら lists_model_label を全エレ機種へ |
| [KH-VFGH-RAIL-JOINT-TRIAL-190](../../cards/practice-guides/KH-VFGH-RAIL-JOINT-TRIAL-190.md) | VFGH — レール継ぎ目据付試行（稲電） | — | VFGH | — | 制御方式・略称のみ | 機種フィルタ対象外。全機種対応なら lists_model_label を全エレ機種へ |
| [KH-VFGH-RECEIVING-BACKUP-BATTERY-123](../../cards/practice-guides/KH-VFGH-RECEIVING-BACKUP-BATTERY-123.md) | MELD なしでも受電盤バッテリー — B79・P1 RAM 退避 | — | VFGH | VFGH | 制御方式・略称のみ | 機種フィルタ対象外。全機種対応なら lists_model_label を全エレ機種へ |
| [KH-VFGH-RUNBY-SW-MONITOR-410](../../cards/practice-guides/KH-VFGH-RUNBY-SW-MONITOR-410.md) | VFGH — ランバイ予報 SW の監視盤発報先（MIC/監視盤） | — | VFGH | VFGH | 制御方式・略称のみ | 機種フィルタ対象外。全機種対応なら lists_model_label を全エレ機種へ |
| [KH-VFGH-SAFETY-COLOR-EXEMPT-262](../../cards/practice-guides/KH-VFGH-SAFETY-COLOR-EXEMPT-262.md) | 安全カラー — VFGH は東日本で新設不要 | — | VFGH | — | 制御方式・略称のみ | 機種フィルタ対象外。全機種対応なら lists_model_label を全エレ機種へ |
| [KH-VFGH-SAI2200C-EMERG-IND-152](../../cards/practice-guides/KH-VFGH-SAI2200C-EMERG-IND-152.md) | SAI2200C バンク内非常用エレの乗場インジ点灯 | — | VFGH | VFGH | 制御方式・略称のみ | 機種フィルタ対象外。全機種対応なら lists_model_label を全エレ機種へ |
| [KH-VFGH-SCALE-BOARD-NO-VOLTAGE-426](../../cards/case-summaries/KH-VFGH-SCALE-BOARD-NO-VOLTAGE-426.md) | 秤基板無出力 — DC 基板故障と秤電源 CN1 抜け | — | VFGH | VFGH | 制御方式・略称のみ | 機種フィルタ対象外。全機種対応なら lists_model_label を全エレ機種へ |
| [KH-VFGH-SHORT-LANDING-LIMIT-428](../../cards/practice-guides/KH-VFGH-SHORT-LANDING-LIMIT-428.md) | 短ランバイ — 終端階から UL/DL 手動運転制限 | — | VFGH | VFGH | 制御方式・略称のみ | 機種フィルタ対象外。全機種対応なら lists_model_label を全エレ機種へ |
| [KH-VFGH-STEEL-CORE-CABLE-131](../../cards/practice-guides/KH-VFGH-STEEL-CORE-CABLE-131.md) | 鋼芯入り制御ケーブル — 誘導電圧対策の要否（芯数・120芯） | — | VFGH | VFGH | 制御方式・略称のみ | 機種フィルタ対象外。全機種対応なら lists_model_label を全エレ機種へ |
| [KH-VFGH-VIP-TABLET-LAMP-13](../../cards/case-summaries/KH-VFGH-VIP-TABLET-LAMP-13.md) | VFGH — VIP 運転灯（YBXA/YBXB） | — | VFGH | — | 制御方式・略称のみ | 機種フィルタ対象外。全機種対応なら lists_model_label を全エレ機種へ |
| [KH-VFGLB-ARES-SERVICE-STOP-175](../../cards/case-summaries/KH-VFGLB-ARES-SERVICE-STOP-175.md) | ARES 戸自閉対策 — 乗場休止で閉じ込め風 | — | VFGLB | VFGLB | 制御方式・略称のみ | 機種フィルタ対象外。全機種対応なら lists_model_label を全エレ機種へ |
| [KH-VFGLB-CAR-TOP-ORDER-104](../../cards/practice-guides/KH-VFGLB-CAR-TOP-ORDER-104.md) | かご上 ST — オーダー確認（7seg・ラベル） | — | VFGLB | VFGLB | 制御方式・略称のみ | 機種フィルタ対象外。全機種対応なら lists_model_label を全エレ機種へ |
| [KH-VFGLB-DOOR-SHORT-RELEASE-419](../../cards/practice-guides/KH-VFGLB-DOOR-SHORT-RELEASE-419.md) | VFGLB 戸短検出の解除（ラッチあり/なし） | — | VFGLB | VFGLB | 制御方式・略称のみ | 機種フィルタ対象外。全機種対応なら lists_model_label を全エレ機種へ |
| [KH-VFGLB-JPA-ACL-JUMPER-189](../../cards/practice-guides/KH-VFGLB-JPA-ACL-JUMPER-189.md) | VFGLB — JPA/ACL ジャンパ（Lists 189 保留・Notes のみ） | — | VFGLB | VFGLB | 制御方式・略称のみ | 機種フィルタ対象外。全機種対応なら lists_model_label を全エレ機種へ |
| [KH-VFGLB-JRE-LOAD-TEST-89](../../cards/practice-guides/KH-VFGLB-JRE-LOAD-TEST-89.md) | JRE 仕様 — 点検 SW 時の負荷試験（リモコン 7C/75） | — | VFGLB | VFGLB | 制御方式・略称のみ | 機種フィルタ対象外。全機種対応なら lists_model_label を全エレ機種へ |
| [KH-VFGLB-MAINT-MODE-FLICKER-173](../../cards/case-summaries/KH-VFGLB-MAINT-MODE-FLICKER-173.md) | 保守点検モード未解除 — 液晶階床点滅 | — | VFGLB | VFGLB | 制御方式・略称のみ | 機種フィルタ対象外。全機種対応なら lists_model_label を全エレ機種へ |
| [KH-VFGLB-MELD-BATTERY-174](../../cards/case-summaries/KH-VFGLB-MELD-BATTERY-174.md) | MELD バッテリー低電圧で移行せず — 交換後も戸開ボタン点滅 | — | VFGLB | VFGLB | 制御方式・略称のみ | 機種フィルタ対象外。全機種対応なら lists_model_label を全エレ機種へ |
| [KH-VFGLB-PIT-IN-MODE-EXIT-265](../../cards/practice-guides/KH-VFGLB-PIT-IN-MODE-EXIT-265.md) | VFGLB — Pit In（Pin）解除手順 | — | VFGLB | VFGLB | 制御方式・略称のみ | 機種フィルタ対象外。全機種対応なら lists_model_label を全エレ機種へ |
| [KH-VFGLB-SETS-64C-MON1-418](../../cards/practice-guides/KH-VFGLB-SETS-64C-MON1-418.md) | VFGLB — SETS 適用時 MON 64C（カゴ上確認の罠） | — | VFGLB | VFGLB | 制御方式・略称のみ | 機種フィルタ対象外。全機種対応なら lists_model_label を全エレ機種へ |
| [KH-VFGLB-TOUCHLESS-PHANTOM-CALL-110](../../cards/case-summaries/KH-VFGLB-TOUCHLESS-PHANTOM-CALL-110.md) | タッチレス — 最下階乗場・かご内の意図しない呼び | — | VFGLB | — | 制御方式・略称のみ | 機種フィルタ対象外。全機種対応なら lists_model_label を全エレ機種へ |
| [KH-VFGLB-UP1-SPRING-177](../../cards/case-summaries/KH-VFGLB-UP1-SPRING-177.md) | 最上階起動不能 — UP1 バネ外れと SETS 40 | — | VFGLB | VFGLB | 制御方式・略称のみ | 機種フィルタ対象外。全機種対応なら lists_model_label を全エレ機種へ |
| [KH-VFGLF-3WAY-LANDING-REST-421](../../cards/practice-guides/KH-VFGLF-3WAY-LANDING-REST-421.md) | VFGLF/VFGLB — 三路式乗場休止スイッチ | — | VFGLF、VFGLB | VFGLF、VFGLB | 制御方式・略称のみ | 機種フィルタ対象外。全機種対応なら lists_model_label を全エレ機種へ |
| [KH-VFGLF-BGM-WIRING-363](../../cards/practice-guides/KH-VFGLF-BGM-WIRING-363.md) | VFGLF/B — 二線式アッテネータ無 BGM 結線 | — | VFGLB、VFGLF | — | 制御方式・略称のみ | 機種フィルタ対象外。全機種対応なら lists_model_label を全エレ機種へ |
| [KH-VFGLF-BRAKE-OVERCURRENT-932-283](../../cards/case-summaries/KH-VFGLF-BRAKE-OVERCURRENT-932-283.md) | VFGLF — 着床後 BK 過電流 932/941 | — | VFGLF | — | 制御方式・略称のみ | 機種フィルタ対象外。全機種対応なら lists_model_label を全エレ機種へ |
| [KH-VFGLF-CPU-RESET-HAND-204](../../cards/practice-guides/KH-VFGLF-CPU-RESET-HAND-204.md) | VFGLF — かご不可時の P1 電源リセット | — | VFGLF | VFGLF | 制御方式・略称のみ | 機種フィルタ対象外。全機種対応なら lists_model_label を全エレ機種へ |
| [KH-VFGLF-CWT-RESTRAINT-BOLT-NOISE-210](../../cards/case-summaries/KH-VFGLF-CWT-RESTRAINT-BOLT-NOISE-210.md) | CWT 枠異音 — おもり抑えボルト締付 | — | VFGLF | VFGLF | 制御方式・略称のみ | 機種フィルタ対象外。全機種対応なら lists_model_label を全エレ機種へ |
| [KH-VFGLF-DOOR-SHORT-CHECK-160](../../cards/case-summaries/KH-VFGLF-DOOR-SHORT-CHECK-160.md) | 戸短検出 — 独立運転復帰では戸短チェック不可 | — | VFGLF | VFGLF | 制御方式・略称のみ | 機種フィルタ対象外。全機種対応なら lists_model_label を全エレ機種へ |
| [KH-VFGLF-EMERG-STOP-RAIL-235](../../cards/case-summaries/KH-VFGLF-EMERG-STOP-RAIL-235.md) | VFGLF — 非常止め試験で降下継続 | — | VFGLF | — | 制御方式・略称のみ | 機種フィルタ対象外。全機種対応なら lists_model_label を全エレ機種へ |
| [KH-VFGLF-FLOOD-SENSOR-ARM-351](../../cards/practice-guides/KH-VFGLF-FLOOD-SENSOR-ARM-351.md) | VFGLF — 冠水センサ本体なし・取付腕のみ届く | — | VFGLF | VFGLF | 制御方式・略称のみ | 機種フィルタ対象外。全機種対応なら lists_model_label を全エレ機種へ |
| [KH-VFGLF-GROUP-PANEL-WIRING-349](../../cards/case-summaries/KH-VFGLF-GROUP-PANEL-WIRING-349.md) | 増設盤 MAF/MAG と MKF/MKG 誤結線 — Z03/P1 焼損 | — | VFGLF | VFGLF | 制御方式・略称のみ | 機種フィルタ対象外。全機種対応なら lists_model_label を全エレ機種へ |
| [KH-VFGLF-GROUP-WIRING-SAVE-MODE-253](../../cards/practice-guides/KH-VFGLF-GROUP-WIRING-SAVE-MODE-253.md) | VFGLF — 群管理結線未完と据付省力乗場モード（索引） | — | VFGLF | — | 制御方式・略称のみ | 機種フィルタ対象外。全機種対応なら lists_model_label を全エレ機種へ |
| [KH-VFGLF-HA-MONITOR-0V-225](../../cards/case-summaries/KH-VFGLF-HA-MONITOR-0V-225.md) | VFGLF — ヘルスエアモニター出力 0V（降圧トランス疑い） | — | VFGLF | — | 制御方式・略称のみ | 機種フィルタ対象外。全機種対応なら lists_model_label を全エレ機種へ |
| [KH-VFGLF-IND-FLOOR-OFFSET-107](../../cards/case-summaries/KH-VFGLF-IND-FLOOR-OFFSET-107.md) | かご内行先予報灯 — 1 階床ズレ（インジ S/W） | — | VFGLF | VFGLF | 制御方式・略称のみ | 機種フィルタ対象外。全機種対応なら lists_model_label を全エレ機種へ |
| [KH-VFGLF-INSTALL-FLAG-361](../../cards/practice-guides/KH-VFGLF-INSTALL-FLAG-361.md) | 据付け中認識フラグ — 引渡し完了で OH 制限（1009 30CF） | — | VFGLF | VFGLF | 制御方式・略称のみ | 機種フィルタ対象外。全機種対応なら lists_model_label を全エレ機種へ |
| [KH-VFGLF-KCD-P1-COMPAT-156](../../cards/practice-guides/KH-VFGLF-KCD-P1-COMPAT-156.md) | VFGLF — KCD-1160 P1 互換と D41（Notes のみ） | — | VFGLF | VFGLF | 制御方式・略称のみ | 機種フィルタ対象外。全機種対応なら lists_model_label を全エレ機種へ |
| [KH-VFGLF-KEIAIN-HARNESS-PINCH-382](../../cards/case-summaries/KH-VFGLF-KEIAIN-HARNESS-PINCH-382.md) | VFGLF — 気配り配線挟み込みで +12V 切・U-CAN 不能 | — | VFGLF | — | 制御方式・略称のみ | 機種フィルタ対象外。全機種対応なら lists_model_label を全エレ機種へ |
| [KH-VFGLF-LHH-32X-DISPLAY-93](../../cards/practice-guides/KH-VFGLF-LHH-32X-DISPLAY-93.md) | VFGLF 表示基板 LHH-32X の手配と現地取扱 | — | — | — | 制御方式・略称のみ | 機種フィルタ対象外。全機種対応なら lists_model_label を全エレ機種へ |
| [KH-VFGLF-LINE-LED-GROUND-414](../../cards/case-summaries/KH-VFGLF-LINE-LED-GROUND-414.md) | ライン LED 挟み込み地絡 — 421 U-CAN | — | VFGLF | VFGLF | 制御方式・略称のみ | 機種フィルタ対象外。全機種対応なら lists_model_label を全エレ機種へ |
| [KH-VFGLF-LINKS-2S-GATE-SW-124](../../cards/practice-guides/KH-VFGLF-LINKS-2S-GATE-SW-124.md) | LINKs 2S — 新ゲートスイッチ設定寸法 | — | VFGLF | VFGLF | 制御方式・略称のみ | 機種フィルタ対象外。全機種対応なら lists_model_label を全エレ機種へ |
| [KH-VFGLF-M1-AC-SAG-397](../../cards/case-summaries/KH-VFGLF-M1-AC-SAG-397.md) | M1 カード — AC 低下 312 と急停止 | — | VFGLF | VFGLF | 制御方式・略称のみ | 機種フィルタ対象外。全機種対応なら lists_model_label を全エレ機種へ |
| [KH-VFGLF-M14-MELDEN-429](../../cards/case-summaries/KH-VFGLF-M14-MELDEN-429.md) | M14 ピンアサイン — 345 MCB(MP) 遮断 | — | VFGLF | VFGLF | 制御方式・略称のみ | 機種フィルタ対象外。全機種対応なら lists_model_label を全エレ機種へ |
| [KH-VFGLF-MULTICAR-MYSERT-PC-PLATE-224](../../cards/practice-guides/KH-VFGLF-MULTICAR-MYSERT-PC-PLATE-224.md) | 異制御マルチカー — マイサート盤 PC 取付板形状 | — | VFGLF | VFGLF | 制御方式・略称のみ | 機種フィルタ対象外。全機種対応なら lists_model_label を全エレ機種へ |
| [KH-VFGLF-OPTION-PANEL-GUARD-148](../../cards/practice-guides/KH-VFGLF-OPTION-PANEL-GUARD-148.md) | オプション盤 — 引っ掛かり防止番線 15 m 境界 | — | VFGLF | VFGLF | 制御方式・略称のみ | 機種フィルタ対象外。全機種対応なら lists_model_label を全エレ機種へ |
| [KH-VFGLF-P15-CABLE-CAGE-217](../../cards/case-summaries/KH-VFGLF-P15-CABLE-CAGE-217.md) | P15 — 最下階制御ケーブルとかご干渉 | — | VFGLF | VFGLF | 制御方式・略称のみ | 機種フィルタ対象外。全機種対応なら lists_model_label を全エレ機種へ |
| [KH-VFGLF-R03-PIT-WIRE-226](../../cards/case-summaries/KH-VFGLF-R03-PIT-WIRE-226.md) | R03 昇降路幹線損傷 — ダウン呼び常時・BP ヒューズ・29 ライン | — | VFGLF | VFGLF | 制御方式・略称のみ | 機種フィルタ対象外。全機種対応なら lists_model_label を全エレ機種へ |
| [KH-VFGLF-RAIL-SPACER-DL-125](../../cards/practice-guides/KH-VFGLF-RAIL-SPACER-DL-125.md) | レール下端スペーサー — DL と手配量 | — | VFGLF | VFGLF | 制御方式・略称のみ | 機種フィルタ対象外。全機種対応なら lists_model_label を全エレ機種へ |
| [KH-VFGLF-REGEN-CONVERTER-WIRING-185](../../cards/case-summaries/KH-VFGLF-REGEN-CONVERTER-WIRING-185.md) | 回生コンバータ中継未配線 — 磁極補正 141 | — | VFGLB・VFGLF | VFGLB、VFGLF | 制御方式・略称のみ | 機種フィルタ対象外。全機種対応なら lists_model_label を全エレ機種へ |
| [KH-VFGLF-REMOTE-WATCH-186](../../cards/practice-guides/KH-VFGLF-REMOTE-WATCH-186.md) | 遠隔監視 — 保守作業見守り機能と MIC 作業届 | — | VFGLB・VFGLF | VFGLF、VFGLB | 制御方式・略称のみ | 機種フィルタ対象外。全機種対応なら lists_model_label を全エレ機種へ |
| [KH-VFGLF-RESOLVER-BOARD-113](../../cards/case-summaries/KH-VFGLF-RESOLVER-BOARD-113.md) | レゾルバ基板 KCZ-990C — 93F 空回し不能 | — | VFGLF | VFGLF | 制御方式・略称のみ | 機種フィルタ対象外。全機種対応なら lists_model_label を全エレ機種へ |
| [KH-VFGLF-S21-B2-PIN-380](../../cards/case-summaries/KH-VFGLF-S21-B2-PIN-380.md) | S21 B2 ピン抜け — 842 と SETS 下降不良 | — | VFGLF | VFGLF | 制御方式・略称のみ | 機種フィルタ対象外。全機種対応なら lists_model_label を全エレ機種へ |
| [KH-VFGLF-SCU20-GS3-149](../../cards/case-summaries/KH-VFGLF-SCU20-GS3-149.md) | SCU-20 通信不成立 — GS3 ロータリー設定（品目表 -01/-02） | — | VFGLF | VFGLF | 制御方式・略称のみ | 機種フィルタ対象外。全機種対応なら lists_model_label を全エレ機種へ |
| [KH-VFGLF-SD-T12-CONTACTOR-95](../../cards/case-summaries/KH-VFGLF-SD-T12-CONTACTOR-95.md) | SD-T12（LBA/LBB）吸引後にブレーキが引かない | — | — | — | 制御方式・略称のみ | 機種フィルタ対象外。全機種対応なら lists_model_label を全エレ機種へ |
| [KH-VFGLF-SD-T21-CONTACTOR-96](../../cards/case-summaries/KH-VFGLF-SD-T21-CONTACTOR-96.md) | SD-T21（#5/M5/LBA）コンタクタ不吸引 | — | — | — | 制御方式・略称のみ | 機種フィルタ対象外。全機種対応なら lists_model_label を全エレ機種へ |
| [KH-VFGLF-SSC-JGS-CR1-197](../../cards/case-summaries/KH-VFGLF-SSC-JGS-CR1-197.md) | SSC 不良 — JGS 経由で CR1 トリップ | — | VFGLB・VFGLF | VFGLF | 制御方式・略称のみ | 機種フィルタ対象外。全機種対応なら lists_model_label を全エレ機種へ |
| [KH-VFGLF-TOUCHLESS-INIT-365](../../cards/practice-guides/KH-VFGLF-TOUCHLESS-INIT-365.md) | VFGLF/B/VFGH — タッチレス釦初期設定 | — | VFGLF、VFGLB、VFGH | — | 制御方式・略称のみ | 機種フィルタ対象外。全機種対応なら lists_model_label を全エレ機種へ |
| [KH-VFGLF-WINCH-CABLE-ROUTE-126](../../cards/practice-guides/KH-VFGLF-WINCH-CABLE-ROUTE-126.md) | 巻上機 — 現地ケーブル交換時の配線ルート | — | VFGLF | VFGLF | 制御方式・略称のみ | 機種フィルタ対象外。全機種対応なら lists_model_label を全エレ機種へ |
| [KH-VFGR-CAR-TOP-RUN-SW-319](../../cards/case-summaries/KH-VFGR-CAR-TOP-RUN-SW-319.md) | VFGR かご上 RUN SW OFF — 手動運転不能 | — | VFGR | VFGR | 制御方式・略称のみ | 機種フィルタ対象外。全機種対応なら lists_model_label を全エレ機種へ |
| [KH-VFGR-DIRECT-COMM-B3B7-354](../../cards/case-summaries/KH-VFGR-DIRECT-COMM-B3B7-354.md) | VFGR 直伝通信未確立 — B3/B7 テレコ（ドアSW・点検SW） | MELCITY | VFGR | VFGR | 制御方式・略称のみ | 機種フィルタ対象外。全機種対応なら lists_model_label を全エレ機種へ |
| [KH-VFGR-FLASH-WRITE-CABLE-284](../../cards/practice-guides/KH-VFGR-FLASH-WRITE-CABLE-284.md) | VFGR — フラッシュ書換時は LAN 外す | — | VFGR | VFGR | 制御方式・略称のみ | 機種フィルタ対象外。全機種対応なら lists_model_label を全エレ機種へ |

## P4 汎用ラベル／空（対応不要の情報）（107 件）

対応不要（全機種向けまたは未記載）。個別の確認行は出さず ID のみ列挙する。

- 汎用ラベル（96 件）: KH-ALL-1D2G-PAD-REVERSED-324, KH-ALL-AC-RUN-MANUAL-255, KH-ALL-AC-SCHEDULE-208, KH-ALL-ACO-E-REMOTE-STOP-377, KH-ALL-ALARM-HISTORY-MC3-300, KH-ALL-ANNOUNCE-LHV10X-MODE-322, KH-ALL-BARRIER-FREE-INSPECTION-135, KH-ALL-BGM-EMERG-WIRING-179, KH-ALL-BRACKET-SPAN-115, KH-ALL-BROADCAST-2-3-WIRE-122, KH-ALL-CABIN-ILLUMINANCE-62LX-282, KH-ALL-CAMERA-COMPOSITE-NTSC-145, KH-ALL-CAR-KETA-BRACKET-GAP-295, KH-ALL-CAR-LOCK-ARM-256, KH-ALL-CBS-FIX-VERIFY-220, KH-ALL-CONDUCTOR-5-DIODE-R1-180, KH-ALL-CONNECTOR-ORDER-236, KH-ALL-CONSTRUCTION-AC-DISUSE-303, KH-ALL-CONSTRUCTION-DLD-REVERSE-183, KH-ALL-CR-SECURITY-FLOOR-DISPLAY-269, KH-ALL-CRIMP-LEAD-HARNESS-ORDER-247, KH-ALL-CUSTOMER-BREAKER-CAPACITY-214, KH-ALL-D11-MINUS-COMMON-409, KH-ALL-DC-SUPPLY-PROTECT-RESET-249, KH-ALL-DOOR-DC321-PULSE0-381, KH-ALL-DRAWING-REF-DWG-386, KH-ALL-DRIP-LANDING-BUTTON-231, KH-ALL-ELEQUICK-LAMP-TEST-168, KH-ALL-ELEV-LOAD-HANDLING-367, KH-ALL-EMERG-ELEV-FIRE-SERVICE-290, KH-ALL-ERROR-CODE-3DIGIT-77, KH-ALL-FCC-A-6FLOOR-153, KH-ALL-FCC-A-FLOOR-153, KH-ALL-FINISH-PROTECTION-SHEET-216, KH-ALL-FIRESTOP-CFAJ-LABEL-146, KH-ALL-FLOOD-SHEAVE-REPLACE-219, KH-ALL-FMS-CAM-SKEW-330, KH-ALL-GROUND-N00-NORMAL-SLOW-176, KH-ALL-GROUP-ALARM-TRIGGER-286, KH-ALL-HA-AC-DIP-SW6-207, KH-ALL-HA-MONITOR-R1-OPEN-360, KH-ALL-HA-RESISTOR-POLARITY-206, KH-ALL-HALL-CHIME-SIGNAL-399, KH-ALL-HALL-LANTERN-WRONG-TYPE-267, KH-ALL-HOIST-HANDEDNESS-SW-188, KH-ALL-HOS-FL1-HALL-LANTERN-289, KH-ALL-HYOGO-TRUNK-SW-331, KH-ALL-INADEN-ORDER-CODE-279, KH-ALL-INSPECTION-LOCK-TYPES-270, KH-ALL-INTERCOM-CMODE-CPD-K-239, KH-ALL-IPHONE-VIB-NOISE-APP-341, KH-ALL-ITV-VOUT1-NOISE-323, KH-ALL-KEIAI-RX1-PINCH-424, KH-ALL-KEIAIN-DOOR-WIRING-407, KH-ALL-LANDING-AAN-NO-SOUND-302, KH-ALL-LANG-LAY-ROPE-TESTER-199, KH-ALL-LATERAL-GUARD-WIRE-277, KH-ALL-LUB236-BAKE-ORDER-106, KH-ALL-M5-CONTACTOR-PULL-64, KH-ALL-MAINT-WIFI-CERT-248, KH-ALL-MAINTCON-ACROBAT-TROUBLESHOOT-258, KH-ALL-MCB-THERMAL-CURVE-391, KH-ALL-MCB-TRIP-CONTACTS-405, KH-ALL-MEGA-FIRE-PANEL-162, KH-ALL-MILAI-HATCHING-337, KH-ALL-OBC10M-RUST-OIL-291, KH-ALL-OFFICE-ABC-WORK-144, KH-ALL-P1-CE1-EMPTY-SW-317, KH-ALL-PL-BREAKER-L10A-293, KH-ALL-PMBK-GROUP-BACKUP-294, KH-ALL-QUALITY-EMERGENCY-CONTACT-245, KH-ALL-RESERVE-TIMER-RSW-292, KH-ALL-RICE-PARTS-ORDER-311, KH-ALL-ROPE-WEDGE-PIN-76, KH-ALL-RUST-OIL-REMOVAL-387, KH-ALL-SEALING-INSTALL-STD-314, KH-ALL-SIGNAGE-TWIST-NOISE-178, KH-ALL-SMOKE-DOOR-SEAL-346, KH-ALL-SMOKE-SW-MOUNT-150, KH-ALL-TECHSPEC-BRAKE-TORQUE-133, KH-ALL-TEST-INSPECTION-ROLES-251, KH-ALL-TEST-ROLES-CERT-280, KH-ALL-TOUCHLESS-LHS1050A-RESET-321, KH-ALL-TRAP-LANDING-ACCESS-230, KH-ALL-UCMP-SW-PARAM-MISMATCH-305, KH-ALL-VOLTAGE-DROP-CABLE-191, KH-ALL-WELD-QA-SHEETS-198, KH-ALL-WELDER-LOW-VOLT-DN-383, KH-ALL-WHISPER-U-BOLT-SIZE-369, KH-ALL-WINCH-BREAKER-INVERTER-332, KH-ALL-X-PARTS-SYSTEM-333, KH-ESC-FALL-GUARD-VS-SUPPORT-254, KH-ESC-INSPECTION-BRAKE-DIST-313, KH-ESC-INSPECTION-KAKARI-CALC-312, KH-JRE-EMER-INTERCOM-MONITOR-423, KH-LV5K-LV6K-CLT-432
- 適用範囲が空（11 件）: KH-ALL-BILNET-PRINT-TEMPLATE-100, KH-ALL-FWCARD-MCENV-DEBUG-118, KH-ALL-INSTALL-TEST-ADJUST-HUB, KH-ALL-MAINTECON-P1-USB-88, KH-ALL-METREP-9INER-REAPPLY-378, KH-ALL-SHAFT-INTERNAL-ROUTING, KH-ALL-SMOKE-FIRE-SERVICE-MELD-227, KH-HEALTH-AIR-TIMER-RELAY-98, KH-IPU-MELD-BATTERY-POLARITY-101, KH-PIT-TRAP-POSITION-394, KH-SMOKE-DOOR-MELD-227
