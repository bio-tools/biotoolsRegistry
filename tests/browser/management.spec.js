const { test, expect } = require('./fixtures');
test.skip(process.env.BIOTOOLS_TEST_MANAGEMENT !== '1', 'Management acceptance is opt-in.');
const password = process.env.BIOTOOLS_TEST_PASSWORD;
const unique = prefix => prefix + '-' + Date.now() + '-' + Math.random().toString(36).slice(2, 6);

async function login(page, path, username = process.env.BIOTOOLS_TEST_USERNAME) {
  await page.goto('/login?next=' + encodeURIComponent(path));
  await page.getByLabel('Username or email:', { exact: true }).fill(username);
  await page.getByLabel('Password:', { exact: true }).fill(password);
  await page.getByRole('button', { name: 'Sign in', exact: true }).click();
  await expect(page).toHaveURL(new RegExp(path.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + '$'));
}

for (const width of [1440, 390]) {
  for (const javaScriptEnabled of [true, false]) {
    test(`domain create, membership, editors and deletion ${width}px JavaScript=${javaScriptEnabled}`, async ({ browser, baseURL }) => {
      test.skip(process.env.BIOTOOLS_TEST_EDITOR_WRITES !== '1', 'Disposable writes required.');
      const context = await browser.newContext({ baseURL, javaScriptEnabled, ignoreHTTPSErrors: true, viewport: { width, height: 1000 } });
      const page = await context.newPage();
      try {
        const id = unique('management-domain');
        await login(page, '/edit-subdomain/');
        await page.getByLabel('Domain identifier:', { exact: true }).fill(id);
        await page.getByLabel('Title:', { exact: true }).fill('Browser managed domain');
        await page.getByLabel('Tool identifiers (one per line):', { exact: true }).fill('editor-demo');
        if (javaScriptEnabled) {
          await page.getByLabel('Username', { exact: true }).fill('migration-management-admin');
          await page.getByLabel('Username', { exact: true }).press('Enter');
          await expect(page.getByRole('button', { name: 'Remove migration-management-admin' })).toBeVisible();
        } else {
          await page.getByLabel('Editors (one username per line):', { exact: true }).fill('migration-management-admin');
        }
        await page.getByRole('button', { name: 'Save domain', exact: true }).click();
        await expect(page).toHaveURL(new RegExp('/edit-domain/' + id + '$'));
        await expect(page.getByRole('status')).toContainText('Domain saved.');
        const stored = await (await context.request.get('/api/d/' + id + '?format=json')).json();
        expect(stored.data.resources.map(tool => tool.biotoolsID)).toEqual(['editor-demo']);
        expect(stored.data.editors).toEqual(['migration-management-admin']);
        const search = await context.request.get('/t?domain=' + id);
        expect(search.status()).toBe(200);
        expect(await search.text()).toContain('href="/editor-demo"');
        await page.getByLabel('Title:', { exact: true }).fill('Revised domain title');
        await page.getByRole('button', { name: 'Save domain', exact: true }).click();
        await expect(page.getByLabel('Title:', { exact: true })).toHaveValue('Revised domain title');
        await page.screenshot({ path: test.info().outputPath('domain.png'), fullPage: true });
        await page.getByLabel('I confirm deletion of this domain.', { exact: true }).check();
        await page.getByRole('button', { name: 'Delete domain', exact: true }).click();
        await expect(page).toHaveURL(/\/domain-manager$/);
        expect((await context.request.get('/api/d/' + id + '?format=json')).status()).toBe(404);
      } finally { await context.close(); }
    });
  }

  test(`JSON validation, explicit save and confirmed disown ${width}px`, async ({ page }) => {
    test.skip(process.env.BIOTOOLS_TEST_EDITOR_WRITES !== '1', 'Disposable writes required.');
    await page.setViewportSize({ width, height: 1000 });
    const id = unique('management-record');
    await login(page, '/register');
    await page.getByLabel('Name', { exact: true }).fill('Management browser fixture');
    await page.getByLabel('bio.tools ID', { exact: true }).fill(id);
    await page.getByLabel('Homepage', { exact: true }).fill('https://example.org/management');
    await page.getByLabel('Description', { exact: true }).fill('A disposable record for validating native management actions.');
    await page.getByLabel('Command-line tool', { exact: true }).check();
    await page.getByRole('button', { name: 'Validate without saving', exact: true }).click();
    await expect(page.getByRole('status', { name: 'Validation status' })).toContainText('Nothing was saved.');
    expect((await page.request.get('/api/t/' + id + '?format=json')).status()).toBe(404);
    await page.locator('.editor-json-panel summary').click();
    const raw = JSON.parse(await page.getByLabel('Resource JSON', { exact: true }).inputValue());
    await page.getByLabel('Resource JSON', { exact: true }).fill('{broken');
    await expect(page.getByLabel('Resource JSON', { exact: true })).toHaveValue('{broken');
    await expect(page.getByRole('button', { name: 'Save changes', exact: true })).toBeDisabled();
    raw.name = 'JSON revised fixture';
    await page.getByLabel('Resource JSON', { exact: true }).fill(JSON.stringify(raw));
    await expect(page.getByLabel('Name', { exact: true })).toHaveValue('JSON revised fixture');
    await page.getByRole('button', { name: 'Save changes', exact: true }).click();
    await expect(page.getByRole('status', { name: 'Save status' })).toHaveText('Changes saved.');
    await page.goto('/' + id + '/manage');
    await page.getByLabel('I confirm this action cannot be undone here.', { exact: true }).check();
    await page.getByRole('button', { name: 'Confirm record action' }).click();
    await expect(page).toHaveURL(new RegExp('/' + id + '$'));
    expect((await (await page.request.get('/api/t/' + id + '?format=json')).json()).owner).toBe('admin');
    const indexed = await (await page.request.get('/api/t?biotoolsID=' + id + '&format=json')).json();
    expect(indexed.count).toBe(1);
    expect(indexed.list[0].owner).toBe('admin');
  });

  for (const javaScriptEnabled of [true, false]) {
    test(`workflow annotation alignment and keyboard access ${width}px JavaScript=${javaScriptEnabled}`, async ({ browser, baseURL }) => {
      const context = await browser.newContext({ baseURL, javaScriptEnabled, ignoreHTTPSErrors: true, viewport: { width, height: 1000 } });
      const page = await context.newPage();
      try {
        await page.goto('/workflows?q=management-workflow');
        const image = page.getByAltText('Annotated workflow management-workflow');
        await expect(image).toBeVisible();
        expect(await image.evaluate(node => node.complete && node.naturalWidth === 1000)).toBe(true);
        const region = page.getByRole('link', { name: 'Inspect Align sequences', exact: true });
        const picture = await image.boundingBox(), box = await region.boundingBox();
        expect(Math.abs((box.x - picture.x) / picture.width - .4)).toBeLessThan(.01);
        expect(Math.abs(box.width / picture.width - .2)).toBeLessThan(.01);
        await region.focus();
        await page.keyboard.press('Enter');
        await expect(page.locator(':target')).toContainText('Align sequences');
        await page.screenshot({ path: test.info().outputPath('workflow.png'), fullPage: true });
      } finally { await context.close(); }
    });
  }
}

