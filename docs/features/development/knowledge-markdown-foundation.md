---
status: proposal
phase: development
related-code:
  - docs/api/rag.md
  - lambda/rag/rag-function/app.py
---

# Knowledge Markdown Foundation

> Design proposal and curation contract for the selected curated Markdown snapshot already under `knowledge/drafts/`. It does not authorize raw OneNote/Lists access or export, further unreviewed transfer, RAG publication, deployment, AWS transfer of separated records, or write-back to OneNote/Lists.

## Purpose

Define a path for organizing curated technical knowledge in EleKnowledge while the local Obsidian Vault remains the canonical source. The design must support exploration of existing knowledge, curation of new observations, human review, controlled publication, and selective return of accepted edits to the Vault.

This is separate from PR #191, whose stated purpose is to consult administrators about read-only OneNote/Lists access. The proposal does not require that access to begin schema and UI design.

## Repository Areas

Keep materials with different trust and runtime roles separate:

| Area | Contents | RAG eligible by default |
| --- | --- | --- |
| `docs/features/development/` | Design, schemas, lifecycle, and implementation decisions | No |
| `tests/fixtures/knowledge/synthetic/` | Clearly synthetic source examples and normalized records | No |
| `knowledge/drafts/` | User-selected curated Markdown snapshot, including engineering-business drafts | No; editing/schema exploration only |
| Future approved knowledge area | Explicitly approved Markdown snapshots with provenance | No; requires a separate publication allowlist |
| Generated ingestion artifacts | Validated, transformed publication output | Only after publication approval and an approved isolated target |

Never infer publication eligibility from a file's presence in Git. Curated engineering-business information is in scope alongside technical knowledge. Keep personal/HR/qualification details, customer/site identifiers, raw OneNote exports, recycle-bin content, raw workbooks, credentials, and operational ledgers out unless separately approved. The current snapshot excludes explicit `confidential`/`restricted` content, the unread internal-URL item, the customer-named hold, and the consolidated error-code-table reference; see `knowledge/drafts/IMPORT-SCOPE.md`.

## Record Model

Use the Vault's stable `record_id` and increment `record_version` when accepted content changes. Preserve source identity, evidence, conditions, exceptions, and uncertainty. Do not make an AI-generated summary a verified fact. The curated Markdown copy is for EleKnowledge-side editing and schema improvement; it does not replace the Vault as canonical source.

The initial schema exploration must cover the Vault's existing technical and engineering-business record types; it is not limited to four technical types:

| Type | Purpose | Required distinction |
| --- | --- | --- |
| `knowhow` | Reusable, sourced knowledge and experience | Recorded statement vs corroborated knowledge; conditions and exceptions |
| `technical_reference` | Description of a function, design, or specification | Source-stated value vs current approved specification |
| `troubleshooting_case` | A single reported investigation | Observation, hypothesis, action status, and outcome are separate |
| `catalog` | Searchable lookup or mapping | A catalog is not a substitute for explanatory knowledge |
| `field_work_reference` | Engineering-business reference used in work | Source guidance vs approved/current field requirement |
| `technical_inquiry` | A technical question and reported response | Inquiry, response, basis, and unresolved applicability are distinct |
| `policy` | Rule or policy statement | Owning scope (`team_rule`, department, company rule/社規, etc.) must be explicit |
| `procedure` | Work or process procedure | Draft procedure vs authorized current procedure; include owner/revision/approval |
| `training` | Training record or learning material | Course/material content vs attendee/HR information |
| `quality_process_reference` | Quality-process information | Process guidance vs case-specific quality records |
| `failure_case` / `case_reference` | Failure report or case-oriented reference | Reported cause/actions/outcome vs independently verified facts |
| `safety_notice` / `safety_critical_trial_reference` | Safety or trial reference | Source statement vs approved safety rule; applicability and reviewer explicit |
| `reference`, `reference_note`, `reference_hold`, `reference_review`, `technical_reference_review`, `standard_reference_review`, `title_only_reference` | Reference state or incomplete entry | Do not treat an unread reference/title-only record as evidence or complete knowledge |
| `other` | Content not yet mapped | Keep visible as unmapped; don't silently discard or invent a type |

Record types are source vocabulary, not an access or publication decision. Preserve them while domain and organizational applicability are separately modeled. Map or normalize these values only through a reviewed schema migration.

Keep `review_status`, `publication_status`, `classification`, and `cloud_approval` independent. Only an explicit, reviewed publication allowlist may enter a retrieval source. Draft, excluded, unknown-classification, or unapproved records must not be indexed or used as answer evidence.

