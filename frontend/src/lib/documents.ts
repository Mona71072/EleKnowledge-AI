import { getIdToken, authHeaders } from './auth-helpers';

/**
 * どの回答の引用から文書を開いたか（到達ファネル「資料を開いた」の計測に使う）。
 * 中継ページ /doc → GET /rag/document に &s=&m= で渡り、rag Lambda が該当の assistant 行に
 * documentOpens を加算する。無くても文書は開ける。
 */
export interface DocumentOpenContext {
  sessionId?: string | null;
  messageId?: string | null;
}

function contextQuery(ctx?: DocumentOpenContext): string {
  if (!ctx?.sessionId || !ctx?.messageId) return '';
  return `&s=${encodeURIComponent(ctx.sessionId)}&m=${encodeURIComponent(ctx.messageId)}`;
}

/**
 * 過去データに保存されている S3 署名付き URL（または素の S3 HTTPS URL）を
 * `s3://bucket/key` URI に逆変換する。S3 の URL と判定できなければ null。
 *
 * 対応形式:
 * - virtual-hosted 形式: `https://<bucket>.s3.<region>.amazonaws.com/<key>?X-Amz-...`
 *   （リージョン省略の `https://<bucket>.s3.amazonaws.com/<key>` も含む）
 * - パス形式:            `https://s3.<region>.amazonaws.com/<bucket>/<key>?...`
 *
 * 署名クエリ（X-Amz-*）は捨てる。key は URL エンコードされている場合があるため
 * decodeURIComponent し、デコード済みの文字列で返す（/doc に渡すときに呼び出し側で
 * 一度だけ再エンコードする。二重エンコード禁止）。
 * パースに失敗した場合も throw せず null を返す（安全側に素通し）。
 */
function s3UriFromHttpsUrl(url: string): string | null {
  try {
    const parsed = new URL(url);
    if (parsed.protocol !== 'https:') return null;

    let bucket: string;
    let rawKey: string;

    const virtualHosted = parsed.hostname.match(/^(.+)\.s3[.-]([a-z0-9-]+\.)?amazonaws\.com$/);
    const pathStyle = parsed.hostname.match(/^s3[.-]([a-z0-9-]+\.)?amazonaws\.com$/);

    if (virtualHosted) {
      bucket = virtualHosted[1];
      rawKey = parsed.pathname.replace(/^\//, '');
    } else if (pathStyle) {
      const [first, ...rest] = parsed.pathname.replace(/^\//, '').split('/');
      bucket = first;
      rawKey = rest.join('/');
    } else {
      return null;
    }

    if (!bucket || !rawKey) return null;
    return `s3://${bucket}/${decodeURIComponent(rawKey)}`;
  } catch {
    // URL・パーセントエンコードとして不正な場合。「S3 ではない」扱いにする。
    return null;
  }
}

/**
 * 引用文書へのリンク。
 *
 * バックエンドは署名付き URL ではなく `s3://` URI を返す。認証なしで開ける URL を
 * DynamoDB やチャット履歴に残さないためで、実 URL はユーザーが開く瞬間に
 * `GET /rag/document` から都度発行する。リンク先を中継ページ `/doc` にすることで、
 * URL をそのまま他人に共有しても相手はログインを求められる。
 *
 * 旧データ（#50 以前に発行済みの署名付き URL が保存されている履歴）も、S3 の URL と
 * 判定できれば bucket/key を `s3://` URI に逆変換して同じ中継ページに流す。
 * 保存済み URL は期限切れで AccessDenied になっていたが、都度発行に乗せ替えることで
 * 過去履歴の引用が復活し、DynamoDB に残る発行済み URL が流出しても意味を持たなくなる。
 * S3 と判定できない https URL のみ従来どおりそのまま開かせる。
 */
export function documentHref(sourceUri: string | undefined | null, ctx?: DocumentOpenContext): string | undefined {
  if (!sourceUri) return undefined;
  if (sourceUri.startsWith('s3://')) {
    return `/doc?uri=${encodeURIComponent(sourceUri)}${contextQuery(ctx)}`;
  }
  const legacyS3Uri = s3UriFromHttpsUrl(sourceUri);
  if (legacyS3Uri) {
    return `/doc?uri=${encodeURIComponent(legacyS3Uri)}${contextQuery(ctx)}`;
  }
  return sourceUri;
}

/** PDF のページ指定はフラグメントで渡す（S3 の署名対象にはならない）。 */
export function documentHrefWithPage(
  sourceUri: string | undefined | null,
  pageNumber?: number,
  ctx?: DocumentOpenContext,
): string | undefined {
  const href = documentHref(sourceUri, ctx);
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
export async function resolveDocumentUrl(sourceUri: string, ctx?: DocumentOpenContext): Promise<string> {
  const token = await getIdToken();
  if (!token) throw new DocumentAuthRequiredError();

  const base = process.env.NEXT_PUBLIC_RAG_API_URL || '';
  if (!base) throw new Error('API設定が見つかりません');

  const res = await fetch(`${base}/rag/document?uri=${encodeURIComponent(sourceUri)}${contextQuery(ctx)}`, {
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
