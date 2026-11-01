const { test, expect } = require('./fixtures');

test.describe('Complete native search', () => {
  test.skip(process.env.BIOTOOLS_TEST_SEARCH_PARITY !== '1', 'Requires the guarded search parity domain fixture.');
  const query = 'domain=search-parity-fixture&topicID=ignored&topicID=%22topic_0080%22&per_page=10&sort=name&ord=asc';
  for (const width of [1440, 390]) {
    for (const mode of ['enhanced', 'no-javascript', 'failed-assets']) {
      test(`${mode} bookmarks, constraints, pagination and comparison at ${width}px`, async ({ browser, baseURL }, info) => {
        const context = await browser.newContext({ baseURL, viewport: { width, height: 900 },
          javaScriptEnabled: mode !== 'no-javascript', ignoreHTTPSErrors: process.env.BIOTOOLS_TEST_LOCAL_TLS === '1' });
        try {
          const page = await context.newPage();
          const scripts = [];
          page.on('request', request => { if (request.resourceType() === 'script') scripts.push(request.url()); });
          if (mode === 'failed-assets') await page.route('**/static/modern/**', route => route.abort());
          const response = await page.goto('/t?' + query);
          expect(response.status()).toBe(200);
          const rows = page.locator('[data-tool-id]');
          await expect(rows).toHaveCount(10);
          await expect(rows.first()).toContainText('Workspace sample 01');
          await expect(page.getByRole('list', { name: 'Active filters' })).toContainText('search-parity-fixture');
          await expect(page.getByRole('list', { name: 'Active filters' })).toContainText('topic_0080');
          if (mode === 'enhanced') await expect(page.locator('.search-workspace')).toBeVisible();
          await page.getByRole(mode === 'enhanced' ? 'button' : 'link', { name: 'Next', exact: true }).click();
          await expect(rows).toHaveCount(3);
          await expect(rows.first()).toContainText('Workspace sample 11');
          expect(new URL(page.url()).searchParams.get('domain')).toBe('search-parity-fixture');
          await page.reload();
          await expect(rows).toHaveCount(3);
          await page.goBack();
          await expect(rows).toHaveCount(10);
          if (mode === 'enhanced') {
            await page.getByLabel('Table', { exact: true }).check();
            await expect(page.locator('tbody tr')).toHaveCount(10);
            await page.locator('.comparison-columns summary').click();
            await page.locator('.comparison-columns').getByLabel('Homepage', { exact: true }).check();
            await expect(page.locator('tbody tr').first()).toContainText('https://example.org/workspace-sample-01');
          } else {
            await page.getByLabel('View', { exact: true }).selectOption('table');
            await page.getByRole('button', { name: 'Apply filters', exact: true }).click();
            await expect(page.locator('tbody tr')).toHaveCount(10);
          }
          await expect(page.getByRole('region', { name: 'Tool results table' })).toBeVisible();
          expect(await page.locator('html').evaluate(element => element.scrollWidth <= innerWidth)).toBe(true);
          await page.screenshot({ path: info.outputPath(`${mode}-${width}.png`), fullPage: true });
          expect(new URL(page.url()).searchParams.has('_legacy')).toBe(false);
          expect(scripts.some(url => url.includes('/dist/'))).toBe(false);
          await page.goto('/t?domain=search-parity-fixture&inputDataTypeID=%22data_2044%22');
          if (mode === 'enhanced') {
            await expect(page.locator('.search-workspace')).toBeVisible();
            if (width < 760) await page.getByRole('button', { name: 'Show filters' }).click();
          } else {
            await page.locator('.native-filters > summary').click();
          }
          const functions = page.locator('[data-filter-group="function"]');
          const inputs = page.locator('[data-filter-group="function.input"]');
          const data = page.locator('[data-filter-group="function.input.data"]');
          for (const group of [functions, inputs, data]) await expect(group).toHaveAttribute('open', '');
          const field = page.locator(mode === 'enhanced' ? '#filter-inputDataTypeID' : '#native-inputDataTypeID');
          await expect(field).toBeVisible();
          await expect(field).toHaveValue('"data_2044"');
          await inputs.locator(':scope > summary').focus();
          await page.keyboard.press('Enter');
          await expect(field).toBeHidden();
          await page.keyboard.press('Enter');
          await expect(field).toBeVisible();
          await field.fill('"data_2045"');
          if (mode === 'enhanced') await field.press('Tab');
          else await page.getByRole('button', { name: 'Apply filters', exact: true }).click();
          await expect(page).toHaveURL(url => url.searchParams.get('inputDataTypeID') === '"data_2045"');
          await page.reload();
          if (mode === 'enhanced') {
            await expect(page.locator('.search-workspace')).toBeVisible();
            if (width < 760) await page.getByRole('button', { name: 'Show filters' }).click();
          } else await page.locator('.native-filters > summary').click();
          await expect(field).toHaveValue('"data_2045"');
          await expect(field).toBeVisible();
          expect(await page.locator('html').evaluate(element => element.scrollWidth <= innerWidth)).toBe(true);
          await page.screenshot({ path: info.outputPath(`nested-filters-${mode}-${width}.png`), fullPage: true });
          await page.goto('/t?domain=missing-search-parity-domain');
          await expect(page.getByRole('heading', { name: 'No tools found' })).toBeVisible();
          const invalid = await page.goto('/t?historicalUnknown=x');
          expect(invalid.status()).toBe(400);
          await expect(page.getByRole('alert')).toBeVisible();
        } finally { await context.close(); }
      });
    }
  }
});
