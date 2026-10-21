import Link from 'next/link';
import { DotsIcon, MenuIcon, PlusIcon } from './SenpaiIcons';

const iconButton = 'flex h-10 w-10 items-center justify-center rounded-full text-gray-600 hover:bg-gray-100 hover:text-gray-900 focus:outline-none focus-visible:ring-2 focus-visible:ring-violet-500 disabled:cursor-not-allowed disabled:opacity-40';
const menuItem = 'block w-full rounded-lg px-3 py-2.5 text-left text-sm text-gray-800 hover:bg-gray-100 focus:outline-none focus-visible:ring-2 focus-visible:ring-violet-500';

/** 細いヘッダー。左にタイトル、右に履歴（モバイル）・新しい相談・⋯メニュー。 */
export function SenpaiChatHeader({ sidebarOpen, onOpenSidebar, onNewChat, newChatDisabled, showDeveloperToggle, developerView, onToggleDeveloperView, menuOpen, onMenuOpenChange }: {
  sidebarOpen: boolean;
  onOpenSidebar: () => void;
  onNewChat: () => void;
  newChatDisabled: boolean;
  showDeveloperToggle: boolean;
  developerView: boolean;
  onToggleDeveloperView: () => void;
  /** ⋯メニューの開閉。外側のクリック・Escape・項目を選んだ後に閉じるのは呼び出し側。 */
  menuOpen?: boolean;
  onMenuOpenChange?: (open: boolean) => void;
}) {
  const close = () => onMenuOpenChange?.(false);
  return (
    <header className="flex h-12 shrink-0 items-center justify-between px-2 sm:px-4">
      <div className="flex min-w-0 items-center gap-1">
        <button type="button" aria-label="履歴を開く" aria-controls="senpai-history" aria-expanded={sidebarOpen} onClick={onOpenSidebar} className={`${iconButton} md:hidden`}><MenuIcon /></button>
        <h1 className="px-2 text-[15px] font-semibold text-gray-900">先輩チャット</h1>
        <span className="text-xs text-gray-500">開発中</span>
      </div>
      <div className="flex items-center gap-1">
        <button type="button" aria-label="新しい相談を始める" title="新しい相談" onClick={onNewChat} disabled={newChatDisabled} className={iconButton}><PlusIcon /></button>
        <details data-senpai-menu="" open={menuOpen} onToggle={(event) => onMenuOpenChange?.(event.currentTarget.open)} className="relative">
          <summary aria-label="メニュー" title="メニュー" className={`${iconButton} cursor-pointer list-none [&::-webkit-details-marker]:hidden`}><DotsIcon /></summary>
          <div className="absolute right-0 z-30 mt-1 w-56 rounded-2xl border border-gray-200 bg-white p-1 shadow-lg">
            <Link href="/admin/knowledge/research" aria-label="ノウハウの確認・編集" onClick={close} className={menuItem}>ノウハウの確認・編集</Link>
            {showDeveloperToggle && (
              <button type="button" aria-pressed={developerView} onClick={() => { onToggleDeveloperView(); close(); }} className={menuItem}>
                開発者表示<span className="ml-2 text-xs text-gray-500">{developerView ? 'オン' : 'オフ'}</span>
              </button>
            )}
            <Link href="/" aria-label="ホームへ戻る" onClick={close} className={menuItem}>ホームへ戻る</Link>
          </div>
        </details>
      </div>
    </header>
  );
}
