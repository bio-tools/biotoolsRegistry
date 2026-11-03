const { test, expect } = require('./fixtures');
const schema = require('../../backend/elixir/biotoolsSchema/resource-ui.generated.json');
const fixtures = require('../../backend/elixirapp/tests/data/ResourceEditor.json');

async function mountEditor(page, resource) {
  await page.goto('/');
  const config = { resource, revision: 'fixture', endpoint: '/test-save/', validateEndpoint: '/test-validate/', previewEndpoint: '/test-preview/', bridgeEndpoint: '/test-bridge/',
    schema, schemaRevision: schema.revision, editUrl: null, detailUrl: '/psiclass', toolTypes: [], edamEndpoint: '/_edam/terms/' };
  await page.evaluate(config => {
    const main = document.querySelector('main');
    const template = document.createElement('template'); template.id = 'test-editor-config';
    const script = document.createElement('script'); script.type = 'application/json'; script.textContent = JSON.stringify(config);
    template.content.append(script);
    const root = document.createElement('div'); root.dataset.vueIsland = 'resource-editor'; root.dataset.vueProps = template.id;
    root.setAttribute('hx-disable', ''); main.replaceChildren(template, root);
    root.dispatchEvent(new CustomEvent('htmx:load', { bubbles: true }));
  }, config);
}

test.describe('Annotation editor presentation', () => {
  test.skip(process.env.BIOTOOLS_TEST_LIVE_FILTERS !== '1', 'Requires the local preview assets.');
  for (const width of [1440, 390]) {
    test(`preview and individually select bridge suggestions at ${width}px`, async ({ page }) => {
      await page.setViewportSize({ width, height: 900 });
      await page.route('**/test-bridge/', route => route.fulfill({ json: { schemaRevision: schema.revision, rejected: [], raw: {},
        suggestions: { topic: [{ term: 'Zeta', uri: 'http://edamontology.org/topic_0002' }, { term: 'Alpha', uri: 'http://edamontology.org/topic_0001' }] } } }));
      await page.route('**/test-preview/', route => {
        const name = route.request().postDataJSON().resource.name;
        return route.fulfill({ contentType: 'text/html', body: '<h1>' + name + '</h1>' });
      });
      await mountEditor(page, fixtures.rich);
      await page.getByText('Import metadata from GitHub', { exact: true }).click();
      await page.getByLabel('GitHub repository URL').fill('https://github.com/maxsonBraunLab/CITEViz/');
      await page.getByRole('button', { name: 'Get suggestions' }).click();
      await page.getByLabel('Action for Topics', { exact: true }).selectOption('merge');
      const suggestions = page.getByRole('group', { name: 'Select Topics items to add' });
      await expect(suggestions.getByRole('checkbox')).toHaveCount(2);
      await expect(suggestions.locator('label').first()).toContainText('Alpha');
      await suggestions.getByLabel('Alpha', { exact: true }).uncheck();
      await expect(suggestions.getByLabel('Zeta', { exact: true })).toBeChecked();
      await page.getByRole('button', { name: 'Apply to draft' }).click();
      await page.getByLabel('Name', { exact: true }).fill('Unsaved preview');
      await page.getByRole('button', { name: 'Preview record' }).click();
      await expect(page.frameLocator('iframe[title="Preview of the tool record"]').getByRole('heading', { name: 'Unsaved preview' })).toBeVisible();
      await page.getByLabel('Name', { exact: true }).fill('Updated draft');
      await expect(page.getByText('Draft changed. Refresh the preview to see the latest changes.')).toBeVisible();
      await page.getByRole('button', { name: 'Refresh preview' }).click();
      await expect(page.frameLocator('iframe[title="Preview of the tool record"]').getByRole('heading', { name: 'Updated draft' })).toBeVisible();
      expect(await page.locator('html').evaluate(element => element.scrollWidth <= innerWidth)).toBe(true);
    });
    test(`form and JSON synchronize without writes at ${width}px`, async ({ page }, testInfo) => {
      await page.setViewportSize({ width, height: 900 });
      await mountEditor(page, fixtures.rich);
      await expect(page.locator('.resource-editor')).toBeVisible();
      await expect(page.locator('.editor-card')).toBeVisible();
      await expect(page.locator('.metadata-section').first()).toBeVisible();
      await expect(page.locator('.function-editor')).toBeVisible();
      await expect(page.locator('.editor-help')).toHaveAttribute('title', /current record in JSON format/);
      await page.locator('.editor-json-panel summary').click();
      const json = page.getByLabel('Resource JSON', { exact: true });
      expect(JSON.parse(await json.inputValue()).name).toBe(fixtures.rich.name);
      await page.getByLabel('Name', { exact: true }).fill('Changed in form');
      await expect.poll(async () => JSON.parse(await json.inputValue()).name).toBe('Changed in form');
      const value = JSON.parse(await json.inputValue());
      value.name = 'Changed in JSON';
      value.credit[0].name = 'A different contributor';
      await json.fill(JSON.stringify(value, null, 2));
      await expect(page.getByLabel('Name', { exact: true })).toHaveValue('Changed in JSON');
      await expect(page.locator('#nested-credit input[id$="-name"]').first()).toHaveValue('A different contributor');
      await json.fill('{broken');
      await expect(page.locator('.json-error')).toContainText('incomplete or invalid');
      await expect(page.getByLabel('Name', { exact: true })).toBeDisabled();
      await expect(page.getByRole('button', { name: 'Save changes', exact: true })).toBeDisabled();
      await page.locator('.editor-json-panel summary').click();
      await expect(page.locator('.json-error')).toBeVisible();
      await page.getByRole('button', { name: 'Restore JSON from form' }).click();
      await expect(page.getByLabel('Name', { exact: true })).toBeEnabled();
      await expect(page.getByLabel('Name', { exact: true })).toHaveValue('Changed in JSON');
      expect(await page.locator('html').evaluate(element => element.scrollWidth <= innerWidth)).toBe(true);
      await page.screenshot({ path: testInfo.outputPath('editor-cards.png'), fullPage: true });
    });
  }
  test('synchronizes a real registry record without saving it', async ({ page, request }) => {
    const response = await request.get('/api/t/psiclass?format=json');
    expect(response.ok()).toBe(true);
    const record = await response.json();
    await mountEditor(page, record);
    await page.locator('.editor-json-panel summary').click();
    const json = page.getByLabel('Resource JSON', { exact: true });
    expect(JSON.parse(await json.inputValue()).biotoolsID).toBe(record.biotoolsID);
    const value = JSON.parse(await json.inputValue()); value.name = 'Local synchronization check';
    await json.fill(JSON.stringify(value));
    await expect(page.getByLabel('Name', { exact: true })).toHaveValue('Local synchronization check');
    await expect(page.locator('.json-error')).toHaveCount(0);
  });
});
