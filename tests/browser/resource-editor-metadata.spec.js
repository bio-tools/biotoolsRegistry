const { test, expect, editorUrl } = require('./fixtures');

test.describe('resource metadata editor', () => {
  test.skip(process.env.BIOTOOLS_TEST_EDITOR_WRITES !== '1', 'Requires disposable registry-write opt-in.');
  test.setTimeout(90000);
  for (const width of [1440, 390]) {
    test(`metadata validation and round trip at ${width}px`, async ({ page, request }, info) => {
      await page.setViewportSize({ width, height: 1000 });
      await page.goto(editorUrl());
      await page.getByLabel('Username or email:', { exact: true }).fill(process.env.BIOTOOLS_TEST_USERNAME);
      await page.getByLabel('Password:', { exact: true }).fill(process.env.BIOTOOLS_TEST_PASSWORD);
      await page.getByRole('button', { name: 'Sign in', exact: true }).click();
      const id = 'metadata-browser-' + Date.now();
      await page.getByLabel('Name', { exact: true }).fill('Metadata Browser Sample');
      await page.getByLabel('bio.tools ID', { exact: true }).fill(id);
      await page.getByLabel('Homepage', { exact: true }).fill('https://example.org/metadata');
      await page.getByLabel('Description', { exact: true }).fill('A disposable metadata editor browser regression resource.');
      await page.getByLabel('License', { exact: true }).selectOption('MIT');
      await page.getByRole('button', { name: 'Add version', exact: true }).click();
      await page.getByLabel('Version 1', { exact: true }).fill('2.0');
      await page.getByRole('button', { name: 'Add language', exact: true }).click();
      await page.getByLabel('Language 1', { exact: true }).selectOption('Python');
      await page.getByRole('button', { name: 'Add credit', exact: true }).click();
      const credit = page.locator('#nested-credit');
      await credit.getByLabel('Credit name', { exact: true }).fill('Metadata Contributor');
      await credit.getByLabel('Email', { exact: true }).fill('bad-email');
      await credit.getByLabel('Entity type', { exact: true }).selectOption('Person');
      await credit.getByRole('button', { name: 'Add role', exact: true }).click();
      await credit.getByLabel('Role 1', { exact: true }).selectOption('Developer');
      await page.getByRole('button', { name: 'Add link', exact: true }).click();
      const link = page.locator('#nested-link');
      await link.getByLabel('URL', { exact: true }).fill('https://example.org/source');
      await link.getByLabel('Type 1', { exact: true }).selectOption('Repository');
      await page.getByRole('button', { name: 'Add publication', exact: true }).click();
      await page.locator('#nested-publication').getByLabel('DOI', { exact: true }).fill('invalid-doi');
      async function save(status) {
        const response = page.waitForResponse(r => r.url().endsWith('/save/'));
        await page.getByRole('button', { name: 'Save changes', exact: true }).click();
        expect((await response).status()).toBe(status);
      }
      await save(400);
      await expect(page.getByRole('alert')).toContainText('credit');
      await expect(page.getByRole('alert')).toContainText('publication');
      await credit.getByLabel('Email', { exact: true }).fill('contributor@example.org');
      // Valid publication persistence is covered with deterministic enrichment in backend tests.
      page.once('dialog', dialog => dialog.accept());
      await page.getByRole('button', { name: 'Remove publication 1', exact: true }).click();
      await save(201);
      await expect(page.getByRole('status', { name: 'Save status' })).toHaveText('Changes saved.');
      let record = await (await request.get('/api/t/' + id + '?format=json')).json();
      expect(record.license).toBe('MIT');
      expect(record.version).toEqual(['2.0']);
      expect(record.language).toEqual(['Python']);
      expect(record.link[0].type).toEqual(['Repository']);
      expect(record.credit[0]).toMatchObject({ name: 'Metadata Contributor', email: 'contributor@example.org', typeRole: ['Developer'] });
      await page.reload();
      await expect(page.getByLabel('License', { exact: true })).toHaveValue('MIT');
      await expect(credit.getByLabel('Email', { exact: true })).toHaveValue('contributor@example.org');
      expect(await page.locator('html').evaluate(el => el.scrollWidth <= innerWidth)).toBe(true);
      const ids = await page.locator('[id]').evaluateAll(nodes => nodes.map(node => node.id));
      expect(new Set(ids).size).toBe(ids.length);
      await page.locator('#metadata-labels').screenshot({ path: info.outputPath('metadata-labels.png') });
      await credit.screenshot({ path: info.outputPath('metadata-credit.png') });
      await page.getByLabel('License', { exact: true }).selectOption('');
      await save(200);
      record = await (await request.get('/api/t/' + id + '?format=json')).json();
      expect(record.license).toBeNull();
      expect(record.credit[0].name).toBe('Metadata Contributor');
    });
  }
});
