import { listCommentSections } from './knowledge-comment-review.mjs';
import { diffLines } from './line-diff.mjs';

/** Return changed sections in diff order, with links only when the current target is unambiguous. */
export function listChangedSections(before, after, rows) {
  const diffRows = rows ?? diffLines(before, after).rows;
  const beforeSections = listCommentSections(before);
  const afterSections = listCommentSections(after);
  const beforeCounts = new Map();
  beforeSections.forEach(({ label }) => beforeCounts.set(label, (beforeCounts.get(label) ?? 0) + 1));
  const afterByLabel = new Map();
  const afterByLine = new Map();
  const beforeByLine = new Map();
  beforeSections.forEach((section) => beforeByLine.set(section.line, section));
  afterSections.forEach((section) => {
    afterByLine.set(section.line, section);
    afterByLabel.set(section.label, [...(afterByLabel.get(section.label) ?? []), section]);
  });
  const entries = new Map();
  const add = (label, status, sectionId) => {
    const existing = entries.get(label);
    if (existing) {
      if (status === 'ambiguous' || (status === 'changed' && existing.status === 'removed')) {
        entries.set(label, status === 'ambiguous' ? { label, status } : { label, status, sectionId });
      }
      return;
    }
    entries.set(label, status === 'changed' ? { label, status, sectionId } : { label, status });
  };
  const addCurrent = (label) => {
    const matches = afterByLabel.get(label) ?? [];
    if (matches.length > 1 || (beforeCounts.get(label) ?? 0) > 1) add(label, 'ambiguous');
    else if (matches.length === 1) add(label, 'changed', matches[0].id);
    else add(label, 'removed');
  };
  const sectionAt = (sections, line) => {
    let low = 0;
    let high = sections.length - 1;
    let found = sections[0];
    while (low <= high) {
      const middle = Math.floor((low + high) / 2);
      if (sections[middle].line <= line) {
        found = sections[middle];
        low = middle + 1;
      } else high = middle - 1;
    }
    return found;
  };

  for (const row of diffRows) {
    if (row.kind === 'same') continue;
    if (row.kind === 'removed' && row.beforeLine) {
      const heading = beforeByLine.get(row.beforeLine);
      if (heading) {
        if ((beforeCounts.get(heading.label) ?? 0) > 1 || (afterByLabel.get(heading.label)?.length ?? 0) > 0) {
          add(heading.label, 'ambiguous');
        } else add(heading.label, 'removed');
        continue;
      }
      const section = sectionAt(beforeSections, row.beforeLine);
      if (section) addCurrent(section.label);
    }
    if (row.kind === 'added' && row.afterLine) {
      const heading = afterByLine.get(row.afterLine);
      if (heading) {
        addCurrent(heading.label);
        continue;
      }
      const section = sectionAt(afterSections, row.afterLine);
      if (section) addCurrent(section.label);
    }
  }
  return [...entries.values()];
}
