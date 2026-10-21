'use client';

import { useState } from 'react';
import { getIdToken } from '@/lib/auth-helpers';
import { inputHash, requestKnowledge, validateConnection } from '@/lib/common-knowledge.mjs';

type Candidate = {
  candidateId: string; candidateRevision: number; candidateType: string; state: string;
  context?: string; summary?: string; targetLinks?: string[];
  targetKnowledgeId?: string; targetRevision?: number;
};
type Version = { bundleHash: string; rawSha256: string; approvalId?: string; status: string; kind: string };
type Card = {
  knowledgeId: string; workingRevision: number; markdown: string;
  versions: Record<string, Version>; review?: { reviewRequestId: string; bundleHash: string } | null;
};
type Saved = { knowledgeId: string; workingRevision: number; candidateRevision: number; bundleHash: string; gitCommit: string };
type Manifest = { generation: number; active: string | null };
type Published = { knowledgeId: string; workingRevision: number; rawSha256: string; markdown: string; generation: number };
const STATE_LABELS: Record<string, string> = {
  unconfirmed: '未確認', in_review: '編集中', awaiting_review: '技術確認待ち',
  reflected: '正本反映済み', held: '保留', rejected: '不採用',
};
const ACTORS = { contributor: '投稿本人', viewer: 'admin閲覧のみ', editor: '編集担当',
  reviewer: '技術確認者', publisher: '公開担当', reader: 'RAG読者', agent: '開発エージェント' };
const INPUT_CLASS = 'w-full rounded border border-gray-300 bg-white p-2 text-sm text-gray-900';
const BUTTON_CLASS = 'rounded border border-violet-300 px-3 py-2 text-sm font-medium text-violet-900 disabled:opacity-40';

