const { test, expect, editorUrl, editorSaveUrl } = require('./fixtures');

const uri = identifier => 'http://edamontology.org/' + identifier;
const functions = page => page.locator('[data-function-id]');
const outputs = section => section.locator('.io-list').nth(1).locator('[data-io-id]');

async function signIn(page, id) {
  await page.goto(editorUrl(id));
  await page.getByLabel('Username or email:', { exact: true }).fill(process.env.BIOTOOLS_TEST_USERNAME);
  await page.getByLabel('Password:', { exact: true }).fill(process.env.BIOTOOLS_TEST_PASSWORD);
  await page.getByRole('button', { name: 'Sign in', exact: true }).click();
  await expect(page.locator('[data-vue-island="resource-editor"]')).toHaveAttribute('data-v-app', '');
}
async function newRecord(page) {
  await signIn(page);
  const id = 'nested-browser-' + Date.now() + '-' + Math.random().toString(36).slice(2, 7);
  await page.getByLabel('Name', { exact: true }).fill('Nested Browser Sample');
  await page.getByLabel('bio.tools ID', { exact: true }).fill(id);
  await page.getByLabel('Homepage', { exact: true }).fill('https://example.org/nested');
  await page.getByLabel('Description', { exact: true }).fill('A disposable nested scientific editor browser regression resource.');
  return id;
}
async function choose(page, container, name, identifier) {
  const opener = container.getByRole('button', { name: new RegExp('^' + name + '(?::|$)') });
  await opener.focus();
  await opener.press('Enter');
  const query = page.getByRole('dialog').getByRole('combobox');
  await expect(query).toBeFocused();
  await query.fill(identifier);
  await expect(page.getByRole('dialog').getByRole('option')).toHaveCount(1);
  await query.press('ArrowDown');
  await query.press('Enter');
  await page.getByRole('button', { name: 'Apply selection', exact: true }).click();
  await expect(opener).toBeFocused();
}
async function save(page, code = 200) {
  const response = page.waitForResponse(response => response.request().method() === 'POST' && response.url().endsWith('/save/'));
  await page.getByRole('button', { name: 'Save changes', exact: true }).click();
  const result = await response;
  expect(result.status()).toBe(code);
  if (code < 400) await expect(page.getByRole('status', { name: 'Save status' })).toHaveText('Changes saved.');
  return result;
}
async function addFunction(page) {
  await page.getByRole('button', { name: 'Add function', exact: true }).click();
  const section = functions(page).last();
  await choose(page, section, 'Choose operation 1', 'operation_0292');
  return section;
}

