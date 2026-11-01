const { test, expect } = require('./fixtures');

const username = process.env.BIOTOOLS_TEST_USERNAME;
const password = process.env.BIOTOOLS_TEST_PASSWORD;
test.skip(process.env.BIOTOOLS_TEST_WORKFLOW_DRAFTS !== '1' || !username || !password,
  'Requires a disposable test account and explicit draft-write opt-in.');

async function signIn(page) {
  await page.goto('/login?next=%2Fworkflows%2Fdesign%2F');
  await page.getByLabel('Username or email:', { exact: true }).fill(username);
  await page.getByLabel('Password:', { exact: true }).fill(password);
  await page.getByRole('button', { name: 'Sign in', exact: true }).click();
  await expect(page).toHaveURL(/\/workflows\/design\/$/);
}

test('private drafts, read-only links, revocation and expired sessions preserve work', async ({ page, context, browser, baseURL }) => {
  const marker = `browser-workflow-${Date.now()}-${Math.random().toString(36).slice(2)}`;
  let viewer;
  try {
    await signIn(page);
    await page.getByLabel('Design title').fill(marker);
    await page.getByRole('button', { name: 'Choose data type' }).click();
    await page.getByRole('combobox', { name: 'Find data terms' }).fill('data_2044');
    await expect(page.getByRole('dialog').getByRole('option')).toHaveCount(1);
    await page.getByRole('dialog').getByRole('option').first().click();
    await page.getByRole('button', { name: 'Apply selection' }).click();
    await page.getByRole('button', { name: 'Search functions' }).click();
    const candidate = page.locator('li').filter({ hasText: 'Sequence Workbench (demo)' }).filter({ has: page.getByRole('button', { name: 'Add function' }) }).first();
    await expect(candidate).toBeVisible();
    await candidate.getByRole('button', { name: 'Add function' }).click();
    await candidate.getByRole('button', { name: 'Add function' }).click();
    await expect(page.getByRole('heading', { name: 'Sequence Workbench (demo)' })).toHaveCount(2);
    await page.getByLabel('Output', { exact: true }).selectOption({ index: 1 });
    await page.getByLabel('Input', { exact: true }).selectOption({ index: 2 });
    await page.getByLabel('Reason for an uncertain connection').fill('Review conversion');
    await page.getByRole('button', { name: 'Connect', exact: true }).click();
    await expect(page.getByRole('list', { name: 'Connections' })).toContainText('Review conversion');
    await page.getByRole('button', { name: 'Save private draft' }).click();
    await expect(page.getByRole('status').filter({ hasText: 'Draft saved privately.' })).toBeVisible();
    await page.getByRole('button', { name: 'Create sharing link' }).click();
    const link = await page.getByLabel('Read-only sharing link').inputValue();
    expect(link).toContain('/workflows/design/#share=');
    viewer = await browser.newContext({ baseURL, ignoreHTTPSErrors: true });
    const guest = await viewer.newPage();
    await guest.goto(link);
    await expect(guest.getByRole('heading', { name: marker })).toBeVisible();
    await expect(guest.getByRole('heading', { name: 'Sequence Workbench (demo)' })).toHaveCount(2);
    await expect(guest.getByRole('list', { name: 'Shared connections' })).toContainText('Review conversion');
    await expect(guest.getByText(/This shared design is read-only/)).toBeVisible();
    await expect(guest.getByRole('button', { name: 'Save private draft' })).toHaveCount(0);
    const copyPage = await context.newPage();
    await copyPage.goto(link);
    await copyPage.getByRole('button', { name: 'Copy to my drafts' }).click();
    await expect(copyPage.getByLabel('Design title')).toHaveValue('Copy of ' + marker);
    await expect(copyPage.getByRole('status').filter({ hasText: 'Draft saved privately.' })).toBeVisible();
    await copyPage.close();
    await page.getByLabel('Design title').fill(marker + '-changed');
    await expect(page.getByRole('button', { name: 'Create sharing link' })).toBeDisabled();
    const downloaded = page.waitForEvent('download');
    await page.getByRole('button', { name: 'Download draft' }).click();
    await downloaded;
    await expect(page.getByRole('button', { name: 'Create sharing link' })).toBeDisabled();
    await page.getByRole('button', { name: 'Revoke sharing' }).click();
    await expect(page.getByRole('status').filter({ hasText: 'Sharing revoked.' })).toBeVisible();
    await expect(page.getByLabel('Design title')).toHaveValue(marker + '-changed');
    await guest.reload();
    await expect(guest.getByRole('alert')).toContainText('Shared design not found');
    await page.getByLabel('Design title').fill(marker + '-after-expiry');
    await context.clearCookies({ name: 'sessionid' });
    await page.getByRole('button', { name: 'Save private draft' }).click();
    await expect(page.getByRole('alert').filter({ hasText: 'session ended' })).toBeVisible();
    await expect(page.getByLabel('Design title')).toHaveValue(marker + '-after-expiry');
    const loginPage = await context.newPage();
    await signIn(loginPage);
    await loginPage.close();
    await page.getByRole('button', { name: 'Reconnect', exact: true }).last().click();
    await page.getByRole('button', { name: 'Save private draft' }).click();
    await expect(page.getByRole('status').filter({ hasText: 'Draft saved privately.' })).toBeVisible();
  } finally {
    if (viewer) await viewer.close();
    try {
      await page.evaluate(async prefix => {
        const response = await fetch('/_workflow/designs/', { headers: { Accept: 'application/json' } });
        if (!response.ok) return;
        const { items } = await response.json();
        const csrf = document.querySelector('meta[name="csrf-token"]')?.content;
        for (const item of items.filter(item => item.title.includes(prefix))) {
          await fetch(`/_workflow/designs/${item.id}/`, { method: 'DELETE', headers: { 'X-CSRFToken': csrf, 'If-Match': item.revision } });
        }
      }, marker);
    } catch { /* The disposable fixture is isolated if the browser lost its session. */ }
  }
});