/** Shared inbox with server authorization and separately persisted editing/review/publication. */
export function CommonKnowledgeInbox() {
  const synthetic = process.env.NEXT_PUBLIC_COMMON_KNOWLEDGE_SYNTHETIC === 'true';
  const [actor, setActor] = useState('viewer');
  const [state, setState] = useState('unconfirmed');
  const [items, setItems] = useState<Candidate[]>([]);
  const [cursor, setCursor] = useState<string | null>(null);
  const [selected, setSelected] = useState<Candidate | null>(null);
  const [card, setCard] = useState<Card | null>(null);
  const [cardId, setCardId] = useState('KH-SYN-A');
  const [markdown, setMarkdown] = useState('# 合成の用語Z\n\n架空機種A・改訂1の説明。実資料ではありません。\n');
  const [kind, setKind] = useState('term_foundation');
  const [context, setContext] = useState('架空機種Aで用語Zの意味を確認したい。実資料ではない合成投稿。');
  const [candidateType, setCandidateType] = useState('unknown_term');
  const [correctionTarget, setCorrectionTarget] = useState('KH-SYN-PREVIOUS');
  const [correctionRevision, setCorrectionRevision] = useState(1);
  const [confirmed, setConfirmed] = useState(false);
  const [reason, setReason] = useState('合成I1の担当者確認');
  const [generation, setGeneration] = useState(0);
  const [expiresAt] = useState(() => Math.floor(Date.now() / 1000) + 3600);
  const [message, setMessage] = useState('');
  const [busy, setBusy] = useState(false);
  const [published, setPublished] = useState<Published | null>(null);
  const [receipt, setReceipt] = useState<Saved | null>(null);
  const [pending, setPending] = useState<{ operationId: string; status: string }[]>([]);

  async function api<T>(path: string, method = 'GET', body?: unknown, revision?: number): Promise<T> {
    const baseUrl = validateConnection({
      baseUrl: process.env.NEXT_PUBLIC_COMMON_KNOWLEDGE_API_URL || '', synthetic,
      development: process.env.NODE_ENV === 'development', hostname: window.location.hostname,
    });
    const token = synthetic ? `synthetic-${actor}` : await getIdToken();
    if (!token) throw new Error('再ログインしてください。');
    return requestKnowledge<T>({ baseUrl, token, actor: synthetic ? actor : 'authenticated', path, method, body, revision });
  }

  async function perform(action: () => Promise<void>) {
    setBusy(true); setMessage(''); setPublished(null);
    try { await action(); } catch (error) {
      setMessage(error instanceof Error ? error.message : '操作できませんでした。');
    } finally { setBusy(false); }
  }

  async function list(next = false) {
    const scope = actor === 'contributor' ? 'mine' : 'inbox';
    const result = await api<{ items: Candidate[]; cursor: string | null }>(
      `/contributions?scope=${scope}&state=${state}${next && cursor ? `&cursor=${encodeURIComponent(cursor)}` : ''}`);
    setItems(result.items); setCursor(result.cursor);
  }

  async function load(identifier: string) {
    const result = await api<Candidate>(`/contributions/${identifier}`);
    setSelected(result); setCard(null); setReceipt(null);
    const target = result.targetLinks?.[0] || result.targetKnowledgeId;
    if (target) {
      const loaded = await api<Card>(`/cards/${target}`);
      setCard(loaded); setCardId(target); setMarkdown(loaded.markdown);
      setKind(loaded.versions[String(loaded.workingRevision)].kind);
    }
  }

  async function transition(next: string) {
    if (!selected) return;
    const result = await api<Candidate>(`/contributions/${selected.candidateId}`, 'PATCH',
      { state: next, reason, ...(next === 'held' ? { resumeCondition: reason } : {}) }, selected.candidateRevision);
    setSelected({ ...selected, ...result }); setMessage('候補の状態を保存しました。');
  }

  async function submit() {
    if (!confirmed) throw new Error('共有する最小文脈を確認してください。');
    // I1's synthetic permission is explicitly server-issued; no real permission is inferred.
    if (!synthetic) throw new Error('実データの共有許可設定は受入待ちです。');
    const body = { candidateType, originRef: { id: `synthetic-${candidateType}-${await inputHash(context)}`, revision: 1 },
      summary: '合成の用語Z・架空機種A', context, domain: 'synthetic', audience: 'synthetic',
      permissionId: 'synthetic-sharing', ...(candidateType === 'unknown_term' ? { term: '用語Z' } : {}),
      ...(candidateType === 'correction' ? { targetKnowledgeId: correctionTarget, targetRevision: correctionRevision } : {}) };
    const result = await api<Candidate>('/contributions', 'POST', { ...body, confirmedHash: await inputHash(body) });
    setSelected(result); setCard(null); setReceipt(null);
    setMessage(`投函を保存しました: ${result.candidateId}`);
  }

  async function save() {
    if (!selected) return;
    if (!synthetic) throw new Error('実データの根拠・保持・共有範囲設定は受入待ちです。');
    const result = await api<Saved>(`/cards/${cardId}/draft`, 'PUT', {
      candidateId: selected.candidateId, candidateRevision: selected.candidateRevision, kind, markdown,
      applicability: '架空機種A・改訂1。他機種には適用しない。',
      sourceRefs: [{ id: 'SYN-ORIGINAL', version: '1', locator: 'p.1', sha256: 'a'.repeat(64),
        claimType: 'source_verified', verified: true }], domain: 'synthetic', audience: 'synthetic',
      expiresAt, unknowns: [],
    }, card?.workingRevision ?? 0);
    setReceipt(result);
    setSelected({ ...selected, candidateRevision: result.candidateRevision, state: 'in_review' });
    setCard(await api<Card>(`/cards/${cardId}`));
    setMessage('Git作業版の保存が完了しました。技術承認と公開は別操作です。');
  }

  async function requestReview() {
    if (!card) return;
    const version = card.versions[String(card.workingRevision)];
    const review = await api<NonNullable<Card['review']>>(`/cards/${cardId}/review-requests`, 'POST',
      { bundleHash: version.bundleHash, reason }, card.workingRevision);
    setCard({ ...card, review });
    if (selected) setSelected({ ...selected, state: 'awaiting_review', candidateRevision: selected.candidateRevision + 1 });
    setMessage('特定版を技術確認待ちにしました。別の確認者が内容を確認してください。');
  }

  async function decide(decision: string) {
    if (!card?.review) return;
    await api(`/cards/${cardId}/decisions`, 'POST', {
      reviewRequestId: card.review.reviewRequestId, bundleHash: card.review.bundleHash, reason, decision,
    }, card.workingRevision);
    if (selected) await load(selected.candidateId);
    setMessage(decision === 'approve' ? '技術承認と正本反映が完了しました。公開はまだです。' : '編集担当へ差し戻しました。');
  }

  async function publication(withdraw: boolean) {
    if (!card) return;
    const version = card.versions[String(card.workingRevision)];
    const result = await api<Manifest>(`/cards/${cardId}/${withdraw ? 'withdraw' : 'publish'}`, 'POST',
      withdraw ? { reason } : { reason, revision: card.workingRevision, approvalId: version.approvalId }, generation);
    setGeneration(result.generation);
    setMessage(withdraw ? '公開を停止しました。次の参照から利用できません。' : '承認した特定版を公開しました。');
  }

  const canEdit = !synthetic || actor === 'editor';
  const canReview = !synthetic || actor === 'reviewer';
  const canPublish = !synthetic || actor === 'publisher';

  return <section aria-label="共通知識インボックス" className="space-y-5 rounded-xl border border-violet-200 bg-white p-5">
    <div><h2 className="text-xl font-bold">ノウハウ・用語と基礎知識</h2>
      <p className="mt-2 text-sm text-gray-600">共有された候補を編集し、特定版の技術確認と公開を別々に行います。</p>
      {synthetic && <p className="mt-2 text-sm text-amber-900">合成I1試行。架空の人物・原本・共有許可だけを使用します。実資料は入力しないでください。</p>}
    </div>
    {synthetic && <label className="block text-sm">合成の操作者<select className={INPUT_CLASS} value={actor} onChange={(event) => {
      setActor(event.target.value); setPublished(null); setMessage(''); setItems([]); setCursor(null); setPending([]);
    }}>{Object.entries(ACTORS).map(([value, label]) => <option key={value} value={value}>{label}</option>)}</select></label>}
    <fieldset disabled={busy} className="space-y-4 disabled:opacity-60">
      {synthetic && actor === 'contributor' && <div className="space-y-2 rounded border p-3">
        <h3 className="font-semibold">共有する候補を投函</h3>
        <label className="block text-sm">候補の種類<select className={INPUT_CLASS} value={candidateType} onChange={(event) => { setCandidateType(event.target.value); setConfirmed(false); }}>
          <option value="field_report">現場報告</option><option value="unknown_term">不明用語</option><option value="correction">訂正</option>
        </select></label>
        {candidateType === 'correction' && <><label className="block text-sm">訂正対象の単元ID<input className={INPUT_CLASS} value={correctionTarget} onChange={(event) => { setCorrectionTarget(event.target.value); setConfirmed(false); }} /></label>
          <label className="block text-sm">訂正対象の承認版<input type="number" className={INPUT_CLASS} min={1} value={correctionRevision} onChange={(event) => { setCorrectionRevision(Number(event.target.value)); setConfirmed(false); }} /></label></>}
        <label className="block text-sm">共有する最小文脈<textarea className={INPUT_CLASS} maxLength={2000} value={context} onChange={(event) => { setContext(event.target.value); setConfirmed(false); }} /></label>
        <label className="block text-sm"><input type="checkbox" checked={confirmed} onChange={(event) => setConfirmed(event.target.checked)} /> この文面を共有候補として保存することを確認しました</label>
        <button className={BUTTON_CLASS} onClick={() => void perform(submit)}>明示して投函</button>
      </div>}
      <div className="flex flex-wrap items-end gap-2">
        <label className="text-sm">候補の状態<select className={INPUT_CLASS} value={state} onChange={(event) => { setState(event.target.value); setCursor(null); }}>
          {Object.entries(STATE_LABELS).map(([value, label]) => <option key={value} value={value}>{label}</option>)}
        </select></label>
        <button className={BUTTON_CLASS} onClick={() => void perform(() => list())}>共有一覧を取得</button>
        {cursor && <button className={BUTTON_CLASS} onClick={() => void perform(() => list(true))}>次のページ</button>}
      </div>
      <ul className="space-y-2">{items.map((item) => <li key={item.candidateId}>
        <button className="text-sm text-violet-900 underline" onClick={() => void perform(() => load(item.candidateId))}>{item.candidateType} · {STATE_LABELS[item.state]} · {item.candidateId}</button>
      </li>)}</ul>
      {selected && <div className="space-y-3 rounded border p-4">
        <h3 className="font-semibold">選択した候補 · {STATE_LABELS[selected.state]} · 第{selected.candidateRevision}版</h3>
        <p className="whitespace-pre-wrap text-sm">{selected.summary}<br />{selected.context}</p>
        <label className="block text-sm">操作の理由<input className={INPUT_CLASS} value={reason} maxLength={2000} onChange={(event) => setReason(event.target.value)} /></label>
        <div className="flex flex-wrap gap-2">
          <button className={BUTTON_CLASS} onClick={() => void perform(() => load(selected.candidateId))}>最新状態を再取得</button>
          {canEdit && <><button className={BUTTON_CLASS} onClick={() => void perform(() => transition('in_review'))}>編集を引き受ける／再開</button>
            <button className={BUTTON_CLASS} onClick={() => void perform(() => transition('held'))}>理由を付けて保留</button></>}
        </div>
        <label className="block text-sm">単元ID<input className={INPUT_CLASS} value={cardId} disabled={!!card} onChange={(event) => setCardId(event.target.value)} /></label>
        <label className="block text-sm">分類<select className={INPUT_CLASS} value={kind} disabled={!canEdit} onChange={(event) => setKind(event.target.value)}>
          <option value="term_foundation">用語・基礎知識</option><option value="case_summary">事例</option><option value="practice_guide">実務ガイド</option>
        </select></label>
        <label className="block text-sm">単元のMarkdown<textarea className={`${INPUT_CLASS} min-h-40 font-mono`} value={markdown} readOnly={!canEdit} onChange={(event) => setMarkdown(event.target.value)} /></label>
        {card && <p className="break-all text-xs text-gray-600">作業版 {card.workingRevision} · {card.versions[String(card.workingRevision)].status} · 承認束 {card.versions[String(card.workingRevision)].bundleHash}</p>}
        {receipt && <p className="break-all text-xs">Git保存済み: {receipt.gitCommit}</p>}
        <div className="flex flex-wrap gap-2">
          {canEdit && <><button className={BUTTON_CLASS} onClick={() => void perform(save)}>Git作業版へ保存</button>
            <button className={BUTTON_CLASS} disabled={!card} onClick={() => void perform(requestReview)}>この版の技術確認を依頼</button></>}
          {canReview && <><button className={BUTTON_CLASS} disabled={!card?.review} onClick={() => void perform(() => decide('approve'))}>この版を技術承認・正本反映</button>
            <button className={BUTTON_CLASS} disabled={!card?.review} onClick={() => void perform(() => decide('return'))}>差し戻す</button></>}
          {canPublish && <><label className="text-sm">確認した公開世代<input type="number" min={0} className={INPUT_CLASS} value={generation} onChange={(event) => setGeneration(Number(event.target.value))} /></label>
            <button className={BUTTON_CLASS} disabled={!card} onClick={() => void perform(() => publication(false))}>承認版を公開</button>
            <button className={BUTTON_CLASS} disabled={!card} onClick={() => void perform(() => publication(true))}>公開を停止</button></>}
        </div>
      </div>}
      <div className="space-y-2 rounded border p-3">
        <h3 className="font-semibold">未完了操作の復旧</h3>
        <p className="text-sm text-gray-600">応答を確認できなかった操作は、同じ操作者で取得し、保存済みの入力から再開できます。</p>
        <button className={BUTTON_CLASS} onClick={() => void perform(async () => {
          const result = await api<{ items: { operationId: string; status: string }[] }>('/operations');
          setPending(result.items);
        })}>自分の未完了操作を取得</button>
        {pending.map((operation) => <div key={operation.operationId} className="text-sm">
          {operation.operationId} · {operation.status}
          <button className={BUTTON_CLASS} onClick={() => void perform(async () => {
            await api(`/operations/${operation.operationId}/retry`, 'POST', {});
            setPending(pending.filter((item) => item.operationId !== operation.operationId));
            if (selected) await load(selected.candidateId);
            setMessage('操作を復旧しました。最新状態を確認してください。');
          })}>同じ操作IDから再開</button>
        </div>)}
      </div>
      <div className="space-y-2 rounded border p-3">
        <h3 className="font-semibold">両AIと共通の公開版確認</h3>
        <label className="block text-sm">読む単元ID<input className={INPUT_CLASS} value={cardId} onChange={(event) => setCardId(event.target.value)} /></label>
        <button className={BUTTON_CLASS} onClick={() => void perform(async () => {
          const result = await api<Published>(`/published/${cardId}`); setPublished(result); setGeneration(result.generation);
        })}>公開版を毎回確認して読む</button>
        {published && <div><p className="break-all text-xs">{published.knowledgeId} · 第{published.workingRevision}版 · {published.rawSha256}</p><pre className="whitespace-pre-wrap text-sm">{published.markdown}</pre></div>}
      </div>
    </fieldset>
    <p role="status" aria-live="polite" className="text-sm">{busy ? '保存先へ確認中…' : message}</p>
  </section>;
}
