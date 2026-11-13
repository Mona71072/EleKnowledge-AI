/**
 * チャット UI の機種絞り込み項目。
 *
 * 値の正本: `knowledge/registry/applicability-vocabulary.json`
 * （`scripts/knowledge/generate_vocabulary.py` が `kb-model-types.generated.mjs` に生成し、
 * サーバーの `UI_MODEL_FILTERS` と同じ値になる。要素完全一致 / listContains）
 *
 * value は API の `filters.modelType` にそのまま渡すキー。
 * targets はサーバーが展開する model_type（画面の説明用。送信には使わない）。
 *
 * カタログ全機種一覧は出さない。取扱外機種（NEXIEZ 系など）は UI から選べない。
 */
import { KB_MODEL_TYPES } from './kb-model-types.generated.mjs';

export type KbModelOption = { value: string; label: string; targets: string[] };

/** サービス取扱の絞り込み項目（語彙ファイルから生成した値） */
export const ALL_MODEL_TYPES: KbModelOption[] = KB_MODEL_TYPES.map(({ value, label, targets }) => ({
  value,
  label,
  targets: [...targets],
}));

/** 互換: 6 項目のため ALL と同一 */
export const POPULAR_MODEL_TYPES: KbModelOption[] = ALL_MODEL_TYPES;
