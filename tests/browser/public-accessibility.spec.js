const { test, expect } = require('./fixtures');

test.skip(process.env.BIOTOOLS_TEST_PUBLIC_A11Y !== '1', 'Requires a local database-backed preview.');

for (const width of [1440, 390, 320]) {
  test(`public pages retain accessible controls and reflow at ${width}px`, async ({ page }) => {
    await page.setViewportSize({ width, height: 900 });
    for (const route of ['/', '/t', '/fastqc', '/workflows', '/about', '/stats', '/login']) {
      const response = await page.goto(route);
      expect(response.status(), route).toBe(200);
      await expect(page.locator('main'), route).toHaveCount(1);
      const problems = await page.evaluate(() => {
        const unnamed = [...document.querySelectorAll('input:not([type=hidden]), select, textarea, button')]
          .filter(element => element.getClientRects().length && !element.closest('[aria-hidden="true"]') &&
            !element.getAttribute('aria-label') && !element.getAttribute('aria-labelledby') &&
            !(element.labels && element.labels.length) && !(element.tagName === 'BUTTON' && element.textContent.trim()) &&
            !(element instanceof HTMLInputElement && ['submit', 'button', 'reset'].includes(element.type) && element.value))
          .map(element => element.outerHTML.slice(0, 180));
        return { unnamed, overflow: document.documentElement.scrollWidth > innerWidth + 1 };
      });
      expect(problems.unnamed, route).toEqual([]);
      expect(problems.overflow, route).toBe(false);
    }
  });
}

test('skip link is keyboard-accessible on public pages', async ({ page }) => {
  await page.goto('/about');
  await page.keyboard.press('Tab');
  await expect(page.getByRole('link', { name: 'Skip to content' })).toBeFocused();
  await page.keyboard.press('Enter');
  await expect(page.locator('#main')).toBeFocused();
});

for (const width of [1440, 900, 390]) {
  test(`tool metadata uses available space at ${width}px`, async ({ page }) => {
    await page.setViewportSize({ width, height: 900 });
    await page.goto('/fastqc');
    const content = page.locator('.detail-content');
    const sections = content.locator(':scope > section[id^="metadata-"]');
    expect(await sections.count()).toBeGreaterThanOrEqual(2);
    const first = await sections.nth(0).boundingBox();
    const second = await sections.nth(1).boundingBox();
    const area = await content.boundingBox();
    const functions = await page.locator('#functions').boundingBox();
    expect(Math.abs(functions.width - area.width)).toBeLessThan(1);
    if (width === 1440) {
      expect(Math.abs(first.y - second.y)).toBeLessThan(1);
      expect(second.x).toBeGreaterThan(first.x + first.width);
    } else {
      expect(Math.abs(first.x - second.x)).toBeLessThan(1);
      expect(second.y).toBeGreaterThan(first.y + first.height - 1);
    }
    expect(await page.locator('html').evaluate(el => el.scrollWidth <= innerWidth + 1)).toBe(true);
  });
}
