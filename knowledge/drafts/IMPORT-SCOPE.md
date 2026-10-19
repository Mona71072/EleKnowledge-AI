# Curated Markdown Import Scope

This snapshot is for developing EleKnowledge's record, review, and editing workflows. The local Vault remains the canonical source. Files in this directory are drafts, not a RAG corpus.

## Source and Selection

- Source set: 654 Markdown files under the local `整備済み資料/技術資料/` directory.
- Selected for this snapshot: 626 records from 654 curated Markdown files. This includes technical knowledge, 51 non-confidential engineering-business records, and three title-only drafts for EleKnowledge to triage. One consolidated error-code-table reference is withheld for the separate AWS lane.
- The screening retains technical knowledge and curated engineering-business records. Business-oriented types are registered under `knowledge_domain: engineering_business` (「工技業務」); original `record_type` and `category` remain intact. The copies otherwise preserve source content and frontmatter, except for the documented snapshot-only attachment note in `ESC_変数定義.md` and the added domain/scope fields on engineering-business records.
- Six records initially flagged by an automated frontmatter scan were manually reviewed and included as technical drafts: `ELV_ACO-E遠方発停_送風機運転継続事例.md`, `ELV_ER運転_緩衝器ストローク事例.md`, `ELV_KM-LD回生コンバーター起動不能_カバー連動状態_ID287事例.md`, `ELV_LV5K_LV6K_CLT寸法_事例記録.md`, `ELV_カゴ内インジ階床表示_参照記録.md`, and `ELV_仮設動力S相接続不良_事例記録.md`. The first five retain unknown classification and unreviewed status. `ELV_カゴ内インジ階床表示_参照記録.md` has a malformed split frontmatter and is included specifically as a schema-repair example; do not infer missing metadata.
- Organizational applicability is separate from record type. `organizational_scope` uses `team_rule`, `department_rule`, `company_rule`, `company_standard`, `external_standard`, `equipment_specific`, or `unknown`. Added business records use `unknown` unless the source explicitly states the scope; do not infer a company rule or section rule from a filename or type.
- The ACO-E case retains its source HTTPS reference unchanged. Its access, rights, and currentness have not been verified; do not fetch it or treat it as evidence until approved.
- Existing review, publication, classification, and cloud-approval fields are preserved. In particular, `unknown`, `in_review`, `not_published`, and `not_reviewed` remain unapproved states.

## Exclusions

- Explicit `confidential`, `confidential_source`, or `restricted` records remain outside this repository snapshot for the later AWS lane (25 files in the current source set).
- `ELV_ドア駆動基板エラー.md`, which contains unread internal PDF URLs with encoded path data.
- `ESC_JR東日本ページ_情報管理確認保留.md`, whose filename contains a customer name and whose content was not reviewed.
- `総点_u形_異常コード一覧.md`, which points to a consolidated error-code table. The table itself is reserved for the separately approved AWS lane. Error codes recorded within individual troubleshooting cases remain in the draft snapshot.
- Raw OneNote pages, Lists/Excel exports, attachments, and files outside the curated Markdown set.

One copied Markdown file, `ESC_変数定義.md`, has a snapshot-only note that its attachment is not included; its source note remains unchanged. The copied record otherwise preserves its existing content and review state.

 Some records retain `classification: unknown`; `ELV_カゴ内インジ階床表示_参照記録.md` has malformed split frontmatter. The snapshot does not reclassify, repair, or approve these records. They remain drafts for workflow/schema development. Before broader access, AI processing, or publication, each record still requires information-management and technical review.

## Publication Gate

Do not configure `knowledge/drafts/` as a Bedrock/Knowledge Base data-source prefix or include it in an ingestion manifest. Git presence does not authorize indexing. Only an explicit, separately reviewed allowlist of approved and published records may be considered for a future isolated retrieval source.