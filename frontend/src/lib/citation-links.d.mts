export function linkCitedNames(
  markdown: string,
  targets: ReadonlyArray<{
    names: ReadonlyArray<string | undefined | null>;
    href: string | undefined | null;
    pageHref?: (page: number) => string | undefined | null;
  }>,
): string;
export function knowhowCardAnchor(prefix: string, knowledgeId: string): string;
