import { afterEach, beforeAll, beforeEach, describe, expect, it, vi } from 'vitest';
import { flushPromises, mount } from '@vue/test-utils';
import { browserRequest, handleHtmxAuthError, installBrowserAuth, reconnectSession } from './browser-auth';
import SessionCheck from './SessionCheck.vue';

const token = 'a'.repeat(64);
const fresh = 'b'.repeat(64);
const mockFetch = vi.fn();
const failure = (status = 401) => new Response(JSON.stringify({ error: {
  code: status === 401 ? 'authentication_required' : 'csrf_failed', loginUrl: '/auth/login/?next=/account/',
} }), { status });

beforeAll(() => installBrowserAuth());
beforeEach(() => {
  vi.stubGlobal('fetch', mockFetch);
  document.head.innerHTML = `<meta name="csrf-token" content="${token}"><meta name="session-url" content="/auth/session/"><meta name="session-user" content="1">`;
  document.body.innerHTML = '<input name="csrfmiddlewaretoken"><input id="draft" value="Unsaved work">'
    + '<div id="authentication-error" hidden><p id="authentication-message"></p><a id="authentication-login" hidden></a></div>';
});
afterEach(() => { mockFetch.mockReset(); vi.unstubAllGlobals(); });

describe('browser session requests', () => {
  it('uses masked CSRF with same-origin cookies and never redirects JSON requests', async () => {
    mockFetch.mockResolvedValue(new Response('{}'));
    await browserRequest('/auth/check/', { method: 'POST' });
    const [url, options] = mockFetch.mock.calls[0];
    expect(url).toBe(location.origin + '/auth/check/');
    expect(options).toMatchObject({ method: 'POST', credentials: 'same-origin', mode: 'same-origin', redirect: 'error', cache: 'no-store' });
    expect(options.headers.get('X-CSRFToken')).toBe(token);
    expect(options.headers.get('Authorization')).toBeNull();
    await browserRequest('/auth/session/');
    expect(mockFetch.mock.calls[1][1].headers.has('X-CSRFToken')).toBe(false);
  });

  it('refuses cross-origin, credential-bearing, non-HTTP and API-token requests before transport', async () => {
    for (const url of ['https://evil.invalid/post', '//evil.invalid/post', 'javascript:alert(1)', 'http://user:secret@localhost/post']) {
      await expect(browserRequest(url, { method: 'POST' })).rejects.toThrow();
    }
    await expect(browserRequest('/post', { headers: { Authorization: 'Token secret' } })).rejects.toThrow('session cookies');
    document.querySelector('meta[name="csrf-token"]')!.remove();
    await expect(browserRequest('/post', { method: 'POST' })).rejects.toThrow('CSRF');
    expect(mockFetch).not.toHaveBeenCalled();
  });

  it('reports expiry and CSRF errors without changing the draft or retrying mutations', async () => {
    for (const status of [401, 403]) {
      mockFetch.mockResolvedValueOnce(failure(status));
      await expect(browserRequest('/post', { method: 'POST' })).rejects.toMatchObject({ status });
      expect(document.getElementById('authentication-error')!.hidden).toBe(false);
      expect((document.getElementById('draft') as HTMLInputElement).value).toBe('Unsaved work');
    }
    expect(mockFetch).toHaveBeenCalledTimes(2);
    mockFetch.mockResolvedValueOnce(new Response('{}', { status: 403 }));
    await expect(browserRequest('/post', { method: 'POST' })).rejects.toMatchObject({ code: 'request_failed' });
  });

  it('refreshes CSRF explicitly after reauthentication, refusing an account switch', async () => {
    mockFetch.mockResolvedValueOnce(new Response(JSON.stringify({ csrfToken: fresh, userId: '1' })));
    await reconnectSession();
    expect(document.querySelector<HTMLMetaElement>('meta[name="csrf-token"]')!.content).toBe(fresh);
    expect(document.querySelector<HTMLInputElement>('input[name="csrfmiddlewaretoken"]')!.value).toBe(fresh);
    mockFetch.mockResolvedValueOnce(new Response(JSON.stringify({ csrfToken: token, userId: '2' })));
    await expect(reconnectSession()).rejects.toThrow('account changed');
    expect(document.querySelector<HTMLMetaElement>('meta[name="csrf-token"]')!.content).toBe(fresh);
    expect((document.getElementById('draft') as HTMLInputElement).value).toBe('Unsaved work');
  });

  it('applies the same CSRF rule to htmx and preserves targets on expiry', () => {
    const detail = { path: '/auth/logout/', verb: 'post', headers: {} as Record<string, string> };
    document.dispatchEvent(new CustomEvent('htmx:configRequest', { detail, cancelable: true }));
    expect(detail.headers['X-CSRFToken']).toBe(token);
    const outbound = new CustomEvent('htmx:configRequest', { detail: { ...detail, path: 'https://evil.invalid/' }, cancelable: true });
    document.dispatchEvent(outbound);
    expect(outbound.defaultPrevented).toBe(true);
    const xhr = { status: 401, getResponseHeader: (header: string) => header === 'X-Login-URL' ? '/auth/login/' : null } as XMLHttpRequest;
    expect(handleHtmxAuthError(xhr)).toBe(true);
    expect(document.getElementById('authentication-error')!.hidden).toBe(false);
    expect((document.getElementById('draft') as HTMLInputElement).value).toBe('Unsaved work');
    expect(handleHtmxAuthError({ status: 500, getResponseHeader: () => null } as unknown as XMLHttpRequest)).toBe(false);
  });

  it('keeps unsafe sign-in links out of the recovery message', async () => {
    mockFetch.mockResolvedValueOnce(new Response(JSON.stringify({ error: { loginUrl: 'https://evil.invalid/' } }), { status: 401 }));
    await expect(browserRequest('/post', { method: 'POST' })).rejects.toThrow();
    expect(document.getElementById('authentication-login')!.hidden).toBe(true);
  });

  it('the Vue island recovers from rejected requests and aborts on teardown', async () => {
    const wrapper = mount(SessionCheck, { props: { endpoint: '/auth/check/' } });
    mockFetch.mockResolvedValueOnce(failure());
    await wrapper.get('button').trigger('click');
    await flushPromises();
    expect(wrapper.get('[role="status"]').text()).toContain('reconnection');
    mockFetch.mockResolvedValueOnce(new Response('{}'));
    await wrapper.get('button').trigger('click');
    await flushPromises();
    expect(wrapper.get('[role="status"]').text()).toBe('Session verified.');
    const signal = mockFetch.mock.calls[1][1].signal;
    wrapper.unmount();
    expect(signal.aborted).toBe(true);
  });
});
