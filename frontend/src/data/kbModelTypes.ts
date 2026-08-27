/**
 * チャット UI の機種絞り込み項目。
 *
 * 正本: `lambda/rag/rag-function/app.py` の `UI_MODEL_FILTERS`
 * （要素完全一致 / listContains。取扱機種スコープ導入後）
 *
 * value は API の `filters.modelType` にそのまま渡すキー。
 * targets はサーバーが展開する model_type（画面の説明用。送信には使わない）。
 *
 * カタログ全機種一覧は出さない。取扱外機種（NEXIEZ 系など）は UI から選べない。
 */
export type KbModelOption = { value: string; label: string; targets: string[] };

/** サービス取扱の絞り込み 6 項目（UI_MODEL_FILTERS とキー・targets を一致させる） */
export const ALL_MODEL_TYPES: KbModelOption[] = [
  {
    value: 'AXIEZ',
    label: 'AXIEZ',
    targets: ['AXIEZ', 'AXIEZ(KE-WF・KE-HF)', '駅舎エレ'],
  },
  {
    value: 'AXIEZ-LINKs',
    label: 'AXIEZ-LINKs',
    targets: ['AXIEZ-LINKs'],
  },
  {
    value: 'NEXCUBE',
    label: 'NEXCUBE',
    targets: ['NEXCUBE', 'NEXCUBE Limited', '特注機械室レスエレベーター'],
  },
  {
    value: 'メルシティ',
    label: 'メルシティ',
    targets: ['メルシティ'],
  },
  {
    value: 'メルワイド',
    label: 'メルワイド',
    targets: ['メルワイド'],
  },
  {
    value: 'エスカレーター',
    label: 'エスカレーター',
    targets: ['エスカレーター'],
  },
];

/** 互換: 6 項目のため ALL と同一 */
export const POPULAR_MODEL_TYPES: KbModelOption[] = ALL_MODEL_TYPES;
