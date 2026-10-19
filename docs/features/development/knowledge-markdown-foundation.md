---
status: proposal
phase: development
related-code:
  - docs/api/rag.md
  - lambda/rag/rag-function/app.py
---

# Knowledge Markdown Foundation

> Design proposal only. This document does not authorize Microsoft access, real-data transfer, RAG publication, deployment, or write-back to OneNote/Lists.

## Purpose

Define a path for organizing curated technical knowledge in EleKnowledge while the local Obsidian Vault remains the canonical source. The design must support exploration of existing knowledge, curation of new observations, human review, controlled publication, and selective return of accepted edits to the Vault.

This is separate from PR #191, whose stated purpose is to consult administrators about read-only OneNote/Lists access. The proposal does not require that access to begin schema and UI design.

## Repository Areas

Keep materials with different trust and runtime roles separate:

| Area | Contents | RAG eligible by default |
| --- | --- | --- |
| `docs/features/development/` | Design, schemas, lifecycle, and implementation decisions | No |
| `tests/fixtures/knowledge/synthetic/` | Clearly synthetic source examples and normalized records | No |
| Future approved knowledge area | Explicitly approved Markdown snapshots with provenance | No; requires a separate publication allowlist |
| Generated ingestion artifacts | Validated, transformed publication output | Only after publication approval and an approved isolated target |

Never infer publication eligibility from a file's presence in Git. Curated engineering-business information is in scope alongside technical knowledge. Keep personal/HR/qualification details, customer/site identifiers, raw OneNote exports, recycle-bin content, raw workbooks, credentials, and operational ledgers out unless separately approved.

## Record Model

Use the Vault's stable `record_id` and increment `record_version` when accepted content changes. Preserve source identity, evidence, conditions, exceptions, and uncertainty. Do not make an AI-generated summary a verified fact.

The first schema exploration should cover these content types:

| Type | Purpose | Required distinction |
| --- | --- | --- |
| `knowhow` | Reusable, sourced knowledge and experience | Recorded statement vs corroborated knowledge; conditions and exceptions |
| `technical_reference` | Description of a function, design, or specification | Source-stated value vs current approved specification |
| `troubleshooting_case` | A single reported investigation | Observation, hypothesis, action status, and outcome are separate |
| `catalog` | Searchable lookup or mapping | A catalog is not a substitute for explanatory knowledge |

Keep `review_status`, `publication_status`, `classification`, and `cloud_approval` independent. Only an explicit, reviewed publication allowlist may enter a retrieval source. Draft, excluded, unknown-classification, or unapproved records must not be indexed or used as answer evidence.

The existing Vault schema is a draft, not yet a validated API contract. Before implementing a parser or API, compare field types and allowed values with the target storage and Knowledge Base constraints. Keep structured link collections in a record registry if the Knowledge Base metadata format cannot represent them safely.

## Knowledge Domain and Organizational Scope

`record_type` describes the shape of a record; it does not say whether the information is technical knowledge or engineering-business information. Add an independent `knowledge_domain` dimension. For this corpus, `engineering_business` is displayed as 「工技業務」 and can include business-oriented types such as `field_work_reference`, `policy`, `procedure`, `training`, and `quality_process_reference` when the content is suitable.

Organizational scope is a separate dimension from both domain and record type. The proposed `organizational_scope` values are `team_rule` (課内ルール), `department_rule`, `company_rule` (社規), `company_standard`, `external_standard`, `equipment_specific`, and `unknown`. Assign a rule scope only when the source explicitly establishes its owner and applicability. Do not infer `company_rule` from `record_type: policy` or infer `team_rule` from a folder name; retain `unknown` until reviewed.

An error code reported within an individual troubleshooting case may be retained with its symptom, source, conditions, and verification status. A consolidated error-code table or code-to-cause catalog is a different data class and is not part of this repository snapshot; keep it in the separately approved AWS handling lane. Curated display-reading guidance that does not reproduce the code table is not itself a code table.

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

## Proposed Initial Test Set

Use synthetic fixtures for parser and workflow tests alongside the curated draft snapshot for editor and schema exploration. Synthetic fixtures must use fictional identifiers and inert URLs such as `https://example.invalid/`; do not place real machine values, source IDs, customer/site details, links, or attachment bytes in fixtures.

The fixtures should exercise:

- one record for each of the four content types above;
- a OneNote-like Markdown source with Japanese text, a table, a Wiki link, and an embed reference;
- a Lists-like item that distinguishes reported actions from independently verified actions;
- an unresolved attachment, a reference-only entry, contradictory status/detail, and a privacy-like canary that must be excluded or redacted.

Every fixture must be visibly marked synthetic and must be excluded from any production ingestion manifest. Do not use a real Vault record as a fixture until its repository transfer and AI-processing use have been approved.

## Acceptance Criteria

1. Schema validation rejects missing/duplicate IDs, invalid state values, and malformed type-specific fields without changing source text.
2. Japanese content, tables, units, negation, conditions, exceptions, evidence mappings, and reported-versus-verified distinctions survive normalization.
3. Missing or unread attachments and inaccessible references remain explicit unresolved states; they do not become evidence.
4. A test proves that docs, fixtures, drafts, and unapproved records cannot enter an ingestion manifest; only an explicit approved-and-published allowlist can.
5. Round-trip tests preserve `record_id`, version, base SHA, and hashes; selected-ID filtering works; conflicts stop for manual resolution.
6. Citation tests distinguish the existing RAG `sourceUri` from future record-to-record links and do not fabricate source URLs.
7. No test or implementation writes to OneNote/Lists, uploads real data, synchronizes a Knowledge Base, or deploys infrastructure.

## Out of Scope

This proposal does not implement Microsoft Graph access, a knowledge CRUD API, an editor UI, automatic bidirectional sync, OneNote/Lists write-back, raw OneNote/Lists export, AWS transfer of the separated code tables/confidential lane, Knowledge Base synchronization, or production deployment. Each requires separate scope, owner approval, security review, and tests against an approved environment.