import { spawnSync } from 'node:child_process';
import { readFileSync } from 'node:fs';
import { evaluateDependencyAudit } from './dependency-audit-policy.mjs';

try {
  const result = spawnSync('npm', ['audit', '--include=dev', '--json'], {
    encoding: 'utf8', shell: process.platform === 'win32', maxBuffer: 20 * 1024 * 1024,
  });
  if (result.error || ![0, 1].includes(result.status)) throw new Error('npm auditを実行できませんでした。');
  const report = JSON.parse(result.stdout);
  const exceptions = JSON.parse(readFileSync(new URL('./dependency-audit-exceptions.json', import.meta.url), 'utf8'));
  const { blocked, excepted } = evaluateDependencyAudit(report, exceptions);
  for (const item of excepted) console.warn(`期限付き例外中（未解消）: ${item.name} ${item.advisories.join(', ')}`);
  for (const item of blocked) console.error(`未許可の${item.severity}: ${item.name} ${item.advisories.join(', ')}`);
  console.info(`全依存監査: 未許可${blocked.length}件、期限付き例外${excepted.length}件`);
  process.exitCode = blocked.length ? 1 : 0;
} catch (error) {
  console.error(`全依存監査を確認できませんでした: ${error.message}`);
  process.exitCode = 1;
}