test('failed assets retain native management forms and an honest editor fallback', async ({ page }) => {
  await page.route('**/static/modern/**', route => route.abort());
  await login(page, '/edit-domain/');
  await expect(page.getByLabel('Editors (one username per line):', { exact: true })).toBeVisible();
  await page.goto('/editor-demo/edit');
  await expect(page.getByRole('link', { name: 'Export stored JSON' })).toBeVisible();
  await expect(page.getByRole('link', { name: 'Open the existing editor' })).toHaveCount(0);
});

test('failed workflow image retains annotation details and recovery', async ({ page }) => {
  await page.route('**/media/workflows/**', route => route.abort());
  await page.goto('/workflows?q=management-workflow');
  await expect(page.getByRole('alert')).toContainText('workflow image could not be loaded');
  await page.locator('.workflow-details summary').first().click();
  await expect(page.getByRole('heading', { name: 'Align sequences', exact: true })).toBeVisible();
  await expect(page.getByRole('link', { name: 'Open or retry full-size image' })).toBeVisible();
});

test('superuser confirms removal of a disposable record', async ({ page }) => {
  test.skip(process.env.BIOTOOLS_TEST_EDITOR_WRITES !== '1', 'Disposable writes required.');
  const id = unique('management-delete');
  await login(page, '/register', 'migration-management-admin');
  await page.getByLabel('Name', { exact: true }).fill('Disposable removal fixture');
  await page.getByLabel('bio.tools ID', { exact: true }).fill(id);
  await page.getByLabel('Homepage', { exact: true }).fill('https://example.org/removal');
  await page.getByLabel('Description', { exact: true }).fill('A temporary resource for confirmed native record removal.');
  await page.getByLabel('Command-line tool', { exact: true }).check();
  await page.getByRole('button', { name: 'Save changes', exact: true }).click();
  await expect(page.getByRole('status', { name: 'Save status' })).toHaveText('Changes saved.');
  await page.goto('/' + id + '/manage');
  await page.getByLabel('Action', { exact: true }).selectOption('delete');
  await page.getByLabel('I confirm this action cannot be undone here.', { exact: true }).check();
  await page.getByRole('button', { name: 'Confirm record action' }).click();
  await expect(page).toHaveURL(/\/profile$/);
  expect((await page.request.get('/api/t/' + id + '?format=json')).status()).toBe(404);
  expect((await (await page.request.get('/api/t?biotoolsID=' + id + '&format=json')).json()).count).toBe(0);
});
