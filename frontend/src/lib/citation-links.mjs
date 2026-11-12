// 回答本文に書かれた資料名・カード名を、その回答で実際に返した資料・カードへのリンクにする（2026-11-12 itai 決定）。
// 番号（E1・技1 など）を見せずに引用を辿れるようにする。リンクにするのは、呼び出し側が渡した一覧にある名前だけで、
// モデルが書いた未知の名前は文字のまま残す（誤ったリンクを作らない）。

const CODE_SEGMENT = /(```[\s\S]*?```|`[^`\n]*`)/u;
// 既存の Markdown リンク・画像（[..](..) / ![..](..)）は触らない。
const EXISTING_LINK = /(!?\[[^\]\n]*\]\([^)\n]*\))/u;
const WORD_CHAR = /[0-9A-Za-z_]/u;
const MIN_NAME_LENGTH = 4;
const MAX_TARGETS = 50;

function escapeRegExp(value) {
  return value.replace(/[.*+?^${}()|[\]\\]/gu, '\\$&');
}

function usableName(name) {
  return typeof name === 'string' && name.trim().length >= MIN_NAME_LENGTH && !/[[\]()\n`]/u.test(name);
}

/** 拡張子付きの資料名は、拡張子なしの書き方（例: TI-1158）でも当てる。 */
function nameVariants(name) {
  const trimmed = name.trim();
  const withoutExtension = trimmed.replace(/\.(pdf|docx?|xlsx?|pptx?)$/iu, '');
  return withoutExtension !== trimmed && withoutExtension.length >= MIN_NAME_LENGTH ? [trimmed, withoutExtension] : [trimmed];
}

/**
 * @param {string} markdown
 * @param {ReadonlyArray<{names: ReadonlyArray<string|undefined|null>, href: string|undefined|null}>} targets
 * @returns {string}
 */
export function linkCitedNames(markdown, targets) {
  if (typeof markdown !== 'string' || !markdown || !Array.isArray(targets) || targets.length === 0) return markdown;
  const hrefByName = new Map();
  for (const target of targets.slice(0, MAX_TARGETS)) {
    if (!target || typeof target.href !== 'string' || !target.href || /[<>\s]/u.test(target.href)) continue;
    for (const name of target.names || []) {
      if (!usableName(name)) continue;
      for (const variant of nameVariants(name)) {
        if (!hrefByName.has(variant)) hrefByName.set(variant, target.href);
      }
    }
  }
  if (hrefByName.size === 0) return markdown;
  const names = [...hrefByName.keys()].sort((left, right) => right.length - left.length);
  const pattern = new RegExp(names.map(escapeRegExp).join('|'), 'gu');
  const linkText = (text) => text.replace(pattern, (match, offset, whole) => {
    const before = whole[offset - 1] ?? '';
    const after = whole[offset + match.length] ?? '';
    if ((WORD_CHAR.test(match[0]) && WORD_CHAR.test(before)) || (WORD_CHAR.test(match.at(-1)) && WORD_CHAR.test(after))) return match;
    return `[${match}](<${hrefByName.get(match)}>)`;
  });
  return markdown.split(CODE_SEGMENT).map((part, index) => (
    index % 2 === 1 ? part : part.split(EXISTING_LINK).map((piece, pieceIndex) => (pieceIndex % 2 === 1 ? piece : linkText(piece))).join('')
  )).join('');
}

/** 先輩チャットのカードへの、同じ画面内のアンカー。 */
export function knowhowCardAnchor(prefix, knowledgeId) {
  return `${prefix}-card-${String(knowledgeId).replace(/[^A-Za-z0-9-]/gu, '-')}`;
}
