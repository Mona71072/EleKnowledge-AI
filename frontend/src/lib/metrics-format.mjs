// ダッシュボード・コスト画面の表示用の純粋関数（node --test で検証。React 依存なし）

const JST_OFFSET_MIN = 9 * 60;

function toJst(iso) {
  if (!iso) return null;
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return null;
  return new Date(d.getTime() + JST_OFFSET_MIN * 60000);
}

/** ISO（UTC）→ JST の "HH:MM" */
export function jstTime(iso) {
  const d = toJst(iso);
  if (!d) return '—';
  return `${String(d.getUTCHours()).padStart(2, '0')}:${String(d.getUTCMinutes()).padStart(2, '0')}`;
}

/** ISO（UTC）→ JST の "M/D HH:MM" */
export function jstDateTime(iso) {
  const d = toJst(iso);
  if (!d) return '—';
  return `${d.getUTCMonth() + 1}/${d.getUTCDate()} ${jstTime(iso)}`;
}

const WEEKDAYS = ['日', '月', '火', '水', '木', '金', '土'];

/** "2026-09-23" → "9/23（火）" */
export function jstDateLabel(yyyyMmDd, withWeekday = true) {
  if (!yyyyMmDd || yyyyMmDd.length < 10) return yyyyMmDd || '—';
  const [y, m, d] = yyyyMmDd.slice(0, 10).split('-').map(Number);
  const label = `${m}/${d}`;
  if (!withWeekday) return label;
  const wd = WEEKDAYS[new Date(Date.UTC(y, m - 1, d)).getUTCDay()];
  return `${label}（${wd}）`;
}

/** USD の表示。null は "—" */
export function formatUsd(value, digits = 2) {
  if (value === null || value === undefined || Number.isNaN(value)) return '—';
  return `${Number(value).toLocaleString('en-US', { minimumFractionDigits: digits, maximumFractionDigits: digits })} USD`;
}

/** ms → 秒表示 "11.2 s"。null は "—" */
export function formatSeconds(ms, digits = 1) {
  if (ms === null || ms === undefined || Number.isNaN(ms)) return '—';
  return `${(Number(ms) / 1000).toFixed(digits)} s`;
}

/** 秒 → "15 分" / "1 時間 5 分" / "継続中"（null） */
export function formatDuration(sec) {
  if (sec === null || sec === undefined) return '継続中';
  const s = Math.max(0, Math.round(Number(sec)));
  if (s < 60) return `${s} 秒`;
  const min = Math.round(s / 60);
  if (min < 60) return `${min} 分`;
  const h = Math.floor(min / 60);
  const rest = min % 60;
  return rest ? `${h} 時間 ${rest} 分` : `${h} 時間`;
}

/** 件数表示。null は "—"（集計なし）と 0 を区別する */
export function formatCount(value) {
  if (value === null || value === undefined) return '—';
  return Number(value).toLocaleString('ja-JP');
}

/**
 * 率の表示規則（設計 §2.7）: 分母が閾値以上のときだけ "12 %" を返し、未満は null。
 */
export function rateLabel(numerator, denominator, minDenominator = 30) {
  if (numerator === null || numerator === undefined || !denominator || denominator < minDenominator) return null;
  return `${Math.round((Number(numerator) / Number(denominator)) * 100)} %`;
}

/**
 * CloudWatch Logs Insights のコンソール URL（△ エンコード形式はコンソール依存。
 * 崩れた場合に備え、画面ではロググループ・時間範囲・保存クエリ名のテキストも併記する）。
 */
export function logsInsightsUrl({ region = 'ap-northeast-1', logGroup, from, to }) {
  if (!logGroup || !from || !to) return null;
  const enc = (s) => encodeURIComponent(s).replace(/%/g, '*');
  const detail = `~(end~'${enc(to)}~start~'${enc(from)}~timeType~'ABSOLUTE~tz~'UTC~source~(~'${enc(logGroup)}))`;
  return `https://${region}.console.aws.amazon.com/cloudwatch/home?region=${region}#logsV2:logs-insights$3FqueryDetail$3D${detail}`;
}

/** 4 段階の状態色に対する表示（アイコン + ラベル。色だけに頼らない） */
export const STATUS_LABELS = {
  good: { label: '正常', icon: '●' },
  warning: { label: '注意', icon: '▲' },
  serious: { label: '悪化', icon: '◆' },
  critical: { label: '重大', icon: '■' },
};

/** 複数の状態のうち最も悪いもの */
export function worstStatus(...statuses) {
  const order = ['good', 'warning', 'serious', 'critical'];
  return statuses.reduce((acc, s) => (order.indexOf(s) > order.indexOf(acc) ? s : acc), 'good');
}
