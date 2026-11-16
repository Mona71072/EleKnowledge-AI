export type KnowhowCardSection = { heading: string; body: string; markdown: string };
export type KnowhowCardView = { title: string; readerSections: KnowhowCardSection[]; editorSections: KnowhowCardSection[] };

export const EDITOR_HEADING_KEYWORDS: readonly string[];
export const FIELD_MATERIAL_SECTION: '現場資料に基づくノウハウ';
export function createFenceTracker(): (line: string) => boolean;
export function isEditorHeading(heading: string): boolean;
export function splitKnowhowCardBody(body: unknown): KnowhowCardView;
export function sectionsToMarkdown(sections: readonly KnowhowCardSection[]): string;
export function breakBeforeNoticeMarks(text: unknown): string;
export function parseH2Heading(line: string): string | null;
