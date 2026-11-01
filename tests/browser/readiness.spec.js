const { test, expect } = require('./fixtures');

test('permanent EDAM lookup and preview alias have the same public contract', async ({ request }) => {
  test.skip(process.env.BIOTOOLS_TEST_READINESS !== '1', 'Requires the migration preview.');
  for (const agent of ['Migration browser', 'Googlebot']) {
    const headers = { 'User-Agent': agent };
    const query = '?scope=topic&q=sequence';
    const permanent = await request.get('/_edam/terms/' + query, { headers });
    const preview = await request.get('/_migration/html/edam/terms/' + query, { headers });
    expect(permanent.status()).toBe(200);
    expect(permanent.headers()['x-biotools-route']).toBe('django-edam');
    expect(permanent.headers()['x-robots-tag']).toBe('noindex, follow');
    expect(await permanent.json()).toEqual(await preview.json());
    expect((await request.get('/_edam/terms/?scope=unknown', { headers })).status()).toBe(400);
    const rejected = await request.post('/_edam/terms/', { headers });
    const previewRejected = await request.post('/_migration/html/edam/terms/', { headers });
    expect(rejected.status()).toBe(403);
    expect(previewRejected.status()).toBe(rejected.status());
  }
});

test('canonical search and editor use the permanent EDAM lookup', async ({ page }) => {
  test.skip(process.env.BIOTOOLS_TEST_READINESS !== '1' || !process.env.BIOTOOLS_TEST_USERNAME,
    'Requires the migration preview and a disposable account.');
  await page.goto('/t');
  const config = selector => page.locator(selector).evaluate(element => JSON.parse(element.content.querySelector('script').textContent));
  expect((await config('#search-config')).edamEndpoint).toBe('/_edam/terms/');
  await page.goto('/editor-demo/edit');
  await page.getByLabel('Username or email:', { exact: true }).fill(process.env.BIOTOOLS_TEST_USERNAME);
  await page.getByLabel('Password:', { exact: true }).fill(process.env.BIOTOOLS_TEST_PASSWORD);
  await page.getByRole('button', { name: 'Sign in', exact: true }).click();
  expect((await config('#editor-config')).edamEndpoint).toBe('/_edam/terms/');
  await expect(page.locator('.resource-editor')).toBeVisible();
  const lookup = page.waitForResponse(response => new URL(response.url()).pathname === '/_edam/terms/');
  await page.getByRole('button', { name: /^Choose topic 1:/ }).click();
  expect((await lookup).status()).toBe(200);
  await expect(page.getByRole('dialog').getByRole('combobox')).toBeFocused();
  await page.getByRole('button', { name: 'Cancel', exact: true }).click();
});

test('production mode hides demonstration pages but retains compatibility routes', async ({ request }) => {
  test.skip(process.env.BIOTOOLS_TEST_DEMOS_DISABLED !== '1', 'Requires the isolated demo-disabled rehearsal.');
  for (const agent of ['Migration browser', 'Googlebot']) {
    const headers = { 'User-Agent': agent };
    for (const path of ['/_migration/html/', '/_migration/html/preview/', '/_migration/html/islands/', '/_migration/html/edam/']) {
      expect((await request.get(path, { headers })).status(), path).toBe(404);
    }
    for (const path of ['/_edam/terms/?scope=topic&q=sequence', '/_migration/html/edam/terms/?scope=topic&q=sequence']) {
      expect((await request.get(path, { headers })).status(), path).toBe(200);
    }
    expect((await request.get('/t', { headers })).status()).toBe(200);
    expect((await request.get('/_migration/html/editor/new/', { headers, maxRedirects: 0 })).status()).toBe(302);
  }
});
