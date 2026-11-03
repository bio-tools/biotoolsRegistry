const { test, expect } = require('./fixtures');

test.describe('Django HTML shell', () => {
  test.skip(process.env.BIOTOOLS_TEST_HTML_SHELL !== '1', 'Set BIOTOOLS_TEST_HTML_SHELL=1 on a deployment with the isolated Django mount.');
  test.use({ javaScriptEnabled: false });

  for (const viewport of [{ width: 1440, height: 1000 }, { width: 390, height: 844 }]) {
    test(`complete page and CSRF form without JavaScript at ${viewport.width}px`, async ({ page }, testInfo) => {
      await page.setViewportSize(viewport);
      const response = await page.goto('/_migration/html/');
      expect(response.status()).toBe(200);
      await expect(page.getByRole('main').getByRole('heading', { name: 'bio.tools', exact: true })).toBeVisible();
      await expect(page.getByRole('navigation', { name: 'Main navigation' })).toBeVisible();
      await expect(page.getByRole('contentinfo')).toBeVisible();
      await expect(page.getByRole('search', { name: 'Site-wide search' })).toHaveAttribute('action', '/t');
      await expect(page.getByRole('main').getByRole('search')).toHaveAttribute('action', '/t');
      await expect(page.getByLabel('Search tools')).toBeVisible();
      await expect(page.locator('script[src*="/dist/"], [ng-app]')).toHaveCount(0);
      expect(await page.getByRole('img', { name: 'bio.tools', exact: true }).evaluate(img => img.complete && img.naturalWidth > 0)).toBe(true);
      await expect(page.getByRole('img', { name: 'bio.tools', exact: true })).toHaveAttribute('src', '/static/html/biotools-white.svg');
      await expect(page.getByRole('banner')).toHaveCSS('background-color', 'rgb(0, 84, 114)');
      const headerSizes = await page.locator('.site-header').evaluate(header => ({
        search: getComputedStyle(header.querySelector('.header-search input')).fontSize,
        navigation: getComputedStyle(header.querySelector('nav')).fontSize,
      }));
      expect(headerSizes.search).toBe(headerSizes.navigation);
      await expect(page.getByRole('navigation', { name: 'Main navigation' }).getByRole('link', { name: 'Tools', exact: true })).toHaveCSS('color', 'rgb(255, 255, 255)');
      await expect(page.getByRole('button', { name: 'Search', exact: true })).toHaveCSS('background-color', 'rgb(0, 84, 114)');
      await expect(page.locator('body')).toHaveCSS('display', 'flex');
      expect(await page.locator('html').evaluate(html => html.scrollWidth <= window.innerWidth)).toBe(true);

      await page.getByRole('button', { name: 'Check session', exact: true }).click();
      await expect(page).toHaveURL(url => url.pathname === '/_migration/html/');
      await expect(page.getByRole('status')).toHaveText('Session check complete.');
      await testInfo.attach(`shell-${viewport.width}`, {
        body: await page.screenshot({ fullPage: true }), contentType: 'image/png',
      });
      await page.reload();
      await expect(page.getByRole('status')).toHaveCount(0);
      await expect(page.getByRole('main').getByRole('heading', { name: 'bio.tools', exact: true })).toBeVisible();
    });
  }
});
