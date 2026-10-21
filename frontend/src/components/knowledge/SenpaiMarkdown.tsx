'use client';

import { Children, isValidElement, type ReactNode } from 'react';
import ReactMarkdown, { type Components } from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { linkResearchRefs, researchRefAnchor } from '@/lib/knowledge-senpai-research-view.mjs';
import { openAncestorDetails } from '@/lib/knowledge-senpai-dom.mjs';

// SECURITY: 回答本文はモデルの出力。生の HTML は react-markdown が描画せず、画像は出さず、
// リンクは同じ画面内の出典アンカーだけを許す（外部へ送る追跡リンクを作らない）。
const REF_ANCHOR = /^#[A-Za-z0-9-]+-ref-([TLK])(\d{1,3})$/u;

// 引用の番号: 技術=技、法令=法、ノウハウ=ノ。色は文字にうっすら付けるだけ。
export const REF_PREFIX: Record<string, string> = { T: '技', L: '法', K: 'ノ' };
// 本文中の番号は、背景なしの軽い上付き文字にする（出典一覧の札は REF_TONES の背景つき）。
const PILL_TEXT: Record<string, string> = { T: 'text-blue-700 hover:text-blue-900', L: 'text-emerald-700 hover:text-emerald-900', K: 'text-violet-700 hover:text-violet-900' };

export const REF_TONES: Record<string, string> = {
  T: 'bg-blue-50 text-blue-700 hover:bg-blue-100',
  L: 'bg-emerald-50 text-emerald-700 hover:bg-emerald-100',
  K: 'bg-violet-50 text-violet-700 hover:bg-violet-100',
};

const TRAILING_PUNCTUATION = /^[。、．，）」』】,.!?！？)]+/u;

function isRefPill(node: ReactNode) {
  return isValidElement<{ href?: unknown }>(node) && typeof node.props.href === 'string' && REF_ANCHOR.test(node.props.href);
}

/**
 * 連続する引用の番号と、そのすぐ後ろの句読点を改行させない1かたまりにする
 * （文末で「。」だけが次の行に落ちるのを防ぐ）。番号の前後の余分な空白も取る。
 */
export function keepRefRunsTogether(children: ReactNode): ReactNode[] {
  const nodes = Children.toArray(children);
  const out: ReactNode[] = [];
  for (let index = 0; index < nodes.length; index += 1) {
    if (!isRefPill(nodes[index])) { out.push(nodes[index]); continue; }
    const run: ReactNode[] = [];
    while (index < nodes.length && (isRefPill(nodes[index]) || (typeof nodes[index] === 'string' && !(nodes[index] as string).trim() && isRefPill(nodes[index + 1])))) {
      if (isRefPill(nodes[index])) run.push(nodes[index]);
      index += 1;
    }
    const next = nodes[index];
    if (typeof next === 'string') {
      const punctuation = TRAILING_PUNCTUATION.exec(next)?.[0] ?? '';
      if (punctuation) { run.push(punctuation); nodes[index] = next.slice(punctuation.length); }
    }
    const previous = out.at(-1);
    if (typeof previous === 'string') out[out.length - 1] = previous.replace(/\s+$/u, '');
    out.push(<span key={`refs-${out.length}`} className="whitespace-nowrap">{run}</span>);
    index -= 1;
  }
  return mutePhrases(out);
}

// 「（ノウハウ・未承認）」は回答のあちこちに出るので、小さく控えめに出す（消さない）。括弧は半角・全角のどちらも。
const MUTED_PHRASE = /([（(]ノウハウ・未承認[）)])/u;

function mutePhrases(nodes: ReactNode[]): ReactNode[] {
  return nodes.flatMap<ReactNode>((node, nodeIndex) => (typeof node !== 'string' || !MUTED_PHRASE.test(node) ? [node] : node.split(MUTED_PHRASE).map((part, index) => (
    index % 2 === 1 ? <span key={`muted-${nodeIndex}-${index}`} className="whitespace-nowrap text-xs font-normal text-gray-500">{part}</span> : part
  )).filter((part) => part !== '')));
}

export type SenpaiMarkdownVariant = 'default' | 'plain' | 'lead';

