const { test, expect } = require('./fixtures');

test.skip(process.env.BIOTOOLS_TEST_EXPERIENCE !== '1', 'Cross-page experience acceptance is opt-in.');
for (const width of [1440, 390, 320]) {
  for (const javaScriptEnabled of [true, false]) {
    test(`cross-page reflow ${width}px JavaScript=${javaScriptEnabled}`, async ({ browser, baseURL }, info) => {
      test.setTimeout(120000);
      const context = await browser.newContext({ baseURL, javaScriptEnabled, ignoreHTTPSErrors: true,
        viewport: { width, height: 1000 } });
      const page = await context.newPage();
      const failures = [];
      try {
        await page.goto('/login?next=/profile');
        await page.getByLabel('Username or email:', { exact: true }).fill(process.env.BIOTOOLS_TEST_USERNAME);
        await page.getByLabel('Password:', { exact: true }).fill(process.env.BIOTOOLS_TEST_PASSWORD);
        await page.getByRole('button', { name: 'Sign in', exact: true }).click();
        await expect(page).toHaveURL(/\/profile$/);
        for (const [name, route] of Object.entries({
          home: '/', search: '/t?domain=search-parity-fixture', detail: '/detail-demo',
          editor: '/editor-demo/edit', profile: '/profile', requests: '/requests',
          domains: '/domain-manager', domain: '/edit-domain/', workflows: '/workflows',
          account: '/profile/email/', about: '/about', communities: '/communities', statistics: '/stats',
        })) {
          const response = await page.goto(route);
          expect(response.status(), route).toBe(200);
          if (javaScriptEnabled && ['search', 'editor'].includes(name)) {
            await expect(page.locator(name === 'search' ? '.search-workspace' : '.resource-editor')).toBeVisible();
          }
          await expect(page.locator('main h1'), route).toHaveCount(1);
          const overflow = await page.evaluate(() => {
            if (document.documentElement.scrollWidth <= innerWidth + 1) return [];
            return [...document.querySelectorAll('main *, header *, footer *')].filter(element => {
              const box = element.getBoundingClientRect();
              return box.width && (box.right > innerWidth + 1 || box.left < -1);
            }).slice(0, 8).map(element => `${element.tagName}.${element.className}: ${element.textContent.slice(0, 70)}`);
          });
          if (overflow.length) failures.push({ route, overflow });
          if (['search', 'detail', 'editor', 'domain', 'workflows'].includes(name)) {
            await page.screenshot({ path: info.outputPath(`${name}.png`), fullPage: true });
          }
        }
        expect(failures, JSON.stringify(failures, null, 2)).toEqual([]);
      } finally { await context.close(); }
    });
  }
}

test('legacy comparison preferences are restored and changes survive reload', async ({ page }) => {
  await page.addInitScript(() => {
    if (sessionStorage.getItem('layout-seeded')) return;
    sessionStorage.setItem('layout-seeded', '1');
    localStorage.removeItem('biotools.search.columns.v1');
    localStorage.setItem('gridState', JSON.stringify({ columns: [
      { name: 'name', visible: true, width: 150 },
      { name: 'homepage', visible: true, width: 240 },
      { name: 'function', visible: false, width: 220 },
      { name: 'function2', visible: true, width: 260 },
      { name: 'description', visible: false, width: 300 },
    ] }));
  });
  await page.goto('/t?domain=search-parity-fixture&view=table');
  await expect(page.locator('.search-workspace')).toBeVisible();
  await page.locator('.comparison-columns summary').click();
  await expect(page.getByText(/previous table columns/)).toBeVisible();
  await expect(page.locator('.comparison-columns').getByLabel('Homepage', { exact: true })).toBeChecked();
  await expect(page.locator('.comparison-columns').getByLabel('Functions › Operations', { exact: true })).not.toBeChecked();
  await expect(page.locator('.comparison-columns').getByLabel('Functions › Inputs', { exact: true })).toBeChecked();
  await expect(page.locator('.comparison-columns').getByLabel('Description', { exact: true })).not.toBeChecked();
  await page.getByLabel('Homepage column width in pixels').fill('340');
  await page.getByLabel('Homepage column width in pixels').press('Tab');
  await page.locator('.comparison-columns').getByLabel('Description', { exact: true }).check();
  await expect(page.getByText('Table layout saved on this browser.')).toBeVisible();
  await page.reload();
  await page.locator('.comparison-columns summary').click();
  await expect(page.getByLabel('Homepage column width in pixels')).toHaveValue('340');
  await expect(page.locator('.comparison-columns').getByLabel('Description', { exact: true })).toBeChecked();
  await expect(page.locator('thead th').nth(1)).toHaveText('Homepage');
  await expect(page.locator('thead th').nth(2)).toHaveText('Functions › Inputs');
});

