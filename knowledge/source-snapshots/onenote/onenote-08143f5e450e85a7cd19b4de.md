---
snapshot_type: "onenote_source_page"
source_system: "OneNote"
onenote_id: "428d8b27-448b-4505-b56d-ede6ecafe32d:1"
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
Training curriculum

◆Explain how to drive P.88

ETP can only be used in ED mode and emergency mode

・Press the RUN and UP buttons simultaneously to control the CAR.

・To stop, press the button opposite to the direction.

◆Explain how to operate brake release P.5

◆High-speed adjustment(VFGLF)

Document no.：C-7-C3950-E(VFGLF Electric System installation Manual)

**⓪****How to use remote control P.18**

**①****Insulation test P.27**

**②****Low-speed sequence test (Voltage checks) P.28**

**③****Terminal stopping device \[NL\]P.96**

④**Magnetic pole adjusting Operation by ED \[NL\] P.133**

**⑤****Temporary setting for inclination sensor of weighing device\[NL\]**

**⑥****Writing floor height memory in low-speed operation\[NL\](FMS) P.100**

**==🔴High-speed operation==**

**⑦****Magnetic pole adjusting Operation by Normal \[NL\] P.101**

**⑧****CWT balance setting \[BL\] P.103**

**⑨****Adjust an angle of the weighing device\[BL\] P.107**

**⑩****Writing BL/NL load weights in Flash-Memory\[BL/NL\]P.108**

**⑪****Write the angle to the label inside the weighing device cover.\[NL\]P.107**

**⑫****Writing the data of unbalance weight of the cables and ropes in Flash-Memory(FMS)**

**⑬****Confirmation of Static braking torque P.105**

**⑭****Confirmation of  Dynamic braking torque P.106**

**⑮****Minute adjustment of activating point of overload detector (29W) P.109**

**⑯****Check for load fluctuation P.121**

**⑰****Adjustment of floor level P.113**

**⑱****TSD running check P.119**

**⑲****TSD margin check P.120**

◆High-speed adjustment(VFGLF)

Goals：Using the adjustment data sheet and Construction documents(C manual) to perform a series of high-speed adjustment tasks

**==🔴⓪==****==🔴How to use remote control P.18==**

【Points】

・PW　　　　　　 ：START→81→OK→1730→OK

・Instralltion mode：STRAT→73→OK

・Normal mode　  ：CLR→CLR

1. Explain the difference between A mode and B mode

A mode：SET1/0=0/8

B mode：SET1/0=0/0

1. Explanation of functions that can be operated by remote control

Independent mode ON/OFF：IND→↑→ON/OFF→OK

LIGHT ON/OFF：LIGHT→↑→→OK

**==🔴①==****==🔴Insulation test P.27==**

【Purpose】

Confirm that the insulation of each equipment and wires is normal to prevent equipment damage, electric shock disasters, and fires due to insulation defects.

【Points】

We will not conduct high-voltage insulation test in this training. If it breaks down, we won't be able to conduct the training.

1. The insulation test must be performed from low voltage (15V).

Q：Do you know why low voltage 15V must be performed first?

A：Low-voltage pre-check detects obvious defects like poor connections or shorts before high voltage check. In other words, preventing equipment damage.

1. After the insulation test, confirm that the voltage between th earth and terminal of 400 on PCB

Q：Do you know why (4) is needed?

A：During an insulation test, the circuit stores electricity like a capacitor.

Since a sudden discharge by the breaker could cause a malfunction,

a voltage is slowly applied under 10 Voltage using a voltmeter with a high earth resistance.

After the insulation resistance test, the correct recovery sequence is

①Earth V check ②Reconnect UPJ and RPW connecter ③Reconnect other connecter

**==🔴②==****==🔴Low-speed sequence test (Voltage checks) P.28==**

【Purpose】

Confirm that the power is received at the voltage that meets the standard and that the transformed value meets the standard.

If the standards are not met, it may lead to malfunction or early deterioration of the equipment.

【Points】

・Voltage and current measurements are carried out according to the data

・Do not carelessly touch the live wire

**==🔴③==****==🔴Terminal stopping device P.96==**

【Purpose】

It is a safety device for stopping in any state when driving to the terminal floor, and at the same time, it is also a position switch that detects the terminal floor of the elevator.

【Points】

・In this training, we will conduct UOT/DOT only. P.97

・After conducting UOT, buzzer rings. Please check error code in car

・Error code 638,668 refers to P9. Error code 63A refers to P20.

==🔴④==**==🔴Magnetic pole adjusting Operation by ED \[NL\] P.133==**

【Purpose】

The phase difference between the stator and the rotor (permanent magnet) in the traction machine is corrected, and an appropriate current is applied to achieve high-precision torque control.

【Points】

**==🔴⑤==****==🔴Temporary setting for inclination sensor of weighing device\[NL\]P.107==**

【Purpose】

・Set a basic point for the amount of change in weighing device to detect the CAR load.

【Points】

・Check the inside of the cover of the inclination sensor of the weighing device and adjust the angle.

**==🔴⑥==****==🔴Writing floor height memory in low-speed operation\[NL\](FMS) P.100==**

【Purpose】

The position of the PAD(Landing device) plate on each floor is written to RAM as the landing position.

【Points】

