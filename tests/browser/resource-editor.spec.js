const { test, expect, canonicalAccounts, editorUrl, editorSaveUrl } = require('./fixtures');

const editor = editorUrl('editor-demo');
const user = process.env.BIOTOOLS_TEST_USERNAME;
const password = process.env.BIOTOOLS_TEST_PASSWORD;
const newID = () => 'editor-browser-' + Date.now() + '-' + Math.random().toString(36).slice(2, 7);

async function signIn(page, url = editorUrl()) {
  await page.goto(url);
  await page.getByLabel('Username or email:', { exact: true }).fill(user);
  await page.getByLabel('Password:', { exact: true }).fill(password);
  await page.getByRole('button', { name: 'Sign in', exact: true }).click();
  await expect(page.locator('[data-vue-island="resource-editor"]')).toHaveAttribute('data-v-app', '');
}
async function fillNew(page, id) {
  await page.getByLabel('Name', { exact: true }).fill('Browser Editor Sample');
  await page.getByLabel('bio.tools ID', { exact: true }).fill(id);
  await page.getByLabel('Homepage', { exact: true }).fill('https://example.org/editor');
  await page.getByLabel('Description', { exact: true }).fill('A disposable resource created by the migrated editor browser regression.');
  await page.getByLabel('Command-line tool', { exact: true }).check();
}
async function save(page, status = 200) {
  const response = page.waitForResponse(response => response.request().method() === 'POST' && response.url().endsWith('/save/'));
  await page.getByRole('button', { name: 'Save changes', exact: true }).click();
  expect((await response).status()).toBe(status);
  if (status < 400) await expect(page.getByRole('status')).toHaveText('Changes saved.');
}

