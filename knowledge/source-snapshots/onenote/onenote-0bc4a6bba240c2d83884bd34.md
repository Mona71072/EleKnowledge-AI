---
snapshot_type: "onenote_source_page"
source_system: "OneNote"
onenote_id: "c3cbdf09-d13b-4aa5-9561-35eec9fc56a6:175"
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
**【営設依頼ポイント】**

・営業設計はへりあき等の検討をせずに、受電盤や制御盤の下に通してほしいと電気屋に依頼していることが多い。

（穴の大きささや位置などを明確に指示しないと、へりあき寸法が満たせなくなる。）

・1P/2P等によって上部と下部受電の場合の盤の穴あけサイズが異なる。（L資料を確認しないといけない）

※営業設計も意識せずに適当なサイズを据付図に書いている場合があるので注意。

・電気設計としては特記仕様書に上部か下部か書いてほしい。（書いていないと下部受電での設計になる。）

**【注意点】**

参考資料：[**アンカー注意事項**](%E3%82%A2%E3%83%B3%E3%82%AB%E3%83%BC%E6%B3%A8%E6%84%8F%E4%BA%8B%E9%A0%85)

・制御盤下部床に穴開けをし入線する場合は、へりあきが満たせているか注意してください。

※制御盤はMELKAの耐震計算書で強度計算を行っており、へりあきが満たせないと強度計算の値も変わってきてしまうので注意してください。

[OneNote attachment reference omitted; attachment not copied]

※現状のM16の場合はへりあきがシビアすぎます。

・2412C生産からすべての盤でM16⇒M12ボルトに変更される。（盤の穴はM16から変更なし。）

盤下固定用アンカーボルトサイズダウンの件[TI-1408.pdf]([URL omitted pending approved OneNote link resolution])

※MELKAの耐震計算書に書いてあるボルト径で施工しなくてはいけないため、アンカーボルト手配にあたり、MR機種では品目表の579，203を確認する必要があります。（記載が無い場合は計算書を参考にしてください。）

・下部受電（受電盤への客先接続方法）の場合は穴あけ位置に注意すること！！

※盤下から電源線を取り込む場合は電気屋に一任となる（穴空け図に記載は無し。）が、しっかりと打合せをしないとアンカーのへありあき寸法が取れなくなってしまう。

[OneNote attachment reference omitted; attachment not copied]

・下部受電と上部受電を変更する場合は注意してください！！

※上部/下部受電盤の設計内容から違ってくる。  (内部線の配線ルートで判断可能。YE401B423)

※無理やり接続すると曲げ径確保、盤内での他機器との接触等の問題が生じる。

**【ヘリあき問題の推奨対策】**

①基本的には盤配置をずらす方向で考えてください。

・不可であれば

②アンカー太さorボルト固定位置の変更。

※制御盤のへりあきが基準外なら、MELKA再計算⇒再申請（検討するまで実施可否は不明）

※機械設計が作成している官庁申請(MELKA)を確認したところ、アンカーボルトサイズが記載されるのは制御盤のみであり、制御盤以外は対象外とのこと。\n