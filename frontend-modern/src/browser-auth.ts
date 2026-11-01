export class BrowserRequestError extends Error {
  constructor(public code: string, public status: number, public loginUrl?: string, public body?: unknown) {
    super(code);
  }
}

function sameOrigin(url: string): URL {
  const target = new URL(url, location.href);
  if (target.origin !== location.origin || !['http:', 'https:'].includes(target.protocol) || target.username || target.password) {
    throw new Error('Browser session requests must use the same origin.');
  }
  return target;
}

function csrfToken(): string {
  const token = document.querySelector<HTMLMetaElement>('meta[name="csrf-token"]')?.content;
  if (!token) throw new Error('Missing CSRF context.');
  return token;
}

function notifyFailure(error: BrowserRequestError): void {
  if (error.code === 'authentication_required' || error.code === 'csrf_failed') {
    document.dispatchEvent(new CustomEvent('biotools:authentication-required', { detail: error }));
  }
}

/** JSON browser endpoints only. Never redirects, retries mutations, or reads API credentials. */
export async function browserRequest(url: string, options: RequestInit = {}): Promise<Response> {
  const target = sameOrigin(url);
  const method = (options.method || 'GET').toUpperCase();
  const headers = new Headers(options.headers);
  headers.set('Accept', 'application/json');
  if (headers.has('Authorization')) throw new Error('Browser requests use session cookies, not API credentials.');
  if (!['GET', 'HEAD', 'OPTIONS'].includes(method)) headers.set('X-CSRFToken', csrfToken());
  const response = await fetch(target.href, { ...options, headers, method, credentials: 'same-origin',
    mode: 'same-origin', redirect: 'error', cache: 'no-store', signal: options.signal ?? AbortSignal.timeout(10000) });
  if (!response.ok) {
    const body = await response.json().catch(() => null);
    const code = response.status === 401 ? 'authentication_required'
      : body?.error?.code === 'csrf_failed' ? 'csrf_failed' : 'request_failed';
    const error = new BrowserRequestError(code, response.status, body?.error?.loginUrl, body);
    notifyFailure(error);
    throw error;
  }
  return response;
}

export async function reconnectSession(): Promise<void> {
  const url = document.querySelector<HTMLMetaElement>('meta[name="session-url"]')?.content;
  if (!url) throw new Error('Missing session endpoint.');
  const data = await (await browserRequest(url)).json();
  const expected = document.querySelector<HTMLMetaElement>('meta[name="session-user"]')?.content;
  if (expected && data.userId !== expected) throw new Error('The account changed. Your page has been kept; reload before continuing.');
  if (typeof data.csrfToken !== 'string' || !/^[a-zA-Z0-9]{64}$/.test(data.csrfToken)) throw new Error('Invalid CSRF response.');
  document.querySelector<HTMLMetaElement>('meta[name="csrf-token"]')!.content = data.csrfToken;
  document.querySelectorAll<HTMLInputElement>('input[name="csrfmiddlewaretoken"]').forEach(input => { input.value = data.csrfToken; });
}

export function handleHtmxAuthError(xhr: XMLHttpRequest): boolean {
  const loginUrl = xhr.getResponseHeader('X-Login-URL');
  const csrfFailed = xhr.getResponseHeader('X-CSRF-Failed') === 'true';
  if ((xhr.status !== 401 || !loginUrl) && !csrfFailed) return false;
  notifyFailure(new BrowserRequestError(csrfFailed ? 'csrf_failed' : 'authentication_required', xhr.status, loginUrl || undefined));
  return true;
}

export function installBrowserAuth(): void {
  document.addEventListener('htmx:configRequest', event => {
    const detail = (event as CustomEvent).detail;
    try {
      sameOrigin(detail.path);
      if (!['get', 'head', 'options'].includes(detail.verb.toLowerCase())) detail.headers['X-CSRFToken'] = csrfToken();
    } catch {
      event.preventDefault();
    }
  });
  document.addEventListener('biotools:authentication-required', event => {
    const error = (event as CustomEvent<BrowserRequestError>).detail;
    const panel = document.getElementById('authentication-error');
    const message = document.getElementById('authentication-message');
    const link = document.getElementById('authentication-login') as HTMLAnchorElement | null;
    if (!panel || !message || !link) return;
    message.textContent = error.code === 'csrf_failed'
      ? 'The security check failed. Reconnect before trying again.'
      : 'Your session has ended. Sign in, then reconnect. Your page has been kept.';
    link.hidden = true;
    if (error.loginUrl) {
      try { link.href = sameOrigin(error.loginUrl).href; link.hidden = false; } catch { /* Never link to an untrusted origin. */ }
    }
    panel.hidden = false;
  });
  document.getElementById('session-reconnect')?.addEventListener('click', async event => {
    const button = event.currentTarget as HTMLButtonElement;
    button.disabled = true;
    try {
      await reconnectSession();
      document.getElementById('authentication-error')!.hidden = true;
    } catch (error) {
      if (!(error instanceof BrowserRequestError)) {
        document.getElementById('authentication-message')!.textContent = error instanceof Error ? error.message : 'Could not reconnect.';
      }
    } finally {
      button.disabled = false;
    }
  });
}
