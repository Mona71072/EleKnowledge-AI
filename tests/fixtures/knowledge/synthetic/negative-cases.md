---
fixture: synthetic
purpose: "Negative cases for exclusion, redaction, and unresolved-source handling"
---

# Synthetic negative cases

All identifiers below are fabricated placeholders. They are not personal, customer, site, or credential data.

## Unresolved source material

- Page reference: `[[SYNTH-MISSING-PAGE]]` (`unverified`)
- Attachment reference: `![[SYNTH-MISSING-IMAGE.png]]` (not present; must not become evidence)
- Inert URL: `https://example.invalid/restricted?token=NOT_A_REAL_TOKEN`

The missing page and image must remain unresolved. The URL is deliberately non-routable and the query value is a literal placeholder, not a credential. Do not request or follow it.

## Exclusion canary

- Person-like placeholder: `SYNTHETIC-PERSON-001`
- Site-like placeholder: `SYNTHETIC-SITE-001`
- Credential-like placeholder: `NOT_A_REAL_SECRET`

This section tests that a record explicitly marked excluded or restricted is rejected by a publication allowlist. Do not use these placeholders as real identity data or copy any real-world values into this fixture.

## Reference-only and conflicting status

A synthetic row may state `status: complete` while its detail says the outcome is unknown. Preserve both source fields, flag the contradiction, and keep the record unpublished until a human resolves it. A title or link without readable evidence must not be converted into verified knowledge.