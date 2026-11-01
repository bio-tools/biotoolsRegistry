const { test, expect } = require('./fixtures');

const route = '/_migration/html/edam/';
const endpoint = route + 'terms/';
const topicURI = 'http://edamontology.org/topic_0080';

async function keySelect(page, scope, query) {
  const opener = page.getByRole('button', { name: `Choose ${scope}`, exact: true });
  await opener.focus();
  await opener.press('Enter');
  const input = page.getByRole('combobox', { name: `Find ${scope} terms` });
  await expect(input).toBeFocused();
  await input.fill(query);
  await expect(page.getByRole('option')).toHaveCount(1);
  await input.press('ArrowDown');
  const active = await input.getAttribute('aria-activedescendant');
  await expect(page.locator(`[id="${active}"]`)).toHaveAttribute('role', 'option');
  await input.press('Enter');
  return input;
}

test.describe('EDAM selector', () => {
  test.skip(process.env.BIOTOOLS_TEST_EDAM !== '1', 'Requires the EDAM selector and provisioned ontology records.');

  for (const width of [1440, 390]) {
    test(`keyboard selection, cancel, removal and validation rerender at ${width}px`, async ({ page }, testInfo) => {
      const errors = [];
      page.on('pageerror', error => errors.push(error.message));
      await page.setViewportSize({ width, height: 1000 });
      await page.goto(route);
      const ids = await page.locator('[id]').evaluateAll(nodes => nodes.map(node => node.id));
      expect(new Set(ids).size).toBe(ids.length);
      await keySelect(page, 'topic', 'topic_0080');
      await expect(page.locator('input[type="hidden"][name="topic"]')).toHaveCount(0);
      const dialog = page.getByRole('dialog');
      await expect(dialog.getByRole('list', { name: 'Pending selection' })).toContainText('Sequence analysis');
      await page.screenshot({ path: testInfo.outputPath('edam-selector.png'), fullPage: true });
      expect(await dialog.evaluate(element => element.scrollWidth <= element.clientWidth)).toBe(true);
      await page.getByRole('button', { name: 'Apply selection', exact: true }).focus();
      await page.keyboard.press('Enter');
      await expect(page.locator('input[type="hidden"][name="topic"]')).toHaveValue(topicURI);
      await expect(page.getByRole('button', { name: 'Choose topic', exact: true })).toBeFocused();
      await keySelect(page, 'topic', 'topic_0091');
      await page.getByRole('button', { name: 'Cancel', exact: true }).focus();
      await page.keyboard.press('Enter');
      await expect(page.locator('input[type="hidden"][name="topic"]')).toHaveCount(1);
      const response = page.waitForResponse(response => response.url().endsWith(route) && response.request().method() === 'POST');
      await page.getByRole('button', { name: 'Validate annotations', exact: true }).focus();
      await page.keyboard.press('Enter');
      expect((await response).status()).toBe(400);
      await expect(page.getByText('This field is required.', { exact: true })).toBeVisible();
      await expect(page.locator('input[type="hidden"][name="topic"]')).toHaveValue(topicURI);
      await expect(page.getByRole('button', { name: 'Remove Sequence analysis', exact: true })).toBeVisible();
      await page.getByLabel('Annotation label:', { exact: true }).fill('EDAM browser check');
      await page.getByRole('button', { name: 'Validate annotations', exact: true }).focus();
      await page.keyboard.press('Enter');
      await expect(page.getByRole('heading', { name: 'Validated annotations', exact: true })).toBeVisible();
      const payload = JSON.parse(await page.locator('#validated-edam').textContent());
      expect(payload.topic).toEqual([{ uri: topicURI, term: 'Sequence analysis' }]);
      await page.getByRole('button', { name: 'Remove Sequence analysis', exact: true }).focus();
      await page.keyboard.press('Enter');
      await expect(page.locator('input[type="hidden"][name="topic"]')).toHaveCount(0);
      await expect(page.getByRole('button', { name: 'Choose topic', exact: true })).toBeFocused();
      expect(await page.locator('html').evaluate(element => element.scrollWidth <= innerWidth)).toBe(true);
      expect(errors).toEqual([]);
    });
  }

  test('all scopes, single data and operation/format payload shapes', async ({ page, request }) => {
    await page.goto(route);
    await page.getByLabel('Annotation label:', { exact: true }).fill('All concept types');
    for (const [scope, identifier] of [['operation', 'operation_0292'], ['data', 'data_0863'], ['format', 'format_1929']]) {
      await keySelect(page, scope, identifier);
      await page.getByRole('button', { name: 'Apply selection', exact: true }).click();
    }
    await page.getByRole('button', { name: 'Validate annotations', exact: true }).click();
    await expect(page.getByRole('heading', { name: 'Validated annotations', exact: true })).toBeVisible();
    const payload = JSON.parse(await page.locator('#validated-edam').textContent());
    expect(payload.operation).toEqual([{ uri: 'http://edamontology.org/operation_0292', term: 'Sequence alignment' }]);
    expect(payload.input.data).toEqual({ uri: 'http://edamontology.org/data_0863', term: 'Sequence alignment' });
    expect(payload.input.format).toEqual([{ uri: 'http://edamontology.org/format_1929', term: 'FASTA' }]);
    const bounded = await request.get(endpoint, { params: { scope: 'operation' } });
    const body = await bounded.json();
    expect(body.items.length).toBeLessThanOrEqual(20);
    expect(body.more).toBe(true);
    expect(Buffer.byteLength(await bounded.text())).toBeLessThan(25000);
    for (const params of [{ scope: 'unknown' }, { scope: 'topic', id: 'http://edamontology.org/data_0863' },
                          { scope: 'topic', id: 'http://edamontology.org/topic_9999' }]) {
      expect((await request.get(endpoint, { params })).status()).toBe(400);
    }
  });

  test('lookup failure/retry and late responses never overwrite newer choices', async ({ page }) => {
    await page.goto(route);
    await page.route('**/edam/terms/**', route => route.fulfill({ status: 503, contentType: 'application/json',
      body: JSON.stringify({ error: { message: 'EDAM terms are temporarily unavailable. Please retry.' } }) }));
    await page.getByRole('button', { name: 'Choose topic', exact: true }).click();
    await expect(page.getByRole('alert')).toContainText('temporarily unavailable');
    await page.unroute('**/edam/terms/**');
    await page.getByRole('button', { name: 'Retry lookup', exact: true }).click();
    await expect(page.getByRole('option').first()).toBeVisible();
    let release;
    const gate = new Promise(resolve => { release = resolve; });
    await page.route('**/edam/terms/**', async intercepted => {
      if (new URL(intercepted.request().url()).searchParams.get('q') === 'topic_0091') {
        const response = await intercepted.fetch();
        await gate;
        await intercepted.fulfill({ response }).catch(() => {});
      } else await intercepted.continue();
    });
    const input = page.getByRole('combobox', { name: 'Find topic terms' });
    const pending = page.waitForRequest(request => new URL(request.url()).searchParams.get('q') === 'topic_0091');
    await input.fill('topic_0091'); await pending;
    await input.fill('topic_0080');
    await expect(page.getByRole('option')).toHaveCount(1);
    await expect(page.getByRole('option')).toContainText('Sequence analysis');
    release();
    await expect(page.getByRole('option')).toContainText('Sequence analysis');
  });

  test.describe('native form', () => {
    test.use({ javaScriptEnabled: false });
    test('validates identifiers without the Vue runtime', async ({ page }) => {
      await page.goto(route);
      await page.getByLabel('Annotation label:', { exact: true }).fill('Native EDAM check');
      await page.getByLabel('Topic URI', { exact: true }).fill(topicURI);
      await page.getByRole('button', { name: 'Validate annotations', exact: true }).click();
      await expect(page.getByRole('heading', { name: 'Validated annotations', exact: true })).toBeVisible();
      const payload = JSON.parse(await page.locator('#validated-edam').textContent());
      expect(payload.topic).toEqual([{ uri: topicURI, term: 'Sequence analysis' }]);
    });
  });
});