test.describe('basic resource editor', () => {
  test.skip(process.env.BIOTOOLS_TEST_EDITOR_WRITES !== '1', 'Requires explicit disposable registry-write opt-in and seed_editor.py.');
  test.beforeEach(() => { expect(user).toBeTruthy(); expect(password).toBeTruthy(); });

  for (const width of [1440, 390]) {
    test(`create, validate, edit and navigation warning at ${width}px`, async ({ page, request, baseURL }, info) => {
      await page.setViewportSize({ width, height: 1000 });
      await signIn(page);
      const id = newID();
      await fillNew(page, id);
      await page.getByLabel('Name', { exact: true }).fill('Invalid / name');
      await save(page, 400);
      await expect(page.locator('#error-name')).not.toBeEmpty();
      await expect(page.getByLabel('Name', { exact: true })).toHaveValue('Invalid / name');
      await page.getByLabel('Name', { exact: true }).fill('Browser Editor Sample');
      await save(page, 201);
      await expect(page).toHaveURL(new URL(editorUrl(id), baseURL).href);
      await expect(page.getByLabel('bio.tools ID', { exact: true })).toHaveAttribute('readonly', '');
      await page.getByLabel('Name', { exact: true }).fill('Browser Editor Updated');
      page.once('dialog', dialog => dialog.dismiss());
      await page.getByRole('link', { name: 'View record', exact: true }).click();
      await expect(page.getByLabel('Name', { exact: true })).toHaveValue('Browser Editor Updated');
      const unload = page.waitForEvent('dialog');
      const reload = page.reload().catch(() => {});
      const dialog = await unload;
      expect(dialog.type()).toBe('beforeunload');
      await dialog.dismiss();
      await reload;
      await save(page);
      const record = await (await request.get('/api/t/' + id + '?format=json')).json();
      expect(record.name).toBe('Browser Editor Updated');
      await page.screenshot({ path: info.outputPath('editor.png'), fullPage: true });
      expect(await page.locator('html').evaluate(element => element.scrollWidth <= innerWidth)).toBe(true);
      await page.getByRole('link', { name: 'View record', exact: true }).click();
      await expect(page.getByRole('heading', { name: 'Browser Editor Updated', exact: true })).toBeVisible();
      await page.getByRole('link', { name: 'Edit record', exact: true }).click();
      await expect(page.getByLabel('Name', { exact: true })).toHaveValue('Browser Editor Updated');
    });
  }

  test('basic edit retains hidden scientific and credit metadata', async ({ page, request }) => {
    const before = await (await request.get('/api/t/editor-demo?format=json')).json();
    await signIn(page, editor);
    await page.getByLabel('Name', { exact: true }).fill('Editor Demo Updated');
    await save(page);
    const after = await (await request.get('/api/t/editor-demo?format=json')).json();
    for (const key of Object.keys(before).filter(key => !['name', 'lastUpdate'].includes(key))) {
      if (['toolType', 'operatingSystem', 'language', 'collectionID'].includes(key)) expect([...after[key]].sort()).toEqual([...before[key]].sort());
      else expect(after[key]).toEqual(before[key]);
    }
    await page.getByLabel('Name', { exact: true }).fill(before.name);
    await save(page);
  });

  for (const width of [1440, 390]) {
    test(`owner permissions validate, save and reload at ${width}px`, async ({ page, request }, info) => {
      await page.setViewportSize({ width, height: 1000 });
      await signIn(page);
      const id = newID();
      await fillNew(page, id);
      const permissions = page.getByRole('region', { name: 'Editing permissions', exact: true });
      await expect(permissions.getByRole('radio', { name: 'Owner only', exact: true })).toBeChecked();
      await save(page, 201);
      await permissions.getByRole('radio', { name: 'Selected users', exact: true }).check();
      await permissions.getByLabel('Username', { exact: true }).fill('no-such-editor-user');
      await permissions.getByRole('button', { name: 'Add user', exact: true }).click();
      await save(page, 400);
      await expect(page.getByRole('alert')).toContainText('Specified user does not exist');
      await expect(permissions).toContainText('no-such-editor-user');
      await permissions.getByRole('button', { name: 'Remove no-such-editor-user', exact: true }).click();
      await permissions.getByLabel('Username', { exact: true }).fill(user);
      await expect(permissions.locator(`datalist option[value="${user}"]`)).toHaveCount(1);
      await permissions.getByRole('button', { name: 'Add user', exact: true }).click();
      await save(page);
      await page.reload();
      await expect(permissions.getByRole('radio', { name: 'Selected users', exact: true })).toBeChecked();
      await expect(permissions.getByRole('button', { name: `Remove ${user}`, exact: true })).toBeVisible();
      await permissions.scrollIntoViewIfNeeded();
      await page.screenshot({ path: info.outputPath('permissions.png') });
      expect(await page.locator('html').evaluate(element => element.scrollWidth <= innerWidth)).toBe(true);
      await permissions.getByRole('radio', { name: 'Any signed-in user', exact: true }).check();
      await save(page);
      let record = await (await request.get('/api/t/' + id + '?format=json')).json();
      expect(record.editPermission).toEqual({ type: 'public', authors: [user] });
      await permissions.getByRole('radio', { name: 'Selected users', exact: true }).check();
      await permissions.getByRole('button', { name: `Remove ${user}`, exact: true }).click();
      await permissions.getByRole('radio', { name: 'Owner only', exact: true }).check();
      await save(page);
      record = await (await request.get('/api/t/' + id + '?format=json')).json();
      expect(record.editPermission).toEqual({ type: 'private', authors: [] });
    });
  }

  for (const width of [1440, 390]) {
    test(`enriched publications and protected identifiers survive save and refresh at ${width}px`, async ({ page, request }, info) => {
      test.skip(process.env.BIOTOOLS_TEST_ENRICHED_EDITOR !== '1', 'Requires the enriched seed_editor.py fixture.');
      await page.setViewportSize({ width, height: 1000 });
      const url = '/api/t/editor-enriched?format=json';
      const before = await (await request.get(url)).json();
      await signIn(page, editorUrl('editor-enriched'));
      const identifiers = page.locator('#nested-otherID');
      const protectedInput = identifiers.getByRole('textbox', { name: 'Identifier value', exact: true })
        .filter({ visible: true });
      const protectedRow = identifiers.locator('.metadata-record').filter({ has: page.locator('input[value="biotools:editor-previous-id"]') });
      await expect(protectedInput.last()).toBeDisabled();
      await expect(protectedRow.getByRole('button', { name: /Remove identifier/ })).toBeDisabled();
      await page.getByLabel('Name', { exact: true }).fill('Enriched Editor Updated');
      await save(page);
      await page.reload();
      await expect(page.getByLabel('Name', { exact: true })).toHaveValue('Enriched Editor Updated');
      const after = await (await request.get(url)).json();
      for (const key of ['publication', 'homepage_status', 'elixir_badge', 'otherID']) expect(after[key]).toEqual(before[key]);
      expect(after.publication[0].metadata.authors).toEqual([{ name: 'Fixture Author' }]);
      await page.locator('#nested-publication').scrollIntoViewIfNeeded();
      await page.screenshot({ path: info.outputPath('enriched-editor.png') });
      expect(await page.locator('html').evaluate(element => element.scrollWidth <= innerWidth)).toBe(true);
      await page.getByLabel('Name', { exact: true }).fill(before.name);
      await save(page);
    });
  }

  test('session expiry retains the draft through sign-in and reconnection', async ({ page, context }) => {
    await signIn(page);
    await fillNew(page, newID());
    await context.clearCookies({ name: 'sessionid' });
    await save(page, 401);
    await expect(page.locator('#authentication-error')).toBeVisible();
    await expect(page.getByLabel('Name', { exact: true })).toHaveValue('Browser Editor Sample');
    const popup = page.waitForEvent('popup');
    await page.locator('#authentication-login').click();
    const login = await popup;
    await login.getByLabel('Username or email:', { exact: true }).fill(user);
    await login.getByLabel('Password:', { exact: true }).fill(password);
    await login.getByRole('button', { name: 'Sign in', exact: true }).click();
    await expect(login.getByRole('heading', { name: canonicalAccounts ? 'My profile' : 'Account', exact: true })).toBeVisible();
    await login.close();
    await page.getByRole('button', { name: 'Reconnect', exact: true }).click();
    await expect(page.locator('#authentication-error')).toBeHidden();
    await save(page, 201);
  });

  test('a stale tab cannot replace newer changes', async ({ page, context }) => {
    await signIn(page, editor);
    const original = await page.getByLabel('Name', { exact: true }).inputValue();
    const stale = await context.newPage();
    await stale.goto(editor);
    await expect(stale.getByLabel('Name', { exact: true })).toHaveValue(original);
    await page.getByLabel('Name', { exact: true }).fill('Newer editor revision');
    await save(page);
    await stale.getByLabel('Name', { exact: true }).fill('Stale editor revision');
    await save(stale, 409);
    await expect(stale.getByRole('alert')).toContainText('changed since it was loaded');
    await expect(stale.getByLabel('Name', { exact: true })).toHaveValue('Stale editor revision');
    await stale.close();
    await page.getByLabel('Name', { exact: true }).fill(original);
    await save(page);
  });

  test('failed transport retains editable values and a downloadable draft', async ({ page }) => {
    await signIn(page, editor);
    await page.getByLabel('Name', { exact: true }).fill('Retained export name');
    await page.route('**' + editorSaveUrl('editor-demo'), route => route.fulfill({ status: 503,
      contentType: 'application/json', body: JSON.stringify({ detail: 'Save unavailable.' }) }));
    await save(page, 503);
    await expect(page.getByRole('alert')).toContainText('Save unavailable.');
    await expect(page.getByLabel('Name', { exact: true })).toHaveValue('Retained export name');
    const download = page.waitForEvent('download');
    await page.getByRole('button', { name: 'Export draft', exact: true }).click();
    const stream = await (await download).createReadStream();
    let data = '';
    for await (const chunk of stream) data += chunk;
    const draft = JSON.parse(data);
    expect(draft.name).toBe('Retained export name');
    expect(draft.function.length).toBeGreaterThan(0);
    expect(draft.credit.length).toBeGreaterThan(0);
    page.once('dialog', dialog => dialog.accept());
    await page.getByRole('button', { name: 'Discard changes', exact: true }).click();
    await expect(page.getByRole('status')).toHaveText('No unsaved changes');
  });

  test('anonymous pages redirect and no-JavaScript offers stored export and retry', async ({ browser, baseURL }) => {
    const context = await browser.newContext({ baseURL, javaScriptEnabled: false, ignoreHTTPSErrors: process.env.BIOTOOLS_TEST_LOCAL_TLS === '1' });
    try {
      const page = await context.newPage();
      await page.goto(editor);
      await expect(page).toHaveURL(/\/(?:auth\/login\/|login\?)/);
      await page.getByLabel('Username or email:', { exact: true }).fill(user);
      await page.getByLabel('Password:', { exact: true }).fill(password);
      await page.getByRole('button', { name: 'Sign in', exact: true }).click();
      await expect(page.getByRole('link', { name: 'Export stored JSON' })).toHaveAttribute('href', '/api/t/editor-demo?format=json');
      await expect(page.getByText('The editor requires JavaScript and its assets.')).toBeVisible();
      await expect(page.getByRole('link', { name: 'Open the existing editor' })).toHaveCount(0);
      await expect(page.getByRole('heading', { name: 'Edit tool', exact: true })).toBeVisible();
    } finally { await context.close(); }
  });
});
