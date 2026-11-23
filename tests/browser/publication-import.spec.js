const { test, expect } = require('./fixtures');

test('review publication suggestions without publishing the draft', async ({ page, baseURL }) => {
  test.skip(process.env.BIOTOOLS_TEST_PUB2TOOLS !== '1', 'Requires the local preview and a disposable account.');
  test.setTimeout(240000);
  const username = process.env.BIOTOOLS_PUB2TOOLS_TEST_USER || '';
  if (baseURL !== 'http://localhost:8005' || !/^pubtest[a-f0-9]{12}$/.test(username)) {
    throw new Error('Use the local preview and a unique disposable pubtest username.');
  }
  await page.goto('/signup');
  await page.getByLabel(/^Email:$/).fill(username + '@example.invalid');
  await page.getByLabel(/^Username:$/).fill(username);
  await page.getByLabel(/^Password:$/).fill('Publication-test-only-2026!');
  await page.getByLabel(/^Password \(again\):$/).fill('Publication-test-only-2026!');
  await page.getByRole('button', { name: 'Create account', exact: true }).click();
  await expect(page.getByRole('heading', { name: 'Account created' })).toBeVisible();
  await page.goto('/register');
  await page.getByRole('textbox', { name: 'Name', exact: true }).fill('Curated draft');
  await page.getByLabel('bio.tools ID', { exact: true }).fill('publication-' + username);
  await page.getByText('Import metadata from a publication', { exact: true }).click();
  await page.getByLabel('DOI, PMID, PMCID or publication URL').fill('10.1093/nar/gkad347');
  await page.getByLabel('Supporting document or webpage URL (optional)').fill('https://biit.cs.ut.ee/gprofiler/page/docs');
  const response = page.waitForResponse(r => r.url().endsWith('/pub2tools-import'), { timeout: 195000 });
  await page.getByRole('button', { name: 'Get suggestions', exact: true }).click();
  expect((await response).status()).toBe(200);
  const section = page.locator('details.github-import').filter({ hasText: 'Import metadata from a publication' });
  await expect(section.getByText('0 pending field changes', { exact: true })).toBeVisible();
  await expect(page.getByRole('textbox', { name: 'Name', exact: true })).toHaveValue('Curated draft');
  await section.getByLabel('Action for Name', { exact: true }).selectOption('replace');
  await page.setViewportSize({ width: 390, height: 900 });
  expect(await page.locator('html').evaluate(html => html.scrollWidth <= innerWidth)).toBe(true);
  await section.getByRole('button', { name: 'Apply to draft', exact: true }).click();
  await expect(page.getByRole('textbox', { name: 'Name', exact: true })).toHaveValue('g:Profiler');
  await expect(page.getByLabel('bio.tools ID', { exact: true })).toHaveValue('publication-' + username);
});
