export type EdamScope = 'topic' | 'operation' | 'data' | 'format';
export interface EdamTerm { uri: string; term: string; definition: string; synonyms: string[]; obsolete: boolean }
export interface EdamSelectorProps {
  modelValue: string[];
  scope: EdamScope;
  endpoint: string;
  label: string;
  branch?: string;
  multiple?: boolean;
  maxSelections?: number;
  name?: string;
  initialTerms?: EdamTerm[];
  suggestions?: string[];
  disabled?: boolean;
  readonly?: boolean;
  compact?: boolean;
}

export async function fetchEdam(endpoint: string, params: URLSearchParams, controller: AbortController) {
  const timeout = setTimeout(() => controller.abort(), 10000);
  try {
    const url = new URL(endpoint, location.href);
    url.search = params.toString();
    const response = await fetch(url, { signal: controller.signal, cache: 'no-store', headers: { Accept: 'application/json' } });
    const body = await response.json();
    if (!response.ok) throw new Error(body.error?.message || 'EDAM lookup failed. Please retry.');
    return body as { items: EdamTerm[]; more: boolean; suggestions: EdamTerm[]; vocabulary?: { revision: string } };
  } finally { clearTimeout(timeout); }
}

export function edamFailure(error: unknown) {
  return error instanceof Error && error.name !== 'AbortError' ? error.message : 'EDAM lookup timed out. Please retry.';
}

export function edamPayload(scope: EdamScope, terms: EdamTerm[]) {
  const values = terms.map(({ uri, term }) => ({ uri, term }));
  return scope === 'data' ? { data: values[0] ?? null } : values;
}
