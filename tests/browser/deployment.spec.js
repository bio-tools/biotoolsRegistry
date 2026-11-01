const { test, expect } = require('./fixtures');

test.describe('Proxy route isolation', () => {
  test.skip(process.env.BIOTOOLS_TEST_HTML_SHELL !== '1', 'Requires the isolated HTML mount.');

  for (const userAgent of ['Migration browser', 'Googlebot']) {
    test(`HTML, fragments and API keep their owners for ${userAgent}`, async ({ request }) => {
      const headers = { 'User-Agent': userAgent };
      const full = await request.get('/_migration/html/preview/', { headers });
      expect(full.status()).toBe(200);
      expect(await full.text()).toContain('<!doctype html>');
      const fragment = await request.get('/_migration/html/preview/?message=Proxy', {
        headers: { ...headers, 'HX-Request': 'true' },
      });
      expect(fragment.status()).toBe(200);
      expect(await fragment.text()).not.toContain('<!doctype html>');
      expect(fragment.headers().vary.toLowerCase()).toContain('hx-request');
      expect(fragment.headers().vary.toLowerCase()).toContain('hx-history-restore-request');
      const restore = await request.get('/_migration/html/preview/', {
        headers: { ...headers, 'HX-Request': 'true', 'HX-History-Restore-Request': 'true' },
      });
      expect(await restore.text()).toContain('<!doctype html>');
      const api = await request.get('/api/env/', { headers: { ...headers, 'Biotools-Html': 'true' } });
      expect(api.status()).toBe(200);
      expect(['Development', 'Production']).toContain(await api.json());
      const asset = await request.get('/static/html/biotools-white.svg', { headers });
      expect(asset.status()).toBe(200);
      expect(asset.headers()['content-type']).toContain('image/svg+xml');
      expect(await asset.text()).toContain('<svg');
    });
  }

  test('errors, account endpoints and similar legacy prefixes stay isolated', async ({ request }) => {
    const missing = await request.get('/_migration/html/missing/');
    expect(missing.status()).toBe(404);
    expect(await missing.text()).toContain('<h1>Page not found</h1>');
    const spoof = await request.get('/api/_migration/html/');
    expect(spoof.status()).toBe(404);
    expect(await spoof.text()).not.toContain('Session check');
    const account = await request.get('/api/rest-auth/socialaccounts/');
    expect(account.status()).toBe(401);
    expect(account.headers()['content-type']).toContain('application/json');
    expect((await request.get('/_migration/htmlish')).status()).toBe(404);
    expect((await request.get('/register', { maxRedirects: 0 })).status()).toBe(302);
    expect(await (await request.get('/')).text()).toContain('bio.tools');
    const search = await request.get('/t');
    expect(await search.text()).toContain('data-vue-island="search-workspace"');
    expect(search.headers()['x-robots-tag']).toBe('noindex, follow');
  });
});
