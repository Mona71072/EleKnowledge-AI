---
snapshot_type: "onenote_source_page"
source_system: "OneNote"
onenote_id: "4fd4eb57-ccb4-42ad-8733-37598686fd63:177"
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
**【Checklist】**

| バッテリー電源 Battery Power Supply | コイン電池の挿入条件を確認する。 Check the insertion condition of the coin battery. |
| --- | --- |

| コイン電池（P1基板） Coin Battery (PI Board) |  |
| --- | --- |
| [OneNote attachment reference omitted; attachment not copied] | [OneNote attachment reference omitted; attachment not copied] |
| もしコイン電池が取り付けられていないと、電源が切れたときにRAMのデータがROMに書き込まれません。 |  |
| If the coin battery is not installed, RAM data will not be written to the ROM when the power supply is shut off. |  |

**【参考情報】**

**【Reference information】**

| **【Unable to Operate in Slow Speed Due to Incomplete Pole Alignment】** |
| --- |
| **不具合** **Issue** 前日はエレベーターが低速で動作していましたが、翌日には動作しなくなりました。 エラーコード「94D: 磁極学習未学習」が表示されました。 The elevator was operable in slow speed the previous day, but became inoperable the next day. Error code “94D: Pole Position Not Learned” was displayed. **原因** **Cause** 最初の低速運転時にP1ボードのバックアップコイン電池が取り付けられていませんでした。そのため、磁極学習データがROMに書き込まれず、RAMにしか残っていませんでした。 長時間の停電後、RAMのデータが失われ、ポールの位置合わせが不完全になり、動作不能になった。 The backup coin battery on the P1 board had not been installed during the initial slow-speed operation. Therefore, the pole-learning data could not be written to ROM and remained only in RAM. After a long power shutdown, the RAM data was lost, resulting in incomplete pole alignment and operation disablement. **対策** **Corrective Action** 磁極学習を行う前に、必ずP1基板のコイン電池を取り付けてください。 Always install the P1 board coin battery before performing pole alignment. エラーコード「94D」が表示された場合は、コイン電池が取り付けられているか確認し、磁極学習を行ってください。 If error code “94D” is displayed, check whether the coin battery is installed and perform pole alignment. |

Note:The data remains until the power supply is turned off, so the issue may occur after a time delay.

**Please perform the necessary checks to prevent the issues described above.**\n