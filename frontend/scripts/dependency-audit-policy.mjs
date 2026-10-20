const GHSA_PATTERN = /^GHSA-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{4}$/i;
const TRACKING_PATTERN = /^https:\/\/github\.com\/yukiworkspace\/EleKnowledge-AI\/(?:issues|pull)\/\d+(?:#(?:issuecomment|pullrequestreview)-\d+)?$/;

/** Evaluate advisory-specific exceptions; malformed and expired records fail closed. */
export function evaluateDependencyAudit(report, exceptions, now = new Date()) {
  if (!report || report.error || !report.vulnerabilities ||
      typeof report.vulnerabilities !== 'object' || Array.isArray(report.vulnerabilities) ||
      !report.metadata?.vulnerabilities || !Array.isArray(exceptions) ||
      !Number.isFinite(now.getTime())) {
    throw new Error('監査結果または例外台帳が不正です。');
  }
  const allowed = new Set();
  for (const entry of exceptions) {
    const expires = entry?.expires;
    const day = typeof expires === 'string' && /^\d{4}-\d{2}-\d{2}$/.test(expires)
      ? new Date(`${expires}T00:00:00Z`) : null;
    if (!GHSA_PATTERN.test(entry?.id ?? '') || !entry?.reason?.trim() ||
        !TRACKING_PATTERN.test(entry?.issue ?? '') ||
        !TRACKING_PATTERN.test(entry?.approvalUrl ?? '') ||
        !day || !Number.isFinite(day.getTime()) || day.toISOString().slice(0, 10) !== expires ||
        allowed.has(entry.id.toLowerCase())) {
      throw new Error('例外には有効なID・理由・期限・追跡Issue・明示承認リンクが必要です。');
    }
    if (now.getTime() > Date.parse(`${expires}T23:59:59.999+09:00`)) {
      throw new Error(`期限切れの例外です: ${entry.id}`);
    }
    allowed.add(entry.id.toLowerCase());
  }

  const vulnerabilities = report.vulnerabilities;
  function advisoryIds(name, visited = new Set()) {
    if (visited.has(name)) return new Set(['unclassified']);
    const next = new Set(visited).add(name);
    const item = vulnerabilities[name];
    if (!item || !Array.isArray(item.via) || item.via.length === 0) return new Set(['unclassified']);
    const ids = new Set();
    for (const via of item.via) {
      if (typeof via === 'string') {
        for (const id of advisoryIds(via, next)) ids.add(id);
      } else {
        const match = /^https:\/\/github\.com\/advisories\/(GHSA-[a-z0-9-]+)$/i.exec(via?.url ?? '');
        ids.add(match && GHSA_PATTERN.test(match[1]) ? match[1].toLowerCase() : 'unclassified');
      }
    }
    return ids;
  }

  const blocked = [];
  const excepted = [];
  for (const [name, vulnerability] of Object.entries(vulnerabilities)) {
    if (!['info', 'low', 'moderate', 'high', 'critical'].includes(vulnerability?.severity)) {
      throw new Error('監査結果の深刻度が不正です。');
    }
    if (!['high', 'critical'].includes(vulnerability.severity)) continue;
    const ids = [...advisoryIds(name)];
    const result = { name, severity: vulnerability.severity, advisories: ids };
    (ids.every((id) => allowed.has(id)) ? excepted : blocked).push(result);
  }
  const declared = Number(report.metadata.vulnerabilities.high ?? 0) + Number(report.metadata.vulnerabilities.critical ?? 0);
  if (!Number.isFinite(declared) || declared !== blocked.length + excepted.length) {
    throw new Error('監査の件数と詳細が一致しません。');
  }
  return { blocked, excepted };
}
