'use client';

import { KnowledgeWorkbench } from '@/components/knowledge/KnowledgeWorkbench';

export default function AdminKnowledgePage() {
  if (process.env.NEXT_PUBLIC_ENABLE_KNOWLEDGE_WORKBENCH !== 'true') {
    return (
      <section className="mx-auto max-w-2xl rounded-xl border border-gray-200 bg-white p-6 text-center">
        <h1 className="text-xl font-bold text-gray-900">ノウハウ確認</h1>
        <p className="mt-3 text-sm leading-6 text-gray-600">この画面は現在無効です。利用環境で有効化されるまで、Markdownを読み込みません。</p>
      </section>
    );
  }

  return <KnowledgeWorkbench />;
}
