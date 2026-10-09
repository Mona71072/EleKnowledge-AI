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

const blocking = Object.values(report.vulnerabilities ?? {}).filter((vulnerability) => (
  ['critical', 'high'].includes(vulnerability.severity)
));

if (blocking.length > 0) {
  console.error('production dependency に未許可の critical/high 脆弱性があります:');
  for (const vulnerability of blocking) {
    console.error(`- ${vulnerability.name}: ${vulnerability.severity}`);
  }
  process.exit(1);
}
