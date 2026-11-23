const { test, expect, openAccountMenu } = require('./fixtures');

test('verification and password reset email work in the local preview', async ({ page, request, baseURL }) => {
  test.skip(process.env.BIOTOOLS_TEST_MAILPIT !== '1', 'Requires the local Mailpit preview and a disposable account.');
  const username = process.env.BIOTOOLS_MAILPIT_TEST_USER || '';
  if (baseURL !== 'http://localhost:8005' || !/^mailtest[a-f0-9]{12}$/.test(username)) {
    throw new Error('Use the local preview and a unique disposable mailtest username.');
  }
  const email = username + '@example.invalid';
  const oldPassword = 'MailTest-old-2026!';
  const newPassword = 'MailTest-new-2026!';

  async function capturedLink(path) {
    let result;
    await expect.poll(async () => {
      const messages = await (await request.get('http://localhost:8025/api/v1/search',
        { params: { query: `to:${email}` } })).json();
      for (const message of messages.messages) {
        const body = await (await request.get(`http://localhost:8025/api/v1/message/${message.ID}`)).json();
        const links = (body.Text || '').match(/http:\/\/localhost:8005\/[^\s<>]+/g) || [];
        result = links.find(link => new URL(link).pathname.startsWith(path));
        if (result) return true;
      }
      return false;
    }, { timeout: 15000 }).toBe(true);
    return result;
  }

  await page.goto('/signup');
  await page.getByLabel(/^Email:$/).fill(email);
  await page.getByLabel(/^Username:$/).fill(username);
  await page.getByLabel(/^Password:$/).fill(oldPassword);
  await page.getByLabel(/^Password \(again\):$/).fill(oldPassword);
  await page.getByRole('button', { name: 'Create account', exact: true }).click();
  await expect(page.getByRole('heading', { name: 'Account created' })).toBeVisible();
  const verification = await capturedLink('/signup/verify-email/');
  await page.goto(verification);
  await expect(page.getByText(/email address.*verified|email.*confirmed/i).first()).toBeVisible();
  await openAccountMenu(page);
  await page.getByRole('button', { name: 'Sign out', exact: true }).click();
  await expect(page.getByRole('heading', { name: 'Sign in', exact: true })).toBeVisible();
  await page.goto('/reset-password');
  await page.getByLabel(/^Email:$/).fill(email);
  await page.getByRole('button', { name: 'Send reset link', exact: true }).click();
  await expect(page.getByRole('heading', { name: 'Check your email' })).toBeVisible();
  const reset = await capturedLink('/reset-password/confirm');
  await page.goto(reset);
  await page.getByLabel(/^New Password:$/).fill(newPassword);
  await page.getByLabel(/^New Password \(again\):$/).fill(newPassword);
  await page.getByRole('button', { name: 'Change password', exact: true }).click();
  await expect(page.getByRole('heading', { name: 'Password changed' })).toBeVisible();
  await page.goto('/login');
  await page.getByLabel('Username or email:', { exact: true }).fill(username);
  await page.getByLabel('Password:', { exact: true }).fill(newPassword);
  await page.getByRole('button', { name: 'Sign in', exact: true }).click();
  await expect(page.getByRole('heading', { name: 'My profile' })).toBeVisible();
  await page.goto(reset);
  await expect(page.getByRole('alert')).toContainText(/invalid or has expired/i);
});
