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
      {props.open && <button type="button" aria-label="履歴を閉じる" onClick={props.onClose} className="fixed inset-0 z-40 bg-black/40 md:hidden" />}
      <aside id="senpai-history" aria-label="相談履歴" onKeyDown={(event) => { if (event.key === 'Escape') props.onClose(); }} className={`fixed inset-y-0 left-0 z-50 flex w-64 shrink-0 flex-col border-r border-gray-200 bg-white transition-transform md:static md:z-auto md:visible md:translate-x-0 ${props.open ? 'visible translate-x-0' : 'invisible -translate-x-full'}`}>
        <div className="flex items-center justify-between border-b border-gray-200 px-4 py-3">
          <h2 className="text-sm font-semibold text-gray-800">相談履歴</h2>
          <button type="button" aria-label="履歴メニューを閉じる" onClick={props.onClose} className="rounded p-1 text-gray-600 hover:bg-gray-100 md:hidden">✕</button>
        </div>
        <div className="border-b border-gray-200 p-4">
          <button type="button" onClick={props.onNew} className="w-full rounded-lg bg-gradient-to-r from-violet-600 to-indigo-600 px-4 py-2.5 text-sm font-semibold text-white hover:from-violet-700 hover:to-indigo-700 focus:outline-none focus:ring-2 focus:ring-violet-400">＋ 新しい相談</button>
        </div>
        <nav aria-label="過去の相談" className="min-h-0 flex-1 space-y-1 overflow-y-auto p-2">
          {props.loading && <p role="status" className="px-3 py-4 text-sm text-gray-500">履歴を読み込み中…</p>}
          {props.error && <div role="alert" className="rounded-lg bg-red-50 p-3 text-xs leading-5 text-red-800"><p>{props.error}</p><button type="button" onClick={props.onRetry} className="mt-2 font-semibold underline underline-offset-2">履歴を再取得</button></div>}
          {!props.loading && !props.error && props.entries.length === 0 && <p className="px-3 py-4 text-sm leading-6 text-gray-500">相談履歴はまだありません。質問すると、ここに表示されます。</p>}
          {props.entries.map((entry) => (
            <button key={entry.conversationId} type="button" onClick={() => props.onSelect(entry.conversationId)} aria-current={entry.conversationId === props.selectedId ? 'page' : undefined} className={`block w-full rounded-lg px-3 py-3 text-left transition-colors focus:outline-none focus:ring-2 focus:ring-violet-400 ${entry.conversationId === props.selectedId ? 'border border-violet-200 bg-violet-50' : 'border border-transparent hover:bg-gray-50'}`}>
              <span className="block truncate text-sm font-medium text-gray-800">{entry.title}</span>
              <span className="mt-1 block text-xs text-gray-500">{new Date(entry.lastMessageTime).toLocaleDateString('ja-JP', { timeZone: 'Asia/Tokyo', month: 'numeric', day: 'numeric' })} · {entry.messageCount}件の質問</span>
              <span className="mt-1 block text-[11px] text-gray-400">{entry.pending ? 'この画面の相談・保存未確認' : `保存期限まで約${entry.daysUntilDeletion}日`}</span>
            </button>
          ))}
          {!props.complete && !props.error && <p className="px-3 py-2 text-xs leading-5 text-amber-800">履歴の一部を表示しています。</p>}
        </nav>
        <p className="border-t border-gray-200 p-4 text-xs leading-5 text-gray-500">相談は60日間保存されます。技術・法令の回答を一つの相談として開き直せます。</p>
      </aside>
    </>
  );
}
