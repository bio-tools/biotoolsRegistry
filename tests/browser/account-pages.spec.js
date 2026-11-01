const { test, expect } = require('./fixtures');
const enabled = process.env.BIOTOOLS_TEST_ACCOUNTS === '1';
const active = true;

test.describe('native account pages', () => {
  test.skip(!enabled, 'Requires the account-page rehearsal.');

  test('route ownership, rollback and API isolation', async ({ request }) => {
    for (const agent of ['Migration browser', 'Googlebot']) {
      for (const path of ['/login', '/signup', '/reset-password', '/profile']) {
        const response = await request.get(path, { headers: { 'User-Agent': agent }, maxRedirects: 0 });
        expect(response.headers()['x-biotools-route']).toBe('django-accounts');
        expect(response.headers()['cache-control']).toContain('no-store');
        expect(response.headers()['referrer-policy']).toBe('same-origin');
        expect(response.headers()['x-robots-tag']).toBe('noindex, follow');
        expect(response.status()).toBe(path === '/profile' ? 302 : 200);
      }
    }
    for (const [path, status] of [['/signup/verify-email/invalid', 200],
      ['/reset-password/confirm?uid=1&token=invalid', 302], ['/orcid/callback/', 503]]) {
      const response = await request.get(path, { maxRedirects: 0 });
      expect(response.status()).toBe(status);
      expect(response.headers()['x-biotools-route']).toBe('django-accounts');
    }
    expect((await request.get('/t')).headers()['x-biotools-route']).toBe('django-search');
    expect((await request.get('/detail-demo')).headers()['x-biotools-route']).toBe('django-detail');
    expect((await request.get('/api/rest-auth/user/')).status()).toBe(401);
    expect((await request.get('/static/html/shell.css')).headers()['content-type']).toContain('text/css');
  });

  for (const javaScriptEnabled of [true, false]) {
    test.describe(`account mutations JavaScript=${javaScriptEnabled}`, () => {
      test.use({ javaScriptEnabled });
      test('create account, change email and password, and sign in again', async ({ page }) => {
        test.skip(!active || process.env.BIOTOOLS_TEST_EDITOR_WRITES !== '1', 'Requires disposable account-write opt-in.');
        const username = 'account-browser-' + Date.now().toString(36);
        const password = 'Browser-account-only-2026';
        await page.goto('/signup');
        await page.getByLabel(/^Email:$/).fill(username + '@example.invalid');
        await page.getByLabel(/^Username:$/).fill(username);
        await page.getByLabel(/^Password:$/).fill(password);
        await page.getByLabel(/^Password \(again\):$/).fill(password);
        await page.getByRole('button', { name: 'Create account', exact: true }).click();
        await expect(page.getByRole('heading', { name: 'Account created', exact: true })).toBeVisible();
        await page.goto('/profile');
        await expect(page.getByRole('heading', { name: 'My profile', exact: true })).toBeVisible();
        await page.getByRole('link', { name: 'Change email', exact: true }).click();
        await page.getByLabel('New email').fill(username + '-updated@example.invalid');
        await page.getByRole('button', { name: 'Change email', exact: true }).click();
        await expect(page.getByText(username + '-updated@example.invalid', { exact: false })).toBeVisible();
        await page.getByRole('button', { name: 'Resend verification email', exact: true }).click();
        await expect(page.getByRole('status').filter({ hasText: 'verification email has been requested' })).toBeVisible();
        await page.getByRole('link', { name: 'Change password', exact: true }).click();
        await page.getByLabel(/^Current Password:$/i).fill(password);
        await page.getByLabel(/^New Password:$/i).fill(password + '-new');
        await page.getByLabel(/^New Password \(again\):$/i).fill(password + '-new');
        await page.getByRole('button', { name: 'Change password', exact: true }).click();
        await expect(page.getByRole('heading', { name: 'My profile', exact: true })).toBeVisible();
        await page.getByRole('button', { name: 'Sign out', exact: true }).click();
        await page.getByLabel('Username or email').fill(username);
        await page.getByLabel(/^Password:$/).fill(password + '-new');
        await page.getByRole('button', { name: 'Sign in', exact: true }).click();
        await expect(page.getByRole('heading', { name: 'My profile', exact: true })).toBeVisible();
      });
    });
    for (const width of [1440, 390]) {
      test.describe(`${width}px JavaScript=${javaScriptEnabled}`, () => {
        test.use({ javaScriptEnabled, viewport: { width, height: 1000 } });
        test('sign in, profile, account forms, requests and sign out', async ({ page }, testInfo) => {
          test.skip(!active);
          await page.goto('/profile');
          await expect(page.getByRole('heading', { name: 'Sign in', exact: true })).toBeVisible();
          await page.getByLabel('Username or email').fill(process.env.BIOTOOLS_TEST_USERNAME);
          await page.getByLabel(/^Password:$/).fill(process.env.BIOTOOLS_TEST_PASSWORD);
          await page.getByRole('button', { name: 'Sign in', exact: true }).click();
          await expect(page.getByRole('heading', { name: 'My profile', exact: true })).toBeVisible();
          await page.reload();
          expect(await page.locator('html').evaluate(el => el.scrollWidth <= innerWidth)).toBe(true);
          await page.screenshot({ path: testInfo.outputPath('profile.png') });
          await page.getByRole('link', { name: 'Change email', exact: true }).click();
          await expect(page.getByLabel('New email')).toBeVisible();
          await page.getByRole('link', { name: 'My profile', exact: true }).click();
          await page.getByRole('link', { name: 'Change password', exact: true }).click();
          await expect(page.getByRole('heading', { name: 'Change password', exact: true })).toBeVisible();
          await page.getByRole('link', { name: 'My profile', exact: true }).click();
          await page.getByRole('link', { name: /^Requests \(/ }).click();
          await expect(page.getByRole('heading', { name: 'Received requests', exact: true })).toBeVisible();
          await page.getByRole('button', { name: 'Sign out', exact: true }).click();
          await expect(page.getByRole('heading', { name: 'Sign in', exact: true })).toBeVisible();
          await page.goto('/profile');
          await expect(page.getByRole('heading', { name: 'Sign in', exact: true })).toBeVisible();
          expect((await page.request.get('/api/rest-auth/user/')).status()).toBe(401);
        });
      });
    }
  }

  test('signup validation, recovery and provider unavailable states', async ({ page }) => {
    test.skip(!active);
    await page.goto('/signup');
    await expect(page.getByRole('heading', { name: 'Create account', exact: true })).toBeVisible();
    await page.getByLabel('Email', { exact: false }).fill('account-browser@example.invalid');
    await page.getByLabel(/^Username:$/).fill('bad username');
    await page.getByLabel(/^Password:$/).fill('Browser-account-only-2026');
    await page.getByLabel(/^Password \(again\):$/).fill('Browser-account-only-2026');
    await page.getByRole('button', { name: 'Create account', exact: true }).click();
    await expect(page.locator('.errorlist').first()).toBeVisible();
    await page.goto('/reset-password');
    await page.getByLabel('Email', { exact: false }).fill('unknown-account-browser@example.invalid');
    await page.getByRole('button', { name: 'Send reset link', exact: true }).click();
    await expect(page.getByRole('heading', { name: 'Check your email', exact: true })).toBeVisible();
    await page.goto('/reset-password/confirm?uid=1&token=invalid');
    await expect(page.getByText('This password reset link is invalid or has expired.')).toBeVisible();
    await page.goto('/signup/verify-email/invalid');
    await expect(page.getByText('This verification link is invalid, expired or already used.')).toBeVisible();
    await page.goto('/login');
    await page.getByRole('button', { name: 'Sign in with ORCID', exact: true }).click();
    await expect(page.getByRole('heading', { name: 'ORCID sign-in unavailable', exact: true })).toBeVisible();
  });

  test('workflow navigation enters native accounts', async ({ page }) => {
    test.skip(!active);
    await page.goto('/workflows');
    if (await page.getByRole('button', { name: 'Toggle navigation', exact: true }).isVisible()) {
      await page.getByRole('button', { name: 'Toggle navigation', exact: true }).click();
    }
    await page.getByRole('link', { name: 'Sign in', exact: true }).click();
    await expect(page.getByRole('heading', { name: 'Sign in', exact: true })).toBeVisible();
    await expect(page.locator('[ng-app]')).toHaveCount(0);
  });
});
