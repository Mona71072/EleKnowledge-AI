---
snapshot_type: "onenote_source_collection"
source_system: "OneNote"
source_page_count: 1039
classification: "unknown"
review_status: "unreviewed"
publication_status: "not_published"
cloud_approval: "not_reviewed"
---

# OneNote Source Snapshot

Individual pages retain their exported `onenote_id`. Filenames are opaque hashes to avoid leaking source titles in paths. Resolve IDs against the approved live OneNote API before adding item links; the export ID is not claimed to be a verified Graph page ID.

- Eligible pages copied: 1039.
- Excluded for confidentiality terms: 72.
- Excluded for credential terms: 7.
- Excluded for identity/customer terms: 45.
- Excluded error-code table candidates: 8.
- Excluded duplicate page IDs: 0.
- `HIERARCHY.json` preserves all 1,039 included page IDs and adds a title/path-free hierarchy mapping inferred from local Vault paths. It matched 1,038 IDs: 805 have a fully matched parent chain, 56 resolve through 18 ID-only parent stubs for screened-out parent pages, 175 are section-root page candidates, 2 have a folder container but no parent page ID, and 1 has no Vault match. Stub records contain only the parent OneNote ID and `content_status: excluded_from_snapshot`; no excluded content, title, or path is included.
- The manifest's `root_container_key` is an opaque hash of the first local path component and only a grouping hint; it is not verified as a OneNote notebook or section. Native notebook/section IDs, the two folder-only parent identities, the one unmatched page's hierarchy, and original page order remain unresolved; filesystem order is not treated as authoritative.
- URL references redacted: 1034.
- Attachment embeds replaced by unresolved placeholders: 2792.
- Original page paths, `.one` files, recycle-bin pages, attachments, credentials, and raw CSV exports are not included.
- This source snapshot is for curation and source reconciliation only. Do not index it into RAG.
- Rebuild the hierarchy mapping with `node scripts/build_onenote_hierarchy.mjs --vault-root <vault-root> --snapshot-root knowledge/source-snapshots/onenote --output knowledge/source-snapshots/onenote/HIERARCHY.json`. It writes page IDs, opaque root-container grouping keys, parent IDs, ancestor IDs, page levels, ID-only stubs for excluded parents, and resolution status only; it does not write source titles or paths.
\n