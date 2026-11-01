const { test, expect } = require('./fixtures');

test.skip(process.env.BIOTOOLS_TEST_CUTOVER !== '1', 'Requires the canonical search and detail fixtures.');

async function expectResults(page, tool, parameters) {
  await expect(page).toHaveURL(url => url.pathname === '/t' &&
    Object.entries(parameters).every(([key, value]) => url.searchParams.get(key) === value ||
      (key === 'ord' && value === 'desc' && !url.searchParams.has(key))));
  await expect(page.getByRole('link', { name: tool.name, exact: true })).toBeVisible();
}

async function expectDetail(page, tool) {
  await expect(page.locator('.tool-detail h1')).toHaveText(tool.name);
  await expect(page.locator('.resource-id')).toHaveText(`biotools:${tool.biotoolsID}`);
  await expect(page.getByRole('link', { name: tool.homepage, exact: true })).toHaveAttribute('href', tool.homepage);
}

test('home to text search to tool detail', async ({ page, tool }) => {
  await page.goto('/');
  await expect(page.getByRole('heading', { name: 'bio.tools', exact: true })).toBeVisible();
  const search = page.getByLabel('Search bio.tools', { exact: true });
  await search.fill(tool.query);
  await search.press('Enter');
  await expectResults(page, tool, { q: tool.query });
  await page.getByRole('link', { name: tool.name, exact: true }).click();
  await expect(page).toHaveURL(url => url.pathname === `/${tool.biotoolsID}`);
  await expectDetail(page, tool);
});

test('applying a tool-type filter updates results and URL', async ({ page, tool }) => {
  await page.goto('/t?' + new URLSearchParams({ q: tool.query }));
  await expectResults(page, tool, { q: tool.query });
  await page.locator('[data-filter-group=""] > summary').click();
  await page.getByRole('button', { name: new RegExp('^' + tool.toolType[0].replace(/[.*+?^${}()|[\]\\]/g, '\\$&')) }).click();
  await expectResults(page, tool, { q: tool.query, toolType: `"${tool.toolType[0]}"` });
});

test('sorting, Back/Forward and refresh preserve a filtered search URL', async ({ page, tool }) => {
  const filters = { q: tool.query, toolType: `"${tool.toolType[0]}"`, sort: 'name', ord: 'asc' };
  await page.goto('/t?' + new URLSearchParams(filters));
  await expectResults(page, tool, filters);
  await page.getByLabel('Order', { exact: true }).selectOption('desc');
  await expectResults(page, tool, { ...filters, ord: 'desc' });
  await page.goBack();
  await expectResults(page, tool, filters);
  await page.goForward();
  await expectResults(page, tool, { ...filters, ord: 'desc' });
  await page.reload();
  await expectResults(page, tool, { ...filters, ord: 'desc' });
});

test('tool detail opens directly in a fresh browser context', async ({ page, tool }) => {
  await page.goto(`/${encodeURIComponent(tool.biotoolsID)}`);
  await expectDetail(page, tool);
});
