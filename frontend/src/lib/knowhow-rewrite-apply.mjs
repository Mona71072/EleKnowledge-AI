// 管理者が「確認して反映する」を選んだ節の本文だけを、カードへ差し込む。
// 見出し行・他の節・frontmatter・改行コード・コードフェンスは変えない。人が編集した節は上書きしない。
import { applyCheckProposals } from './knowhow-card-proposal.mjs';
import { findRewriteStructureProblem, readSections } from './knowhow-rewrite-sections.mjs';

function reject(message) {
  throw new TypeError(message);
}

const isBlank = (line) => line.trim() === '';

/** 節の本文行（見出しの次の行から次の見出しの前まで）を、前後の空行の数を保ったまま新しい本文に入れ替える。 */
function replaceBody(lines, section, body) {
  const current = lines.slice(section.start, section.end);
  const last = section.end >= lines.length;
  const allBlank = current.every(isBlank);
  const leading = allBlank ? 1 : current.findIndex((line) => !isBlank(line));
  const trailing = allBlank ? (last ? Math.max(0, current.length - 1) : 1)
    : current.length - 1 - current.findLastIndex((line) => !isBlank(line));
  return [
    ...lines.slice(0, section.start),
    ...Array(leading).fill(''),
    ...body.replace(/\r\n?/gu, '\n').trim().split('\n'),
    ...Array(trailing).fill(''),
    ...lines.slice(section.end),
  ];
}

function uniqueSection(sections, heading) {
  const found = sections.filter((section) => section.heading === heading);
  return found.length === 1 ? found[0] : null;
}

function classify(items, current, expected) {
  const ready = [];
  const stale = [];
  for (const { heading, body } of items) {
    const now = uniqueSection(current.sections, heading);
    const before = uniqueSection(expected.sections, heading);
    if (!now || !before || now.body !== before.body) stale.push(heading);
    else if (body.replace(/\r\n?/gu, '\n').trim() !== now.body) ready.push({ heading, body, section: now });
  }
  return { ready, stale };
}

/**
 * 選んだ節の本文を置き換える。
 * `expectedBody` は書き換え案を作った時点の本文。いまの本文のその節が `expectedBody` の同じ節と違う（編集された、
 * 節が無くなった、同名の節が複数ある）ときは、その節を反映せず `stale` に入れる。他の節が変わっていても影響しない。
 * @param {string} markdown いまの本文（frontmatter 付きでもよい）
 * @param {ReadonlyArray<{ heading: string, body: string }>} accepted
 * @param {string} expectedBody
 * @returns {{ markdown: string, applied: number, stale: string[] }}
 */
export function applySectionRewrites(markdown, accepted, expectedBody) {
  if (typeof markdown !== 'string' || typeof expectedBody !== 'string' || !Array.isArray(accepted)) {
    reject('本文・反映する節・案を作った時点の本文を指定してください。');
  }
  if (accepted.some((item) => !item || typeof item.heading !== 'string' || findRewriteStructureProblem(item.body))) {
    reject('反映する節の本文を確認してください。見出し行や閉じていないコードフェンスは入れられません。');
  }
  const current = readSections(markdown);
  const { ready, stale } = classify(accepted, current, readSections(expectedBody));
  if (ready.length === 0) return { markdown, applied: 0, stale };
  const eol = markdown.includes('\r\n') ? '\r\n' : '\n';
  const lines = [...ready].sort((a, b) => b.section.start - a.section.start)
    .reduce((acc, item) => replaceBody(acc, item.section, item.body), current.lines);
  const headings = (value) => readSections(value.join('\n')).sections.map((section) => section.heading);
  if (headings(lines).join('\n') !== headings(current.lines).join('\n')) reject('節の構成が変わるため反映できません。');
  return { markdown: lines.join(eol), applied: ready.length, stale };
}

/**
 * 節の書き換えと、既存の追記（applyCheckProposals）を、1つの結果にまとめる。どちらか一方だけでもよい。
 * 書き換えを先に行う（追記の節は書き換えの対象ではないので互いに干渉しない）。
 * @param {string} body
 * @param {{ rewrites: ReadonlyArray<{heading: string, body: string}>, expectedBody: string, proposals: ReadonlyArray<{question: string, checkedOn: string, markdown: string}> }} edits
 */
export function composeCardEdits(body, { rewrites, expectedBody, proposals }) {
  const rewritten = rewrites.length
    ? applySectionRewrites(body, rewrites, expectedBody)
    : { markdown: body, applied: 0, stale: [] };
  const appended = proposals.length
    ? applyCheckProposals(rewritten.markdown, proposals)
    : { markdown: rewritten.markdown, applied: 0, skipped: 0 };
  return {
    markdown: appended.markdown,
    rewritten: rewritten.applied,
    stale: rewritten.stale,
    applied: appended.applied,
    skipped: appended.skipped,
  };
}
