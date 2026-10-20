'use client';

import Link from 'next/link';
import { KnowledgeWorkbench } from '@/components/knowledge/KnowledgeWorkbench';

export default function AdminKnowledgeResearchPage() {
  if (process.env.NEXT_PUBLIC_ENABLE_KNOWLEDGE_WORKBENCH !== 'true') {
    return (
      <section className="mx-auto max-w-2xl rounded-xl border border-gray-200 bg-white p-6 text-center">
        <span className="rounded-full bg-violet-100 px-2.5 py-1 text-xs font-semibold text-violet-900">開発中</span>
        <h1 className="mt-3 text-xl font-bold text-gray-900">工技先輩</h1>
        <p className="mt-3 text-sm leading-6 text-gray-600">この画面は現在無効です。有効化されるまで、質問やMarkdownを読み込みません。</p>
        <Link href="/admin/knowledge" className="mt-4 inline-flex text-sm font-semibold text-blue-700 underline underline-offset-2">ノウハウ確認へ戻る</Link>
      </section>
    );
  }

  return (
    <div className="space-y-4">
      <Link href="/admin/knowledge" className="inline-flex text-sm font-semibold text-blue-700 underline underline-offset-2">ノウハウ確認へ戻る</Link>
      <KnowledgeWorkbench research />
    </div>
  );
}
