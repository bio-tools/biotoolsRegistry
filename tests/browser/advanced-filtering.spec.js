const { test, expect } = require('./fixtures');

const route = process.env.BIOTOOLS_TEST_CUTOVER === '1' ? '/t' : '/_migration/html/search/';
const endpoint = process.env.BIOTOOLS_TEST_CUTOVER === '1' ? '/_search/data/' : route + 'data/';

test.describe('Advanced search filtering', () => {
  test.skip(process.env.BIOTOOLS_TEST_SEARCH !== '1', 'Requires the fictional workspace samples.');

  for (const width of [1440, 390]) {
    test(`candidate scope, promotion and history at ${width}px`, async ({ page }, testInfo) => {
      const requests = [];
      const errors = [];
      page.on('request', request => { if (new URL(request.url()).pathname === endpoint) requests.push(request.url()); });
      page.on('pageerror', error => errors.push(error.message));
      await page.setViewportSize({ width, height: 1000 });
      const payload = page.waitForResponse(response => new URL(response.url()).pathname === endpoint);
      await page.goto(route + '?q=Workspace+sample&sort=name&ord=asc&per_page=10');
      const response = await payload;
      const bytes = (await response.body()).length;
      const body = await response.json();
      const items = page.locator('article[data-tool-id]');
      await expect(items).toHaveCount(10);
      if (width < 760) await page.getByRole('button', { name: 'Show filters' }).click();
      await page.locator('.advanced-panel summary').click();
      const session = await page.context().newCDPSession(page);
      const before = await session.send('Runtime.getHeapUsage');
      const originalURL = page.url();
      await page.getByLabel('Added on or after', { exact: true }).fill('2026-01-08');
      await page.getByLabel('Added on or after', { exact: true }).press('Tab');
      await expect(items).toHaveCount(3);
      await expect(page.locator('.candidate-scope')).toContainText('3 of 10 loaded tools');
      await expect(page.locator('.candidate-scope')).toContainText('13 server matches');
      await expect(page.locator('.candidate-scope')).toContainText('Partial candidate set');
      expect(page.url()).toBe(originalURL);
      expect(requests).toHaveLength(1);
      await page.getByLabel('Table', { exact: true }).check();
      await expect(page.locator('tbody tr')).toHaveCount(3);
      await page.getByLabel('Cards', { exact: true }).check();
      await expect(items).toHaveCount(3);
      await expect(page.locator('.candidate-scope')).toContainText('3 of 10 loaded tools');
      expect(requests).toHaveLength(3); // View switches load the selected representation, not promoted filters.
      const after = await session.send('Runtime.getHeapUsage');
      await session.detach();
      const measurement = { width, bytes, candidates: body.candidates, requestsBeforePromotion: requests.length,
        candidateJSONBytes: Buffer.byteLength(JSON.stringify(body.items)),
        heapBefore: before.usedSize, heapAfter: after.usedSize };
      console.log('ADVANCED_FILTER_MEASUREMENTS ' + JSON.stringify(measurement));
      await testInfo.attach('advanced-filter-measurements', { body: JSON.stringify(measurement), contentType: 'application/json' });
      expect(await page.locator('html').evaluate(html => html.scrollWidth <= innerWidth)).toBe(true);
      await page.screenshot({ path: testInfo.outputPath('advanced-candidates.png'), fullPage: true });
      await page.getByRole('button', { name: 'Apply to all matches', exact: true }).click();
      await expect(items).toHaveCount(6);
      await expect(page.locator('.candidate-scope')).toBeHidden();
      await expect(page.locator('.server-filters')).toContainText('Added: 2026-01-08 to any');
      await expect(page.getByRole('status')).toContainText('6 tools');
      expect(requests).toHaveLength(4);
      const promotedURL = page.url();
      expect(JSON.parse(new URL(promotedURL).searchParams.get('advanced'))).toEqual([
        { scope: 'server', type: 'range', field: 'added', min: '2026-01-08' },
      ]);
      await page.reload();
      await expect(items).toHaveCount(6);
      await page.goBack();
      await expect(items).toHaveCount(10);
      await expect(page.locator('.candidate-scope')).toBeHidden();
      await page.goForward();
      await expect(items).toHaveCount(6);
      if (width < 760 && await page.getByRole('button', { name: 'Show filters' }).isVisible()) await page.getByRole('button', { name: 'Show filters' }).click();
      if (!(await page.locator('.advanced-panel').evaluate(element => element.open))) await page.locator('.advanced-panel summary').click();
      await page.getByLabel('Added on or before', { exact: true }).fill('2026-01-10');
      await page.getByLabel('Added on or before', { exact: true }).press('Tab');
      await expect(items).toHaveCount(3);
      await expect(page.locator('.candidate-scope')).toContainText('All server matches loaded');
      await page.getByRole('button', { name: 'Apply to all matches', exact: true }).click();
      await expect(items).toHaveCount(3);
      await expect(page.getByRole('status')).toContainText('3 tools');
      await page.getByRole('button', { name: 'Remove Added: 2026-01-08 to any', exact: true }).click();
      await expect(items).toHaveCount(10);
      await page.getByRole('button', { name: 'Clear all', exact: true }).click();
      await expect(page.locator('.server-filters')).toBeHidden();
      expect(new URL(page.url()).search).toBe('');
      expect(errors).toEqual([]);
    });
  }

  test('Boolean and ontology filters, zero candidates and strict API validation', async ({ page, request }) => {
    await page.goto(route + '?q=Workspace+sample');
    const items = page.locator('article[data-tool-id]');
    await expect(items).toHaveCount(13);
    await page.locator('.advanced-panel summary').click();
    await page.getByLabel('Publication', { exact: true }).selectOption('yes');
    await expect(page.getByRole('heading', { name: 'No candidates match' })).toBeVisible();
    await expect(page.locator('.candidate-scope')).toContainText('0 of 13 loaded tools');
    await page.getByLabel('Publication', { exact: true }).selectOption('no');
    await expect(items).toHaveCount(13);
    await page.getByRole('button', { name: 'Apply to all matches', exact: true }).click();
    await page.getByRole('button', { name: 'Choose edam topic', exact: true }).click();
    const topic = page.getByRole('combobox', { name: 'Find topic terms' });
    await topic.fill('topic_0080');
    await expect(page.getByRole('dialog').getByRole('option')).toHaveCount(1);
    await topic.press('ArrowDown');
    await topic.press('Enter');
    await page.getByRole('button', { name: 'Apply selection', exact: true }).click();
    await expect(items).toHaveCount(13);
    await expect(page.locator('.server-filters li')).toHaveCount(1);
    await expect(page.locator('.active-constraints')).toContainText('topic_0080');
    await expect(items).toHaveCount(13);
    await page.getByLabel('Added on or before', { exact: true }).fill('2025-01-01');
    await page.getByLabel('Added on or before', { exact: true }).press('Tab');
    await expect(page.getByRole('heading', { name: 'No candidates match' })).toBeVisible();
    await page.getByRole('button', { name: 'Apply to all matches', exact: true }).click();
    await expect(page.getByRole('heading', { name: 'No tools found' })).toBeVisible();
    const invalid = JSON.stringify([{ scope: 'server', type: 'script', field: 'anything', value: 'return true' }]);
    const response = await request.get(endpoint, { params: { advanced: invalid } });
    expect(response.status()).toBe(400);
    expect((await response.json()).error.field).toBe('advanced');
    await page.goto(route + '?advanced=' + encodeURIComponent(invalid));
    await expect(page.getByRole('alert')).toContainText('Invalid advanced filters');
    await page.getByRole('button', { name: 'Clear all', exact: true }).click();
    await expect(items.first()).toBeVisible();
  });
});
