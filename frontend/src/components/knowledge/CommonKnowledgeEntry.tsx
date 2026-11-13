import Link from 'next/link';
import { Card } from '@/components/ui/Card';

/**
 * Normal-home entry for common knowledge. Shown to every signed-in user of an enabled build:
 * what each user may do is decided by the API's grant table, not by Cognito admin membership.
 */
export function CommonKnowledgeEntry({ enabled = false }: { enabled?: boolean }) {
  if (!enabled) return null;

  return (
    <Link href="/admin/knowledge" className="group block h-full">
      <Card variant="default" padding="md" className="h-full border-2 border-transparent transition-all duration-300 group-hover:-translate-y-1 group-hover:border-violet-200 group-hover:shadow-xl">
        <div className="mb-4 flex items-start justify-between gap-3">
          <div className="flex h-14 w-14 items-center justify-center rounded-xl bg-gradient-to-br from-violet-500 to-fuchsia-600 text-white shadow-md">
            <svg className="h-7 w-7" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5s3.332.477 4.5 1.253v13C19.832 18.477 18.246 18 16.5 18s-3.332.477-4.5 1.253" />
            </svg>
          </div>
          <span className="rounded-full border border-violet-200 bg-violet-100 px-3 py-1.5 text-xs font-semibold text-violet-900">検証中</span>
        </div>
        <h3 className="mb-2 text-xl font-semibold text-gray-900 transition-colors group-hover:text-violet-700">ノウハウ・用語と基礎知識</h3>
        <p className="text-sm leading-relaxed text-gray-600">現場の気づきや不明な用語を共有し、確認・承認された知識を読めます。できる操作は割り当てられた権限で決まります。</p>
        <div className="mt-4 inline-flex items-center text-sm font-semibold text-violet-700">
          開く
          <svg className="ml-1 h-4 w-4 transition-transform group-hover:translate-x-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
          </svg>
        </div>
      </Card>
    </Link>
  );
}
