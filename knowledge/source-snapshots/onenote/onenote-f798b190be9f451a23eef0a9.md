---
snapshot_type: "onenote_source_page"
source_system: "OneNote"
onenote_id: "e50b2b63-0986-439a-9765-e8bdfdbbd1be:1"
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

[Ville-feuille ビル設備制御サービス　試験要領・成績書]([URL omitted pending approved OneNote link resolution])

[ロボット連動　STEP3試験　動画]([URL omitted pending approved OneNote link resolution])（RICEロボット）

[【ロボット連動_勉強会】_水野.pptx]([URL omitted pending approved OneNote link resolution])

【注意点】

**・****Ville-feuille****のロボット連動時にかご内****CR****スイッチが無効（平常）側だと、かご呼びが登録されずロボットが行先階に行けない。**

【目次】

①連動前ELSGW盤結線・設定について

②連動立ち合い

③実際に発生した不具合事例

①連動前ELSGW盤結線・設定について

ELSGW盤の結線についてはエレナビと同様であり

エレナビとエレロボ両方適用の場合も通信線DPE、DNE、RPE、RNEの4線のみである。

（接続方法はC資料[C-7-C3330]([URL omitted pending approved OneNote link resolution]) P19参照）

※C資料に記載されている接続図だと、上からDNE、DPE、RNE、RPEの順であるが

監視盤JB符号図だと、DPXE(DPE)、DNXE(DNE)、RPXE(RPE)、RNXE(PNE)であるため

接続する際、監視盤JB符号図を参照すること

（どちらに合わせるよう改善提案提出済み）

[OneNote attachment reference omitted; attachment not copied]

現場ごとのエレナビもしくはエレロボ特記仕様書を営設から入手しておき、

ELSGW盤のIPアドレス、サブネットマスクなどが現場ごとの特殊番号が割り当てられてないか確認する。

特殊番号が割り当てられている場合、現地で変更する必要がある。

（変更方法はC資料[C-7-C3331]([URL omitted pending approved OneNote link resolution]) P10~13参照）

[OneNote attachment reference omitted; attachment not copied]

ELSGW盤～IoTゲート間のLANケーブルを接続し通信が確立したら、

通信異常が出てないかIoTゲート側（BMや空シ工）で確認してもらう。

ELSGW盤ではインクリント表示はEV側との接続エラー確認であり、

IoTゲート側で通信異常が発生してる可能性がある。

②連動立ち合い

連動の手順として、STEP1　STEP2　STEP3があり、

立ち合いが必要なのはSTEP2以降である。

STEP1：BM・空シ工内部での機器設定や通信確立

STEP2：IoTゲートからELSGWに模擬信号を送りEVが連動動作をするか。

STEP3：EV、BM・空シ工、ロボット業者の三社合同で行う。実際のロボットを用いて連動確認。

※BM・空シ工が主体となり、稲電作製の「試験要領書」をもとに連動確認を行っていく。

（事前に[Ville-feuille ビル設備制御サービス　試験要領・成績書_暫定版.pdf]([URL omitted pending approved OneNote link resolution])を客先に提出している。）

※ロボット連動の場合は稲電が「Ville-feuille ビル設備制御サービス　試験要領・成績書」を作成してくれる。

※エレナビの場合は「試験要領書」を電気設計に作成してもらってる（言わないと作ってくれないし、複雑ではないエレナビの場合はC資料等に従って実施願うといわれる。）が、BMでも作成することが多いため無駄作業にならないように打合せしておくこと。（特に全階床エレナビ等の複雑な場合は、電気設計か空シ工に「試験要領書等」を作ってもらい、空シ工と相談しながら進めること。）

③実際に発生した不具合事例

1)ELSGW盤～IoTゲートで通信異常が発生している件

ELSGW盤にLANケーブル接続後、IoTゲート側で通信異常が出っぱなしであった。

空シ工と打ち合わせをしてみるとサブネットマスクが本現場、特殊であることが分かり

仕様書通りに変更してみると通信異常が治った。

2)STEP2試験にてEVが連動動作しない件

模擬信号にて連動を確認しようとしたところ、EVが動作しなかった。

IoTゲートから模擬信号がELSGW盤まで送信されているがEVが反応しない。

Puttyにてログを採取し稲電に解析依頼したところ、IoTゲートとELSGW盤のバンク番号が異なっている

ことが発覚した。

本現場、4バンクありEV側はOLバンク、OMバンク、OHバンク、E1バンクの順番で1,2,3,4であったが

IoTゲート側はE1バンク、OLバンク、OMバンク、OHバンクの順番で1,2,3,4であった。

IoTゲート側でバンク順番をEV側に合わせていただき、再度試験したところ

連動動作良好となった。

[OneNote attachment reference omitted; attachment not copied]\n