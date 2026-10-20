// 調査ジョブの回答表示で使う、画面に依存しない小さな補助関数。

const REF_PATTERN = /(?<![\\[])\[([TLK]\d{1,3})\](?![(:])/gu;
const CODE_SEGMENT = /(```[\s\S]*?```|`[^`\n]*`)/u;

/** 出典一覧の `<li id>` と本文中のリンクが共有するアンカー名。 */
export function researchRefAnchor(prefix, ref) {
  return `${prefix}-ref-${ref}`;
}

/**
 * 回答本文の [T1] [L1] [K1] を、出典一覧へ飛ぶ Markdown リンクにする。
 * 取得結果にある参照だけを対象にし、コード部分・既存のリンク・定義は変えない。
 *
 * @param {string | undefined} markdown
 * @param {ReadonlySet<string>} knownRefs
 * @param {string} anchorPrefix 画面内で一意な接頭辞（相談ごと）
 */
export function linkResearchRefs(markdown, knownRefs, anchorPrefix) {
  if (typeof markdown !== 'string' || !markdown) return '';
  if (!knownRefs || knownRefs.size === 0) return markdown;
  return markdown.split(CODE_SEGMENT).map((part, index) => (
    index % 2 === 1 ? part : part.replace(REF_PATTERN, (match, ref) => (
      knownRefs.has(ref) ? `[\\[${ref}\\]](#${researchRefAnchor(anchorPrefix, ref)})` : match
    ))
  )).join('');
}

/** 経過時間を「12秒」「1分05秒」で表す。 */
export function formatElapsed(ms) {
  const seconds = Number.isFinite(ms) && ms > 0 ? Math.floor(ms / 1000) : 0;
  if (seconds < 60) return `${seconds}秒`;
  return `${Math.floor(seconds / 60)}分${String(seconds % 60).padStart(2, '0')}秒`;
}

const MAX_QUESTION_CODEPOINTS = 2_000;
const SUPPLEMENT_LABEL = '\n補足: ';

const STEP_LABELS = Object.freeze({
  understand: { done: '質問を整理しました', failed: '質問を整理できませんでした' },
  knowhow: { done: 'ノウハウを確認しました', failed: 'ノウハウを確認できませんでした' },
  tech_search: { done: '技術資料を検索しました', failed: '技術資料を検索できませんでした' },
  law_search: { done: '法令を確認しました', failed: '法令を確認できませんでした' },
  sufficiency: { done: '不足を確認しました', failed: '不足を確認できませんでした' },
  retry_search: { done: '言い換えて再検索しました', failed: '再検索できませんでした' },
  doc_page: { done: '資料のページを確認しました', failed: '資料のページを確認できませんでした' },
  clarify: { done: '確認点を整理しました', failed: '確認点を整理できませんでした' },
  synthesize: { done: '回答をまとめました', failed: '回答をまとめられませんでした' },
  verify: { done: '根拠を照合しました', failed: '根拠を照合できませんでした' },
});

/** 行の表示名。実行中はサーバーの labelJa、終わった行は完了形、省略は「…（省略）」、失敗は「…できませんでした」。 */
export function stepRowLabel(row) {
  const labels = STEP_LABELS[row.step];
  if (row.status === 'done') return labels?.done ?? row.labelJa;
  if (row.status === 'failed') return labels?.failed ?? row.labelJa;
  if (row.status === 'skipped') return `${row.labelJa.replace(/中$/u, '')}（省略）`;
  return row.labelJa;
}

const SECTION_KINDS = Object.freeze({ 結論の候補: 'conclusion', '食い違い・不足': 'caution', 次に確認すること: 'todo' });

/**
 * 統一回答を見出し（## ...）ごとに分ける。結論・食い違い・次に確認することの見出しが
 * 1つも無ければ null を返し、呼び出し側は本文をそのまま表示する。
 *
 * @param {string | undefined} markdown
 * @returns {{kind: 'conclusion'|'caution'|'todo'|'normal', heading?: string, body: string}[] | null}
 */
