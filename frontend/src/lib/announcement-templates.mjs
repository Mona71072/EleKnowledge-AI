// お知らせのテンプレート（設計 docs/design-2026-09-10-dashboard-v2.md §10.3）。
// 文面はランブックの案内文と同じ言い回しにする。{{ }} は公開前に埋める穴。
// React 依存なしの純粋データ + 関数（node --test で検証）。

export const ANNOUNCEMENT_TEMPLATES = [
  {
    key: 'incident',
    name: '障害中（回答が返らない）',
    type: 'notice',
    severity: 'critical',
    pinned: true,
    showInChat: true,
    when: 'ダッシュボード「いま」が P1 のとき',
    title: '回答が返らない事象が発生しています（対応中）',
    body:
      '{{時刻}} ごろから、質問への回答が返らない・エラーになる事象が発生しています。\n\n' +
      '- 現在、原因の切り分けと復旧作業を行っています\n' +
      '- 復旧見込み: {{復旧見込み}}\n' +
      '- 復旧しましたら本お知らせを更新します\n\n' +
      'お急ぎの場合は、資料は従来の共有フォルダから直接ご参照ください。',
  },
  {
    key: 'recovered',
    name: '復旧',
    type: 'notice',
    severity: 'info',
    pinned: false,
    showInChat: true,
    when: 'OK メールを見たら。障害告知を同時に表示終了',
    title: '回答が返らない事象は復旧しました',
    body:
      '{{復旧時刻}} に復旧を確認しました。ご迷惑をおかけしました。\n\n' +
      '- 発生: {{発生時刻}} 〜 {{復旧時刻}}\n' +
      '- 影響: 質問への回答がエラーになる\n' +
      '- 原因と再発防止は改めてお知らせします',
  },
  {
    key: 'signup_stop',
    name: '新規登録の受付を一時停止',
    type: 'notice',
    severity: 'warning',
    pinned: true,
    showInChat: false,
    when: 'P2-cognito-signups-40 が鳴ったら（ランブック §5.6）',
    title: '本日の新規登録の受付を一時停止しています',
    body:
      '確認メールの 1 日あたりの送信数が上限に近づいたため、本日の新規登録の受付を一時停止しています。\n\n' +
      '- 明日 9 時以降に再開します\n' +
      '- すでに登録済みの方はそのままご利用いただけます',
  },
  {
    key: 'mail_limit',
    name: 'メール上限に達した方へ',
    type: 'notice',
    severity: 'warning',
    pinned: false,
    showInChat: false,
    when: 'P1-cognito-email-errors が鳴ったら（ランブック §5.6）',
    title: '確認メールが届かなかった方へ',
    body:
      '本日のメール送信数が上限に達したため、確認コードのメールが届かない場合があります。\n\n' +
      '- 明日 9 時以降に、確認画面の「確認コードを再送信」からお試しください\n' +
      '- 「登録が完了していません」と表示された方だけ、新規登録をやり直してください',
  },
  {
    key: 'maintenance',
    name: 'メンテナンス予告',
    type: 'maintenance',
    severity: 'warning',
    pinned: true,
    showInChat: true,
    when: '定時後デプロイの前日',
    title: '{{日付}} {{開始}}〜{{終了}} にメンテナンスを行います',
    body:
      'システム更新のため、下記の時間帯はご利用いただけません。\n\n' +
      '- 日時: {{日付}} {{開始}}〜{{終了}}\n' +
      '- 影響: ログイン・質問ができません\n' +
      '- 終了後、改めてお知らせします',
  },
  {
    key: 'model',
    name: '生成モデルの切替',
    type: 'update',
    severity: 'info',
    pinned: false,
    showInChat: false,
    when: 'ランブック §7.3 の切替後',
    title: '回答を生成するモデルを切り替えました',
    body:
      '{{日付}} に、回答を生成する AI モデルを切り替えました。\n\n' +
      '- 回答の表現や所要時間が変わることがあります\n' +
      '- 気になる点は 👎 の理由か「こうなってほしい」からお知らせください',
  },
];

export function getTemplate(key) {
  return ANNOUNCEMENT_TEMPLATES.find((t) => t.key === key) || null;
}

/** {{名前}} を vars の値で埋める。無い穴はそのまま残す（公開前に人が埋める）。 */
export function fillTemplate(text, vars = {}) {
  return String(text || '').replace(/\{\{([^}]+)\}\}/g, (m, name) => {
    const key = name.trim();
    return Object.prototype.hasOwnProperty.call(vars, key) && vars[key] != null ? String(vars[key]) : m;
  });
}

/** 文中に残っている穴の名前（重複なし、出現順） */
export function templatePlaceholders(text) {
  const out = [];
  for (const m of String(text || '').matchAll(/\{\{([^}]+)\}\}/g)) {
    const key = m[1].trim();
    if (!out.includes(key)) out.push(key);
  }
  return out;
}
