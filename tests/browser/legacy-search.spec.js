const { test, expect, openFilterField } = require('./fixtures');

test('legacy records are hidden until explicitly selected', async ({ page, request, baseURL }) => {
  test.skip(process.env.BIOTOOLS_TEST_LIVE_LEGACY !== '1', 'Requires a local preview with legacy records.');
  if (!['localhost', '127.0.0.1'].includes(new URL(baseURL).hostname)) throw new Error('Local preview required.');
  const legacy = await (await request.get('/_search/data/', { params: { maturity: 'Legacy', per_page: '10' } })).json();
  expect(legacy.count).toBeGreaterThan(0);
  await page.goto('/t');
  await expect(page.getByText('Legacy tools are hidden by default.', { exact: false })).toBeVisible();
  await page.locator('[data-filter-group=""] > summary').click();
  await openFilterField(page, 'maturity');
  const maturity = page.getByLabel('Maturity', { exact: true });
  await maturity.fill('"Legacy"');
  await maturity.press('Tab');
  await expect(page).toHaveURL(url => url.searchParams.get('maturity') === '"Legacy"');
  await expect(page.getByRole('status').filter({ hasText: `${legacy.count} tools` })).toBeVisible();
  await page.reload();
  await expect(page.getByLabel('Maturity', { exact: true })).toHaveValue('"Legacy"');
});

test('legacy selection also works without JavaScript', async ({ browser, baseURL }) => {
  test.skip(process.env.BIOTOOLS_TEST_LIVE_LEGACY !== '1', 'Requires a local preview with legacy records.');
  if (!['localhost', '127.0.0.1'].includes(new URL(baseURL).hostname)) throw new Error('Local preview required.');
  const context = await browser.newContext({ baseURL, javaScriptEnabled: false });
  try {
    const page = await context.newPage();
    await page.goto('/t');
    await page.locator('.native-filters > summary').click();
    await page.locator('[data-filter-group=""] > summary').click();
    await openFilterField(page, 'maturity');
    await page.getByLabel('Maturity', { exact: true }).fill('"Legacy"');
    await page.getByRole('button', { name: 'Apply filters', exact: true }).click();
    await expect(page).toHaveURL(url => url.searchParams.get('maturity') === '"Legacy"');
    await page.locator('.native-filters > summary').click();
    await expect(page.getByLabel('Maturity', { exact: true })).toHaveValue('"Legacy"');
  } finally { await context.close(); }
});
