// 2026-10-20 業務担当の説明: AXIEZ と AXIEZ-LINKs は制御方式・据付・機械が大きく異なる別製品。
// ここに無い機種は製品名だけを表示し、推測した仕様を出さない。
const MODEL_FACTS = {
  AXIEZ: 'VFGLB・巻上機下部',
  'AXIEZ-LINKs': 'VFGLF・巻上機上部',
};

/** 機種名に、業務担当が確認済みの特徴だけを添える。 */
export function modelWithFacts(model) {
  return MODEL_FACTS[model] ? `${model}（${MODEL_FACTS[model]}）` : model;
}

/** 選択機種と別製品だけを対象とする未確認カードに出す注意。一致・全機種・不明は何も出さない。 */
export function modelFitNotice(match, selectedModel) {
  if (!selectedModel || match.modelFit !== 'other_product') return null;
  const products = match.modelFitProducts ?? [];
  const subject = products.length > 0 ? products.map(modelWithFacts).join('、') : '別の機種区分';
  return `${subject}の事例です。選択中の ${modelWithFacts(selectedModel)}でも当てはまるかは要確認です。`;
}

/** ノウハウ全般に付ける注意（設計 2026-11-11 WP4・§4.12）。正式資料の代わりにしない。 */
export const KNOWHOW_NOT_OFFICIAL_NOTICE = 'ノウハウは正規文書ではありません。根拠は正式資料で確認してください。';

/** 状態の表示。共通知識で公開した版（approved）は「検証済み」、それ以外は下書き。 */
export function knowhowStatusLabel(match) {
  return match?.status === 'approved' ? '検証済み（参照用）' : '未承認（下書き）';
}

/** 適用範囲を担当者が確認していないカードに出す注意。適用範囲の情報が無ければ何も出さない。 */
export function scopeUnverifiedNotice(match) {
  const scope = match?.modelScope;
  if (!scope || typeof scope !== 'object') return null;
  return scope.scope_status === 'verified' ? null : '機種の適用範囲は未確認です。';
}
