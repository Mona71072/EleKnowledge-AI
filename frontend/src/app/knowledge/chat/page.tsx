'use client';

import Link from 'next/link';
import { KnowledgeSenpaiChat } from '@/components/knowledge/KnowledgeSenpaiChat';

export default function KnowledgeChatPage() {
  const enabled = process.env.NEXT_PUBLIC_ENABLE_KNOWLEDGE_WORKBENCH === 'true';

  return (
    <div className="min-h-screen bg-gray-50">
      <main className="mx-auto max-w-7xl space-y-5 px-4 py-6 sm:px-6 lg:px-8">
        <Link href="/" className="inline-flex text-sm font-semibold text-blue-700 underline underline-offset-2">ホームに戻る</Link>
        {enabled ? <KnowledgeSenpaiChat /> : (
          <section className="rounded-xl border border-gray-200 bg-white p-6">
            <h1 className="text-xl font-bold text-gray-900">工技先輩（開発中）</h1>
            <p className="mt-2 text-sm text-gray-600">この環境では、工技先輩の開発機能は無効です。</p>
          </section>
        )}
      </main>
    </div>
  );
}