The existing Vault schema is a draft, not yet a validated API contract. Before implementing a parser or API, compare field types and allowed values with the target storage and Knowledge Base constraints. Keep structured link collections in a record registry if the Knowledge Base metadata format cannot represent them safely. Preserve source record types, including legacy values, during exploration; normalize them only with a documented, reviewed mapping.

## Knowledge Domain and Organizational Scope

`record_type` describes the shape of a record; it does not say whether the information is technical knowledge or engineering-business information. Add an independent `knowledge_domain` dimension. For this corpus, `engineering_business` is displayed as 「工技業務」 and can include business-oriented types such as `field_work_reference`, `policy`, `procedure`, `training`, and `quality_process_reference` when the content is suitable.

Organizational scope is a separate dimension from both domain and record type. The proposed `organizational_scope` values are `team_rule` (課内ルール), `department_rule`, `company_rule` (社規), `company_standard`, `external_standard`, `equipment_specific`, and `unknown`. Assign a rule scope only when the source explicitly establishes its owner and applicability. Do not infer `company_rule` from `record_type: policy` or infer `team_rule` from a folder name; retain `unknown` until reviewed.

An error code reported within an individual troubleshooting case may be retained with its symptom, source, conditions, and verification status. A consolidated error-code table or code-to-cause catalog is a different data class and is not part of this repository snapshot; keep it in the separately approved AWS handling lane. Curated display-reading guidance that does not reproduce the code table is not itself a code table.

## Curation and Writing Rules

EleKnowledge editing must follow the curated-record rules, not treat every Markdown file as equivalent source material:

- The selected curated Markdown snapshot is editable knowledge. Original OneNote Markdown exports, raw Lists/Excel exports, indexes, and ledgers are not interchangeable with curated records. Do not ingest a raw export merely because it is Markdown.
- Keep the YAML frontmatter and body consistent. Preserve `record_id`; increment `record_version` when an accepted record changes. Retain source path, source filename, OneNote ID when present, and evidence provenance.
- Do not invent metadata to make a record pass validation. Preserve absent/unknown values, report malformed frontmatter, and route it to a repair queue instead of silently rewriting the source snapshot.
- Use the provided structure where it fits: summary/purpose, applicability, conditions, knowledge or function, rationale, cautions/exceptions, related material, and source/review history. Omit inapplicable sections instead of filling them with guesses.
- Write in Japanese, retaining source-language names/codes where useful. Preserve units, negation, limits, conditions, exceptions, and chronology. Do not normalize ambiguous values into a definitive standard.
- Separate source-stated information, a reporter's account, an interpretation/hypothesis, independent corroboration, and current approved requirements. A reported action is not a verified action; a status marked complete does not prove a successful outcome.
- For troubleshooting, retain symptom, investigation sequence, cause assessment, actions (reported vs verified), outcome, and unknowns. Keep individual error codes attached to their case context; do not turn cases into a consolidated code table.
- Treat Lists-exported Excel as a transport/review copy, not the authoritative source. Retain the original List item identifier and source provenance when available; distinguish `vault_original` from `user_provided_extract`, and never claim independent verification from an extract alone.
- Keep scope dimensions independent: `knowledge_domain` identifies technical knowledge vs `engineering_business` (工技業務); `organizational_scope` identifies `team_rule` (課内ルール), department, `company_rule` (社規), standards, equipment-specific scope, or `unknown`. Only the source or an authorized reviewer can establish scope.
- Preserve unresolved references. Record whether an attachment exists separately from whether it has been read. Resolve Obsidian links/embeds or mark them unresolved; never create an `evidence_source` from a title/link alone.
- Do not turn an unreviewed function description or incident into an operational, safety, electrical, adjustment, inspection, or acceptance procedure. If the source is procedural, keep its review/currentness/approval state visible and require the responsible review before presenting it as actionable guidance.
- Classify confidential, personal, customer/site, and access-controlled content before AI processing. Unknown classification remains a draft gate, not approval.

## Source Intake and Curation

Treat OneNote pages and Microsoft Lists items as distinct source formats; do not assume that either source can be read until the owner approves the target, authentication method, permissions, and AI-processing boundary.

The proposed flow is:

1. Read an explicitly authorized page or item and retain its stable source identifier, source link, retrieval time, and source revision when available.
2. Normalize text, tables, headings, and supported attachment references without silently dropping Japanese text, negation, units, conditions, or row-level provenance.
3. Validate the normalized draft against the record schema and report missing or unresolved source material.
4. Let a curator edit a proposal while preserving the source and evidence mapping.
5. Have an accountable reviewer decide technical correctness, information classification, and publication separately.
6. Publish an approved snapshot to an approved isolated data target; trigger retrieval indexing only through a separately authorized process.

