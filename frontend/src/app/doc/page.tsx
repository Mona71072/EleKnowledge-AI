'use client';

import { useEffect, useState, Suspense } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import Link from 'next/link';
import { Button } from '@/components/ui/Button';
import { ErrorMessage } from '@/components/ui/ErrorMessage';
import { resolveDocumentUrl, DocumentAuthRequiredError } from '@/lib/documents';

/**
 * 引用文書の中継ページ。
 *
 * ログイン済みなら短命の署名付き URL を取得して実ファイルへ遷移し、未ログインなら
 * ログイン画面へ送って、ログイン後にこのページへ戻す。これにより引用リンクの URL を
 * そのまま共有しても、受け取った人は登録ユーザーでなければ文書を開けない。
 */
function DocContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [error, setError] = useState('');
  const [needsLogin, setNeedsLogin] = useState(false);

  useEffect(() => {
    const uri = searchParams.get('uri');
    // どの回答の引用から開いたか（到達ファネルの計測用。無くても開ける）
    const ctx = { sessionId: searchParams.get('s'), messageId: searchParams.get('m') };
    const ctxQuery = ctx.sessionId && ctx.messageId ? `&s=${encodeURIComponent(ctx.sessionId)}&m=${encodeURIComponent(ctx.messageId)}` : '';
    if (!uri) {
      setError('文書が指定されていません。');
      return;
    }

    let cancelled = false;

    (async () => {
      try {
        const url = await resolveDocumentUrl(uri, ctx);
        if (cancelled) return;
        // PDF のページ指定は署名対象外のフラグメントなので、そのまま引き継ぐ
        const fragment = window.location.hash;
        window.location.replace(fragment ? `${url}${fragment}` : url);
      } catch (err) {
        if (cancelled) return;
        if (err instanceof DocumentAuthRequiredError) {
          setNeedsLogin(true);
          const back = `/doc?uri=${encodeURIComponent(uri)}${ctxQuery}${window.location.hash}`;
          router.replace(`/login?next=${encodeURIComponent(back)}`);
          return;
        }
        console.error('Document resolve error:', err);
        setError(err instanceof Error ? err.message : '文書を開けませんでした。');
      }
    })();

    return () => {
      cancelled = true;
    };
  }, [searchParams, router]);

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-lg shadow-xl p-8 w-full max-w-[28rem] text-center">
        {error ? (
          <>
            <h1 className="text-xl font-bold text-gray-900 mb-4">文書を開けませんでした</h1>
            <ErrorMessage message={error} variant="error" className="mb-6 text-left" />
            <Button
              type="button"
              variant="primary"
              size="md"
              onClick={() => router.push('/chat')}
              className="w-full"
            >
              チャットに戻る
            </Button>
            <p className="text-gray-600 text-sm mt-4">
              <Link href="/" className="text-blue-600 hover:text-blue-700 font-semibold">
                ホームへ
              </Link>
            </p>
          </>
        ) : (
          <>
            <div
              className="mx-auto mb-5 h-9 w-9 animate-spin rounded-full border-2 border-gray-200 border-t-blue-600"
              role="status"
              aria-label="読み込み中"
            />
            <h1 className="text-lg font-semibold text-gray-900">
              {needsLogin ? 'ログイン画面に移動します…' : '文書を開いています…'}
            </h1>
            <p className="text-gray-600 text-sm mt-2">
              {needsLogin
                ? 'この資料の閲覧にはログインが必要です。'
                : 'まもなく資料が表示されます。'}
            </p>
          </>
        )}
      </div>
    </div>
  );
}

export default function DocPage() {
  return (
    <Suspense fallback={<div className="min-h-screen bg-gray-50" />}>
      <DocContent />
    </Suspense>
  );
}
