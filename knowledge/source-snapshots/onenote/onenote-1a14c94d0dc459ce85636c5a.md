---
snapshot_type: "onenote_source_page"
source_system: "OneNote"
onenote_id: "ec02c9c5-cdb7-4e83-bc9a-e950a58b6a11:82"
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
<u>イナーシャ同定運転</u>（EA-972-5-2-9参照）

エレベーターの実際の速度パターンを理想の速度パターンに近づけるために実施している。

理想の速度パターンは現場ごとの昇降行程やかごの自重等が加味されていないため、走行時その影響を受け、実際に必要なトルクと理想トルクに差異が生じ振動が発生してしまう。その差異をイナーシャ同定運転にて補い、振動を抑制している。

**※イナーシャ同定運転をする前に****TSD****動作位置の測定を必ず実施すること。**

[OneNote attachment reference omitted; attachment not copied]

モデル規範で理想のトルクパターンと理想タコを算出し、モデルイナーシャで理想トルクとイナーシャゲインからトルク指令値を算出する。また、イナーシャ同定器で理想トルク、理想タコ、タコからイナーシャゲインを同定する。PI制御で理想タコとタコの差から補正トルクを算出している。

【通常イナーシャ】

[OneNote attachment reference omitted; attachment not copied]

【高速イナーシャ】

[OneNote attachment reference omitted; attachment not copied]

[OneNote attachment reference omitted; attachment not copied]

【参考】

・イナーシャ同定運転後のイナーシャ同定値は下記の方法で確認および設定変更が出来る。

・高速イナーシャ同定は高揚程エレベーターの調整時間短縮のために追加された機能である。どちらを使用しても学習値は同じであるため、昇降路全高により使い分けること。

[OneNote attachment reference omitted; attachment not copied]\n