The intake service must not follow arbitrary URLs, bypass source permissions, copy signed URLs or tokens into records, or treat a linked-but-unread document as evidence. Obsidian `[[WikiLink]]` and `![[embed]]` syntax must be resolved or reported as unresolved; do not silently render a broken link as a valid attachment.

## Source of Truth and Round Trip

The local Vault remains the canonical editable source during the initial phase. Do not support concurrent editing of the same record in the Vault and application.

For an application-side proposal, record a transfer manifest containing the selected `record_id`s, source `record_version`s, base Git commit SHA, and content hashes. Return only explicitly selected records. Before applying a proposal to the Vault, compare it with the recorded base and current local content. Any mismatch, concurrent edit, identity change, rename, deletion, or merge requires manual resolution; never overwrite or pull the repository wholesale.

After human acceptance, update the local canonical record, increment its version, and retain the accepted application commit as provenance. Do not automatically write to OneNote or Lists. A paste-ready OneNote suggestion remains a proposal until its page owner confirms that it was applied.

## Access, Audit, and Publication

- Separate read, edit, review, publication, and administration permissions. Enforce authorization on the server; a hidden UI control is not an access boundary.
- Keep author, reviewer, approver, timestamps, and decision reasons in an auditable backend or protected review record rather than user-editable frontmatter.
- Preserve least-privilege access to source material and derived knowledge. A user's permission to read a source does not automatically authorize broader publication of its derivative.
- Keep draft storage, published storage, and retrieval indexes distinct. Exclude design documents and test fixtures from ingestion prefixes and indexing jobs.
- Store only validated, approved links. Reject unsafe URL schemes and never record credentials, temporary access tokens, or signed query strings.
- Treat citations as references to the exact approved record version; do not imply that a source was current or independently verified unless that review occurred.

## Test Set

Use synthetic fixtures for parser and workflow tests alongside the curated draft snapshot for editor and schema exploration. Synthetic fixtures must use fictional identifiers and inert URLs such as `https://example.invalid/`; do not place real machine values, source IDs, customer/site details, links, or attachment bytes in fixtures.

The fixtures should exercise:

- one record for each of the four content types above;
- business-domain examples for an explicitly scoped `team_rule` and `company_rule`, plus an `unknown` scope that must not be inferred (`tests/fixtures/knowledge/synthetic/business-scope.json`);
- a OneNote-like Markdown source with Japanese text, a table, a Wiki link, and an embed reference;
- a Lists-like item that distinguishes reported actions from independently verified actions;
- an unresolved attachment, a reference-only entry, contradictory status/detail, and a privacy-like canary that must be excluded or redacted.

Every fixture must be visibly marked synthetic and must be excluded from any production ingestion manifest. Do not use a real Vault record as a fixture until its repository transfer and AI-processing use have been approved.

## Acceptance Criteria

1. Schema validation rejects missing/duplicate IDs, invalid state values, and malformed type-specific fields without changing source text.
2. Japanese content, tables, units, negation, conditions, exceptions, evidence mappings, and reported-versus-verified distinctions survive normalization.
3. `knowledge_domain` and `organizational_scope` remain independent; scope is inferred only from explicit source evidence, with separate handling for 課内ルール and 社規.
4. Missing or unread attachments and inaccessible references remain explicit unresolved states; they do not become evidence.
5. A test proves that docs, fixtures, drafts, and unapproved records cannot enter an ingestion manifest; only an explicit approved-and-published allowlist can.
6. Round-trip tests preserve `record_id`, version, base SHA, and hashes; selected-ID filtering works; conflicts stop for manual resolution.
7. Citation tests distinguish the existing RAG `sourceUri` from future record-to-record links and do not fabricate source URLs.
8. No test or implementation writes to OneNote/Lists, uploads real data, synchronizes a Knowledge Base, or deploys infrastructure.

## Out of Scope

This proposal does not implement Microsoft Graph access, a knowledge CRUD API, an editor UI, automatic bidirectional sync, OneNote/Lists write-back, raw OneNote/Lists export, AWS transfer of the separated code tables/confidential lane, Knowledge Base synchronization, or production deployment. The selected curated Markdown snapshot is already present for draft editing; any additional transfer or publication requires separate scope, owner approval, security review, and tests against an approved environment.