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
/** 聞き返しへの補足を足すとき、元の質問のうち最低限ここまでは必ず残す（文字数）。 */
export const CLARIFY_ORIGINAL_RESERVE = 1_000;

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

// 統一回答の見出し。新形式（結論 / 根拠と手順 / 確認が必要な点）と、保存済みの旧形式を同じ3つの役割に対応づける。
const LEAD_HEADINGS = new Set(['結論', '結論の候補']);
const EVIDENCE_HEADINGS = new Set(['根拠と手順', '技術資料から', '法令から', 'ノウハウ（未承認・参考）']);
const NOTE_HEADINGS = new Set(['確認が必要な点', '食い違い・不足', '次に確認すること']);

/**
 * 統一回答を「結論（先頭の文）」「根拠と手順」「確認が必要な点」の3つに分ける。
 * 旧形式の「技術資料から / 法令から / ノウハウ」は見出しを出さずに「根拠と手順」へまとめ、
 * 「食い違い・不足」「次に確認すること」は「確認が必要な点」へまとめる。
 * 知っている見出しが1つも無ければ null を返し、呼び出し側は本文をそのまま表示する。
 *
 * @param {string | undefined} markdown
 * @returns {{lead: string, evidence: string, notes: string} | null}
 */
export function structureAnswer(markdown) {
  if (typeof markdown !== 'string' || !markdown.trim()) return null;
  const parts = { lead: [], evidence: [], notes: [] };
  let known = false;
  let target = 'lead';
  let current = [];
  const flush = () => {
    const body = current.join('\n').trim();
    if (body) parts[target].push(body);
    current = [];
  };
  for (const line of markdown.split('\n')) {
    const heading = line.match(/^##\s+(.+?)\s*$/u);
    if (!heading) { current.push(line); continue; }
    flush();
    const title = heading[1];
    if (LEAD_HEADINGS.has(title)) { known = true; target = 'lead'; }
    else if (EVIDENCE_HEADINGS.has(title)) { known = true; target = 'evidence'; }
    else if (NOTE_HEADINGS.has(title)) { known = true; target = 'notes'; }
    else { target = 'evidence'; current.push(line); } // 知らない見出しは根拠の中に見出しごと残す
  }
  flush();
  if (!known) return null;
  return { lead: parts.lead.join('\n\n'), evidence: parts.evidence.join('\n\n'), notes: parts.notes.join('\n\n') };
}

const codepoints = (value) => Array.from(String(value ?? '').trim());
const LABEL_LENGTH = Array.from(SUPPLEMENT_LABEL).length;

/**
 * 聞き返しへの補足に入力できる最大文字数。元の質問のうち先頭 CLARIFY_ORIGINAL_RESERVE 文字までは、
 * 補足がどれだけ長くても必ず残るようにする。
 */
export function clarifySupplementLimit(original) {
  return Math.max(0, MAX_QUESTION_CODEPOINTS - LABEL_LENGTH - Math.min(codepoints(original).length, CLARIFY_ORIGINAL_RESERVE));
}

/** 元の質問と補足をつなぐと 2000 文字を超え、元の質問が一部省略されて検索されるか。 */
export function clarifyOriginalTruncated(original, supplement) {
  return codepoints(original).length + LABEL_LENGTH + codepoints(supplement).length > MAX_QUESTION_CODEPOINTS;
}

/**
 * 聞き返しへの返事を、元の質問につなげた検索用の質問にする（2000 文字まで）。
 * 長すぎるときは元の質問側を切り詰める。元の質問の先頭 CLARIFY_ORIGINAL_RESERVE 文字は残し、
 * 補足は clarifySupplementLimit までを残す。
 */
export function composeClarifyQuestion(original, supplement) {
  const supplementChars = codepoints(supplement);
  const originalChars = codepoints(original);
  const keepSupplement = Math.min(supplementChars.length, clarifySupplementLimit(original));
  const keepOriginal = Math.max(0, Math.min(originalChars.length, MAX_QUESTION_CODEPOINTS - LABEL_LENGTH - keepSupplement));
  return `${originalChars.slice(0, keepOriginal).join('')}${SUPPLEMENT_LABEL}${supplementChars.slice(0, keepSupplement).join('')}`;
}

/** composeClarifyQuestion の逆。保存済みの質問を「元の質問」と「補足」に戻す。補足の形でなければ null。 */
export function splitClarifyQuestion(query) {
  if (typeof query !== 'string') return null;
  const index = query.lastIndexOf(SUPPLEMENT_LABEL);
  if (index <= 0) return null;
  const original = query.slice(0, index).trim();
  const supplement = query.slice(index + SUPPLEMENT_LABEL.length).trim();
  return original && supplement ? { original, supplement } : null;
}

const SETTLED_ANNOUNCEMENTS = Object.freeze({ answer: '回答ができました', clarify: '条件の確認が必要です。入力欄に答えを書いてください', not_found: '該当する情報を確認できませんでした' });

/**
 * スクリーンリーダー向けの通知文。調査が始まったら「調査中です」を1回、終わったら結果を1回だけ。
 * 画面の途中経過（手順・経過秒数）は通知しない。
 * @param {boolean} wasRunning 直前の実行中フラグ
 * @param {{running: boolean, turns: readonly object[]}} snapshot
 * @param {string} current 今の通知文（変化がなければそのまま返す）
 */
export function nextAnnouncement(wasRunning, snapshot, current = '') {
  if (snapshot.running) return wasRunning ? current : '調査中です';
  if (!wasRunning) return current;
  const latest = snapshot.turns.at(-1);
  if (!latest) return '';
  const research = latest.research;
  if (research) {
    if (research.status === 'completed') return SETTLED_ANNOUNCEMENTS[research.result?.kind] ?? '';
    if (research.status === 'failed') return '調査に失敗しました';
    return research.status === 'cancelled' ? '中止しました' : '';
  }
  return [latest.normal, latest.law].some((lane) => lane?.status === 'success') ? SETTLED_ANNOUNCEMENTS.answer : '';
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
