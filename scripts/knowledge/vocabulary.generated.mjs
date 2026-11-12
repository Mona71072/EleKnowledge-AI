// 生成物。直接編集しない。元: knowledge/registry/applicability-vocabulary.json。
// 再生成: python scripts/knowledge/generate_vocabulary.py

// 機種キー → カードの model_scope に書かれた値の別名（NFKC・小文字化済み）。build-senpai-index.mjs が使う。
export const MODEL_ALIASES = Object.freeze({
  'AXIEZ': Object.freeze(['axiez', 'axiez(ke-wf・ke-hf)', '駅舎エレ']),
  'AXIEZ-LINKs': Object.freeze(['axiez-links']),
  'NEXCUBE': Object.freeze(['nexcube', 'nexcube limited', '特注機械室レスエレベーター']),
  'メルシティ': Object.freeze(['メルシティ', 'melcity']),
  'メルワイド': Object.freeze(['メルワイド', 'melwide']),
  'エスカレーター': Object.freeze(['エスカレーター', 'escalator']),
});
export const GENERIC_ELEVATOR_LABEL = '全エレ機種';
export const GENERIC_ESCALATOR_LABEL = '全エス機種';