export function splitAnswerSections(markdown) {
  if (typeof markdown !== 'string' || !markdown.trim()) return null;
  const sections = [];
  let current = { kind: 'normal', lines: [] };
  const flush = () => {
    const body = current.lines.join('\n').trim();
    if (current.heading !== undefined || body) sections.push({ kind: current.kind, ...(current.heading !== undefined ? { heading: current.heading } : {}), body });
  };
  for (const line of markdown.split('\n')) {
    const heading = line.match(/^##\s+(.+?)\s*$/u);
    if (heading) {
      flush();
      current = { kind: SECTION_KINDS[heading[1]] ?? 'normal', heading: heading[1], lines: [] };
    } else {
      current.lines.push(line);
    }
  }
  flush();
  return sections.some((section) => section.kind !== 'normal') ? sections : null;
}

/**
 * 聞き返しへの返事を、元の質問につなげた検索用の質問にする（2000 文字まで）。
 * 長すぎるときは元の質問側を切り詰め、利用者が書いた補足を優先して残す。
 */
export function composeClarifyQuestion(original, supplement) {
  const supplementChars = Array.from(String(supplement ?? '').trim());
  const originalChars = Array.from(String(original ?? '').trim());
  const labelLength = Array.from(SUPPLEMENT_LABEL).length;
  const keepSupplement = Math.min(supplementChars.length, MAX_QUESTION_CODEPOINTS - labelLength - Math.min(originalChars.length, 1));
  const keepOriginal = Math.max(0, Math.min(originalChars.length, MAX_QUESTION_CODEPOINTS - labelLength - keepSupplement));
  return `${originalChars.slice(0, keepOriginal).join('')}${SUPPLEMENT_LABEL}${supplementChars.slice(0, keepSupplement).join('')}`;
}

/** 聞き返しが機種・型式を尋ねているか（そうなら機種の選択肢を出す）。 */
export function clarifyAsksModel(result) {
  return /機種|型式/u.test([...(result?.clarifyQuestions ?? []), result?.answerMarkdown ?? ''].join('\n'));
}

/** 質問から読めた機種が、選択中の機種と違うとき {detected, selected} を返す。 */
export function modelMismatch(result, selectedModel, knownModels) {
  const detected = result?.understanding?.modelType;
  if (typeof detected !== 'string' || !selectedModel || detected === selectedModel || !knownModels?.has(detected)) return null;
  return { detected, selected: selectedModel };
}

/** 回答と、番号（[T1] など）つきの出典を、そのまま貼れるプレーンテキストにする。 */
export function buildCopyText(result) {
  const { tech, law, knowhow } = result.sources;
  const lines = [
    ...tech.map((source) => `[${source.ref}] ${source.title}${source.pageNumber ? ` ${source.pageNumber}ページ` : ''}`),
    ...law.map((source) => `[${source.ref}] ${source.lawTitle}${source.provision ? ` ${source.provision}` : ''}${source.effectiveDate ? `（施行日 ${source.effectiveDate}）` : ''}`),
    ...knowhow.used.map((card) => `[${card.ref}] ${card.title} v${card.cardVersion}（未承認・参考）`),
  ];
  const answer = result.answerMarkdown.trim();
  return lines.length ? `${answer}\n\n出典\n${lines.join('\n')}` : answer;
}

/** クリップボードへ書く。許可されない・使えない環境では false を返す。 */
export async function copyText(text, clipboard = globalThis.navigator?.clipboard) {
  try {
    await clipboard.writeText(text);
    return true;
  } catch {
    return false;
  }
}

export const EXAMPLE_QUESTIONS = Object.freeze([
  'AXIEZ-LINKsのドアが開閉時に異音がします。考えられる原因と確認手順を教えてください',
  'メルシティのかご内の照明が点灯しないときに、最初に確認することは何ですか',
  '昇降機の定期点検で、法令上確認が必要な項目を根拠と一緒に教えてください',
]);

const strip = (text) => String(text ?? '').replace(/[\s　、。．，・…「」『』（）()『』:：\-–]+/gu, '').replace(/中$/u, '');

/** 手順の補足が、手順名の言い換えにすぎないか（そうなら表示しない）。 */
export function isRedundantDetail(row) {
  const detail = strip(row.detailJa);
  if (!detail) return true;
  return [row.labelJa, stepRowLabel(row)].some((label) => {
    const base = strip(label);
    return base && (detail === base || detail.includes(base) || base.includes(detail));
  });
}
