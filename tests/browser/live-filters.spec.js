const { test, expect, openFilterField, openAdvancedField } = require('./fixtures');

test.describe('Registry filter sidebar', () => {
  test.skip(process.env.BIOTOOLS_TEST_LIVE_FILTERS !== '1', 'Requires a populated local registry.');
  for (const width of [1440, 390]) {
    test(`compact fields retain selections and keyboard access at ${width}px`, async ({ page }) => {
      await page.setViewportSize({ width, height: 900 });
      await page.goto('/t');
      if (width < 760) await page.getByRole('button', { name: 'Show filters' }).click();
      const group = page.locator('[data-filter-group=""]');
      const summary = group.locator(':scope > summary');
      await summary.focus();
      await page.keyboard.press('Enter');
      const fields = group.locator(':scope > .filter-group-body > .filter-field:visible');
      await expect(fields).toHaveCount(6);
      const more = group.getByRole('button', { name: /Show all .* fields/ });
      await more.focus();
      await page.keyboard.press('Enter');
      await expect.poll(() => fields.count()).toBeGreaterThan(6);
      await openFilterField(page, 'maturity');
      await page.getByLabel('Maturity', { exact: true }).fill('"Legacy"');
      await page.getByLabel('Maturity', { exact: true }).press('Tab');
      await expect(page).toHaveURL(url => url.searchParams.get('maturity') === '"Legacy"');
      await group.getByRole('button', { name: 'Show fewer fields' }).click();
      await expect(group.locator('[data-filter-field="maturity"]')).toBeVisible();
      await expect(group.locator('[data-filter-field="maturity"] > summary')).toContainText('Legacy');
      await page.reload();
      if (width < 760) await page.getByRole('button', { name: 'Show filters' }).click();
      await expect(page.getByLabel('Maturity', { exact: true })).toHaveValue('"Legacy"');
      expect(await page.locator('html').evaluate(html => html.scrollWidth <= innerWidth)).toBe(true);
    });
    test(`searches real domains, names and EDAM terms at ${width}px`, async ({ page, request }) => {
      await page.setViewportSize({ width, height: 900 });
      await page.emulateMedia({ colorScheme: 'dark' });
      const errors = [];
      page.on('pageerror', error => errors.push(error.message));
      await page.goto('/t');
      await expect(page.locator('.result-status').first()).toContainText('tools');
      if (width < 760) await page.getByRole('button', { name: 'Show filters' }).click();
      const sidebar = page.locator('aside[aria-label="Search filters"]');
      await expect(sidebar.locator('.advanced-panel')).toHaveCount(1);
      await expect(sidebar.locator('[data-filter-group="function"]')).toHaveCount(0);
      for (const [scope, label, key] of [
        ['topic', 'topic', 'topicID'], ['operation', 'operation', 'operationID'],
        ['data', 'data type', 'dataTypeID'], ['format', 'format', 'dataFormatID'],
      ]) {
        await sidebar.getByRole('button', { name: `Choose edam ${label}`, exact: true }).click();
        const dialog = page.getByRole('dialog');
        const options = dialog.getByRole('option');
        await expect(options.first()).toBeVisible();
        await options.first().click();
        const chosen = await dialog.locator('.selected-terms li').first().innerText();
        await dialog.getByRole('button', { name: 'Apply selection' }).click();
        await expect.poll(() => new URL(page.url()).searchParams.has(key)).toBe(true);
        const selected = new URL(page.url()).searchParams.get(key);
        expect(selected).toMatch(new RegExp(`${scope}_[0-9]+`));
        await expect(sidebar).toContainText(chosen.replace('×', '').trim());
        const result = await request.get('/_search/data/', { params: { [key]: selected } });
        expect(result.status()).toBe(200);
        expect((await result.json()).count).toBeGreaterThanOrEqual(0);
        await page.getByRole('button', { name: `Remove ${key} filter` }).click();
      }
      await sidebar.locator('[data-filter-group="registry"] > summary').click();
      await openFilterField(page, 'domain');
      const domains = sidebar.locator('#filter-domain');
      await expect.poll(async () => domains.locator('option').count()).toBeGreaterThan(1);
      const domain = await domains.locator('option').nth(1).getAttribute('value');
      await domains.selectOption(domain);
      await expect.poll(() => new URL(page.url()).searchParams.get('domain')).toBe(domain);
      await page.getByRole('button', { name: 'Remove domain filter' }).click();
      const creditGroup = sidebar.locator('[data-filter-group="credit"]');
      await creditGroup.locator('summary').first().click();
      await openFilterField(page, 'creditName');
      const credit = sidebar.locator('#filter-creditName');
      await expect(credit).toBeVisible();
      await credit.click();
      let dialog = page.getByRole('dialog');
      await dialog.locator('input[type="search"]').fill('smith');
      await expect.poll(() => dialog.locator('.choice-list button').count(), { timeout: 15000 }).toBeGreaterThan(0);
      await dialog.getByRole('button', { name: 'Cancel' }).click();
      await sidebar.locator('[data-filter-group=""] > summary').click();
      await openFilterField(page, 'collectionID');
      await sidebar.locator('#filter-collectionID').click();
      dialog = page.getByRole('dialog');
      await dialog.locator('input[type="search"]').fill('3D-BioInfo');
      await dialog.getByRole('button', { name: '3D-BioInfo', exact: true }).click();
      await expect.poll(() => new URL(page.url()).searchParams.get('collectionID')).toBe('"3D-BioInfo"');
      await expect(page.locator('.result-status').first()).toContainText('10 tools');
      await expect(page.locator('article[data-tool-id="swiss-model_workspace"]')).toBeVisible();
      await page.getByRole('button', { name: 'Remove collectionID filter' }).click();
      if (!await sidebar.locator('[data-filter-group=""]').evaluate(element => element.open)) await sidebar.locator('[data-filter-group=""] > summary').click();
      await openFilterField(page, 'license');
      await sidebar.locator('#filter-license').click();
      dialog = page.getByRole('dialog');
      await dialog.locator('input[type="search"]').fill('Apache-2.0');
      await dialog.getByRole('button', { name: 'Apache-2.0', exact: true }).click();
      await expect.poll(() => new URL(page.url()).searchParams.get('license')).toBe('"Apache-2.0"');
      await page.getByRole('button', { name: 'Remove license filter' }).click();
      await expect(page.locator('.tool-result').first()).toBeVisible();
      const sizes = await page.evaluate(() => {
        const size = selector => getComputedStyle(document.querySelector(selector)).fontSize;
        return [size('.header-search input'), size('#workspace-query'), size('.header-search button'), size('.filter-heading button'),
          size('.scientific-filters summary'), size('.advanced-panel summary'), size('.site-header nav a'), size('.tool-result p')];
      });
      expect(sizes[0]).toBe(sizes[1]);
      expect(sizes[2]).toBe(sizes[3]);
      expect(sizes[4]).toBe(sizes[5]);
      expect(sizes[6]).toBe(sizes[7]);
      const colors = await page.evaluate(() => {
        const style = getComputedStyle(document.querySelector('#search-sort option'));
        return [style.color, style.backgroundColor, getComputedStyle(document.documentElement).colorScheme];
      });
      expect(colors).toEqual(['rgb(38, 58, 67)', 'rgb(255, 255, 255)', 'light']);
      expect(await page.locator('html').evaluate(html => html.scrollWidth <= innerWidth)).toBe(true);
      expect(errors).toEqual([]);
    });
  }
  test('matching options and candidate date filters remain usable', async ({ page }) => {
    await page.goto('/t');
    await page.locator('.matching-options > summary').click();
    await page.getByLabel('Within each category').selectOption('any');
    await page.getByLabel('EDAM hierarchy').selectOption('narrower');
    await expect(page).toHaveURL(url => url.searchParams.get('edamMatch') === 'any' && url.searchParams.get('edamExpand') === 'narrower');
    await page.locator('.advanced-panel > summary').click();
    await openAdvancedField(page, 'added');
    await page.getByLabel('Added on or after', { exact: true }).fill('2020-01-01');
    await page.getByLabel('Added on or after', { exact: true }).press('Tab');
    await expect(page.locator('.candidate-scope')).toBeVisible();
    await page.getByRole('button', { name: 'Apply to all matches', exact: true }).click();
    await expect(page).toHaveURL(url => JSON.parse(url.searchParams.get('advanced') || '[]').some(filter => filter.field === 'added'));
    await page.reload();
    await page.locator('.advanced-panel > summary').click();
    await expect(page.locator('.server-filters')).toContainText('2020-01-01');
  });
  test('shared header typography is consistent on public pages', async ({ page }) => {
    for (const route of ['/', '/about', '/psiclass', '/workflows/design/']) {
      await page.goto(route);
      const sizes = await page.evaluate(() => {
        const size = selector => getComputedStyle(document.querySelector(selector)).fontSize;
        return [size('body'), size('.site-header nav a'), size('.header-search input'), size('.header-search button')];
      });
      expect(sizes).toEqual(['14px', '14px', '14px', '14px']);
    }
  });
});
