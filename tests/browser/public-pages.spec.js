const { test, expect } = require('./fixtures');

test.describe('Native public pages', () => {
  test.skip(process.env.BIOTOOLS_TEST_PUBLIC !== '1', 'Requires public-page cutover and the disposable search domain fixture.');
  const enabled = true;

  test('route ownership, shortcuts, errors and API boundaries', async ({ request }) => {
    test.setTimeout(enabled ? 30000 : 120000);
    for (const agent of ['Migration browser', 'Googlebot']) {
      for (const path of ['/', '/about', '/community', '/communities', '/domains', '/stats']) {
        const response = await request.get(path, { headers: { 'User-Agent': agent } });
        expect(response.status(), path).toBe(200);
        const body = await response.text();
        expect(response.headers()['x-biotools-route']).toBe('django-public');
        expect(body).not.toContain('ng-app');
        expect(body).not.toContain('/dist/');
        expect(response.headers()['x-robots-tag']).toBe(path === '/domains' ? 'noindex, follow' : 'index, follow');
      }
    }
    for (const [path, family] of [['/t', 'search'], ['/detail-demo', 'detail'], ['/login', 'accounts']]) {
      expect((await request.get(path)).headers()['x-biotools-route']).toBe('django-' + family);
    }
    if (!enabled) return;
    for (const path of ['/schema', '/governance', '/events', '/mail', '/faq', '/apidoc', '/changelog', '/helpdesk', '/projects', '/roadmap']) {
      const response = await request.get(path + '?next=https://untrusted.invalid', { maxRedirects: 0 });
      expect(response.status()).toBe(302);
      expect(response.headers().location).not.toContain('untrusted.invalid');
      expect(response.headers().location).toMatch(/^https?:\/\//);
    }
    for (const path of ['/404', '/not-a-public-page/extra', '/about/missing', '/about/edit', '/schema/extra', '/missing-public-fixture']) {
      const response = await request.get(path);
      expect(response.status(), path).toBe(404);
      expect(await response.text()).not.toContain('ng-app');
    }
    expect((await request.get('/api/env/')).status()).toBe(200);
    expect(await (await request.get('/about?_legacy=1')).text()).not.toContain('ng-app');
    const preview = await request.get('/_migration/html/public/about');
    expect(await preview.text()).toContain('name="robots" content="noindex, follow"');
  });

  test('workflow navigation enters native public pages', async ({ page }) => {
    test.skip(!enabled);
    for (const name of ['About', 'Communities', 'Domains']) {
      await page.goto('/workflows');
      await expect(page.locator('[ng-app]')).toHaveCount(0);
      await page.getByRole('navigation').getByRole('link', { name, exact: true }).click();
      await expect(page.locator('[ng-app]')).toHaveCount(0);
      await expect(page.getByRole('heading', { level: 1 })).toBeVisible();
    }
  });

  for (const width of [1440, 390]) {
    for (const mode of ['enhanced', 'no-javascript', 'failed-assets']) {
      test(`${mode} public navigation, domains and statistics at ${width}px`, async ({ browser, baseURL }, info) => {
        test.skip(!enabled);
        const context = await browser.newContext({ baseURL, viewport: { width, height: 900 },
          javaScriptEnabled: mode !== 'no-javascript', ignoreHTTPSErrors: process.env.BIOTOOLS_TEST_LOCAL_TLS === '1' });
        try {
          const page = await context.newPage();
          const errors = [];
          page.on('pageerror', error => errors.push(error.message));
          if (mode === 'failed-assets') await page.route('**/static/modern/**', route => route.abort());
          await page.goto('/');
          await expect(page.getByRole('heading', { level: 1 })).toHaveText('bio.tools');
          await expect(page.locator('.site-header')).toHaveCSS('background-color', 'rgb(0, 84, 114)');
          await page.getByLabel('Search bio.tools', { exact: true }).fill('Workspace sample');
          await page.getByRole('button', { name: 'Search', exact: true }).click();
          await expect(page.locator('[data-tool-id]')).toHaveCount(13);
          for (const path of ['/', '/about', '/communities']) {
            await page.goto(path);
            const images = page.locator('.public-copy img');
            await expect.poll(() => images.evaluateAll(nodes => nodes.every(image => image.complete && image.naturalWidth > 0))).toBe(true);
            expect(await page.locator('html').evaluate(node => node.scrollWidth <= innerWidth)).toBe(true);
            if (path === '/about') {
              await expect(page.locator('.about-summary-cell .fa[aria-hidden="true"]')).toHaveCount(12);
              const icon = page.locator('.about-summary-cell .fa-globe');
              await expect(icon).toHaveCSS('font-family', '"bio.tools icons"');
              expect(await icon.evaluate(el => getComputedStyle(el, '::before').content)).not.toBe('none');
              await expect(page.locator('.citation-list > li')).toHaveCount(5);
              await expect(page.getByRole('link', { name: '10.1093/nar/gkag420', exact: true })).toHaveAttribute('href', 'https://doi.org/10.1093/nar/gkag420');
              await page.locator('.about-section').filter({ has: page.getByRole('heading', { name: 'Publications and citing' }) })
                .screenshot({ path: info.outputPath(`publications-${width}-${mode}.png`) });
            }
            await page.screenshot({ path: info.outputPath(`${path.slice(1) || 'home'}-${width}-${mode}.png`), fullPage: true });
          }
          await expect(page.locator('a[href="/t?domain=proteomics"]').first()).toBeAttached();
          await page.getByRole('navigation', { name: 'Main navigation' }).getByRole('link', { name: 'Domains', exact: true }).click();
          await page.getByLabel('Search domains', { exact: true }).fill('search-parity-fixture');
          await page.getByRole('button', { name: 'Search', exact: true }).click();
          await expect(page.locator('.domain-entry')).toHaveCount(1);
          await page.reload();
          await expect(page.getByLabel('Search domains', { exact: true })).toHaveValue('search-parity-fixture');
          expect(await page.locator('html').evaluate(node => node.scrollWidth <= innerWidth)).toBe(true);
          await page.screenshot({ path: info.outputPath(`domains-${width}-${mode}.png`), fullPage: true });
          await page.locator('.domain-entry h2 a').click();
          await expect(page.locator('[data-tool-id]')).toHaveCount(13);
          await page.goBack();
          await expect(page.locator('.domain-entry')).toHaveCount(1);
          await page.getByLabel('Search domains', { exact: true }).fill('not-a-matching-domain');
          await page.getByRole('button', { name: 'Search', exact: true }).click();
          await expect(page.getByText('No domains found.', { exact: true })).toBeVisible();
          const stats = await page.goto('/stats');
          expect(stats.status()).toBe(200);
          await expect(page.locator('.statistics-section')).toHaveCount(4);
          await expect(page.locator('.statistics-totals dd').first()).not.toBeEmpty();
          await page.getByText('Top contributors', { exact: true }).click();
          await expect(page.locator('details').filter({ has: page.getByText('Top contributors', { exact: true }) }).locator('meter').first()).toBeVisible();
          expect(await page.locator('html').evaluate(node => node.scrollWidth <= innerWidth)).toBe(true);
          await page.screenshot({ path: info.outputPath(`statistics-${width}-${mode}.png`), fullPage: true });
          expect(errors).toEqual([]);
        } finally { await context.close(); }
      });
    }
  }
});
