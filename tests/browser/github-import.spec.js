const { test, expect, editorUrl } = require('./fixtures');

test.describe('GitHub metadata import', () => {
  test.skip(process.env.BIOTOOLS_TEST_GITHUB_IMPORT !== '1', 'Requires the disposable bridge provider and editor-write opt-in.');
  test.beforeEach(() => expect(process.env.BIOTOOLS_TEST_EDITOR_WRITES).toBe('1'));

  for (const width of [1440, 390]) {
    test(`review, apply, save and reload at ${width}px`, async ({ page, request }, info) => {
      await page.setViewportSize({ width, height: 1000 });
      await page.goto('/register');
      const username = 'migration-bridge-' + width;
      await page.getByLabel('Username or email:', { exact: true }).fill(username);
      await page.getByLabel('Password:', { exact: true }).fill(process.env.BIOTOOLS_TEST_PASSWORD);
      await page.getByRole('button', { name: 'Sign in', exact: true }).click();
      await expect(page.locator('[data-vue-island="resource-editor"]')).toHaveAttribute('data-v-app', '');
      const id = 'bridge-browser-' + width + '-' + Date.now() + '-' + Math.random().toString(36).slice(2, 6);
      await page.getByRole('textbox', { name: 'Name', exact: true }).fill('Curated draft name');
      await page.getByLabel('bio.tools ID', { exact: true }).fill(id);
      await page.getByLabel('Homepage', { exact: true }).fill('https://example.org/bridge');
      await page.getByLabel('Description', { exact: true }).fill('A curated draft description to preserve during bridge review.');
      await page.getByText('Import metadata from GitHub', { exact: true }).click();
      await page.getByLabel('GitHub repository URL').fill('https://github.com/bio-tools/registry');
      const imported = page.waitForResponse(r => r.url().endsWith('/github-to-biotools'));
      await page.getByRole('button', { name: 'Get suggestions', exact: true }).press('Enter');
      expect((await imported).status()).toBe(200);
      await expect(page.getByText('0 pending field changes', { exact: true })).toBeVisible();
      await page.getByLabel('Action for Name', { exact: true }).selectOption('replace');
      await page.getByLabel('Action for License', { exact: true }).selectOption('replace');
      await page.getByRole('textbox', { name: 'Name', exact: true }).fill('Changed during review');
      await expect(page.getByRole('button', { name: 'Refresh comparison' })).toBeVisible();
      await page.getByRole('button', { name: 'Refresh comparison' }).click();
      await page.getByLabel('Action for Name', { exact: true }).selectOption('replace');
      await page.getByLabel('Action for License', { exact: true }).selectOption('replace');
      await page.screenshot({ path: info.outputPath('github-review.png'), fullPage: true });
      expect(await page.locator('html').evaluate(el => el.scrollWidth <= innerWidth)).toBe(true);
      await page.getByRole('button', { name: 'Apply to draft', exact: true }).press('Enter');
      await expect(page.getByRole('textbox', { name: 'Name', exact: true })).toHaveValue('GitHub suggested tool');
      await expect(page.getByLabel('bio.tools ID', { exact: true })).toHaveValue(id);
      expect((await request.get('/api/t/' + id + '?format=json')).status()).toBe(404);
      const saved = page.waitForResponse(r => r.request().method() === 'POST' && r.url().endsWith('/save/'));
      await page.getByRole('button', { name: 'Save changes', exact: true }).click();
      expect((await saved).status()).toBe(201);
      await page.goto(editorUrl(id));
      await expect(page.getByRole('textbox', { name: 'Name', exact: true })).toHaveValue('GitHub suggested tool');
      const record = await (await request.get('/api/t/' + id + '?format=json')).json();
      expect(record.license).toBe('3D-Slicer-1.0');
      expect(record.owner).toBe(username);
      expect(record.description).toContain('curated draft description');
    });
  }

  test('provider failure retains the editable draft', async ({ page }) => {
    await page.goto('/register');
    await page.getByLabel('Username or email:', { exact: true }).fill('migration-bridge-failure');
    await page.getByLabel('Password:', { exact: true }).fill(process.env.BIOTOOLS_TEST_PASSWORD);
    await page.getByRole('button', { name: 'Sign in', exact: true }).click();
    await expect(page.locator('[data-vue-island="resource-editor"]')).toHaveAttribute('data-v-app', '');
    await page.getByRole('textbox', { name: 'Name', exact: true }).fill('Retained after provider failure');
    await page.getByText('Import metadata from GitHub', { exact: true }).click();
    await page.getByLabel('GitHub repository URL').fill('https://github.com/bio-tools/failure');
    const failed = page.waitForResponse(r => r.url().endsWith('/github-to-biotools'));
    await page.getByRole('button', { name: 'Get suggestions', exact: true }).click();
    expect((await failed).status()).toBe(502);
    await expect(page.getByText('GitHub import returned an unavailable or invalid response. Your draft is unchanged.', { exact: true })).toBeVisible();
    await expect(page.getByRole('textbox', { name: 'Name', exact: true })).toHaveValue('Retained after provider failure');
    await expect(page.getByRole('textbox', { name: 'Name', exact: true })).toBeEditable();
  });
});

test('disabled bridge keeps manual editing and rejects provider transport', async ({ page }) => {
  test.skip(process.env.BIOTOOLS_TEST_GITHUB_IMPORT_DISABLED !== '1', 'Requires bridge disabled after rehearsal.');
  await page.goto('/register');
  await page.getByLabel('Username or email:', { exact: true }).fill(process.env.BIOTOOLS_TEST_USERNAME);
  await page.getByLabel('Password:', { exact: true }).fill(process.env.BIOTOOLS_TEST_PASSWORD);
  await page.getByRole('button', { name: 'Sign in', exact: true }).click();
  await expect(page.getByText('GitHub import is unavailable. You can enter metadata manually.', { exact: true })).toBeVisible();
  await expect(page.getByRole('textbox', { name: 'Name', exact: true })).toBeEditable();
  expect(await page.evaluate(async () => (await fetch('/github-to-biotools', { method: 'POST',
    headers: { Accept: 'application/json', 'Content-Type': 'application/json',
      'X-CSRFToken': document.querySelector('meta[name="csrf-token"]').content }, body: '{}' })).status)).toBe(503);
});
