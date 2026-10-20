import Link from 'next/link';
import { Card } from '@/components/ui/Card';

/** Normal-home entry for the admin-only development workspace. */
export function KnowledgeChatEntry({ isAdmin = false, enabled = false }: { isAdmin?: boolean; enabled?: boolean }) {
  if (!isAdmin || !enabled) return null;

  return (
    <Link href="/knowledge/chat" className="group block h-full">
      <Card variant="default" padding="md" className="h-full border-2 border-transparent transition-all duration-300 group-hover:-translate-y-1 group-hover:border-violet-200 group-hover:shadow-xl">
        <div className="mb-4 flex items-start justify-between gap-3">
          <div className="flex h-14 w-14 items-center justify-center rounded-xl bg-gradient-to-br from-violet-600 to-indigo-700 text-white shadow-md">
            <svg className="h-7 w-7" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
            </svg>
          </div>
          <span className="rounded-full border border-violet-200 bg-violet-100 px-3 py-1.5 text-xs font-semibold text-violet-900">開発中・管理者限定</span>
        </div>
        <h3 className="mb-2 text-xl font-semibold text-gray-900 transition-colors group-hover:text-violet-700">先輩チャット</h3>
        <p className="text-sm leading-relaxed text-gray-600">技術KBや法令KBについて会話形式で質問し、回答と出典を確認できます。</p>
        <div className="mt-4 inline-flex items-center text-sm font-semibold text-violet-700">
          チャットを開く
          <svg className="ml-1 h-4 w-4 transition-transform group-hover:translate-x-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
          </svg>
        </div>
      </Card>
    </Link>
  );
}
