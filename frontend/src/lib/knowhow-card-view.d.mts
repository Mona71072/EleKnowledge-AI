export type KnowhowCardSection = { heading: string; body: string; markdown: string };
export type KnowhowCardView = { title: string; readerSections: KnowhowCardSection[]; editorSections: KnowhowCardSection[] };

export const EDITOR_HEADING_KEYWORDS: readonly string[];
export function isEditorHeading(heading: string): boolean;
export function splitKnowhowCardBody(body: unknown): KnowhowCardView;
export function sectionsToMarkdown(sections: readonly KnowhowCardSection[]): string;
export function breakBeforeNoticeMarks(text: unknown): string;
