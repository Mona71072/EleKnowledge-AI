/* eslint-disable */
// 利用者マニュアル / 管理者向け確認表 を PDF 化する（Playwright + Chromium）
// 使い方: node build-pdf.js  （playwright は scratchpad 側の node_modules を参照）
const path = require('path');
const fs = require('fs');
const { chromium } = require(process.env.PLAYWRIGHT_DIR
  ? path.join(process.env.PLAYWRIGHT_DIR, 'node_modules', 'playwright')
  : 'playwright');

const here = __dirname;
const jobs = [
  { html: 'eleknowledge-user-manual.html', pdf: 'EleKnowledge_利用者マニュアル_v1.pdf', title: 'EleKnowledge 利用者マニュアル' },
  { html: 'admin-verification-sheet.html', pdf: 'EleKnowledge_管理者向け確認表_v1.pdf', title: 'EleKnowledge 管理者向け確認表' },
];

(async () => {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();
  for (const j of jobs) {
    const src = path.join(here, j.html);
    if (!fs.existsSync(src)) { console.log('skip (missing)', j.html); continue; }
    await page.goto('file:///' + src.replace(/\\/g, '/'), { waitUntil: 'networkidle' });
    await page.evaluate(() => document.fonts.ready);
    await page.pdf({
      path: path.join(here, j.pdf),
      format: 'A4',
      printBackground: true,
      preferCSSPageSize: true,
      displayHeaderFooter: true,
      headerTemplate: `<div style="width:100%;font-size:8px;color:#64748b;padding:0 16mm;display:flex;justify-content:space-between;font-family:'BIZ UDPGothic','Yu Gothic','Meiryo',sans-serif;"><span>${j.title}</span><span>第1版 2026-09-09</span></div>`,
      footerTemplate: `<div style="width:100%;font-size:8px;color:#64748b;text-align:center;font-family:'BIZ UDPGothic','Yu Gothic','Meiryo',sans-serif;"><span class="pageNumber"></span> / <span class="totalPages"></span></div>`,
      margin: { top: '16mm', bottom: '18mm', left: '16mm', right: '16mm' },
    });
    console.log('wrote', j.pdf);
  }
  await browser.close();
})().catch((e) => { console.error(e); process.exit(1); });
