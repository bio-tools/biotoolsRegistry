const { test, expect } = require('./fixtures');

const preview = '/_migration/html/preview/';

test.describe('Progressive HTML', () => {
  test.skip(process.env.BIOTOOLS_TEST_HTML_SHELL !== '1', 'Set BIOTOOLS_TEST_HTML_SHELL=1 with the modern assets built.');

  for (const width of [1440, 390]) {
    test(`fragment swap, canonical history and refresh at ${width}px`, async ({ page }, testInfo) => {
      await page.setViewportSize({ width, height: 844 });
      await page.goto(preview);
      await page.locator('header').evaluate(header => { header.dataset.retained = 'yes'; });
      await page.getByLabel('Message:', { exact: true }).fill('Hello & welcome');
      const responsePromise = page.waitForResponse(response => response.request().headers()['hx-request'] === 'true');
      await page.getByRole('button', { name: 'Preview', exact: true }).click();
      const response = await responsePromise;
      expect(response.status()).toBe(200);
      expect(await response.text()).not.toContain('<!doctype html>');
      await expect(page.locator('#preview-result')).toHaveText('Hello & welcome');
      await expect(page.locator('header')).toHaveAttribute('data-retained', 'yes');
      await expect(page).toHaveURL(url => url.searchParams.get('message') === 'Hello & welcome');
      await page.goBack();
      await expect(page.locator('#preview-result')).toHaveText('Welcome to bio.tools.');
      await expect(page).toHaveURL(url => url.pathname === preview && !url.search);
      await page.goForward();
      await expect(page.locator('#preview-result')).toHaveText('Hello & welcome');
      await page.reload();
      await expect(page.getByRole('heading', { name: 'Message preview', exact: true })).toBeVisible();
      await expect(page.locator('#preview-result')).toHaveText('Hello & welcome');
      expect(await page.locator('html').evaluate(html => html.scrollWidth <= innerWidth)).toBe(true);
      await testInfo.attach(`htmx-${width}`, { body: await page.screenshot({ fullPage: true }), contentType: 'image/png' });
    });
  }

  test('loading, server, network and validation failures allow retry', async ({ page }) => {
    await page.goto(preview);
    let release;
    const pending = new Promise(resolve => { release = resolve; });
    await page.route('**/preview/?*', async route => {
      await pending;
      await route.fulfill({ status: 500, contentType: 'text/html', body: 'Server error' });
    });
    await page.getByLabel('Message:', { exact: true }).fill('Retry message');
    const submit = page.getByRole('button', { name: 'Preview', exact: true });
    await submit.click();
    await expect(page.locator('#preview-loading')).toBeVisible();
    await expect(submit).toBeDisabled();
    release();
    await expect(page.getByRole('alert')).toContainText('The request could not be completed');
    await expect(submit).toBeEnabled();
    await expect(page.locator('#preview-loading')).toBeHidden();
    await expect(page.locator('#preview-result')).toHaveText('Welcome to bio.tools.');
    await expect(page).toHaveURL(url => !url.search);
    await page.unroute('**/preview/?*');
    await page.route('**/preview/?*', route => route.abort());
    await submit.click();
    await expect(page.getByRole('alert')).toBeVisible();
    await expect(submit).toBeEnabled();
    await page.unroute('**/preview/?*');
    await page.getByLabel('Message:', { exact: true }).fill('   ');
    const invalidResponse = page.waitForResponse(response => response.status() === 400);
    await submit.click();
    await invalidResponse;
    await expect(page.getByRole('alert')).toBeVisible();
    await expect(page.locator('#preview-result')).toHaveText('Welcome to bio.tools.');
    await page.getByLabel('Message:', { exact: true }).fill('Retry message');
    await submit.click();
    await expect(page.locator('#preview-result')).toHaveText('Retry message');
    await expect(page.getByRole('alert')).toBeHidden();
  });

  for (const fallback of ['disabled', 'unavailable']) {
    test.describe(`JavaScript ${fallback}`, () => {
      test.use({ javaScriptEnabled: fallback !== 'disabled' });
      test('GET submission returns a complete canonical page', async ({ page }) => {
        if (fallback === 'unavailable') {
          await page.route('**/static/modern/**', route => route.abort());
        }
        await page.goto(preview);
        await page.getByLabel('Message:', { exact: true }).fill('Native submission');
        const responsePromise = page.waitForResponse(response => response.request().isNavigationRequest());
        await page.getByRole('button', { name: 'Preview', exact: true }).click();
        const response = await responsePromise;
        expect(response.status()).toBe(200);
        expect(response.request().headers()['hx-request']).toBeUndefined();
        expect(await response.text()).toContain('<!doctype html>');
        await expect(page.locator('#preview-result')).toHaveText('Native submission');
        await expect(page).toHaveURL(url => url.searchParams.get('message') === 'Native submission');
        await page.reload();
        await expect(page.locator('#preview-result')).toHaveText('Native submission');
      });
    });
  }
});