test('keyboard focus and 200 percent reflow on tool detail', async ({ page }) => {
  await page.setViewportSize({ width: 640, height: 900 });
  await page.goto('/detail-demo');
  await page.addStyleTag({ content: 'html { zoom: 2 }' });
  await page.keyboard.press('Tab');
  await expect(page.getByRole('link', { name: 'Skip to content' })).toBeFocused();
  await page.keyboard.press('Enter');
  await expect(page.locator('#main')).toBeFocused();
  const diagram = page.getByRole('group', { name: 'Function 1: inputs to operations to outputs' });
  await expect(diagram).toContainText('Input');
  await expect(diagram).toContainText('Operation');
  await expect(diagram).toContainText('Output');
  const boxes = await diagram.locator(':scope > div').evaluateAll(nodes => nodes.map(node => node.getBoundingClientRect().top));
  expect(boxes[0]).toBeLessThan(boxes[1]);
  expect(boxes[1]).toBeLessThan(boxes[2]);
  const overflowing = await page.evaluate(() => [...document.querySelectorAll('main *, header *, footer *')].filter(element => {
    const box = element.getBoundingClientRect();
    return box.width && (box.right > innerWidth + 1 || box.left < -1);
  }).slice(0, 5).map(element => element.tagName + '.' + element.className));
  expect(overflowing).toEqual([]);
});

test('sparse record with long unbroken values reflows on mobile', async ({ page, browser, baseURL }, info) => {
  test.skip(process.env.BIOTOOLS_TEST_EDITOR_WRITES !== '1', 'Requires disposable writes.');
  const id = 'experience-long-' + Date.now();
  const longValue = 'longsequence'.repeat(30);
  await page.goto('/register');
  await page.getByLabel('Username or email:', { exact: true }).fill(process.env.BIOTOOLS_TEST_USERNAME);
  await page.getByLabel('Password:', { exact: true }).fill(process.env.BIOTOOLS_TEST_PASSWORD);
  await page.getByRole('button', { name: 'Sign in', exact: true }).click();
  await page.getByLabel('Name', { exact: true }).fill('Sparse long value fixture');
  await page.getByLabel('bio.tools ID', { exact: true }).fill(id);
  await page.getByLabel('Homepage', { exact: true }).fill('https://example.org/' + longValue);
  await page.getByLabel('Description', { exact: true }).fill('Sparse record ' + longValue);
  await page.getByLabel('Command-line tool', { exact: true }).check();
  await page.getByRole('button', { name: 'Save changes', exact: true }).click();
  await expect(page.getByRole('status', { name: 'Save status' })).toHaveText('Changes saved.');
  const context = await browser.newContext({ baseURL, javaScriptEnabled: false, ignoreHTTPSErrors: true,
    viewport: { width: 320, height: 900 } });
  try {
    const mobile = await context.newPage();
    await mobile.goto('/' + id);
    await expect(mobile.getByText('Sparse record ' + longValue)).toBeVisible();
    await expect(mobile.getByRole('heading', { name: 'Functions', exact: true })).toHaveCount(0);
    expect(await mobile.locator('html').evaluate(node => node.scrollWidth <= innerWidth + 1)).toBe(true);
    await mobile.screenshot({ path: info.outputPath('long-detail.png'), fullPage: true });
    await mobile.goto('/t?q=' + id);
    await expect(mobile.locator('[data-tool-id="' + id + '"]')).toBeVisible();
    expect(await mobile.locator('html').evaluate(node => node.scrollWidth <= innerWidth + 1)).toBe(true);
  } finally { await context.close(); }
});

