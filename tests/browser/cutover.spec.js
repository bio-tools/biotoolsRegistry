const { test, expect } = require('./fixtures');
const detail = process.env.BIOTOOLS_EXPECT_DETAIL !== '0';
const search = process.env.BIOTOOLS_EXPECT_SEARCH !== '0';

test.describe('canonical cutover', () => {
  test.skip(process.env.BIOTOOLS_TEST_CUTOVER !== '1', 'Requires the disposable detail and search fixtures.');
  for (const agent of ['Migration browser', 'Googlebot']) {
    test(`route ownership and isolation for ${agent}`, async ({ request }) => {
      const headers = { 'User-Agent': agent };
      for (const [path, family] of [['/detail-demo', 'detail'], ['/t?q=Migration', 'search']]) {
        const response = await request.get(path, { headers });
        expect(response.status()).toBe(200);
        expect(response.headers()['x-biotools-route']).toBe('django-' + family);
        expect(response.headers()['cache-control']).toContain('no-store');
        expect(await response.text()).not.toContain('ng-app');
      }
      const api = await request.get('/api/t/detail-demo?format=json', { headers });
      expect((await api.json()).biotoolsID).toBe('detail-demo');
      expect((await request.get('/api/schema/', { headers })).status()).toBe(200);
      expect((await request.get('/api/rest-auth/socialaccounts/', { headers })).status()).toBe(401);
    });
  }

  test('detail aliases and missing records', async ({ request }) => {
    for (const path of ['/tool/detail-demo', '/t/detail-demo/', '/biotools:detail-demo', '/DETAIL-DEMO/']) {
      const response = await request.get(path + '?tab=functions', { maxRedirects: 0 });
      expect(response.status()).toBe(302);
      expect(response.headers().location).toBe('/detail-demo?tab=functions');
      expect((await request.get(response.headers().location)).status()).toBe(200);
    }
    expect((await request.get('/missing-cutover-record')).status()).toBe(404);
  });

  test('supported search filters stay native without a redirect loop', async ({ request }) => {
    test.skip(!search);
    const response = await request.get('/t?domain=proteomics&topicID=topic_0080&topicID=topic_0121', { maxRedirects: 0 });
    expect(response.status()).toBe(200);
    expect(response.headers().location).toBeUndefined();
    expect(await response.text()).not.toContain('name="_legacy"');
  });

  for (const width of [1440, 390]) {
    test(`home to canonical search and detail at ${width}px`, async ({ page, tool }, info) => {
      test.skip(!detail || !search);
      await page.setViewportSize({ width, height: 1000 });
      await page.goto('/');
      await page.getByRole('link', { name: 'Tools', exact: true }).click();
      await expect(page.locator('[data-vue-island="search-workspace"]')).toHaveAttribute('data-v-app', '');
      await page.goto('/t?' + new URLSearchParams({ q: tool.name, per_page: '10' }));
      await expect(page.getByRole('link', { name: tool.name, exact: true })).toBeVisible();
      await page.reload();
      await page.getByRole('link', { name: tool.name, exact: true }).click();
      await expect(page).toHaveURL(url => url.pathname === '/' + tool.biotoolsID);
      await expect(page.locator('.tool-detail h1')).toHaveText(tool.name);
      expect(await page.locator('html').evaluate(el => el.scrollWidth <= innerWidth)).toBe(true);
      await page.screenshot({ path: info.outputPath('canonical-detail.png'), fullPage: true });
      await page.reload();
      await expect(page.locator('.tool-detail h1')).toHaveText(tool.name);
      await page.goBack();
      await expect(page.locator('[data-vue-island="search-workspace"]')).toHaveAttribute('data-v-app', '');
      await page.goForward();
      await page.getByRole('link', { name: 'Manage record', exact: true }).click();
      await expect(page.getByRole('heading', { name: 'Sign in', exact: true })).toBeVisible();
    });
  }
});
