---
snapshot_type: "onenote_source_page"
source_system: "OneNote"
onenote_id: "2ed09071-65ef-4d9d-8bfa-f17730307e3d:1"
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
弱電線とは・・・動力としての電気（主回路電源/照明電源）を供給する強電の対義語で主に電気的な信号を伝えたり、あるいはその電気信号で機器を制御することなどを指す。通信・制御・情報に関する分野の線。

What are Low Voltage Wires...? They are the opposite of high voltage wires, which supply power (main circuit power/lighting power). They primarily transmit electrical signals or control equipment with those electrical signals. These are wires in the fields of communication, control, and information.

48V以下の低い電圧のもの。

Those with low voltage of 48V or less.

弱電線の結線は、エレベータ～客先機器間の接続が基本多いため、導通確認及び客先側と何色の線で結線するかの確認が必要である。

Since low voltage wiring primarily involves connections between the elevator and customer equipment, continuity checks and confirmation of which color wire to connect to the customer side are necessary.

上記確認を必ず行ってから結線を行うこと。（結線ミス、感電災害等の防止）

Always perform the above checks before wiring. (To prevent wiring errors, electric shock accidents, etc.)

本資料にて基本的な弱電線の制御盤側の結線先を記す。

This document describes the basic connection points for low voltage wires on the control panel side.

弱電線の結線（火報・接点出力・電話線・BGM・インターホン）

Low Voltage Wiring Connections (Fire Alarm, Contact Output, Telephone Line, BGM, Intercom)

(1)●火報-2芯線（赤/透明が一般的）

●Fire Alarm - 2-core wire (red/transparent is common)

①火災検知→

Fire detection →

②←コモン線（24V）

←Common line (24V)

③24V→

24V →

④火災を検知すると接点が閉じる

Contact closes when fire is detected.

⑤24V検出すると火災管制へ移行

Transitions to fire control when 24V is detected.

⑥FECA：赤（火災）：透（コモン）

FECA: Red (Fire): Transparent (Common)

⑦※例外あり

*Exceptions apply

(1)●インターホン(2P※多局の場合、1局+1P)

●Intercom (2P *For multi-station, 1 station + 1P)

①非常時、エレベータから外部へ連絡を取るもの。

For emergency, to contact outside from the elevator.

②基本的には、管理人室等に設置され24時間常に連絡できるようにする必要がある。

Basically, it should be installed in a management office or similar location and be accessible 24 hours a day.

③24時間対応が不可の場合、外部（共用部等）でインターホンの鳴動が確認でき、鳴動時の対応が明示する必要がある。令第129条の10 第3講第三号

If 24-hour response is not possible, the intercom's ringing must be confirmable externally (e.g., in common areas), and the response procedure for ringing must be clearly specified. Article 129-10, Paragraph 3, Item 3 of the Ordinance.

④EV 呼出釦

EV Call Button

⑤24V多極の場合は「EB1A」「EB2」に接続

For 24V multi-pole, connect to "EB1A" and "EB2".

⑥電源（＋/－）、送信/受信、選局を結線

Connect power (+/-), transmit/receive, and station selection.

(1)●BGMスピーカ（非常放送）

●BGM Speaker (Emergency Broadcast)

①消防法で地上11階以上と地下3階以上は非常放送を設置しなければならない。

According to the Fire Service Act, emergency broadcast systems must be installed on the 11th floor and above, and the 3rd basement floor and below.

②非常放送が適用され「音声調整機器（BGMスイッチ（開戸内）とアッテネータ）」を設ける場合は3線式とする。消防法施工例第24条

If an emergency broadcast is applied and "audio adjustment equipment (BGM switch (inside open door) and attenuator)" is provided, a 3-wire system shall be used. Fire Service Act Enforcement Ordinance Article 24.

③2線式の場合はBGMスイッチとアッテネータ無し。

In the case of a 2-wire system, there is no BGM switch or attenuator.

④2線式：同一の信号線で放送が送られる。3線式：それぞれの信号で放送が送られる。

2-wire system: Broadcast sent over a single signal line. 3-wire system: Broadcast sent over separate signal lines.

⑤万が一の火災が発生した際に建物内の人々に警報と避難誘導を行うための設備。

Equipment for alerting and guiding people in the building to evacuate in the event of a fire.

⑥BGM1：青（一般放送）

BGM1: Blue (General Broadcast)

⑦BGM2：透（コモン）

BGM2: Transparent (Common)

⑧BGM3：赤（非常放送）

BGM3: Red (Emergency Broadcast)

⑨3線式

3-wire system

⑩2線式

2-wire system

(1)●一括接点（異常・閉込め・インターホン等）

●Collective Contact (Abnormality, Entrapment, Intercom, etc.)

①EV側で接点を持っており、各異常等を検出すると接点が閉じて管理人室等に設置されている警報盤へ発報を行う。

The EV side has contacts, and when various abnormalities are detected, the contacts close, sending an alarm to the alarm panel installed in the management room or similar location.

②各異常を一括（同じ信号として）発報する場合と、各々別信号で出力する場合がある。

There are cases where all abnormalities are reported collectively (as the same signal) and cases where each is output as a separate signal.

③異常を検知すると接点が閉じる

Contact closes when abnormality is detected.

④電圧等を検出すると発報

Alarm is triggered when voltage, etc., is detected.

⑤AXIEZ-LNKｓ：YE317C610参照

AXIEZ-LNKs: Refer to YE317C610

⑥動作フロー：D-C-844.1-J参照

Operation Flow: Refer to D-C-844.1-J

(1)●電話線

●Telephone Line

①MIC（情報センター）にて遠隔監視するための線。電波が悪く無線で連絡が取れない場合に有線にて連絡を取るための線。保守時に使用するため、行先を確認し、工事試験報告書へ記入。基本的にMDF盤にある。

A line for remote monitoring by MIC (Information Center). It is used for wired communication when radio waves are poor and wireless communication is not possible. Used during maintenance, so confirm the destination and record it in the construction test report. It is typically located in the MDF panel.

②MDF盤・・・電話局や外部に通じる通信回線などをすべて収容し集線装置。

MDF Panel: A concentration device that houses all communication lines leading to telephone offices and external connections.

③将来必要とされる線を盤に事前配線し、需要に応じて盤内配線の変更のみで対応できるように設けている。

It is designed so that future necessary lines are pre-wired in the panel, allowing for changes only in the panel wiring as needed.

(2)●ITVカゴ内カメラ（同軸ケーブル）

●CCTV Car Camera (Coaxial Cable)

①カゴ内の映像を外部モニターへ映し出すための結線。カゴ室内状況を監視するシステム。

Wiring to display car interior footage on an external monitor. A system for monitoring the car interior status.

②カゴ内液晶2画面タイプの場合

For car interior with 2 LCD screens

③EV側と外部の同軸を接続する。

Connect the EV side coaxial cable to the external coaxial cable.\n