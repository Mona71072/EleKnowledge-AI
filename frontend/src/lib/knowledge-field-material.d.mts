export type FieldMaterialSource = {
  filename: string;
  text: string;
  sha256: string;
  sourceId: string;
};

export type FieldMaterialMetadata = {
  sourceId: string;
  filename: string;
  title: string;
  version: string;
  locator: string;
  url?: string;
};

export const MAX_FIELD_MATERIAL_BYTES: 262144;
export const MAX_FIELD_MATERIAL_EXCERPT_CHARS: 2000;
export const MAX_FIELD_MATERIAL_SUMMARY_CHARS: 2000;

/** Extract deduplicated field-report references from the unique dedicated H2 outside fences. */
export function getFieldMaterialSourceRefs(markdown: string): Array<{
  ref_type: 'knowhow';
  knowhow_id: string;
  origin: 'field_report';
}>;

/** Read one selected local .md/.txt file; the returned value never retains the File. */
export function readFieldMaterialFile(file: File): Promise<FieldMaterialSource>;

/** Return the exact excerpt if it is a bounded contiguous substring of sourceText. */
export function validateFieldMaterialExcerpt(sourceText: string, excerpt: string): string;

/** Validate attribution fields; links must be public HTTPS links without credentials, query, or fragment. */
export function normalizeFieldMaterialMetadata(
  input: Pick<FieldMaterialMetadata, 'title' | 'version' | 'locator' | 'url'>,
  source: Pick<FieldMaterialSource, 'sourceId' | 'filename'>,
): FieldMaterialMetadata;

/** Insert only a human-reviewed summary and attribution. The reviewed flag is mandatory. */
export function insertFieldMaterialMarkdown(
  markdown: string,
  acceptedSummary: string,
  metadata: FieldMaterialMetadata,
  options: { reviewed: boolean },
): string;
