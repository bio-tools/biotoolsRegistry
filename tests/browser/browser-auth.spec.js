const { test, expect } = require('./fixtures');

const mount = '/_migration/html';
const username = process.env.BIOTOOLS_TEST_USERNAME;
const password = process.env.BIOTOOLS_TEST_PASSWORD;

async function signIn(page) {
  await page.getByLabel('Username or email:', { exact: true }).fill(username);
  await page.getByLabel('Password:', { exact: true }).fill(password);
  await page.getByRole('button', { name: 'Sign in', exact: true }).click();
  await expect(page.getByRole('heading', { name: 'Account', exact: true })).toBeVisible();
}

test.describe('migrated browser authentication', () => {
  test.skip(process.env.BIOTOOLS_TEST_BROWSER_AUTH !== '1', 'Requires migrated browser auth and a disposable fixture account.');
  test.beforeEach(() => { expect(username).toBeTruthy(); expect(password).toBeTruthy(); });

  for (const width of [1440, 390]) {
    test(`login, Vue session check and htmx logout at ${width}px`, async ({ page, context }, testInfo) => {
      const errors = [];
      page.on('pageerror', error => errors.push(error.message));
      await page.setViewportSize({ width, height: 1000 });
      await page.goto(mount + '/account/');
      await expect(page).toHaveURL(new RegExp(mount + '/auth/login/'));
      await page.getByLabel('Username or email:', { exact: true }).fill(username);
      await page.getByLabel('Password:', { exact: true }).fill('wrong-password');
      await page.getByRole('button', { name: 'Sign in', exact: true }).click();
      await expect(page.getByText('Unable to sign in with these credentials.')).toBeVisible();
      await page.screenshot({ path: testInfo.outputPath('login.png'), fullPage: true });
      await signIn(page);
      await expect(page.locator('[data-vue-island="session-check"]')).toHaveAttribute('data-v-app', '');
      const response = page.waitForResponse(response => response.url().endsWith('/auth/check/'));
      await page.getByRole('button', { name: 'Verify session', exact: true }).click();
      expect((await response).status()).toBe(200);
      await expect(page.getByText('Session verified.', { exact: true })).toBeVisible();
      const cookie = (await context.cookies()).find(cookie => cookie.name === 'sessionid');
      expect(cookie.httpOnly).toBe(true);
      expect(cookie.sameSite).toBe('Lax');
      const storage = await page.evaluate(() => ({ local: { ...localStorage }, session: { ...sessionStorage } }));
      if (storage.session['biotools-tool-count']) {
        expect(JSON.parse(storage.session['biotools-tool-count']).count).toBeGreaterThanOrEqual(0);
        delete storage.session['biotools-tool-count'];
      }
      expect(storage)
        .toEqual({ local: {}, session: { 'htmx-current-path-for-history': mount + '/account/' } });
      if (width === 1440) {
        const alignment = await page.locator('.site-header nav').evaluate(nav => {
          const first = nav.querySelector('a').getBoundingClientRect();
          const logout = nav.querySelector('.nav-button').getBoundingClientRect();
          return Math.abs(first.y + first.height / 2 - logout.y - logout.height / 2);
        });
        expect(alignment).toBeLessThanOrEqual(2);
      }
      await page.screenshot({ path: testInfo.outputPath('account.png'), fullPage: true });
      expect(await page.locator('html').evaluate(element => element.scrollWidth <= innerWidth)).toBe(true);
      const logout = page.waitForResponse(response => response.url().endsWith('/auth/logout/'));
      await page.getByRole('button', { name: 'Sign out', exact: true }).click();
      expect((await logout).headers()['hx-redirect']).toBe(mount + '/auth/login/');
      await expect(page.getByRole('heading', { name: 'Sign in', exact: true })).toBeVisible();
      expect(errors).toEqual([]);
    });
  }

  test('expired Vue request and sign-in in another tab allow explicit reconnection', async ({ page, context }) => {
    await page.goto(mount + '/account/');
    await signIn(page);
    await context.clearCookies({ name: 'sessionid' });
    await page.getByRole('button', { name: 'Verify session', exact: true }).click();
    await expect(page.locator('#authentication-error')).toContainText('Your session has ended.');
    await expect(page).toHaveURL(new RegExp(mount + '/account/$'));
    const popup = page.waitForEvent('popup');
    await page.locator('#authentication-login').click();
    const login = await popup;
    await signIn(login);
    await login.close();
    await page.getByRole('button', { name: 'Reconnect', exact: true }).click();
    await expect(page.locator('#authentication-error')).toBeHidden();
    await page.getByRole('button', { name: 'Verify session', exact: true }).click();
    await expect(page.getByText('Session verified.', { exact: true })).toBeVisible();
  });

  test('htmx expiry keeps an entered annotation instead of swapping in login HTML', async ({ page, context }) => {
    await page.goto(mount + '/account/');
    await signIn(page);
    await page.goto(mount + '/edam/');
    await page.getByLabel('Annotation label:', { exact: true }).fill('Unsaved annotation');
    await context.clearCookies({ name: 'sessionid' });
    const response = page.waitForResponse(response => response.url().endsWith('/auth/logout/'));
    await page.getByRole('button', { name: 'Sign out', exact: true }).click();
    expect((await response).status()).toBe(401);
    await expect(page.locator('#authentication-error')).toBeVisible();
    await expect(page.getByLabel('Annotation label:', { exact: true })).toHaveValue('Unsaved annotation');
    await expect(page).toHaveURL(new RegExp(mount + '/edam/$'));
    await expect(page.getByRole('heading', { name: 'Sign in', exact: true })).toHaveCount(0);
  });

  test('missing CSRF is rejected and reconnect refreshes stale form credentials', async ({ page }) => {
    await page.goto(mount + '/account/');
    await signIn(page);
    const rejected = await page.evaluate(async mount => {
      const response = await fetch(mount + '/auth/check/', { method: 'POST', headers: { Accept: 'application/json' } });
      return { status: response.status, body: await response.json() };
    }, mount);
    expect(rejected).toEqual({ status: 403, body: { error: { code: 'csrf_failed' } } });
    await page.evaluate(() => { document.querySelector('meta[name="csrf-token"]').content = 'x'.repeat(64); });
    await page.getByRole('button', { name: 'Verify session', exact: true }).click();
    await expect(page.locator('#authentication-error')).toContainText('security check failed');
    await page.getByRole('button', { name: 'Reconnect', exact: true }).click();
    await expect(page.locator('#authentication-error')).toBeHidden();
    await page.getByRole('button', { name: 'Verify session', exact: true }).click();
    await expect(page.getByText('Session verified.', { exact: true })).toBeVisible();
  });

  test('ordinary forms work without JavaScript and recovery API routes remain Django-owned', async ({ browser, baseURL, request }) => {
    const context = await browser.newContext({ baseURL, javaScriptEnabled: false,
      ignoreHTTPSErrors: process.env.BIOTOOLS_TEST_LOCAL_TLS === '1' });
    try {
      const page = await context.newPage();
      await page.goto(mount + '/account/');
      await signIn(page);
      await page.getByRole('button', { name: 'Verify session', exact: true }).click();
      await expect(page.getByText('Session verified.', { exact: true })).toBeVisible();
      await page.getByRole('button', { name: 'Sign out', exact: true }).click();
      await expect(page.getByRole('heading', { name: 'Sign in', exact: true })).toBeVisible();
    } finally { await context.close(); }
    const recovery = await request.get('/api/rest-auth/password/reset/confirm/invalid/invalid/', { headers: { Accept: 'application/json' } });
    expect(recovery.status()).toBe(405);
    expect(recovery.headers()['content-type']).toContain('application/json');
    const foreign = await request.post('/api/rest-auth/socialaccounts/999999/disconnect/');
    expect(foreign.status()).toBe(401);
  });
});
