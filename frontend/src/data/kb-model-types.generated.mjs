// 生成物。直接編集しない。元: knowledge/registry/applicability-vocabulary.json。
// 再生成: python scripts/knowledge/generate_vocabulary.py

// 画面の機種一覧。value は API の filters.modelType に渡すキー、targets はサーバーが展開する model_type。
export const KB_MODEL_TYPES = Object.freeze([
  Object.freeze({ value: 'AXIEZ', label: 'AXIEZ', targets: Object.freeze(['AXIEZ', 'AXIEZ(KE-WF・KE-HF)', '駅舎エレ']) }),
  Object.freeze({ value: 'AXIEZ-LINKs', label: 'AXIEZ-LINKs', targets: Object.freeze(['AXIEZ-LINKs']) }),
  Object.freeze({ value: 'NEXCUBE', label: 'NEXCUBE', targets: Object.freeze(['NEXCUBE', 'NEXCUBE Limited', '特注機械室レスエレベーター']) }),
  Object.freeze({ value: 'メルシティ', label: 'メルシティ', targets: Object.freeze(['メルシティ']) }),
  Object.freeze({ value: 'メルワイド', label: 'メルワイド', targets: Object.freeze(['メルワイド']) }),
  Object.freeze({ value: 'エスカレーター', label: 'エスカレーター', targets: Object.freeze(['エスカレーター']) }),
]);

// 機種キーの一覧（UI_MODEL_FILTERS のキー・検索の MODEL_ALIASES のキーと同じ）。
export const KB_MODEL_KEYS = Object.freeze(['AXIEZ', 'AXIEZ-LINKs', 'NEXCUBE', 'メルシティ', 'メルワイド', 'エスカレーター']);
