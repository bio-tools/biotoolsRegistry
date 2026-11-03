const { test: base, expect } = require('@playwright/test');

const test = base.extend({
  page: async ({ page }, use, testInfo) => {
    // Optional legacy decoration/analytics must not gate local application tests.
    await page.route(/^https:\/\/(fonts\.googleapis\.com|fonts\.gstatic\.com|plausible\.galaxyproject\.eu|d1bxh8uas1mnw7\.cloudfront\.net|badge\.dimensions\.ai)\//,
      route => route.abort());
    await page.route('https://cdn.jsdelivr.net/gh/athenarc/bip-plugin@main/**', route => route.abort());
    const diagnostics = [];
    page.on('console', message => {
      if (['warning', 'error'].includes(message.type())) {
        diagnostics.push({ event: 'console', level: message.type(), text: message.text() });
      }
    });
    page.on('pageerror', error => diagnostics.push({ event: 'pageerror', text: error.message }));
    page.on('requestfailed', request => diagnostics.push({
      event: 'requestfailed', method: request.method(), url: request.url(), error: request.failure(),
    }));
    page.on('response', response => {
      if (response.status() >= 400) {
        diagnostics.push({ event: 'http', status: response.status(), url: response.url() });
      }
    });
    await use(page);
    if (testInfo.status !== testInfo.expectedStatus) {
      await testInfo.attach('browser-diagnostics', {
        body: JSON.stringify({ url: page.url(), diagnostics }, null, 2),
        contentType: 'application/json',
      });
    }
  },

  tool: async ({ request, baseURL }, use) => {
    const id = process.env.BIOTOOLS_TEST_TOOL_ID || 'signalp';
    let tool;
    try {
      const response = await request.get(`/api/t/${encodeURIComponent(id)}?format=json`, { timeout: 10000 });
      expect(response.ok(), `Fixture API returned HTTP ${response.status()}`).toBeTruthy();
      tool = await response.json();
      expect(tool.biotoolsID).toBe(id);
      expect(typeof tool.name).toBe('string');
      expect(tool.name.trim()).not.toBe('');
      expect(typeof tool.homepage).toBe('string');
      expect(tool.homepage.trim()).not.toBe('');
      expect(Array.isArray(tool.toolType)).toBeTruthy();
      expect(typeof tool.toolType[0]).toBe('string');
      expect(tool.toolType[0].trim()).not.toBe('');
    } catch (error) {
      throw new Error(`Browser fixture unavailable at ${baseURL}: tool "${id}" must exist with a name, homepage and tool type. ` +
        'Start the backend, seed and index the fixture, or set BIOTOOLS_BASE_URL and BIOTOOLS_TEST_TOOL_ID. ' +
        `See tests/browser/README.md.\n${error.message}`, { cause: error });
    }
    await use({ ...tool, query: process.env.BIOTOOLS_TEST_QUERY || id });
  },
});

const canonicalEditor = process.env.BIOTOOLS_TEST_CANONICAL_EDITOR === '1';
const canonicalAccounts = process.env.BIOTOOLS_TEST_ACCOUNTS === '1' && process.env.BIOTOOLS_EXPECT_ACCOUNTS !== '0';
const editorUrl = id => canonicalEditor ? (id ? `/${id}/edit` : '/register')
  : '/_migration/html/editor/' + (id ? `tool/${id}/` : 'new/');
const editorSaveUrl = id => editorUrl(id).replace(/\/$/, '') + '/save/';

module.exports = { test, expect, canonicalEditor, canonicalAccounts, editorUrl, editorSaveUrl };
