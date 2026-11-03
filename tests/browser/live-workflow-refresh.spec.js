const { test, expect } = require('./fixtures');

test.describe('Detail and workflow presentation', () => {
  test.skip(process.env.BIOTOOLS_TEST_LIVE_FILTERS !== '1', 'Requires the local database-backed preview.');
  test('dates, detail links, arrows and signed-out actions', async ({ page }) => {
    await page.setViewportSize({ width: 1440, height: 900 });
    await page.goto('/t?view=table&per_page=10');
    const table = page.locator('.result-table table');
    await expect(table.locator('tbody tr').first()).toBeVisible();
    const headings = await table.locator('thead th').allTextContents();
    for (const name of ['Addition date', 'Last update']) {
      const index = headings.findIndex(text => text.trim() === name);
      expect(index).toBeGreaterThanOrEqual(0);
      const values = await table.locator(`tbody tr td:nth-child(${index + 1})`).allTextContents();
      for (const value of values) expect(value.trim()).toMatch(/^\d{4}-\d{2}-\d{2}$|^-$/);
    }
    await page.goto('/psiclass');
    await expect(page.getByRole('link', { name: 'Manage record' })).toHaveCount(0);
    await expect(page.getByRole('link', { name: 'Edit record' })).toHaveCount(0);
    await expect(page.locator('.edam-term a[title^="Search bio.tools"]').first()).toBeVisible();
    await expect(page.locator('.edam-term a[title="Open this term in the EDAM ontology"]').first()).toBeVisible();
    const alignment = await page.locator('.function-flow').first().evaluate(flow => {
      const boxes = [...flow.children].map(element => element.getBoundingClientRect());
      return boxes.map(box => box.top + box.height / 2);
    });
    expect(Math.max(...alignment) - Math.min(...alignment)).toBeLessThan(2);
  });
  test('workflow overview shows compact annotations without source links', async ({ page }) => {
    await page.goto('/workflows');
    await expect(page.locator('.workflow-grid .workflow').first()).toBeVisible();
    await expect(page.getByText('Workflow source')).toHaveCount(0);
    const preview = page.locator('.workflow-preview a').first();
    if (await preview.count()) {
      await preview.click();
      await expect(page.locator(':target')).toBeVisible();
      const target = page.locator(':target');
      await expect(target.locator('a').first()).toHaveText(/bio.tools entry|EDAM concept|Open annotation/);
    }
  });
  test('search results show names and selecting an output prepares the next input search', async ({ page }) => {
    await page.setViewportSize({ width: 390, height: 900 });
    const uri = id => `http://edamontology.org/${id}`;
    const data = { uri: uri('data_2044'), term: 'Sequence name' };
    const output = { id: 'out-1', data: { uri: uri('data_0863'), term: 'Sequence' }, formats: [{ uri: uri('format_1929'), term: 'FASTA' }] };
    const input = { id: 'in-1', data, formats: [] };
    const resource = { id: 'demo', name: 'Demo tool', revision: { token: 'revision' } };
    const fn = { id: 'function-1', token: 'function-token', operations: [{ uri: uri('operation_2928'), term: 'Sequence alignment' }], input: [input],
      output: [output, { id: 'out-2', data: { uri: 'invalid-uri', term: 'Unmapped output' }, formats: [] }] };
    const searches = [];
    await page.route('**/_workflow/matches/**', route => {
      searches.push(new URL(route.request().url()).searchParams);
      return route.fulfill({ json: { items: [{ resource, function: fn, io: { ...input, direction: 'input' },
        evidence: { data: { state: 'exact' } }, referenceFingerprint: 'fixture' }], schemaRevision: 'schema', vocabularyRevisions: {},
        source: { note: 'Recorded functions only.' }, pagination: { next: null, note: 'Live results.' } } });
    });
    await page.route('**/_workflow/function/**', route => route.fulfill({ json: { resource, function: fn, schemaRevision: 'schema' } }));
    await page.goto('/workflows/design/');
    await expect(page.getByText('ⓘ').first()).toHaveAttribute('title', /broader and narrower/);
    await expect(page.getByText('ⓘ').last()).toHaveAttribute('title', /missing, obsolete or unrecognized/);
    await page.getByRole('button', { name: 'Choose data type' }).click();
    await page.getByRole('combobox', { name: 'Find data terms' }).fill('data_2044');
    await page.getByRole('dialog').getByRole('option').first().click();
    await page.getByRole('button', { name: 'Apply selection' }).click();
    await page.getByRole('button', { name: 'Search functions' }).click();
    const candidate = page.locator('.candidate-list li').first();
    await expect(candidate).toContainText('Sequence alignment');
    await expect(candidate).not.toContainText('edamontology.org');
    await candidate.getByRole('button', { name: 'Add tool to workflow' }).click();
    await expect(page.locator('.steps-list')).toContainText('Demo tool');
    await page.getByLabel('Output', { exact: true }).selectOption({ index: 1 });
    await expect(page.getByText('Output selected for an input search.', { exact: false })).toBeVisible();
    await page.getByRole('button', { name: 'Search functions' }).click();
    await expect.poll(() => searches.length).toBe(2);
    expect(searches[1].get('direction')).toBe('input');
    expect(searches[1].get('data')).toBe(uri('data_0863'));
    expect(searches[1].get('format')).toBe(uri('format_1929'));
    expect(searches[1].get('operation')).toBe('');
    await page.getByLabel('Output', { exact: true }).selectOption({ index: 2 });
    await expect(page.getByText('This output has no usable EDAM data type or format.', { exact: false })).toBeVisible();
    await expect(page.getByRole('button', { name: 'Search functions' })).toBeDisabled();
    expect(await page.locator('html').evaluate(element => element.scrollWidth <= innerWidth)).toBe(true);
  });
});
