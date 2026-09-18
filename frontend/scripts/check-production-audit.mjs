import { spawnSync } from 'node:child_process';

const auditResult = spawnSync('npm', ['audit', '--omit=dev', '--json'], {
  encoding: 'utf8',
  shell: process.platform === 'win32',
});

let report;

try {
  report = JSON.parse(auditResult.stdout);
} catch {
  console.error('npm audit の JSON 結果を解析できませんでした。');
  process.exit(1);
}

const POSTCSS_EXCEPTION_SOURCES = new Set([1124252, 1139510]);
const POSTCSS_EXCEPTION_EXPIRY = '2026-10-16';

function isAllowedPostcssException(vulnerability) {
  if (vulnerability.name !== 'postcss' || vulnerability.severity !== 'high') {
    return false;
  }

  if (new Date() > new Date(`${POSTCSS_EXCEPTION_EXPIRY}T23:59:59Z`)) {
    return false;
  }

  const highAdvisories = vulnerability.via.filter(
    (advisory) => typeof advisory === 'object' && advisory.severity === 'high',
  );

  return highAdvisories.length > 0
    && highAdvisories.every((advisory) => POSTCSS_EXCEPTION_SOURCES.has(advisory.source));
}

const blocking = Object.values(report.vulnerabilities ?? {}).filter((vulnerability) => (
  ['critical', 'high'].includes(vulnerability.severity)
  && !isAllowedPostcssException(vulnerability)
));

const exceptions = Object.values(report.vulnerabilities ?? {}).filter((vulnerability) => (
  isAllowedPostcssException(vulnerability)
));

if (exceptions.length > 0) {
  console.warn(
    `期限付き例外（${POSTCSS_EXCEPTION_EXPIRY}まで）: postcss の既知の high は Next.js 16 系へのメジャー更新が必要なため、Issue #120 で追跡します。`,
  );
}

if (blocking.length > 0) {
  console.error('production dependency に未許可の critical/high 脆弱性があります:');
  for (const vulnerability of blocking) {
    console.error(`- ${vulnerability.name}: ${vulnerability.severity}`);
  }
  process.exit(1);
}
