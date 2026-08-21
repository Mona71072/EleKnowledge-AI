import type { FailureItem, FeedbackReason } from './chat-failures';

/** しきい値以上で改善提案カードを出す（試用初期） */
export const IMPROVEMENT_PROPOSAL_THRESHOLD = 3;

export type ReasonFilterKey =
  | 'all'
  | 'reason_omitted'
  | FeedbackReason;

export interface FailureSignalSummary {
  total: number;
  badCount: number;
  notFoundCount: number;
  reasonCounts: Record<string, number>;
  badWithoutReason: number;
}

export type ProposalRuleId =
  | 'wrong_doc'
  | 'unresolved'
  | 'bad_answer'
  | 'not_found'
  | 'reason_omitted';

export interface ImprovementProposal {
  id: ProposalRuleId;
  title: string;
  count: number;
  body: string;
  actions: string[];
  owner: string;
  /** 一覧を絞るときの reason キー（not_found は kind） */
  filterKind?: 'bad' | 'not_found';
  filterReason?: ReasonFilterKey;
}

const PROPOSAL_TEMPLATES: Record<
  ProposalRuleId,
  {
    title: string;
    body: string;
    actions: string[];
    owner: string;
    filterKind?: 'bad' | 'not_found';
    filterReason?: ReasonFilterKey;
  }
> = {
  wrong_doc: {
    title: '資料候補の精度',
    body: '候補資料が別物になっています。検索・フィルタ・機種一致を見直してください。',
    actions: [
      'failures から golden 候補を 3 件追加し run_retrieve_eval.py で確認',
      'ABBREV_MAP・カテゴリ過絞り・model_type 空欄を確認',
      '改善時のみ phase2 sam deploy（itai）',
    ],
    owner: 'mona → 必要なら SAM（itai）',
    filterReason: 'wrong_doc',
  },
  unresolved: {
    title: '解決失敗の振り分け',
    body:
      '資料は出た／見たが判断材料にならなかった報告です。資料が悪いと決め打ちせず、件ごとに人手で振り分けてください。',
    actions: [
      '検索ミス／snippet 弱い／作文／聞き返し不足／KB 欠落 のどれかを確認',
      '振り分け後に golden 化またはプロンプト・KB 作業へ',
      'KB 再同期が必要なら itai に依頼',
    ],
    owner: 'mona（KB 作業は itai）',
    filterReason: 'unresolved',
  },
  bad_answer: {
    title: '作文品質',
    body: '回答文の断定・誤要約が問題です。弱ゲートとプロンプトを確認してください。',
    actions: [
      '該当セッションをチャットで開き引用と本文を照合',
      '節目で第2層 Faithfulness（BYOI）を検討',
    ],
    owner: 'mona',
    filterReason: 'bad_answer',
  },
  not_found: {
    title: 'ヒット不足',
    body: '弱い検索で not_found が多いです。本命優先 retrieve・略語・カテゴリ過絞りを確認してください。',
    actions: [
      'カテゴリ未指定・機種フィルタの有無を failures で確認',
      'golden に not_found タグ付きで追加',
    ],
    owner: 'mona',
    filterKind: 'not_found',
  },
  reason_omitted: {
    title: '理由採取率',
    body: '👎 はあるが理由チップ未選択が多いです。必須化はせず、現場に理由選択を促してください。',
    actions: [
      'チャット UI の 👎 理由が見えているか確認',
      '重要案件は failures で個別に読む',
    ],
    owner: 'mona',
    filterReason: 'reason_omitted',
  },
};

export function aggregateFailureSignals(items: FailureItem[]): FailureSignalSummary {
  const reasonCounts: Record<string, number> = {};
  let badCount = 0;
  let notFoundCount = 0;
  let badWithoutReason = 0;

  for (const item of items) {
    if (item.signals.includes('not_found') || item.responseType === 'not_found') {
      notFoundCount += 1;
    }
    if (item.feedback === 'bad' || item.signals.includes('bad')) {
      badCount += 1;
      const reason = item.feedbackReason;
      if (reason) {
        reasonCounts[reason] = (reasonCounts[reason] || 0) + 1;
      } else {
        badWithoutReason += 1;
      }
    }
  }

  return {
    total: items.length,
    badCount,
    notFoundCount,
    reasonCounts,
    badWithoutReason,
  };
}

export function buildImprovementProposals(
  summary: FailureSignalSummary,
  threshold = IMPROVEMENT_PROPOSAL_THRESHOLD,
): ImprovementProposal[] {
  const proposals: ImprovementProposal[] = [];

  const add = (id: ProposalRuleId, count: number) => {
    if (count < threshold) return;
    const tmpl = PROPOSAL_TEMPLATES[id];
    proposals.push({
      id,
      count,
      title: tmpl.title,
      body: tmpl.body,
      actions: tmpl.actions,
      owner: tmpl.owner,
      filterKind: tmpl.filterKind,
      filterReason: tmpl.filterReason,
    });
  };

  add('wrong_doc', summary.reasonCounts.wrong_doc || 0);
  add('unresolved', summary.reasonCounts.unresolved || 0);
  add('bad_answer', summary.reasonCounts.bad_answer || 0);
  add('not_found', summary.notFoundCount);
  add('reason_omitted', summary.badWithoutReason);

  return proposals;
}

export function filterFailureItems(
  items: FailureItem[],
  kind: 'all' | 'bad' | 'not_found',
  reasonFilter: ReasonFilterKey,
): FailureItem[] {
  let filtered = items;

  if (kind === 'bad') {
    filtered = filtered.filter(
      (i) => i.feedback === 'bad' || i.signals.includes('bad'),
    );
  } else if (kind === 'not_found') {
    filtered = filtered.filter(
      (i) => i.responseType === 'not_found' || i.signals.includes('not_found'),
    );
  }

  if (reasonFilter === 'all') return filtered;

  if (reasonFilter === 'reason_omitted') {
    return filtered.filter(
      (i) =>
        (i.feedback === 'bad' || i.signals.includes('bad')) && !i.feedbackReason,
    );
  }

  return filtered.filter((i) => i.feedbackReason === reasonFilter);
}
