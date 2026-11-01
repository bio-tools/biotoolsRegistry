const { test, expect } = require('./fixtures');
const { execFileSync } = require('node:child_process');
const { createHash, randomBytes } = require('node:crypto');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');

test('same-build schema activation, persistence and compatible rollback through both proxies', async ({ browser }, info) => {
  test.skip(process.env.BIOTOOLS_SCHEMA_REHEARSAL !== 'biotools-refresh', 'Explicit isolated-database rehearsal opt-in required.');
  test.setTimeout(600000);
  const root = path.resolve(__dirname, '../..');
  const directory = fs.mkdtempSync(path.join(os.tmpdir(), 'biotools-schema-'));
  fs.chmodSync(directory, 0o755);
  const database = 'test_schema_ui_' + randomBytes(4).toString('hex');
  const override = path.join(directory, 'compose.json');
  const manifest = fs.readFileSync(path.join(root, 'backend/elixir/static/modern/manifest.json'));
  const asset = JSON.parse(manifest)['src/main.js'].file;
  const bundle = fs.readFileSync(path.join(root, 'backend/elixir/static/modern', asset));
  const sha = bytes => createHash('sha256').update(bytes).digest('hex');
  const evidence = { database, directory, bundle: asset, sha256: sha(bundle), phases: [] };
  const states = [];
  const pageErrors = [];
  let replaced = false;
  function compose(args, fixture = true) {
    try {
      return execFileSync('docker', ['compose', '-f', 'compose.refresh.json', ...(fixture ? ['-f', override] : []), ...args],
        { cwd: root, encoding: 'utf8', timeout: 180000, maxBuffer: 8 * 1024 * 1024 });
    } catch (error) {
      throw new Error(`${error.message}\n${error.stdout || ''}\n${error.stderr || ''}`, { cause: error });
    }
  }
  function shell(code) {
    return compose(['exec', '-T', '--user', `${process.getuid()}:${process.getgid()}`, 'backend', 'python', 'manage.py', 'shell', '-c', code]);
  }
  async function ready(context) {
    await expect(async () => {
      const response = await context.request.get('/login');
      expect(response.status()).toBe(200);
    }).toPass({ timeout: 60000, intervals: [1000, 2000] });
  }
  async function config(page, name = 'editor') {
    return page.locator(`#${name}-config`).evaluate(element => JSON.parse(element.content.querySelector('script').textContent));
  }
  async function sameBundle(page) {
    const source = await page.locator('script[type="module"][src]').getAttribute('src');
    expect(source).toContain(asset);
    const response = await page.request.get(source);
    expect(response.ok()).toBe(true);
    expect(sha(await response.body())).toBe(evidence.sha256);
  }
  async function save(page, status) {
    const response = page.waitForResponse(response => response.url().endsWith('/save/') && response.request().method() === 'POST');
    await page.getByRole('button', { name: 'Save changes', exact: true }).click();
    const result = await response;
    expect(result.status(), await result.text()).toBe(status);
    return result;
  }
  async function activate(phase) {
    fs.writeFileSync(path.join(directory, 'active'), phase);
    compose(['restart', 'backend', 'apache']);
    shell(`from elixirapp.tests.schema_rehearsal import vocabulary; vocabulary('${phase}')`);
    for (const state of states) await ready(state.context);
    evidence.phases.push({ phase, revision: JSON.parse(fs.readFileSync(path.join(directory, phase + '.json'))).revision });
    expect(fs.readFileSync(path.join(root, 'backend/elixir/static/modern/manifest.json'))).toEqual(manifest);
  }
  try {
    fs.writeFileSync(path.join(directory, 'active'), 'baseline');
    // The fixture settings reject any database outside this narrowly named test namespace.
    const service = { environment: { DJANGO_SETTINGS_MODULE: 'elixirapp.tests.schema_rehearsal_settings',
      BIOTOOLS_SCHEMA_REHEARSAL: 'biotools-refresh', BIOTOOLS_MYSQL_DB: database },
      volumes: [{ type: 'bind', source: directory, target: '/schema-rehearsal' }] };
    fs.writeFileSync(override, JSON.stringify({ services: { backend: service, apache: service } }));
    compose(['exec', '-T', 'mysql', 'mysql', '-uroot', '-pelixirroot', '-e',
      `CREATE DATABASE ${database}; GRANT ALL ON ${database}.* TO 'elixir'@'%';`], false);
    replaced = true;
    compose(['up', '-d', '--no-deps', 'backend', 'apache']);
    shell('from elixirapp.tests.schema_rehearsal import generate; generate()');
    compose(['exec', '-T', 'backend', 'python', 'manage.py', 'migrate', '--noinput']);
    shell('from elixirapp.tests.schema_rehearsal import seed; seed()');
    for (const [proxy, baseURL] of [['apache', 'http://localhost:8003'], ['caddy', 'https://localhost:8443']]) {
      for (const [size, width] of [['desktop', 1440], ['mobile', 390]]) {
        const context = await browser.newContext({ baseURL, ignoreHTTPSErrors: true, viewport: { width, height: 1000 } });
        const page = await context.newPage();
        page.on('pageerror', error => pageErrors.push(error.message));
        page.on('console', message => { if (message.type() === 'error') console.log('SCHEMA_CONSOLE_ERROR', message.text()); });
        const id = `schema-${proxy}-${size}`;
        const state = { context, page, id, proxy, size };
        states.push(state);
        await ready(context);
        await page.goto(`/${id}/edit`);
        await page.getByLabel('Username or email:', { exact: true }).fill('schema-test');
        await page.getByLabel('Password:', { exact: true }).fill('Schema-test-only-2026');
        await page.getByRole('button', { name: 'Sign in', exact: true }).click();
        await expect(page.getByLabel('Name', { exact: true })).toHaveValue('Schema Rehearsal');
        state.baseline = await config(page);
        expect(state.baseline.schema.contract.fields.download.item.fields).not.toHaveProperty('cmd');
        await sameBundle(page);
        await page.getByRole('button', { name: /^Choose topic 1:/ }).click();
        await expect(page.getByRole('dialog')).toContainText('Bioinformatics');
        await expect(page.getByRole('dialog').getByRole('combobox')).toBeFocused();
        await page.getByRole('button', { name: 'Cancel', exact: true }).press('Enter');
        await expect(page.getByRole('dialog')).toHaveCount(0);
        await page.getByLabel('Name', { exact: true }).fill('Unsaved schema draft');
        await expect(page.getByRole('button', { name: 'Discard changes', exact: true })).toBeEnabled();
      }
    }
    await activate('added');
    for (const { page, baseline, id, proxy, size } of states) {
      await page.bringToFront();
      await expect(page.getByLabel('Name', { exact: true })).toHaveValue('Unsaved schema draft');
      await save(page, 409);
      await expect(page.getByRole('alert')).toContainText('resource schema changed');
      await expect(page.getByLabel('Name', { exact: true })).toHaveValue('Unsaved schema draft');
      const download = page.waitForEvent('download');
      await page.getByRole('button', { name: 'Export draft', exact: true }).click();
      const draft = JSON.parse(fs.readFileSync(await (await download).path()));
      expect(draft.name).toBe('Unsaved schema draft');
      expect(draft.topic[0].uri).toBe('http://edamontology.org/topic_0091');
      await page.getByRole('button', { name: /^Choose topic 1:/ }).click();
      await expect(page.getByRole('dialog')).toContainText('Revised bioinformatics');
      await page.getByRole('button', { name: 'Cancel', exact: true }).press('Enter');
      await expect(page.getByRole('button', { name: /^Choose topic 1:/ })).toContainText('Revised bioinformatics');
      page.once('dialog', dialog => dialog.accept());
      await page.reload();
      const current = await config(page);
      expect(current.schemaRevision).not.toBe(baseline.schemaRevision);
      await sameBundle(page);
      await expect(page.getByLabel('Release maturity', { exact: true })).toHaveValue('Mature');
      await expect(page.getByText('Activated fixture release guidance: added', { exact: true })).toBeVisible();
      await expect(page.getByLabel('Function annotation added', { exact: true })).toBeVisible();
      await expect(page.locator('.function-diagram')).toHaveCount(1);
      await expect(page.getByLabel('Installation command', { exact: true })).toBeVisible();
      await page.getByLabel('Installation command', { exact: true }).fill('install schema-fixture');
      await page.getByLabel('Release maturity', { exact: true }).selectOption('Preview');
      await save(page, 200);
      await page.reload();
      await expect(page.getByLabel('Installation command', { exact: true })).toHaveValue('install schema-fixture');
      await expect(page.getByLabel('Release maturity', { exact: true })).toHaveValue('Preview');
      const stored = await (await page.request.get(`/api/t/${id}?format=json`)).json();
      expect(stored.download[0].cmd).toBe('install schema-fixture');
      expect(stored.topic[0].uri).toBe('http://edamontology.org/topic_0091');
      expect(await page.locator('html').evaluate(element => element.scrollWidth <= innerWidth)).toBe(true);
      await page.locator('#nested-download').screenshot({ path: info.outputPath(`${proxy}-${size}-new-field.png`) });
      const detail = await page.context().newPage();
      await detail.goto(`/${id}`);
      await expect(detail.getByText('Installation command', { exact: true })).toBeVisible();
      await expect(detail.getByText('install schema-fixture', { exact: true })).toBeVisible();
      await detail.goto('/t');
      const search = await config(detail, 'search');
      expect(search.filters.toolType).toBe('Application category added');
      expect(search.filters).not.toHaveProperty('download.cmd');
      expect(search.schemaRevision).toBe(current.schemaRevision);
      await detail.close();
      // Preserve a soon-to-be-removed value in storage to exercise correction after activation.
      await page.getByLabel('Release maturity', { exact: true }).selectOption('Mature');
      await save(page, 200);
    }
    await activate('removed');
    for (const { page, id } of states) {
      await page.reload();
      await sameBundle(page);
      await expect(page.getByLabel('Release stage', { exact: true })).toHaveValue('Mature');
      await expect(page.locator('#nested-maturity option:disabled')).toHaveText('Mature (no longer allowed)');
      await expect(page.getByRole('button', { name: 'Save changes', exact: true })).toBeDisabled();
      await expect(page.getByLabel('Installation command', { exact: true })).toHaveValue('install schema-fixture');
      await page.getByLabel('Release stage', { exact: true }).selectOption('Preview');
      // Bypass only the UI's enum restriction, retaining its current metadata and revisions.
      await page.route(`**/${id}/edit/save/`, route => {
        const body = route.request().postDataJSON();
        body.resource.maturity = 'Mature';
        return route.continue({ postData: JSON.stringify(body) });
      }, { times: 1 });
      const rejected = await save(page, 400);
      expect(await rejected.text()).toContain('maturity');
      await save(page, 200);
    }
    await activate('added');
    for (const { page } of states) {
      await page.reload();
      await sameBundle(page);
      await expect(page.getByLabel('Release maturity', { exact: true })).toHaveValue('Preview');
      await expect(page.getByLabel('Installation command', { exact: true })).toHaveValue('install schema-fixture');
      await expect(page.locator('#nested-maturity option[value="Mature"]')).toHaveCount(1);
      await save(page, 200);
    }
    shell('from elixirapp.tests.schema_rehearsal import assert_persisted; assert_persisted()');
    expect(pageErrors).toEqual([]);
    await info.attach('schema-rehearsal', { body: JSON.stringify(evidence, null, 2), contentType: 'application/json' });
  } finally {
    try {
      for (const { context } of states) await context.close();
    } finally {
      if (replaced) compose(['up', '-d', '--no-deps', 'backend', 'apache'], false);
      fs.writeFileSync(path.join(directory, 'evidence.json'), JSON.stringify(evidence, null, 2));
      console.log('SCHEMA_REHEARSAL', JSON.stringify(evidence));
    }
  }
});
