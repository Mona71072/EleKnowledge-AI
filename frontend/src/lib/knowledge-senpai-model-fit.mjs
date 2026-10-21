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
