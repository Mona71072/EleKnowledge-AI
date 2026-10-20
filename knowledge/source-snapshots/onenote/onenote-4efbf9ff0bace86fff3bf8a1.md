---
snapshot_type: "onenote_source_page"
source_system: "OneNote"
onenote_id: "d8955d07-6b7e-48ca-9936-9df3db4e3e7f:1"
knowledge_domain: "unknown"
organizational_scope: "unknown"
classification: "unknown"
review_status: "unreviewed"
publication_status: "not_published"
cloud_approval: "not_reviewed"
source_links_resolved: false
attachments_included: false
---

> Source snapshot for EleKnowledge-side organization. Not curated, not verified, and not RAG-eligible.

## OneNote content
[OneNote attachment reference omitted; attachment not copied]

SETS・・・スムーズ終端階非常減速装置（Smooth Emergency Terminal Slowdown）

SETS... Smooth Emergency Terminal Slowdown System

(1)MRL機種向けの装置。終端階付近で異常な速度を検知した際にカゴを緩衝器の許容速度以下に減速させる。通常、カゴ速度が上がるほど緩衝器の許容速度も上がる（緩衝器が長くなる）ため、ピット及びOHを大きくする必要があった。

A device for MRL models. It decelerates the car to below the buffer's permissible speed if an abnormal speed is detected near the terminal floor. Normally, as car speed increases, the buffer's permissible speed also increases (requiring longer buffers), necessitating larger pits and overheads.

(2)しかし、この装置によりどの速度でも緩衝器の許容速度を一定に減速させるため、速度に関係なく同じスペースの昇降路に設置が可能となった。

However, this device allows deceleration to a constant permissible buffer speed at any car speed, making installation possible in the same hoistway space regardless of speed.

76.SETS適用有の場合の調整作業

Adjustment Work When SETS is Applied

(1)高速調整時、このSETS装置が問題なく機能しているか確認を行う。

During high-speed adjustment, confirm that this SETS device functions without problems.

ガバナエンコーダの方向・速度確認

Governor Encoder Direction and Speed Confirmation

(1)作業内容

Work Procedure

①赤外線リモコンにて確認モードへ移行させ、乗場ETPにて運転を行う。

Switch to confirmation mode using the infrared remote control and operate from the landing ETP.

②運転時、乗場インジにて運転方向及びカゴ速度が表示されるので問題ないことを確認する。

During operation, the operating direction and car speed are displayed on the landing indicator; confirm there are no problems.

(2)目的

Purpose

①SETSが適用される場合、ガバナにエンコーダが設置される。SETSでは、このガバナエンコーダにて速度及び運転方向を検知している。

When SETS is applied, an encoder is installed on the governor. SETS detects speed and operating direction using this governor encoder.

②本調整にて問題なく速度を検知しているか、エンコーダの回転方向が合っているか確認している。

This adjustment confirms whether speed is detected without problems and if the encoder's rotation direction is correct.

(3)図がないため、具体的な内容を省略

(Specific content omitted as no diagram is provided)

(4)調速機エンコーダより検出したカゴ速度及び運転方向をSETS基板へ入力。

Car speed and operating direction detected by the governor encoder are input to the SETS board.

80.SETS-Lの基準位置スイッチ動作点の確認

Confirmation of SETS-L Reference Position Switch Activation Points

(1)作業内容

Work Procedure

①各基準位置スイッチUP1/UP2/DN1/DN2の取付位置が正しいか確認を行う。

Confirm that the mounting positions of each reference position switch UP1/UP2/DN1/DN2 are correct.

(2)目的

Purpose

①基準位置スイッチ検出時、カゴ速度に問題がないか監視している。（速度校正位置）

When a reference position switch is detected, the car speed is monitored for any issues. (Speed calibration position)

②基準位置スイッチの取付位置を誤るとSETSが正常に機能できないため、取付位置の確認を行う。

If the reference position switches are mounted incorrectly, SETS cannot function properly, so confirm the mounting positions.

(3)図がないため、具体的な内容を省略

(Specific content omitted as no diagram is provided)

81.2026/6/9

2026/6/9

SETSチェック

SETS Check

(1)作業内容

Work Procedure

①SETS検査モードへ移行させ、中間階付近にて試験を実施。

Transition to SETS inspection mode and perform the test near an intermediate floor.

②カゴ内または乗場インジケータに表示される以下のデータを確認する。

Confirm the following data displayed inside the car or on the landing indicator.

①E-stop発生速度(m/min)…急停止発生時のカゴ速度(最高速＋10%～-5%以内)

①E-stop activation speed (m/min)... Car speed at emergency stop activation (within max speed +10% to -5%)

②E-stop発生位置(mm)…最下階FLからの距離。昇降路中間位置。

②E-stop activation position (mm)... Distance from bottom floor FL. Hoistway intermediate position.

③E-stop 発生ETS パターン(m/min)…制御盤が指示した試験速度

③E-stop activation ETS pattern (m/min)... Test speed commanded by the control panel.

④減速測定距離(mm)…仮想バッファ位置速度検出位置。

④Deceleration measurement distance (mm)... Virtual buffer position speed detection position.

⑤仮想バッファ位置速度(m/min)…E-STOP発生位置から設計上のCWTランバイ値分移動したカゴ速度。

⑤Virtual buffer position speed (m/min)... Car speed after moving by the designed CWT runby value from the E-STOP activation position.

(2)目的

Purpose

①本試験モードは、昇降路中間位置でSETSが動作したと仮定してブレーキを動作させ、仮想バッファ位置で許容衝突速度以下に減速できているか確認している。

This test mode assumes SETS has activated at an intermediate hoistway position, operates the brake, and confirms whether deceleration to below the permissible impact speed at the virtual buffer position is achieved.

②実動作をすると、機器の破損が発生する可能性があるため仮想にて実施する。

This is performed virtually because actual operation may cause equipment damage.\n