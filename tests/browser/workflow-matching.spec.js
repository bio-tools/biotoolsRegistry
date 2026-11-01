const { test, expect } = require('./fixtures');

test.describe('workflow matching', () => {
  test.skip(process.env.BIOTOOLS_TEST_WORKFLOW_MATCHING !== '1', 'Requires the local detail-demo fixture and EDAM data.');

  for (const agent of ['Mozilla/5.0', 'Googlebot']) {
    test(`matches public function records for ${agent}`, async ({ request }) => {
      const params = { direction: 'input', data: 'http://edamontology.org/data_2044',
        format: 'http://edamontology.org/format_1929', operation: 'http://edamontology.org/operation_2928', limit: '50' };
      const items = [];
      let cursor;
      for (let page = 0; page < 20; page++) {
        const response = await request.get('/_workflow/matches/', { params: { ...params, ...(cursor ? { cursor } : {}) },
          headers: { 'User-Agent': agent } });
        expect(response.status()).toBe(200);
        expect(response.headers()['x-biotools-route']).toBe('django-workflow-matches');
        const body = await response.json();
        expect(body.source.consistency).toBe('live');
        expect(body.pagination.scanned).toBeLessThanOrEqual(100);
        items.push(...body.items);
        cursor = body.pagination.next;
        if (!cursor) break;
      }
      expect(cursor).toBeFalsy();
      const fixture = items.find(item => item.resource.id === 'detail-demo');
      expect(fixture.io.data.uri).toBe(params.data);
      expect(fixture.io.formats.some(format => format.uri === params.format)).toBe(true);
      expect(fixture.function.operations.some(operation => operation.uri === params.operation)).toBe(true);
      expect(fixture.evidence.operation.state).toBe('exact');
      expect(JSON.stringify(items)).not.toContain('editPermission');
      expect((await request.get('/_workflow/matches/', { params: { direction: 'input' } })).status()).toBe(400);
    });
  }
});