test('multiple functions remain distinct and readable on mobile', async ({ page }, info) => {
  await page.setViewportSize({ width: 390, height: 900 });
  await page.goto('/editor-demo');
  const functions = page.locator('.function-row');
  expect(await functions.count()).toBeGreaterThanOrEqual(2);
  await expect(functions.nth(0)).toContainText('Input');
  await expect(functions.nth(0)).toContainText('Operation');
  await expect(functions.nth(0)).toContainText('Output');
  await expect(functions.nth(1)).toContainText('Function 2');
  expect(await page.locator('html').evaluate(node => node.scrollWidth <= innerWidth + 1)).toBe(true);
  await page.locator('#functions').screenshot({ path: info.outputPath('multiple-functions.png') });
});

test('visible form controls have accessible names across migrated pages', async ({ page }) => {
  await page.goto('/login?next=/profile');
  await page.getByLabel('Username or email:', { exact: true }).fill(process.env.BIOTOOLS_TEST_USERNAME);
  await page.getByLabel('Password:', { exact: true }).fill(process.env.BIOTOOLS_TEST_PASSWORD);
  await page.getByRole('button', { name: 'Sign in', exact: true }).click();
  for (const route of ['/', '/t', '/detail-demo', '/editor-demo/edit', '/profile', '/requests',
    '/domain-manager', '/edit-domain/', '/workflows', '/profile/email/', '/about', '/communities', '/stats']) {
    await page.goto(route);
    if (route === '/editor-demo/edit') await expect(page.locator('.resource-editor')).toBeVisible();
    const unnamed = await page.evaluate(() => [...document.querySelectorAll('input:not([type=hidden]), select, textarea, button')]
      .filter(element => element.getClientRects().length && !element.getAttribute('aria-label') && !element.getAttribute('aria-labelledby') &&
        !(element.labels && element.labels.length) && !(element.tagName === 'BUTTON' && element.textContent.trim()) &&
        !(element instanceof HTMLInputElement && ['submit', 'button', 'reset'].includes(element.type) && element.value))
      .map(element => element.outerHTML.slice(0, 160)));
    expect(unnamed, route + ': ' + unnamed.join('\n')).toEqual([]);
  }
});

test('keyboard navigation exposes visible focus across migrated pages', async ({ page }) => {
  await page.goto('/login?next=/profile');
  await page.getByLabel('Username or email:', { exact: true }).fill(process.env.BIOTOOLS_TEST_USERNAME);
  await page.getByLabel('Password:', { exact: true }).fill(process.env.BIOTOOLS_TEST_PASSWORD);
  await page.getByRole('button', { name: 'Sign in', exact: true }).click();
  for (const route of ['/t', '/detail-demo', '/editor-demo/edit', '/profile', '/requests', '/edit-domain/', '/workflows', '/about']) {
    await page.goto(route);
    await page.locator('main').focus();
    for (let i = 0; i < 8; i++) {
      await page.keyboard.press('Tab');
      const focus = await page.evaluate(() => {
        const element = document.activeElement, style = getComputedStyle(element), rect = element.getBoundingClientRect();
        return { tag: element.tagName, visible: rect.width > 0 && rect.height > 0,
          outline: style.outlineStyle !== 'none' && parseFloat(style.outlineWidth) > 0 };
      });
      if (focus.tag === 'BODY') break;
      expect(focus.visible, route + ' ' + focus.tag).toBe(true);
      expect(focus.outline, route + ' ' + focus.tag).toBe(true);
    }
  }
});
