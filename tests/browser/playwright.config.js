const { defineConfig } = require('@playwright/test');

const baseURL = process.env.BIOTOOLS_BASE_URL || 'http://localhost:8000';
const target = new URL(baseURL);
if (!['http:', 'https:'].includes(target.protocol) || target.pathname !== '/' ||
    target.search || target.hash || target.username || target.password) {
  throw new Error('BIOTOOLS_BASE_URL must be an HTTP(S) origin, without a path or credentials.');
}
if (Boolean(process.env.BIOTOOLS_TEST_USERNAME) !== Boolean(process.env.BIOTOOLS_TEST_PASSWORD)) {
  throw new Error('Set both BIOTOOLS_TEST_USERNAME and BIOTOOLS_TEST_PASSWORD, or neither.');
}

module.exports = defineConfig({
  testDir: '.',
  testMatch: '*.spec.js',
  workers: 1,
  retries: 0,
  forbidOnly: Boolean(process.env.CI),
  timeout: 30000,
  expect: { timeout: 10000 },
  reporter: [['list'], ['html', { open: 'never' }]],
  use: {
    baseURL: target.origin,
    browserName: 'chromium',
    ignoreHTTPSErrors: process.env.BIOTOOLS_TEST_LOCAL_TLS === '1',
    viewport: { width: 1440, height: 1000 },
    actionTimeout: 10000,
    navigationTimeout: 15000,
    screenshot: 'only-on-failure',
    trace: 'retain-on-failure',
  },
});
