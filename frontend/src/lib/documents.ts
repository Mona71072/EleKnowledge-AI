import { getIdToken, authHeaders } from './auth-helpers';

/**
 * 引用文書へのリンク。
 *
 * バックエンドは署名付き URL ではなく `s3://` URI を返す。認証なしで開ける URL を
 * DynamoDB やチャット履歴に残さないためで、実 URL はユーザーが開く瞬間に
 * `GET /rag/document` から都度発行する。リンク先を中継ページ `/doc` にすることで、
 * URL をそのまま他人に共有しても相手はログインを求められる。
 */
export function documentHref(sourceUri: string | undefined | null): string | undefined {
  if (!sourceUri) return undefined;
  // 旧データ（署名付き URL が保存済みの履歴）はそのまま開かせる。
  // 期限切れなら S3 側がエラーを返す。
  if (!sourceUri.startsWith('s3://')) return sourceUri;
  return `/doc?uri=${encodeURIComponent(sourceUri)}`;
}

/** PDF のページ指定はフラグメントで渡す（S3 の署名対象にはならない）。 */
export function documentHrefWithPage(
  sourceUri: string | undefined | null,
  pageNumber?: number,
): string | undefined {
  const href = documentHref(sourceUri);
  if (!href || !pageNumber) return href;
  return `${href}#page=${pageNumber}`;
}

export class DocumentAuthRequiredError extends Error {
  constructor() {
    super('ログインが必要です');
    this.name = 'DocumentAuthRequiredError';
  }
}

/**
 * `s3://` URI を、実際に開ける短命の署名付き URL に解決する。
 * 未ログインなら DocumentAuthRequiredError を投げる。
 */
export async function resolveDocumentUrl(sourceUri: string): Promise<string> {
  const token = await getIdToken();
  if (!token) throw new DocumentAuthRequiredError();

  const base = process.env.NEXT_PUBLIC_RAG_API_URL || '';
  if (!base) throw new Error('API設定が見つかりません');

  const res = await fetch(`${base}/rag/document?uri=${encodeURIComponent(sourceUri)}`, {
    headers: authHeaders(token),
  });

  if (res.status === 401 || res.status === 403) throw new DocumentAuthRequiredError();
  if (!res.ok) {
    let message = `文書を開けませんでした (${res.status})`;
    try {
      const data = await res.json();
      message = data.message || data.error || message;
    } catch {
      /* レスポンスが JSON でない場合は既定のメッセージを使う */
    }
    throw new Error(message);
  }

  const data = await res.json();
  if (!data.url) throw new Error('文書のURLを取得できませんでした');
  return data.url as string;
}
