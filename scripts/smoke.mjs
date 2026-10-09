/* Minimal CI smoke test: serve the repository as GitHub Pages will, load the
 * app in headless Chromium, and assert it reaches a usable state.
 *
 * Deliberately narrow. The full interaction suite needs a GPU to be useful;
 * this one answers the question CI actually needs answered — "did we ship a
 * page that boots?" — in about thirty seconds.
 *
 *   npm install playwright && npx playwright install --with-deps chromium
 *   node scripts/smoke.mjs
 */
import { chromium } from 'playwright';
import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.dirname(path.dirname(fileURLToPath(import.meta.url)));
const PORT = Number(process.env.PORT || 4178);

const MIME = {
  '.html': 'text/html', '.js': 'text/javascript', '.css': 'text/css',
  '.json': 'application/json', '.geojson': 'application/geo+json',
  '.svg': 'image/svg+xml', '.png': 'image/png', '.txt': 'text/plain',
  '.webmanifest': 'application/manifest+json', '.xml': 'application/xml',
};

const server = http.createServer((req, res) => {
  let p = decodeURIComponent(req.url.split('?')[0]);
  if (p.endsWith('/')) p += 'index.html';
  const file = path.join(ROOT, p);
  if (!file.startsWith(ROOT) || !fs.existsSync(file)
      || fs.statSync(file).isDirectory()) {
    res.writeHead(404); res.end('not found'); return;
  }
  res.writeHead(200, {
    'content-type': MIME[path.extname(file)] ?? 'application/octet-stream',
  });
  fs.createReadStream(file).pipe(res);
});
await new Promise((r) => server.listen(PORT, r));

const problems = [];
const ok = (label, pass, detail = '') => {
  console.log(`${pass ? 'ok  ' : 'FAIL'} ${label}${detail ? `  — ${detail}` : ''}`);
  if (!pass) problems.push(label);
};

const browser = await chromium.launch({
  args: ['--use-gl=angle', '--use-angle=swiftshader',
         '--enable-unsafe-swiftshader', '--no-sandbox'],
});
const page = await browser.newPage({ viewport: { width: 1280, height: 800 } });

const consoleErrors = [];
page.on('pageerror', (e) => consoleErrors.push(e.message));
page.on('console', (m) => { if (m.type() === 'error') consoleErrors.push(m.text()); });
page.on('requestfailed', (r) => {
  if (r.url().startsWith(`http://127.0.0.1:${PORT}`)) {
    consoleErrors.push(`request failed: ${r.url()}`);
  }
});

await page.goto(`http://127.0.0.1:${PORT}/`, { waitUntil: 'domcontentloaded',
                                               timeout: 60000 });

// The catalogue paints before the globe, so the list is the first signal.
await page.waitForFunction(() => document.querySelectorAll('.site-row').length > 10,
                           { timeout: 60000 }).catch(() => {});
ok('site list renders', (await page.locator('.site-row').count()) > 10,
   `${await page.locator('.site-row').count()} rows`);

const count = await page.locator('#resultCount').textContent();
ok('catalogue count displayed', /\d+ sites/.test(count ?? ''), count);

// Boot overlay clears once the globe is live.
await page.waitForFunction(() => {
  const b = document.querySelector('#boot');
  return !b || b.hasAttribute('hidden');
}, { timeout: 120000 }).catch(() => {});
ok('boot overlay clears', await page.evaluate(() => {
  const b = document.querySelector('#boot');
  return !b || b.hasAttribute('hidden');
}), await page.evaluate(() => document.querySelector('#bootMsg')?.textContent));

ok('WebGL canvas created', await page.evaluate(() => {
  const c = document.querySelector('#globe canvas');
  return !!c && c.width > 100;
}));

// A dossier must open and populate.
await page.locator('.site-row').first().click();
await page.waitForFunction(() => document.querySelectorAll('.callout').length >= 3,
                           { timeout: 30000 }).catch(() => {});
ok('dossier renders claim, record and context',
   (await page.locator('.callout').count()) >= 3,
   `${await page.locator('.callout').count()} sections`);
ok('dossier links out to sources',
   (await page.locator('.linklist a').count()) >= 4,
   `${await page.locator('.linklist a').count()} links`);

// The OGC tab must reach the service documents.
await page.click('#tabServices');
await page.waitForFunction(() => document.querySelectorAll('.endpoint').length > 0,
                           { timeout: 30000 }).catch(() => {});
ok('OGC service metadata loads',
   (await page.locator('.endpoint').count()) >= 4,
   `${await page.locator('.endpoint').count()} endpoints`);

const fatal = consoleErrors.filter((e) =>
  !/favicon|Cesium ion|WebGL|SwiftShader|GPU stall|texture/i.test(e));
ok('no fatal console errors', fatal.length === 0,
   fatal.slice(0, 3).join(' | '));

await browser.close();
server.close();

if (problems.length) {
  console.error(`\n${problems.length} smoke check(s) failed`);
  process.exit(1);
}
console.log('\nsmoke test passed');
