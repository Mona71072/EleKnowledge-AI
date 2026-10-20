---
snapshot_type: "onenote_source_page"
source_system: "OneNote"
onenote_id: "a8c15103-95f4-4d08-897a-403d412bffb5:103"
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
【参考資料】

[メンテコン総括資料.pdf]([URL omitted pending approved OneNote link resolution])

【稲電過去依頼事項】

[富士ソフト汐留事務所ビルA棟【MTCQ1101】]([URL omitted pending approved OneNote link resolution])

**デジタルレコーダー**

**【デジタルレコーダーとは？】**

デジタルレコーダーとはトリガ検出条件を自ら設定できる昇降機メニューの機能である。本機能では信号の連続的な変化を閲覧できる。そのため電流異常が発生したタイミングを特定するなど不具合原因を探る際や、EV動作中の秤値を確認するなど動作チェックを行う際に使用可能である。

主に不具合対応などで稲電からデジタルレコーダーを使用したデータ採取を要求された際に使用する。

［使用例］

・不具合原因追究のため稲電からデジタルレコーダーにデータ採取を依頼された時。

・信号の変化を確認する時

デジタルレコーダーを使用する際は以下の流れで操作をする

①デジタルレコーダーにてトリガ条件を設定する

②EVを動作させる

③EV動作中にトリガ検出

④Pl基板にトリガ検出時点前後の信号変化が保存される，＇

⑤デジタルレコーダーにてPl基板に保存名された信号データを確認する。

**【デジタルレコーダーの使い方】**

昇降機メニューから故障対応拡張のタブを選択し、デジタルレコーダーを選択する。

[OneNote attachment reference omitted; attachment not copied]

デジタルレコーダーが起動したら、「設定」を押す。

[OneNote attachment reference omitted; attachment not copied]

トリガ条件の設定画面が開くので、トリガ条件を設定する。

[OneNote attachment reference omitted; attachment not copied]

**\[手順****\]**

①設定する チャンネル数( 信号数)を 選択する。②設定をする 信号とアドレスを指定する。 (信号名とアドレスを正確に入力しないと動作しないので注意！）

③トリガ 検出の条件を設定する。(後項にて説明）

④トリガポイントを設定する。(どこにトリガ検出点を置くか設定する）

8ch：256周期、16ch：128周期、32ch：64周期まで記録できる中で、 記録するポイントを指定している。

※データ保存量の関係で、保存するアドレスの量（ch数）によって保存可能周期が変わってくる。

⑤トレース周期(測定点間の間隔)を設定する。(1ms = 0.001秒)

ex.32chで100msで取得した際、6.4秒間記録できる。

⑥有効にした場合、トレースデータにも記録が保存される。

**⑦トリガを検出した際に MIC** **(****MELTEC 情報 センター） へ 発報 する 。**

**（工技業務では****<u>無効</u>****に設定すること）**

⑧条件を入力し終えたら「保存」をした後に「終了」をする。

<u>※①～⑤は稲電指示によるもの</u>

**\[上記のトリガ条件の入力方法について****\]**

[OneNote attachment reference omitted; attachment not copied]

・YES→指定した設定値に合致した際にトリガを検出する。

・NO→指定した設定値に合致しなかった際にトリガを検出する。

・＞→指定した設定値より大きい値になった際にトリガを検出する。

・＜→指定した設定値より小さい値になった際にトリガを検出する。

・M →ビット信号が「 0 以外 」になった際に トリガを検出する。

・B →ビット信号が「 0 」になった際にトリガを検出する。

・OR →次の条件を入力する 。

(① OR ②と設定した場合、①か②のどちらかの条件に合致した際にトリガを検出する。)

・AND→ 条件を増やす。

(① AND ②と設定した場合、①と②の 両方の 条件に合致した際にトリガを検出する。)

・END→ 条件の入力を終える。

（① END と設定した場合、①の条件に合致した際にトリガを検出する。）

※①が1chの条件、②が2chの条件、③が、、、となる。

ex.・トリガ条件：1ch≠０の時（1chが0以外の値になった時）

①トリガ条件00 NO END

・トリガ条件：1ch＝0、2ch≠０の時（1chの値が0以外になった時かつ2chの値が０になった時）

①トリガ条件00 YES AND　②トリガ条件00 NO END

・トリガ条件：1ch＝0か2ch＝０の時（1chの値が0になった時か2chの値が０になった時）

①トリガ条件00 YES OR　②トリガ条件00 YES END

トリガ条件の設定を終えたら、「開始」を押し、EV を動作させる。

（この際には保守合理化 S/W をインス トールしたままにしておくこと）

[OneNote attachment reference omitted; attachment not copied]

**【デジタルレコーダーの使用例】**

（例）デジタルレコーダーを用いて、ブレーキ電流が切れてから BK 接点が ON するまでの時間を

計測する。今回用いる信号は以下の通り。

[OneNote attachment reference omitted; attachment not copied]

条件を下図のように入力して、「保存」→「終了」する。

今回は指定した 1ch (ブレーキ電流指令）の信号が「００」になった際にトリガを検出するように設定

[OneNote attachment reference omitted; attachment not copied]

**【トリガ検出の結果****】**

[OneNote attachment reference omitted; attachment not copied]

**【保存データの見方****】**

\[手順\]

①メンテコンを起動し、「保存ファイル参照・印字」を選択

[OneNote attachment reference omitted; attachment not copied]

②故障対応拡張→デジタルレコーダーを選択

[OneNote attachment reference omitted; attachment not copied]

③接続した機種を選択→結果を選択

[OneNote attachment reference omitted; attachment not copied]

④保存したデータが見れる

[OneNote attachment reference omitted; attachment not copied]

※保存したいデータをクリックし、印刷（PDFで保存）を押すことでローカルにデータを落とすことが出来る。

[OneNote attachment reference omitted; attachment not copied]\n