test.describe('nested resource editor', () => {
  test.skip(process.env.BIOTOOLS_TEST_EDITOR_WRITES !== '1', 'Requires explicit disposable registry-write opt-in and seed_editor.py.');
  test.setTimeout(90000);

  for (const width of [1440, 390]) {
    test(`scientific create, reorder and removal at ${width}px`, async ({ page, request }, info) => {
      await page.setViewportSize({ width, height: 1000 });
      const id = await newRecord(page);
      await addFunction(page);
      const first = functions(page).first();
      await first.getByRole('button', { name: 'Add operation', exact: true }).click();
      await choose(page, first, 'Choose operation 2', 'operation_0004');
      for (const kind of ['input', 'output']) {
        for (const identifier of ['data_0863', 'data_2044']) {
          await first.getByRole('button', { name: `Add ${kind}`, exact: true }).click();
          const io = first.locator('.io-list').nth(kind === 'input' ? 0 : 1).locator('[data-io-id]').last();
          await choose(page, io, 'Choose data', identifier);
          await io.getByRole('button', { name: 'Add format', exact: true }).click();
          await choose(page, io, 'Choose format 1', 'format_1929');
        }
      }
      await first.getByLabel('Note', { exact: true }).fill('The first independent function note.');
      await first.getByLabel('Command (cmd)', { exact: true }).fill('align --input sequences.fa');
      await outputs(first).last().getByRole('button', { name: 'Add format', exact: true }).click();
      await choose(page, outputs(first).last(), 'Choose format 2', 'format_1915');
      const firstID = await first.getAttribute('data-function-id');
      await addFunction(page);
      await functions(page).last().getByLabel('Note', { exact: true }).fill('The second independent function note.');
      const moved = page.locator(`[data-function-id="${firstID}"]`);
      await moved.getByRole('button', { name: 'Move function 1 down', exact: true }).press('Enter');
      await expect(functions(page).last()).toHaveAttribute('data-function-id', firstID);
      await moved.getByRole('button', { name: 'Move input 2 up', exact: true }).press('Enter');
      await moved.getByRole('button', { name: 'Move output 2 up', exact: true }).press('Enter');
      const result = await save(page, 201);
      const payload = result.request().postDataJSON().resource;
      expect(JSON.stringify(payload)).not.toContain(firstID);
      const record = await (await request.get('/api/t/' + id + '?format=json')).json();
      expect(record.function).toHaveLength(2);
      expect(record.function[0].note).toBe('The second independent function note.');
      const saved = record.function[1];
      expect(saved.operation.map(item => item.uri).sort()).toEqual([uri('operation_0004'), uri('operation_0292')]);
      expect(saved.input.map(item => item.data.uri)).toEqual([uri('data_2044'), uri('data_0863')]);
      expect(saved.output.map(item => item.data.uri)).toEqual([uri('data_2044'), uri('data_0863')]);
      expect(saved.output[0].format).toHaveLength(2);
      expect(saved.cmd).toBe('align --input sequences.fa');
      await page.reload();
      await expect(functions(page)).toHaveCount(2);
      const second = functions(page).last();
      page.once('dialog', dialog => dialog.dismiss());
      await second.getByRole('button', { name: 'Remove output 1', exact: true }).click();
      await expect(outputs(second)).toHaveCount(2);
      page.once('dialog', dialog => dialog.accept());
      await second.getByRole('button', { name: 'Remove output 1', exact: true }).click();
      await expect(outputs(second)).toHaveCount(1);
      await save(page);
      expect((await (await request.get('/api/t/' + id + '?format=json')).json()).function[1].output).toHaveLength(1);
      const ids = await page.locator('[id]').evaluateAll(nodes => nodes.map(node => node.id));
      expect(new Set(ids).size).toBe(ids.length);
      expect(await page.locator('html').evaluate(element => element.scrollWidth <= innerWidth)).toBe(true);
      const diagram = functions(page).last().locator('.function-diagram');
      const inputBox = await diagram.locator('.io-list').first().boundingBox();
      const operationBox = await diagram.locator('.function-operations').boundingBox();
      const outputBox = await diagram.locator('.io-list').last().boundingBox();
      if (width > 760) {
        expect(inputBox.x + inputBox.width).toBeLessThan(operationBox.x);
        expect(operationBox.x + operationBox.width).toBeLessThan(outputBox.x);
      } else {
        expect(inputBox.y + inputBox.height).toBeLessThan(operationBox.y);
        expect(operationBox.y + operationBox.height).toBeLessThan(outputBox.y);
      }
      await expect(diagram.locator('.flow-arrow')).toHaveCount(2);
      await page.locator('.function-editor').screenshot({ path: info.outputPath('nested-editor.png') });
    });
  }

  test('real nested validation follows a moved output and recovers without losing the draft', async ({ page }) => {
    await newRecord(page);
    await addFunction(page);
    const section = functions(page).first();
    for (let index = 0; index < 2; index++) {
      await section.getByRole('button', { name: 'Add output', exact: true }).click();
      await choose(page, outputs(section).last(), 'Choose data', 'data_0863');
    }
    await outputs(section).last().getByRole('button', { name: 'Add format', exact: true }).click();
    await choose(page, outputs(section).last(), 'Choose format 1', 'format_1929');
    const outputID = await outputs(section).last().getAttribute('data-io-id');
    // Inject a wrong-scope URI at the transport boundary; validation is still the real backend.
    await page.route('**' + editorSaveUrl(), route => {
      const body = route.request().postDataJSON();
      body.resource.function[0].output[1].format[0].uri = uri('data_0863');
      return route.continue({ postData: JSON.stringify(body) });
    }, { times: 1 });
    await save(page, 400);
    const errored = page.locator(`[data-io-id="${outputID}"]`);
    await expect(errored.locator('.nested-error').filter({ hasText: /\S/ })).toHaveCount(1);
    await expect(page.getByRole('alert')).toContainText('function / 1 / output / 2 / format / 1');
    await section.getByRole('button', { name: 'Move output 2 up', exact: true }).press('Enter');
    await expect(outputs(section).first()).toHaveAttribute('data-io-id', outputID);
    await expect(page.getByRole('alert')).toContainText('function / 1 / output / 1 / format / 1');
    await page.getByRole('alert').getByRole('link').click();
    await expect(errored.locator('[data-concept-id]')).toBeFocused();
    await save(page, 201);
    await expect(page.getByRole('alert')).toHaveCount(0);
  });

  test('editing a rich existing function preserves unrelated metadata', async ({ page, request }) => {
    const before = await (await request.get('/api/t/editor-demo?format=json')).json();
    await signIn(page, 'editor-demo');
    const note = functions(page).first().getByLabel('Note', { exact: true });
    const original = await note.inputValue();
    await note.fill('A nested browser round-trip preservation check.');
    await save(page);
    const after = await (await request.get('/api/t/editor-demo?format=json')).json();
    for (const key of Object.keys(before).filter(key => !['function', 'lastUpdate'].includes(key))) {
      if (['toolType', 'operatingSystem', 'language', 'collectionID'].includes(key)) expect([...after[key]].sort()).toEqual([...before[key]].sort());
      else expect(after[key]).toEqual(before[key]);
    }
    expect(after.function[0].note).toBe('A nested browser round-trip preservation check.');
    await note.fill(original);
    await save(page);
    expect((await (await request.get('/api/t/editor-demo?format=json')).json()).function).toEqual(before.function);
  });
});
