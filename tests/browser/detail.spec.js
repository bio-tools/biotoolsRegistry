const { test, expect } = require('./fixtures');
const canonical = process.env.BIOTOOLS_TEST_CUTOVER === '1';

test.describe('Server-rendered tool detail', () => {
  test.skip(process.env.BIOTOOLS_TEST_DETAIL !== '1', 'Requires the local detail-demo fixture');

  for (const width of [1440, 390]) {
    test(`rich detail, native links and refresh without JavaScript at ${width}px`, async ({ browser, baseURL }, testInfo) => {
      const context = await browser.newContext({
        baseURL, javaScriptEnabled: false, viewport: { width, height: 1000 },
        ignoreHTTPSErrors: process.env.BIOTOOLS_TEST_LOCAL_TLS === '1',
      });
      try {
        const page = await context.newPage();
        const requested = [];
        page.on('request', request => requested.push(request.url()));
        const url = canonical ? '/detail-demo' : '/_migration/html/tool/detail-demo/';
        expect((await page.goto(url)).status()).toBe(200);
        await expect(page).toHaveTitle('Sequence Workbench (demo) | bio.tools');
        await expect(page.getByRole('heading', { level: 1 })).toHaveText('Sequence Workbench (demo)');
        for (const heading of ['Overview', 'Functions', 'Documentation', 'Downloads', 'Publications', 'Credits', 'Registry record']) {
          await expect(page.getByRole('heading', { name: heading, exact: true })).toBeVisible();
        }
        await expect(page.getByRole('link', { name: 'https://example.org/sequence-workbench', exact: true }))
          .toHaveAttribute('href', 'https://example.org/sequence-workbench');
        await expect(page.getByRole('link', { name: '10.5555/detail-demo', exact: true }))
          .toHaveAttribute('href', 'https://doi.org/10.5555/detail-demo');
        await expect(page.getByRole('link', { name: 'Sequence analysis', exact: true }))
          .toHaveAttribute('href', '/t?topicID=%22topic_0080%22');
        await expect(page.getByRole('link', { name: 'MIT', exact: true }))
          .toHaveAttribute('href', 'https://spdx.org/licenses/MIT');
        const summary = page.locator('summary').filter({ hasText: 'Abstract' });
        await summary.focus();
        await summary.press('Enter');
        await expect(page.locator('details')).toHaveAttribute('open', '');
        expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBeTruthy();
        expect(await page.locator('.site-header').evaluate(el => getComputedStyle(el).backgroundColor)).toBe('rgb(0, 84, 114)');
        expect(await page.locator('.brand img').evaluate(img => img.complete && img.naturalWidth > 0)).toBeTruthy();
        expect(requested.every(url => new URL(url).origin === new URL(baseURL).origin)).toBeTruthy();
        await page.screenshot({ path: testInfo.outputPath('tool-detail.png'), fullPage: true });
        await page.locator('#publications').screenshot({ path: testInfo.outputPath('publications.png') });
        await testInfo.attach('tool-detail', { path: testInfo.outputPath('tool-detail.png'), contentType: 'image/png' });
        await page.reload();
        await expect(page.getByRole('heading', { level: 1 })).toHaveText('Sequence Workbench (demo)');
        await page.getByRole('link', { name: 'migration-fixture', exact: true }).click();
        await expect(page).toHaveURL(url => url.pathname === (canonical ? '/migration-fixture' : '/_migration/html/tool/migration-fixture/'));
        await expect(page.getByRole('heading', { level: 1 })).toHaveText('Migration Fixture');
        await expect(page.locator('#publications')).toHaveCount(0);
        await page.goBack();
        await expect(page.getByRole('heading', { level: 1 })).toHaveText('Sequence Workbench (demo)');
      } finally {
        await context.close();
      }
    });
  }

  test('browser and bot requests retain HTML and API ownership', async ({ request, page, baseURL }) => {
    for (const agent of ['Migration browser', 'Googlebot']) {
      const response = await request.get('/_migration/html/tool/detail-demo/', { headers: { 'User-Agent': agent } });
      expect(response.status()).toBe(200);
      expect(await response.text()).toContain('<h1>Sequence Workbench (demo)</h1>');
      expect((await request.get('/_migration/html/tool/unknown-detail/')).status()).toBe(404);
    }
    const api = await request.get('/api/t/detail-demo?format=json');
    expect((await api.json()).biotoolsID).toBe('detail-demo');
    const detail = await request.get('/detail-demo');
    expect(await detail.text()).not.toContain('ng-app');
    await page.route('**/*', route => new URL(route.request().url()).origin === new URL(baseURL).origin
      ? route.continue() : route.abort());
    await page.goto('/detail-demo', { waitUntil: 'domcontentloaded' });
    await expect(page.getByRole('heading', { name: /Sequence Workbench \(demo\)/ })).toBeVisible();
    for (const text of ['Sequence analysis', 'FASTA', 'ClustalW', 'Example Research Team', 'Example Methods', 'MIT']) {
      await expect(page.locator('body')).toContainText(text);
    }
    await page.goto('/_migration/html/tool/detail-demo/');
    await expect(page.getByRole('heading', { name: 'Sequence Workbench (demo)' })).toBeVisible();
    expect(await page.locator('script').count()).toBe(0);
  });
});
