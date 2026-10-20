import type { SenpaiHistoryEntry } from '@/hooks/useSenpaiHistory';

type Props = {
  open: boolean;
  entries: readonly SenpaiHistoryEntry[];
  selectedId?: string;
  loading: boolean;
  error: string;
  complete: boolean;
  onNew: () => void;
  onSelect: (id: string) => void;
  onClose: () => void;
  onRetry: () => void;
};

export function SenpaiConversationSidebar(props: Props) {
  return (
    <>
      {props.open && <button type="button" aria-label="履歴を閉じる" onClick={props.onClose} className="fixed inset-0 z-40 bg-black/30 md:hidden" />}
      <aside id="senpai-history" aria-label="相談履歴" onKeyDown={(event) => { if (event.key === 'Escape') props.onClose(); }} className={`fixed inset-y-0 left-0 z-50 flex w-72 shrink-0 flex-col bg-gray-50 transition-transform md:static md:z-auto md:visible md:translate-x-0 md:border-r md:border-gray-100 ${props.open ? 'visible translate-x-0' : 'invisible -translate-x-full'}`}>
        <div className="flex items-center justify-between px-3 pb-1 pt-3">
          <h2 className="px-2 text-xs font-medium text-gray-500">相談履歴</h2>
          <button type="button" aria-label="履歴メニューを閉じる" onClick={props.onClose} className="flex h-10 w-10 items-center justify-center rounded-full text-gray-500 hover:bg-gray-100 focus:outline-none focus-visible:ring-2 focus-visible:ring-violet-500 md:hidden">✕</button>
        </div>
        <div className="px-3 pb-2">
          <button type="button" onClick={props.onNew} className="min-h-10 w-full rounded-xl border border-gray-200 bg-white px-3 text-left text-sm text-gray-800 hover:bg-gray-100 focus:outline-none focus-visible:ring-2 focus-visible:ring-violet-500">新しい相談</button>
        </div>
        <nav aria-label="過去の相談" className="min-h-0 flex-1 space-y-0.5 overflow-y-auto px-2 pb-2">
          {props.loading && <p role="status" className="px-3 py-4 text-sm text-gray-500">履歴を読み込み中…</p>}
          {props.error && <div role="alert" className="px-3 py-3 text-xs leading-5 text-red-700"><p>{props.error}</p><button type="button" onClick={props.onRetry} className="mt-2 underline underline-offset-2">履歴を再取得</button></div>}
          {!props.loading && !props.error && props.entries.length === 0 && <p className="px-3 py-4 text-sm leading-6 text-gray-500">相談履歴はまだありません。質問すると、ここに表示されます。</p>}
          {props.entries.map((entry) => (
            <button key={entry.conversationId} type="button" onClick={() => props.onSelect(entry.conversationId)} aria-current={entry.conversationId === props.selectedId ? 'page' : undefined} className={`block min-h-10 w-full rounded-xl px-3 py-2 text-left focus:outline-none focus-visible:ring-2 focus-visible:ring-violet-500 ${entry.conversationId === props.selectedId ? 'bg-gray-200/70' : 'hover:bg-gray-100'}`}>
              <span className="block truncate text-sm text-gray-900">{entry.title}</span>
              <span className="mt-0.5 block text-[11px] text-gray-500">{new Date(entry.lastMessageTime).toLocaleDateString('ja-JP', { timeZone: 'Asia/Tokyo', month: 'numeric', day: 'numeric' })} · {entry.messageCount}件の質問 · {entry.pending ? 'この画面の相談・保存未確認' : `保存期限まで約${entry.daysUntilDeletion}日`}</span>
            </button>
          ))}
          {!props.complete && !props.error && <p className="px-3 py-2 text-xs leading-5 text-amber-700">履歴の一部を表示しています。</p>}
        </nav>
        <p className="px-4 py-3 text-[11px] leading-4 text-gray-400">相談は60日間保存され、再読み込み後も履歴から開き直せます。</p>
      </aside>
    </>
  );
}