**==🔴⑦==****==🔴Magnetic pole adjusting Operation by Normal \[NL\] P.101==**

【Purpose】

It is more accurate than low-speed(ED) operation.

【Points】

・Magnetic pole alignment (AUTO) should be performed at the beginning of high-speed output.

・It should also be done when the P1 board or an encoder of traction machine is replaced.

**==🔴⑧==****==🔴CWT balance setting \[BL\] P.103==**

【Purpose】

The CAR and CWT are balanced to improve transportation efficiency and prevent equipment burnout and fire due to overcurrent.

【Points】

・You can do this P.103 way. But the below is better way.

・If you use SET1/0=0/9  in (  B  )mode , you can confirm the intermediate position motor current + CWT adjustment amount measuring function on the hall Indicator. P.53

・A indicates the CWT adjustment amount.

・B indicates motor current in UP direction.

・C indicates motor current in DN direction.

※This is also fine when checking on construction site.

**==🔴⑨==****==🔴Adjust an angle of the weighing device\[BL\] P.107==**

【Purpose】

・Set a basic point for the amount of change in weighing device to detect the CAR load.

【Points】

・Check the inside of the cover of the inclination sensor of the weighing device and adjust the angle.

・Starting scale: Improved ride comfort, improved implantation accuracy.

・Management scale: override detection, prank cancellation

**==🔴⑩==****==🔴Writing BL/NL load weights in Flash-Memory\[BL/NL\]P.108==**

【Purpose】

・The tilt angle of the weighing device is determined, and the load in CAR is detected and the appropriate operation is performed for that situation.

【Points】

・After writing weight in Flash-Memory, you fill in the values on the data sheet and control pannel.

**==🔴⑪==****==🔴Write the angle to the label inside the weighing device cover.==**

**==🔴⑫==****==🔴Writing the data of unbalance weight of the cables and rops in Flash-Memory(FMS)==**

【Purpose】

・Due to the position relationship between the CAR and the CWT, the weight of the traveling cable and main rope causes an unbalance in the balance. As a result, when starting (when the brake is opened), the CAR is pulled to the CWT and a starting shock is generated. To prevent this starting shock, writing the load to RAM during unbalance.

【Points】

・After writing weight in Flash-Memory, you fill in the values on the data sheet and control pannel.

・By writing floor height memory in both low speed mode and high speed mode, high accuracy is achieved

**==🔴⑬==****==🔴Confirmation of Static braking torque P.105==**

【Purpose】

・Ensures that the CAR does not fall when stopped by  static braking torque.

【Points】

・The standard for static braking torque is 1.5 times the load weight plus a 30% motor measurement error, making it 180 or more.

**==🔴⑭==****==🔴Confirmation of  Dynamic braking torque P.106==**

【Purpose】

Ensures the car is stationary during an emergency stop while driving with dynamic braking torque.

**==🔴⑮==****==🔴Check for load fluctuation P.121==**

【Purpose】

Confirm that the motor currents at each load is not an abnormal current value for the motor current rating.

【Points】

・Tests will be conducted at NL, BL, FL, and OL.

・When you conduct at OL, make ineffective the load-in-car signal(29W_WGHO) P.109

★Caution

・After checking for load fluctuation at OL, you immediately return WGHO to its original setting.

・If WGHO is 0(zero), the CAR in Normal mode does not drive. So, you won't forget put it back.

**==🔴⑯==****==🔴Minute adjustment of activating point of overload detector (29W) P.109==**

【Purpose】

・Confirm to load the car with 110% of the rated load, which will activate the overload detector in the car.

【Points】

・Mitsubishi elevertors must be set to activate when loading the car with 105-110%.

**==🔴⑰==****==🔴Adjustment of floor level P.113==**

【Purpose】

It improves the safety and comfort of users by suppressing shaking and vibration during driving and eliminating steps during implantation.

【Points】

・In this training, conduct PTSH, DNSH, FSHFT WGHG.

・PTSH：(adjustment of ride comfort directly before landing)

If the car overshoots or poses directly before landing, it is considered to be due to improper remaining distance pattern. It can be

corrected with the parameter PTSH.

・DNSH：(adjustment in the vicinity of the landing only for down operation) DN direction

If the landing error occurs in the downward landing, it is considered to be due to cause a peculiar plate detection error to the inductor

relay. It can be corrected with the parameter DNSH.

・FSHFT

The gap of the landing of the each floor can be adjusted individually without the adjustment of the landing plate.

・WGHG P.110

When the car tends to jump out when the brake is released during operation. \[NL\]

→If it pops out to the UP side, set it to "F" direction.

→If it pops out to the DN side, set it to "0" direction.

**==🔴⑱==****==🔴TSD running check P.119==**

【Purpose】

If the car does not slow down sufficiently due to an abnormality in the  PAD(Landing device) plate when driving on the terminal floor, the CAR is forced to slow down and stop in order to reach the floor safely.　Confirming error of levels

【Points】

**==🔴⑲==****==🔴TSD margin check P.120==**

【Purpose】

・If the car does not slow down sufficiently due to an abnormality in the  PAD(Landing device) plate when driving on the terminal floor, the CAR is forced to slow down and stop in order to reach the floor safely.

・It is used to verify that there is a margin of safety operation.

貼り付け元  \<[URL omitted pending approved OneNote link resolution]>\n