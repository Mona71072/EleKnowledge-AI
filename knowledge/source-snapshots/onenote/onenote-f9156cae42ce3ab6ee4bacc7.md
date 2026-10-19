---
snapshot_type: "onenote_source_page"
source_system: "OneNote"
onenote_id: "c3cbdf09-d13b-4aa5-9561-35eec9fc56a6:128"
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
**【質問】**

**・制御ケーブルが****3****本以上の場合のつり位置（順番）がわからない。**

①制御ケーブルの手配を確認するには。PT.21の機器接続配置図を確認する。

※PT.21以外にも品番599のどこかの一時図にあります。（案件毎に一時図の構成も違うため何とも言えません。）

⇒現場で見てもらった方がいいかもしれません。

②手配本数は4本（60C、44C、44C、54C（光入り））だとする。

③手配された各ケーブルの関係を[C-10-C5.81-J.pdf]([URL omitted pending approved OneNote link resolution])で確認する。

※芯数の多いものをレール側の2本にする。（60Cと54C（光入り）がレール側になる。）

※その2本の重ね吊りの際の内外は下記表に照らし合わせて考える。（60Cが内側、54C（光入り）が外側となる。）

[OneNote attachment reference omitted; attachment not copied]

[OneNote attachment reference omitted; attachment not copied]

※吊り間隔は「制御ケーブルの適用（[C-10-C10.21-J.pdf]([URL omitted pending approved OneNote link resolution])）」を参考にすること。（設計値の記載なし）

| [OneNote attachment reference omitted; attachment not copied] | [OneNote attachment reference omitted; attachment not copied] | [OneNote attachment reference omitted; attachment not copied] | [OneNote attachment reference omitted; attachment not copied] |
| --- | --- | --- | --- |
| 60心 ⇒線いっぱい | 54心（光入り） ⇒光ケーブル保護パイプ有 | 44心（TP入り） ⇒黒被服のシールド入りTP有 | 鋼芯ワイヤー |

**・制御ケーブルの中間振れ止め****/****吊手が基準内に取りつかない。**

■中間JBを基準より上げる時の懸念

・制御ケーブル長が足りなくなる

⇒かご下の余長処理分を使えば問題ない？

・保護金網の長さが足りなくなる。

・突き下げ運転時に制御ケーブルが張ってしまう可能性がある

■中間JBを基準より下げる時の懸念

・制御ケーブル～中間JBの配線が足りなくなる

⇒若干長めに手配しているため、0.5m程度であれば問題ないと考えます。

・最上階FLから上方へ移動する際に制御ケーブルが張ってしまう可能性がある

①TR/2＋1～３mの基準になぜ取りつかないのかヒアリングする。

※設計上では＋1～３mの位置には取付可能と考えられているが、レイアウトで一概には言えない。（稲電設計も営業設計もブラケット位置などは確認はしていない。（M系ではレール立て図は機設だが電気設計とのやり取りが微妙））

※「制御ケーブルの適用（[C-10-C10.21-J.pdf]([URL omitted pending approved OneNote link resolution])）」を参考にする。

※＋1～３mのバッファーを考えて制御ケーブルを手配しているため、基準外だとその他寸法に影響が出る可能性がある。

[OneNote attachment reference omitted; attachment not copied]

②経験上では制御ケーブルが余るため、＋4ｍだと対応できる。

※下記L寸法が満たせるように据付してもらい、吊り間隔等OneNote reference (unresolved in snapshot): 据付基準が満たせているか確認してください。

※ケーブルが足りて各基準を満たせることができれば問題はない。（電設・渡部さんに確認済み）

[OneNote attachment reference omitted; attachment not copied]

【注意点】

・制御ケーブル鋼芯ワイヤー破断発生の件（連メモ:25-35）

[OneNote attachment reference omitted; attachment not copied]

[OneNote attachment reference omitted; attachment not copied]

[OneNote attachment reference omitted; attachment not copied]

**<u>鋼芯入り制御ケーブルの設置電線の取付について【</u>**[C-10-C5-K12.1-J.pdf]([URL omitted pending approved OneNote link resolution])**<u>】</u>**

エアコン電線入りの制御ケーブルのみ接地電線を取りつければいいのか問い合わせがあったのでまとめます

・接地理由

エアコン付きエレにおいて、制御ケーブルの鋼芯に誘導電圧が発生し、鋼芯に触れると微弱な電圧を感じる場合があるため、

鋼芯を接地することで誘導電圧を抑制している。

接地方法

※制御ケーブル2本吊りの場合、エアコン電線入りの制御ケーブルのみではなく

2本まとめて接地線を取り付けること

[OneNote attachment reference omitted; attachment not copied]\n