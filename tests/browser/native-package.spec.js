const fs = require('node:fs');
const path = require('node:path');
const { test, expect } = require('./fixtures');

test.describe('legacy-free packaged candidate', () => {
  test.skip(process.env.BIOTOOLS_TEST_NATIVE_PACKAGE !== '1', 'Requires the isolated native image rehearsal.');

  test('native routes, API and retained files work for browsers and crawlers', async ({ request, baseURL }) => {
    for (const agent of ['Migration browser', 'Googlebot']) {
      for (const [url, family] of [
        ['/', 'public'], ['/about?_legacy=1', 'public'], ['/t', 'search'],
        ['/login', 'accounts'], ['/workflows', 'management'], ['/workflows/design/', 'management'],
      ]) {
        const response = await request.get(url, { headers: { 'User-Agent': agent } });
        expect(response.status(), url).toBe(200);
        expect(response.headers()['x-biotools-route'], url).toBe(`django-${family}`);
        const body = await response.text();
        expect(body, url).not.toContain('ng-app');
        if (url === '/about?_legacy=1') expect(body).toContain(`rel="canonical" href="${baseURL}/about"`);
      }
    }
    expect((await request.get('/api/env/')).status()).toBe(200);
    expect((await request.get('/api/admin/', { maxRedirects: 0 })).status()).toBe(302);
    const sitemap = await request.get('/api/sitemap.xml');
    expect(sitemap.status()).toBe(200);
    expect(sitemap.headers()['content-type']).toContain('application/xml');
    expect((await request.get('/_edam/terms/?scope=data&q=data_2044')).status()).toBe(200);
    for (const url of ['/static/html/favicon.ico', '/favicon.ico', '/img/favicon.ico', '/robots.txt']) {
      expect((await request.get(url)).status(), url).toBe(200);
    }
    expect(await (await request.get('/robots.txt')).text()).toContain('Disallow: /');
    const schemaPath = 'biotools-1.0/biotools-1.0.xsd';
    const schema = await request.get(`/resources/${schemaPath}`);
    expect(schema.status()).toBe(200);
    expect(await schema.body()).toEqual(fs.readFileSync(path.resolve(__dirname, '../../registry-assets/resources', schemaPath)));
    for (const asset of ['img/biotools.svg', 'json/model.json']) {
      const response = await request.get('/' + asset);
      expect(response.status(), asset).toBe(200);
      expect(await response.body()).toEqual(fs.readFileSync(path.resolve(__dirname, '../../registry-assets', asset)));
    }
    const workflowImage = await request.get('/media/workflows/management-workflow.png');
    expect(workflowImage.status()).toBe(200);
    expect((await workflowImage.body()).subarray(0, 8)).toEqual(Buffer.from('89504e470d0a1a0a', 'hex'));
    for (const url of ['/resources/', '/static/', '/media/']) {
      expect([403, 404], url).toContain((await request.get(url)).status());
    }
    for (const url of ['/index.html', '/dist/app.min.js', '/static/missing.css', '/resources/missing.xsd']) {
      expect((await request.get(url)).status(), url).toBe(404);
    }
  });

  test('search works without JavaScript', async ({ browser, baseURL }) => {
    const context = await browser.newContext({ baseURL, javaScriptEnabled: false,
      ignoreHTTPSErrors: process.env.BIOTOOLS_TEST_LOCAL_TLS === '1' });
    try {
      const page = await context.newPage();
      await page.goto('/t');
      await page.locator('#native-search').fill('Migration');
      await page.locator('.native-search').getByRole('button', { name: 'Search', exact: true }).click();
      await expect(page).toHaveURL(/\bq=Migration/);
      await expect(page.locator('#native-search')).toHaveValue('Migration');
      await expect(page.getByRole('region', { name: 'Search results' })).toBeVisible();
    } finally {
      await context.close();
    }
  });

  test('production HTTPS sign-in uses secure session and CSRF cookies', async ({ page, context }) => {
    test.skip(process.env.BIOTOOLS_TEST_SECURE_COOKIES !== '1', 'Requires the secure production rehearsal and a disposable account.');
    await page.goto('/login');
    const csrf = (await context.cookies()).find(cookie => cookie.name === 'csrftoken');
    expect(csrf?.secure).toBe(true);
    await page.getByLabel('Username or email:', { exact: true }).fill(process.env.BIOTOOLS_TEST_USERNAME);
    await page.getByLabel('Password:', { exact: true }).fill(process.env.BIOTOOLS_TEST_PASSWORD);
    await page.getByRole('button', { name: 'Sign in', exact: true }).click();
    await expect(page.getByRole('heading', { name: 'My profile', exact: true })).toBeVisible();
    const session = (await context.cookies()).find(cookie => cookie.name === 'sessionid');
    expect(session?.secure).toBe(true);
    expect(session?.httpOnly).toBe(true);
  });

  for (const width of [1440, 390]) {
    test(`modern workflow designer loads at ${width}px`, async ({ page }) => {
      await page.setViewportSize({ width, height: 900 });
      const errors = [];
      page.on('pageerror', error => errors.push(error.message));
      await page.goto('/workflows/design/');
      await expect(page.getByRole('heading', { name: 'Workflow designer' })).toBeVisible();
      await expect(page.getByRole('button', { name: 'Search functions' })).toBeVisible();
      expect(errors).toEqual([]);
    });
  }
});
