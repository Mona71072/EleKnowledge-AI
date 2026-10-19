---
snapshot_type: "onenote_source_page"
source_system: "OneNote"
onenote_id: "2fd509b2-87aa-4e26-8cd6-6d51680accc1:1"
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
**【技術共有リスト】・**[負荷試験の電流値がMCBブレーカー定格電流を超えてしまう件]([URL omitted pending approved OneNote link resolution])

**・**[MCBブレーカーのトリップ接点について]([URL omitted pending approved OneNote link resolution])

**【****MCCB****（****MCB****）と****ELCB****（****ELB****）の違い】**

**・****MCCB****（****MCB****）：Molded Case Circuit Breaker**

MCCBとMCBは日本語にすると「配線用遮断器」であり、自宅用の配線用遮断器（いわゆるブレーカ）は、Miniature Circuit Breakerの略でMCBと呼ぶこともある。MCCBとMCBには違いはなく、基本的に同じものです。

※「NFB（No Fuse Breaker：ノーヒューズブレーカー）」、「NF」とは三菱電機におけるMCCBの商標を指すのです。

【役割】

過負荷（ワット数が大きいものを多く接続など）や短絡（ショート）の際に機器に過剰な負担がかかり故障するのを防ぐ

**・****ELCB****（****ELB****）：Earth Leakage  Circuit Breaker**

ELBはEarth Leakaget Breaker の略、ELCBはEarth Leakage  Circuit Breakerの略であり、両方とも漏電遮断器と訳されます。つまり、ELCBとELBには違いはなく、同じものです。

※水濡れなどによる漏電を防げることから、水回りにはこちらのELB、ELCBが設置されることが基本であるが、MCCBと同様の過電流が機器に流れることを防ぐ機能も併せ持っていることがほとんどです。

※「NV」とは三菱電機におけるELCBの商標を指すのです。

【役割】

漏電（地絡）が起こった場合の感電を防ぐ

**【各機種のＮＦ、ＮＶの適用条件】**

ＭＲＬの動力電源は「ＮＶ」の使用を基本としている。冠水する可能性があるため。（照明電源はNFを使用）

※MRLの電源用ブレーカー名は「MCB」だが、実際にはELCBが基本的に適用されている。

ＭＲの動力電源は「ＮＦ」と「ＮＶ」の展開を作っている。（基本的にはＮＦを使用しているが、客先要求でＮＶをつけることもある。）

※病院では漏電により停電すると人命に関わるのでNFにするらしい（昔、日立エレが病院で漏電して停電させたことがあるらしい）。

※海外のＭＲは基本的には客先受電なので盤内にはＮＦを使用している。

※非常エレの場合は消防時にも使用されるので漏電しても動かすためにＮVを使用しない。

**【現場での注意点】**

・かご上にある照明のためのLEDユニット等を確認するために、天蓋を開けたりするときに地絡や何かの原因で漏電や過電流を検知すると、客先の漏電遮断器が先に落ちてしまうことがある。（照明回路は基本的にNFBが適用されているため。）

[100Vラインが地絡し客先の漏電警報機が異常発報する件]([URL omitted pending approved OneNote link resolution])

・客先が漏電遮断器だとエレ側より先に落ちる可能性があるので注意してください。

（・客先のブレーカーがNFかNVかを確認しないといけないんじゃないの？？）

**【****漏電遮断器の接地を単独にしなければいけない理由****】**

※内線規程（1350-13）：漏電遮断器で保護されている電路と保護されていない電路に施設される機器などの接地線及び接地極は、共用しないこと。ただし、２Ω以下の低抵抗の接地極を使用する場合は、この限りでない。

・ＭＣＣＢ保護の回路で地絡のトラブルが発生した場合、ＥＬＣＢで保護した機器が誤動作して停止することはない。 ・ ＭＣＣＢ保護回路で地絡した場合、ＥＬＣＢ保護の機器フレ－ムに人体 が接触したとき、感電し非常に危険であるので、機器接地は単独にする必要がある。（ＥＬＣＢ取付場所は水気の多い場所であること）

※MRL機種に関して「漏電遮断器の接地を単独にしなくていの？（客先から1本しかアースをもらっていない。）」問題に関しては、別途工品等に聞かないといけない。

[OneNote attachment reference omitted; attachment not copied]

[三菱電機関西適塾20150605資料.ppt]([URL omitted pending approved OneNote link resolution])\n