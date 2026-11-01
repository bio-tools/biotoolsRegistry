const { test, expect, canonicalEditor } = require('./fixtures');
const user = process.env.BIOTOOLS_TEST_USERNAME;

test.describe('canonical editor routes', () => {
  test.skip(!canonicalEditor, 'Requires the canonical editor fixture.');
  for (const agent of ['Migration browser', 'Googlebot']) {
    test(`editor route ownership and isolation for ${agent}`, async ({ request }) => {
      for (const path of ['/register', '/register/', '/editor-demo/edit', '/requests']) {
        const response = await request.get(path, { headers: { 'User-Agent': agent }, maxRedirects: 0 });
        expect(response.status(), path).toBe(302);
        expect(response.headers()['x-biotools-route']).toBe(path.startsWith('/requests') ? 'django-requests' : 'django-editor');
        expect(response.headers().location).toContain('/login?');
        expect(response.headers()['x-robots-tag']).toBe('noindex, follow');
      }
      expect((await request.get('/api/rest-auth/user/')).status()).toBe(401);
    });
  }
  for (const width of [1440, 390]) {
    test(`account navigation enters the editor and requests at ${width}px`, async ({ page }) => {
      await page.setViewportSize({ width, height: 1000 });
      await page.goto('/login');
      await page.getByLabel('Username or email:', { exact: true }).fill(user);
      await page.getByLabel('Password:', { exact: true }).fill(process.env.BIOTOOLS_TEST_PASSWORD);
      await page.getByRole('button', { name: 'Sign in', exact: true }).click();
      await page.goto('/register');
      await expect(page.locator('[data-vue-island="resource-editor"]')).toHaveAttribute('data-v-app', '');
      await page.reload();
      await expect(page.getByLabel('Name', { exact: true })).toBeVisible();
      await page.goto('/requests');
      await expect(page.getByRole('heading', { name: 'Received requests', exact: true })).toBeVisible();
      await page.reload();
      await expect(page.getByRole('heading', { name: 'Sent requests', exact: true })).toBeVisible();
      expect(await page.locator('html').evaluate(el => el.scrollWidth <= innerWidth)).toBe(true);
      await page.getByRole('button', { name: 'Sign out', exact: true }).click();
      await expect(page.getByRole('heading', { name: 'Sign in', exact: true })).toBeVisible();
      await page.goto('/register');
      await expect(page.getByRole('heading', { name: 'Sign in', exact: true })).toBeVisible();
    });
  }
});
