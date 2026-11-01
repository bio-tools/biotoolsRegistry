const { test, expect, canonicalEditor, editorUrl, editorSaveUrl } = require('./fixtures');

const mount = '/_migration/html';
const requests = canonicalEditor ? '/requests' : mount + '/requests';
const user = process.env.BIOTOOLS_TEST_USERNAME;
const password = process.env.BIOTOOLS_TEST_PASSWORD;
const unique = () => Date.now().toString(36) + Math.random().toString(36).slice(2, 6);

async function signIn(page) {
  await page.goto(mount + '/account/');
  await page.getByLabel('Username or email:', { exact: true }).fill(user);
  await page.getByLabel('Password:', { exact: true }).fill(password);
  await page.getByRole('button', { name: 'Sign in', exact: true }).click();
  await expect(page.getByRole('heading', { name: 'Account', exact: true })).toBeVisible();
}

async function post(context, path, data) {
  const token = (await context.cookies()).find(cookie => cookie.name === 'csrftoken').value;
  return context.request.post(path, { data, headers: { 'X-CSRFToken': token, Accept: 'application/json' } });
}

test.describe('ownership and session interoperability', () => {
  test.skip(process.env.BIOTOOLS_TEST_SESSION_BRIDGE !== '1', 'Requires the session bridge and disposable registry-write opt-in.');
  test.beforeEach(() => {
    expect(process.env.BIOTOOLS_TEST_EDITOR_WRITES).toBe('1');
    expect(user).toBeTruthy(); expect(password).toBeTruthy();
  });

  for (const width of [1440, 390]) {
    test(`editing and ownership requests survive replacement and transfer at ${width}px`, async ({ page, context, browser, baseURL }, info) => {
      await page.setViewportSize({ width, height: 1000 });
      await signIn(page);
      const id = 'request-browser-' + unique();
      await page.goto(editorUrl());
      const schemaRevision = await page.locator('#editor-config').evaluate(template =>
        JSON.parse(template.content.querySelector('script').textContent).schemaRevision);
      const response = await post(context, editorSaveUrl(), { revision: null, schemaRevision, resource: {
        biotoolsID: id, name: 'Request Browser Sample', homepage: 'https://example.org/request',
        description: 'Disposable ownership request regression fixture.', toolType: ['Command-line tool'],
      } });
      expect(response.status()).toBe(201);
      const sender = await browser.newContext({ baseURL, javaScriptEnabled: false,
        viewport: { width, height: 1000 }, ignoreHTTPSErrors: process.env.BIOTOOLS_TEST_LOCAL_TLS === '1' });
      try {
        const username = 'request-' + unique();
        await sender.request.get('/api/browser-session/');
        const signup = await post(sender, mount + '/api/rest-auth/registration/', {
          username, email: username + '@example.org', password1: password, password2: password,
        });
        expect(signup.status()).toBe(201);
        expect(await signup.json()).not.toHaveProperty('key');
        const senderPage = await sender.newPage();
        for (const kind of ['Editing rights', 'Ownership', 'Editing rights']) {
          await senderPage.goto(requests + '/tool/' + id + '/');
          await senderPage.getByRole('radio', { name: kind, exact: true }).check();
          await senderPage.getByRole('button', { name: 'Send request', exact: true }).click();
          await expect(senderPage.getByText('Request sent.', { exact: true })).toBeVisible();
        }
        await page.goto(requests);
        let rows = page.locator('article').filter({ has: page.getByRole('link', { name: id, exact: true }) });
        await rows.filter({ hasText: 'Editing rights requested' }).first().getByRole('button', { name: 'Accept', exact: true }).click();
        await expect(page.getByText('Request accepted.', { exact: true })).toBeVisible();
        // Save a replacement version before the remaining ownership decision.
        const editor = await sender.request.get(editorUrl(id));
        expect(editor.status()).toBe(200);
        await page.goto(editorUrl(id));
        await page.getByLabel('Name', { exact: true }).fill('Request Browser Updated');
        await page.getByRole('button', { name: 'Save changes', exact: true }).click();
        await expect(page.getByRole('status')).toHaveText('Changes saved.');
        await page.goto(requests);
        rows = page.locator('article').filter({ has: page.getByRole('link', { name: id, exact: true }) });
        await rows.filter({ hasText: 'Ownership requested' }).getByRole('button', { name: 'Accept', exact: true }).click();
        await expect(page.getByText('Request accepted.', { exact: true })).toBeVisible();
        await expect(page.locator('article').filter({ hasText: id })).toHaveCount(0);
        const oldOwner = await context.request.get(editorUrl(id));
        expect(oldOwner.status()).toBe(403);
        await senderPage.goto(requests);
        await senderPage.getByRole('region', { name: 'Received requests' }).getByRole('button', { name: 'Decline', exact: true }).click();
        await expect(senderPage.getByText('Request declined.', { exact: true })).toBeVisible();
        await senderPage.getByRole('checkbox', { name: 'Include completed' }).check();
        await senderPage.getByRole('button', { name: 'Apply', exact: true }).click();
        await expect(senderPage.getByRole('region', { name: 'Sent requests' })).toContainText('Accepted');
        await senderPage.screenshot({ path: info.outputPath('requests.png'), fullPage: true });
        expect(await senderPage.locator('html').evaluate(element => element.scrollWidth <= innerWidth)).toBe(true);
        const final = await (await context.request.get('/api/t/' + id + '?format=json')).json();
        expect(final.owner).toBe(username);
        expect(final.name).toBe('Request Browser Updated');
      } finally { await sender.close(); }
    });
  }

  test('expired browser session cannot mutate through the bridge', async ({ page, context }) => {
    await signIn(page);
    await page.goto('/profile');
    await expect(page.getByRole('heading', { name: 'My profile', exact: true })).toBeVisible();
    await context.clearCookies({ name: 'sessionid' });
    const response = await post(context, mount + '/api/request/conclude', { requestId: 'absent', accept: true });
    expect(response.status()).toBe(403);
    await page.reload();
    await expect(page.getByRole('heading', { name: 'Sign in', exact: true })).toBeVisible();
  });
});
