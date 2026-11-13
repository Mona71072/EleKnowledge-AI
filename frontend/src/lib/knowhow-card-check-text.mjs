// 一括照合の質問づくりで使う、文字の切り出しと掃除。AI は使わない。

// カード内の管理用の呼び名。質問文（検索に使う文）には入れない。
const MANAGEMENT_WORD = /Lists|OneNote|§|KH-[A-Z0-9]|list_item_id|情報管理/u;
const MANAGEMENT_PAREN = /[（(][^（）()]*(?:Lists|OneNote|§|KH-[A-Z0-9]|list_item_id|情報管理)[^（）()]*[）)]/gu;
const MANAGEMENT_TOKEN = /KH-[A-Z0-9][A-Z0-9-]*|§\s*\d+|list_item_id\s*[:：]?\s*\d*|Lists(?:\s*\d+)?|OneNote/gu;

// 資料番号（SUE-3-17、S-EL-323.1、S-EL・323、P-6-S900.01-B）。ノウハウID（KH-…）は除く。
const DOCUMENT_NUMBER = String.raw`(?<![A-Za-z0-9-])(?!KH-)[A-Z]{1,4}(?:-[A-Z0-9]+(?:\.[0-9A-Z]+)*|・\d+(?:\.\d+)*)+`;
// 規格・法令の番号（告示 1455、JIS3525、29 条）。
const RULE_NUMBER = String.raw`告示\s?(?:第\s?)?\d+(?:\s?号)?|JIS\s?[A-Z]?\s?\d{3,5}|(?:第\s?)?(?<!\d)\d+\s?条`;
// 単位つきの数値（800 mm、62.5 lx、500msec）。
const UNIT = 'mm|cm|kg|kN|kW|kΩ|MΩ|mA|msec|ms|sec|lx|ルクス|Hz|％|%|℃|°C|秒|Ω|V|A|N|m';
const QUANTITY = String.raw`(?<![A-Za-z0-9.\-/])\d+(?:\.\d+)?\s?(?:${UNIT})(?![A-Za-z])`;
const VALUE_TOKEN = new RegExp(`(${DOCUMENT_NUMBER})|${RULE_NUMBER}|${QUANTITY}`, 'gu');
const DOCUMENT_TOKEN = new RegExp(`^(?:${DOCUMENT_NUMBER})$`, 'u');

/** 法令・安全に関わる語。長い語を先に置く（「建築基準法施行令」を「建築基準法」より先に拾う）。 */
export const LAW_TERMS = Object.freeze([
  '建築基準法施行令', '建築基準法', '労働安全衛生規則', '労働安全衛生法', '労働安全衛生', '安衛法', '安衛則', '労基',
  '消防法', '電気事業法', '電気設備技術基準', '構造規格', '告示', '法令', '法規', '法定',
  '官検', '完了検査', '落成検査', '定期検査', '確認申請', '耐震', '防火', '遮煙',
  '安全対策', '使用禁止', '墜落', '感電', '特別教育',
]);
const LAW_TERM = new RegExp(LAW_TERMS.join('|'), 'gu');

/** 1行あたりの処理対象の最大文字数。これを超える部分は掃除・検出の対象にしない（正規表現の処理時間を抑える）。 */
export const MAX_TEXT_LINE_CHARS = 2_000;
const LINK_LABEL_MAX = 300;
const LINK_TARGET_MAX = 500;
const MARKDOWN_LINK = new RegExp(String.raw`!?\[([^\]\n]{0,${LINK_LABEL_MAX}})\]\([^)\n]{0,${LINK_TARGET_MAX}}\)`, 'gu');

/** 1行の長さを上限で切る（コードポイント単位ではなく UTF-16 単位でよい。後続の正規表現の入力を抑えるため）。 */
export const clampLine = (text) => String(text ?? '').slice(0, MAX_TEXT_LINE_CHARS);

const unique = (values) => [...new Set(values)];
const tidy = (text) => text.replace(/\s+/gu, ' ').replace(/\s*([。、])\s*/gu, '$1').trim();

/** Markdown の飾り（強調・リンク・コード記号）を外して、文字だけにする。 */
export function stripMarkdown(text) {
  return tidy(clampLine(text)
    .replace(MARKDOWN_LINK, '$1')
    .replace(/\*\*|__|`/gu, ''));
}

/** 管理用の呼び名（Lists 399、§399、ノウハウID、OneNote）を含むか。 */
export function hasManagementTerms(text) {
  return MANAGEMENT_WORD.test(String(text ?? ''));
}

/** 管理用の呼び名と、それだけを説明する括弧書きを取り除く。機種名・数値・資料番号は残す。 */
export function stripManagementTerms(text) {
  return tidy(clampLine(text).replace(MANAGEMENT_PAREN, '').replace(MANAGEMENT_TOKEN, ' '));
}

/**
 * 数値・基準・規格番号・資料番号を、出てきた順に重複なしで返す。
 * @param {string} text
 * @returns {string[]}
 */
export function extractValueTokens(text) {
  const tokens = Array.from(clampLine(text).matchAll(VALUE_TOKEN), (match) => (
    match[1] === undefined || /\d/u.test(match[1]) ? match[0].trim() : ''
  ));
  return unique(tokens.filter(Boolean));
}

/** 資料番号の形をしているか（数値だけの基準と区別する）。 */
export function isDocumentNumber(token) {
  return DOCUMENT_TOKEN.test(token) && /\d/u.test(token);
}

/** 法令・安全に関わる語を、出てきた順に重複なしで返す。 */
export function findLawTerms(text) {
  return unique(Array.from(clampLine(text).matchAll(LAW_TERM), (match) => match[0]));
}

/** ほぼ同じ文かを比べるための、記号と空白を除いた形。 */
export function comparisonKey(text) {
  return stripMarkdown(text).replace(/[\s\p{P}\p{S}]/gu, '').toLowerCase();
}
