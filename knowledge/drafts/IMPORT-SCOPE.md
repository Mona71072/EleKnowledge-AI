# Curated Markdown Import Scope

This snapshot is for developing EleKnowledge's record, review, and editing workflows. The local Vault remains the canonical source. Files in this directory are drafts, not a RAG corpus.

## Source and Selection

- Source set: 654 Markdown files under the local `整備済み資料/技術資料/` directory.
- Selected for this snapshot: 567 records. The first batch contains 3 records listed in [IMPORT-NOTES.md](IMPORT-NOTES.md); this batch adds 564 records.
- The screening retained substantial, typed knowledge records such as catalogs, technical references, know-how, failure cases, and troubleshooting cases. Existing frontmatter and file content were copied without rewriting.
- Existing review, publication, classification, and cloud-approval fields are preserved. In particular, `unknown`, `in_review`, `not_published`, and `not_reviewed` remain unapproved states.

## Exclusions

- Explicit `confidential`, `confidential_source`, `restricted`, or missing classification.
- Missing `record_type`; business-oriented types `field_work_reference`, `policy`, `procedure`, `quality_process_reference`, and `training`; technical inquiries and title-only references.
- Very short/bodyless records that do not contain enough content for the initial schema workflow.
- `ELV_ドア駆動基板エラー.md`, which contains unread internal PDF URLs with encoded path data.
- `ESC_JR東日本ページ_情報管理確認保留.md`, whose filename contains a customer name and whose content was not reviewed.
- Raw OneNote pages, Lists/Excel exports, attachments, and files outside the curated Markdown set.

One copied Markdown file, `ESC_変数定義.md`, has a snapshot-only note that its attachment is not included; its source note remains unchanged. The copied record otherwise preserves its existing content and review state.

Some otherwise-eligible records retain `classification: unknown`; this snapshot does not reclassify or approve them. It preserves their existing draft status for controlled schema and workflow work only. Before broader access, AI processing, or publication, each record still requires information-management and technical review.

## Publication Gate

Do not configure `knowledge/drafts/` as a Bedrock/Knowledge Base data-source prefix or include it in an ingestion manifest. Git presence does not authorize indexing. Only an explicit, separately reviewed allowlist of approved and published records may be considered for a future isolated retrieval source.