function makeComponents(refTitles: Readonly<Record<string, string>>, knownRefs: ReadonlySet<string>, anchorPrefix: string): Components {
  return {
    a: ({ href, children }) => {
      const match = typeof href === 'string' ? REF_ANCHOR.exec(href) : null;
      if (!match || typeof href !== 'string') return <span>{children}</span>;
      const refId = `${match[1]}${match[2]}`;
      // 取得結果にある出典で、この回答（相談）のアンカーだけをリンクにする。本文中に書かれた偽の番号は文字のまま出す。
      if (!knownRefs.has(refId) || href !== `#${researchRefAnchor(anchorPrefix, refId)}`) return <span>{children}</span>;
      return (
        <a href={href} title={refTitles[refId]} onClick={() => openAncestorDetails(document.getElementById(href.slice(1)))} className={`relative -top-1 mx-px inline-block rounded px-0.5 align-baseline text-[10px] font-normal leading-none no-underline before:absolute before:-inset-x-1.5 before:-inset-y-3 hover:underline focus:outline-none focus-visible:ring-2 focus-visible:ring-violet-500 ${PILL_TEXT[match[1]]}`}>{`${REF_PREFIX[match[1]]}${match[2]}`}</a>
      );
    },
    img: ({ alt }) => <span>{alt ? `（画像: ${alt}）` : ''}</span>,
    h1: ({ children }) => <h5 className="mt-5 text-sm font-semibold text-gray-900 first:mt-0">{children}</h5>,
    h2: ({ children }) => <h5 className="mt-5 text-sm font-semibold text-gray-900 first:mt-0">{children}</h5>,
    h3: ({ children }) => <h6 className="mt-4 text-sm font-semibold text-gray-900 first:mt-0">{children}</h6>,
    h4: ({ children }) => <h6 className="mt-4 text-sm font-semibold text-gray-900 first:mt-0">{children}</h6>,
    h5: ({ children }) => <h6 className="mt-4 text-sm font-semibold text-gray-900 first:mt-0">{children}</h6>,
    h6: ({ children }) => <h6 className="mt-4 text-sm font-semibold text-gray-900 first:mt-0">{children}</h6>,
    p: ({ children }) => <p className="mt-3 break-words first:mt-0">{keepRefRunsTogether(children)}</p>,
    ul: ({ children }) => <ul className="mt-3 list-disc space-y-2 pl-5 marker:text-gray-400 first:mt-0">{children}</ul>,
    ol: ({ children }) => <ol className="mt-3 list-decimal space-y-2 pl-6 marker:font-medium marker:text-gray-500 first:mt-0">{children}</ol>,
    li: ({ children }) => <li>{keepRefRunsTogether(children)}</li>,
    blockquote: ({ children }) => <blockquote className="mt-2 border-l-2 border-gray-300 pl-3 text-gray-600">{children}</blockquote>,
    pre: ({ children }) => <pre className="mt-2 overflow-x-auto rounded-lg bg-gray-100 p-3 text-xs">{children}</pre>,
    code: ({ children }) => <code className="rounded bg-gray-100 px-1 font-mono text-[13px]">{children}</code>,
    table: ({ children }) => <div className="mt-2 overflow-x-auto"><table className="min-w-full border-collapse text-xs">{children}</table></div>,
    th: ({ children }) => <th className="border border-gray-200 bg-gray-50 px-2 py-1 text-left font-medium">{children}</th>,
    td: ({ children }) => <td className="border border-gray-200 px-2 py-1 align-top">{keepRefRunsTogether(children)}</td>,
  };
}

/** 統一回答の本文。[T1] [L1] [K1] を出典一覧へ飛ぶ小さな番号（技1・法1・ノ1）にして表示する。 */
export function SenpaiMarkdown({ markdown, knownRefs, anchorPrefix, refTitles = {}, variant = 'default', className = '' }: {
  markdown: string;
  knownRefs: ReadonlySet<string>;
  anchorPrefix: string;
  refTitles?: Readonly<Record<string, string>>;
  /** `plain` は小さめの文字で、補足ブロック（確認が必要な点）用。`lead` は結論（先頭の文）用で、少し大きく中くらいの太さ。 */
  variant?: SenpaiMarkdownVariant;
  className?: string;
}) {
  return (
    <div className={`min-w-0 break-words [overflow-wrap:anywhere] ${variant === 'plain' ? 'text-sm leading-6 text-gray-700' : variant === 'lead' ? 'text-[17px] font-medium leading-8 text-gray-900' : 'text-[15px] leading-7 text-gray-900'} ${className}`}>
      <ReactMarkdown remarkPlugins={[remarkGfm]} components={makeComponents(refTitles, knownRefs, anchorPrefix)}>
        {linkResearchRefs(markdown, knownRefs, anchorPrefix)}
      </ReactMarkdown>
    </div>
  );
}
