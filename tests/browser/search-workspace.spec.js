const { test, expect } = require('./fixtures');

const canonical = process.env.BIOTOOLS_TEST_CUTOVER === '1';
const route = canonical ? '/t' : '/_migration/html/search/';
const endpoint = canonical ? '/_search/data/' : route + 'data/';
const query = 'Workspace sample';

test.describe('Vue search workspace', () => {
  test.skip(process.env.BIOTOOLS_TEST_SEARCH !== '1', 'Set BIOTOOLS_TEST_SEARCH=1 after seeding local workspace samples.');

  for (const width of [1440, 390]) {
    test(`URL history, filters, pages and display modes at ${width}px`, async ({ page, request }, testInfo) => {
      const errors = [];
      page.on('pageerror', error => errors.push(error.message));
      await page.setViewportSize({ width, height: 900 });
      await page.goto(route + '?q=Workspace+sample&per_page=10&page=2&sort=name&ord=asc');
      const querySizes = await page.locator('.query-form').evaluate(form => ({
        field: getComputedStyle(form.querySelector('input')).fontSize,
        label: getComputedStyle(form.querySelector('label')).fontSize,
      }));
      expect(querySizes.field).toBe(querySizes.label);
      const items = page.locator('article[data-tool-id]');
      await expect(items).toHaveCount(3);
      await expect(items.first()).toContainText('Workspace sample 11');
      await expect(page.getByLabel('Page size', { exact: true })).toHaveValue('10');
      await page.reload();
      await expect(items).toHaveCount(3);
      await page.getByLabel('Page size', { exact: true }).selectOption('25');
      await expect(items).toHaveCount(13);
      await expect(page).toHaveURL(url => url.searchParams.get('per_page') === '25' && !url.searchParams.has('page'));
      await page.goBack();
      await expect(items).toHaveCount(3);
      await page.goForward();
      await expect(items).toHaveCount(13);
      for (const size of ['50', '100', '10']) {
        await page.getByLabel('Page size', { exact: true }).selectOption(size);
        await expect(items).toHaveCount(size === '10' ? 10 : 13);
        await page.reload();
        await expect(page.getByLabel('Page size', { exact: true })).toHaveValue(size);
        await expect(items).toHaveCount(size === '10' ? 10 : 13);
      }
      await page.getByRole('button', { name: 'Next', exact: true }).click();
      await expect(items).toHaveCount(3);
      await page.getByRole('button', { name: 'Previous', exact: true }).click();
      await expect(items).toHaveCount(10);
      if (width < 760) await page.getByRole('button', { name: 'Show filters' }).click();
      await page.locator('[data-filter-group=""] > summary').click();
      await page.getByRole('button', { name: 'Command-line tool 7', exact: true }).click();
      await expect(items).toHaveCount(7);
      await expect(page).toHaveURL(url => url.searchParams.get('toolType') === '"Command-line tool"');
      await page.getByLabel('Order', { exact: true }).selectOption('desc');
      await expect(items.first()).toContainText('Workspace sample 13');
      const publicResponse = await request.get('/api/t/', { params: { q: query, toolType: '"Command-line tool"', sort: 'name', ord: 'desc', format: 'json' } });
      const publicBody = await publicResponse.json();
      expect(await items.evaluateAll(nodes => nodes.map(node => node.dataset.toolId))).toEqual(publicBody.list.map(tool => tool.biotoolsID));
      await page.getByLabel('Table', { exact: true }).check();
      const comparison = await page.locator('#search-config').evaluate(node => JSON.parse(node.content.querySelector('script').textContent).comparisonFields);
      await expect(page.getByRole('columnheader', { name: comparison.additionDate, exact: true })).toBeVisible();
      await expect(page.getByRole('columnheader', { name: comparison.lastUpdate, exact: true })).toBeAttached();
      await expect(page.locator('tbody tr')).toHaveCount(7);
      await page.getByLabel('Cards', { exact: true }).check();
      if (width < 760) await page.getByRole('button', { name: 'Hide filters' }).click();
      await page.evaluate(() => scrollTo(0, 0));
      expect(await page.locator('html').evaluate(html => html.scrollWidth <= innerWidth)).toBe(true);
      await expect(page.locator('.site-header')).toHaveCSS('background-color', 'rgb(0, 84, 114)');
      expect(await page.locator('.brand img').evaluate(image => image.complete && image.naturalWidth > 0)).toBe(true);
      const screenshot = testInfo.outputPath('search-workspace.png');
      await page.screenshot({ path: screenshot, fullPage: true });
      await testInfo.attach('search-workspace', { path: screenshot, contentType: 'image/png' });
      await items.first().getByRole('link').click();
      await expect(page.getByRole('heading', { level: 1 })).toContainText('Workspace sample 13');
      await page.goBack();
      await expect(items).toHaveCount(7);
      expect(errors).toEqual([]);
    });
  }

  test('malformed links, empty results, backend error and retry', async ({ page, request }) => {
    for (const query of ['page=0', 'per_page=bad', 'per_page=500', 'sort=unknown', 'unknown=x']) {
      const response = await request.get(endpoint + '?' + query);
      expect(response.status()).toBe(400);
      expect((await response.json()).error.code).toBe('invalid_search');
    }
    await page.goto(route + '?page=0');
    await expect(page.getByRole('alert')).toContainText('Invalid page');
    await page.getByRole('button', { name: 'Clear all' }).click();
    await expect(page.locator('article[data-tool-id]').first()).toBeVisible();
    await page.getByLabel('Search bio.tools', { exact: true }).fill('unmatchableworkspacevalue');
    await expect(page.getByRole('heading', { name: 'No tools found' })).toBeVisible();
    await page.route('**' + endpoint + '**', route => route.fulfill({ status: 503, contentType: 'application/json',
      body: JSON.stringify({ error: { message: 'Search is temporarily unavailable. Please retry.' } }) }));
    await page.getByLabel('Search bio.tools', { exact: true }).fill(query);
    await expect(page.getByRole('alert')).toContainText('temporarily unavailable');
    await page.unroute('**' + endpoint + '**');
    await page.getByRole('button', { name: 'Retry', exact: true }).click();
    await expect(page.locator('article[data-tool-id]')).toHaveCount(13);
    await expect(page.getByRole('alert')).toBeHidden();
  });

  test('a delayed previous response cannot replace a newer query', async ({ page }) => {
    await page.goto(route + '?q=Workspace+sample');
    await expect(page.locator('article[data-tool-id]')).toHaveCount(13);
    let release;
    const gate = new Promise(resolve => { release = resolve; });
    await page.route('**' + endpoint + '**', async intercepted => {
      if (new URL(intercepted.request().url()).searchParams.get('q') === '"Workspace sample 01 (fictional)"') {
        const response = await intercepted.fetch();
        await gate;
        await intercepted.fulfill({ response }).catch(() => {});
      } else await intercepted.continue();
    });
    const pending = page.waitForRequest(request => new URL(request.url()).searchParams.get('q') === '"Workspace sample 01 (fictional)"');
    await page.getByLabel('Search bio.tools', { exact: true }).fill('"Workspace sample 01 (fictional)"');
    await pending;
    await expect(page.getByRole('status')).toHaveText('Searching...');
    await page.getByLabel('Search bio.tools', { exact: true }).fill('"Workspace sample 02 (fictional)"');
    await expect(page.locator('article[data-tool-id]')).toHaveCount(1);
    await expect(page.locator('article h2')).toContainText('Workspace sample 02');
    release();
    await expect(page.locator('article h2')).toContainText('Workspace sample 02');
  });
});
