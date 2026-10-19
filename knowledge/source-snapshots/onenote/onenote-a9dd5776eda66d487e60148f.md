---
snapshot_type: "onenote_source_page"
source_system: "OneNote"
onenote_id: "683d4748-d076-4625-8d7b-5e7151ece49b:1"
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
P.8

(1) Door switch short-circuit detecting function

・If the door switch short-circuit is detected (error code 73E) or DOOR CUT function is activated, the car is prevented to run by NORMAL operation.

(2) ==🟡UCMP(Unintended Car Movement Protection)==

・==🟡If you want to reset the CPU, you need to shut off the power and power on==.    Using RST SW(toggle switch on P1) causes UMD relay on failure(==🟡error code 85B==) detection(though actually not mulfunction).

・In INSPECTION mode, if the car is in relevel zone and door is opened, instantaneous(about 0.5s or less) pushing UP or DN switch sometimes causes UMD relay off.

・If the UMD off(==🟡error code 80B==) was detected, the error remains until power on the elevator in INSPECTION mode. So if the UMD off was occurred, you ==🟡need to shut off the power and power on the elevator in INSPECTION mode== after removing the cause.

(3) Operation mode

・The following table represents the details of operation modes.

[OneNote attachment reference omitted; attachment not copied]

(4) MANUAL operation at the hall

・Only ED mode is provided to ETP. Safety switch of the safety-gear, governor, buffer and final limit switch are short-circuited in ED mode.

・If you change the elevator mode from NORMAL mode to ED mode while safety circuit (#29) is intercepted, the control panel will judge that the emergency electric operation is executed. Therefore, NORMAL operation will be prevented when you change the elevator mode to NORMAL mode again (==🟡error code 638,668==). For restoring to NORMAL mode, work as follows.

Note: For GB, same condition as above when safety switch of the safety-gear or final limit switch is activated (error code 669).

a) Turn NORMAL/ED switch on ==🟡ETP to ED== side.

b)Set to ==🟡SET1/0=3/2 in B mode== by the infrared remote controller (Installation mode)) or P1 card in the Contrl panel.

(For details of the setting, see 1-14.)

c) Confirm the display (7SEG/Hall indicator) “==🟡CLr/CLR==” (Restoring mode is set).

d) ==🟡Shut off the power and power on.==

e) Set to ==🟡SET1/0=0/8== by the infrared remote controller (Installation mode)) or P1 card in the Contrl panel.

f) Turn NORMAL/ED switch to ==🟡NORMAL== side.

NOTE: The restoring mode is canceled by changing SET1/0 or when 30 minutes past from the time setting the mode.

(5) ==🟡Pit inspection device (Reset pit operation limit mode)==

・When you turn NORMAL/INSPECTION switch of Pit inspection device from INSPECTION side to NORMAL side, the operation mode

remains INSPECTION mode (#29 remains off). Please reset the pit operation limit mode in the following procedure.

(a) Check the following conditions  - Hall/Pit doors and Hall emergency doors are closed.

RESET- Safety switches around the pit are turned on.

(b) Perform procedures in accordance with applicable regulations.

(b-1) \[EN\]

The key switch of Hall reset device is turned to RESET side.

[OneNote attachment reference omitted; attachment not copied]

(6) Door bypass function

・Door bypass device is provided for maintenance. In order to activate Door bypass function, turn NORMAL/BYPASS switch to BYPASS

side and turn HALL/CAR switch to HALL side (for hall doors) or CAR side (for car door and door locking device).

・Only INSPECTION operation (on car and in pit) is usable during Door bypass function is activated.

・The audible signal at the car and flashing light under the car are activated during car movement.\n