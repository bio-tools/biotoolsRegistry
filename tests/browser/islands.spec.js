const { test, expect } = require('./fixtures');

const preview = '/_migration/html/islands/';

test.describe('Vue island runtime', () => {
  test.skip(process.env.BIOTOOLS_TEST_ISLANDS !== '1', 'Set BIOTOOLS_TEST_ISLANDS=1 with the modern assets built.');

  for (const width of [1440, 390]) {
    test(`independent roots and repeated fragment/root replacement at ${width}px`, async ({ page }, testInfo) => {
      const errors = [];
      page.on('pageerror', error => errors.push(error.message));
      page.on('console', message => {
        if (['error', 'warning'].includes(message.type())) errors.push(message.text());
      });
      await page.setViewportSize({ width, height: 844 });
      await page.goto(preview);
      const first = page.getByRole('status', { name: 'First counter', exact: true });
      const second = page.getByRole('status', { name: 'Second counter', exact: true });
      await expect(first).toHaveText('3');
      await expect(second).toHaveText('7');
      await page.locator('header').evaluate(header => { header.dataset.retained = 'yes'; });
      await page.evaluate(() => { window.islandUnmounts = []; });
      for (let cycle = 0; cycle < 5; cycle++) {
        await page.getByRole('button', { name: 'Increase First counter', exact: true }).click();
        await page.getByRole('button', { name: 'Increase Second counter', exact: true }).click();
        await expect(first).toHaveText('4');
        await expect(second).toHaveText('8');
        // Observe Vue's public teardown hook without adding production diagnostics.
        await page.locator('[data-vue-island]').evaluateAll(roots => {
          roots.forEach(root => root.__vue_app__.onUnmount(() => {
            window.islandUnmounts.push(root.isConnected);
          }));
        });
        const response = page.waitForResponse(response => response.request().headers()['hx-request'] === 'true');
        await page.getByRole('button', { name: 'Reset counters', exact: true }).click();
        expect((await response).status()).toBe(200);
        await expect(first).toHaveText('3');
        await expect(second).toHaveText('7');
        expect(await page.evaluate(() => window.islandUnmounts)).toEqual(Array((cycle + 1) * 2).fill(true));
        await expect(page.locator('[data-vue-island]')).toHaveCount(2);
      }
      await page.getByRole('button', { name: 'Increase Second counter', exact: true }).click();
      for (let cycle = 0; cycle < 3; cycle++) {
        await page.getByRole('button', { name: 'Increase First counter', exact: true }).click();
        await expect(first).toHaveText('4');
        await page.getByRole('button', { name: 'Reset first counter', exact: true }).click();
        await expect(first).toHaveText('3');
        await expect(second).toHaveText('8');
      }
      await expect(page.locator('header')).toHaveAttribute('data-retained', 'yes');
      await expect(page.locator('.site-header')).toHaveCSS('background-color', 'rgb(0, 84, 114)');
      await expect(page.locator('.counter-controls').first()).toHaveCSS('display', 'flex');
      expect(await page.locator('.brand img').evaluate(image => image.complete && image.naturalWidth > 0)).toBe(true);
      expect(await page.locator('html').evaluate(html => html.scrollWidth <= innerWidth)).toBe(true);
      const increase = page.getByRole('button', { name: 'Increase First counter', exact: true });
      await increase.focus();
      await page.keyboard.press('Enter');
      await expect(first).toHaveText('4');
      const screenshot = testInfo.outputPath('vue-islands.png');
      await page.screenshot({ path: screenshot, fullPage: true });
      await testInfo.attach(`islands-${width}`, { path: screenshot, contentType: 'image/png' });
      await page.reload();
      await expect(first).toHaveText('3');
      expect(errors).toEqual([]);
    });
  }

  test('inserts removed roots and keeps markup-like fragment props inert', async ({ page }) => {
    await page.goto(preview);
    await expect(page.locator('output')).toHaveCount(2);
    await page.route('**/islands/', route => route.fulfill({
      contentType: 'text/html', body: '<section id="island-demos" aria-label="Counters"></section>',
    }));
    await page.getByRole('button', { name: 'Reset counters', exact: true }).click();
    await expect(page.locator('[data-vue-island]')).toHaveCount(0);
    await page.unroute('**/islands/');
    const label = '</script></template><img src=x onerror="window.islandInjection=true"> & text';
    const safeLabel = JSON.stringify(label).replace(/</g, '\\u003C').replace(/>/g, '\\u003E').replace(/&/g, '\\u0026');
    await page.route('**/islands/', async route => {
      const response = await route.fetch();
      const body = (await response.text()).replace('"label": "First counter"', `"label": ${safeLabel}`);
      await route.fulfill({ response, body });
    });
    await page.getByRole('button', { name: 'Reset counters', exact: true }).click();
    await expect(page.locator('#first-counter h2')).toHaveText(label);
    await expect(page.locator('#first-counter img')).toHaveCount(0);
    expect(await page.evaluate(() => window.islandInjection)).toBeUndefined();
    await page.locator('#first-counter button[title="Increase"]').click();
    await expect(page.locator('#first-counter output')).toHaveText('4');
  });

  test.describe('without JavaScript', () => {
    test.use({ javaScriptEnabled: false });
    test('keeps server values and a native reset form', async ({ page }) => {
      await page.goto(preview);
      await expect(page.getByRole('heading', { name: 'First counter' })).toBeVisible();
      await expect(page.locator('#first-counter p')).toHaveText('3');
      await page.getByRole('button', { name: 'Reset counters', exact: true }).click();
      await expect(page.getByRole('heading', { name: 'Vue runtime preview' })).toBeVisible();
      await expect(page.locator('#first-counter p')).toHaveText('3');
    });
  });
});
