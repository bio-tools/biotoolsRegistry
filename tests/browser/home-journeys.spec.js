const { test, expect } = require('./fixtures');

test.describe('Home page journeys', () => {
  test.skip(process.env.BIOTOOLS_TEST_LIVE_FILTERS !== '1', 'Requires the local database-backed preview.');
  for (const width of [1440, 390]) {
    test(`journey actions, example and input/output filters at ${width}px`, async ({ page }) => {
      await page.setViewportSize({ width, height: 900 });
      await page.goto('/');
      for (const name of ['Find a tool', 'Plan a workflow', 'Explore collections', 'Use tools with other services']) {
        await expect(page.getByRole('heading', { name, exact: true })).toBeVisible();
      }
      await expect(page.getByRole('link', { name: 'Create a collection' })).toHaveAttribute('href', '/edit-domain/');
      await expect(page.getByRole('link', { name: 'Register a tool' })).toHaveAttribute('href', '/register');
      await expect(page.locator('.journey-examples a').first()).toHaveAttribute('href', /^\/t\?domain=/);
      expect(await page.locator('html').evaluate(element => element.scrollWidth <= innerWidth)).toBe(true);
      await page.getByRole('link', { name: 'Command-line tools for multiple sequence alignment with FASTA input' }).click();
      await expect(page.locator('.result-status').first()).toContainText('tools');
      let params = new URL(page.url()).searchParams;
      expect(params.get('operationID')).toBe('"operation_0492"');
      expect(params.get('inputDataFormatID')).toBe('"format_1929"');
      if (width < 760) await page.getByRole('button', { name: 'Show filters' }).click();
      const direction = page.getByLabel('Match EDAM format in');
      await expect(direction).toHaveValue('input');
      await expect(page.locator('.scientific-field').filter({ has: direction })).toContainText('FASTA');
      await direction.selectOption('output');
      await expect.poll(() => new URL(page.url()).searchParams.get('outputDataFormatID')).toBe('"format_1929"');
      await expect.poll(() => new URL(page.url()).searchParams.has('inputDataFormatID')).toBe(false);
      await page.reload();
      if (width < 760) await page.getByRole('button', { name: 'Show filters' }).click();
      await expect(direction).toHaveValue('output');
      await page.goBack();
      await expect(direction).toHaveValue('input');
    });
    test(`EDAM suggestions support keyboard and exact concept search at ${width}px`, async ({ page }) => {
      await page.setViewportSize({ width, height: 900 });
      await page.goto('/');
      const field = page.getByRole('combobox', { name: 'Search bio.tools' });
      await field.fill('protein fold');
      const suggestion = page.getByRole('option').filter({ hasText: 'Protein folds and structural domains' });
      await expect(suggestion).toBeVisible();
      await field.press('ArrowDown');
      await expect(field).toHaveAttribute('aria-activedescendant', /home-suggestion-/);
      await field.press('Escape');
      await expect(field).toHaveAttribute('aria-expanded', 'false');
      await field.fill('protein folds');
      await expect(suggestion).toBeVisible();
      await suggestion.click();
      await expect.poll(() => new URL(page.url()).searchParams.get('topicID')).toMatch(/topic_\d{4}/);
      await expect(page.locator('.result-status').first()).toContainText('tools');
    });
  }
  test('free-text search still works if EDAM lookup fails', async ({ page }) => {
    await page.route('**/_edam/terms/**', route => route.fulfill({ status: 503, json: { error: { message: 'offline' } } }));
    await page.goto('/');
    const field = page.getByRole('combobox', { name: 'Search bio.tools' });
    await field.fill('MAFFT');
    await expect(page.locator('#home-suggestion-status')).toContainText('still search by text');
    await field.press('Enter');
    await expect.poll(() => new URL(page.url()).searchParams.get('q')).toBe('MAFFT');
    await expect(page.locator('.result-status').first()).toContainText('tools');
  });
  test('home actions and free-text search work without JavaScript', async ({ browser, baseURL }) => {
    const context = await browser.newContext({ baseURL, javaScriptEnabled: false });
    try {
      const page = await context.newPage();
      await page.goto('/');
      await expect(page.getByRole('heading', { name: 'Plan a workflow' })).toBeVisible();
      await page.getByLabel('Search bio.tools', { exact: true }).fill('MAFFT');
      await page.getByRole('button', { name: 'Search', exact: true }).click();
      expect(new URL(page.url()).searchParams.get('q')).toBe('MAFFT');
      await expect(page.getByRole('link', { name: 'MAFFT', exact: true }).first()).toBeVisible();
    } finally { await context.close(); }
  });
});
