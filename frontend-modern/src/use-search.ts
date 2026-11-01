import { computed, onMounted, onUnmounted, ref } from 'vue';
import { defaultState, parseSearch, serializeSearch, type SearchConfig, type SearchResponse, type SearchState } from './search-state';
import { matchesFilters, parseAdvanced, type AdvancedFilter } from './advanced-filters';

export function useSearch(config: SearchConfig) {
  const state = ref(defaultState());
  const result = ref<SearchResponse | null>(null);
  const loading = ref(false);
  const error = ref('');
  const localFilters = ref<AdvancedFilter[]>([]);
  const localError = ref('');
  const candidates = computed(() => result.value?.items ?? []);
  const visibleItems = computed(() => candidates.value.filter(item => matchesFilters(item.filterValues, localFilters.value)));
  let sequence = 0;
  let controller: AbortController | undefined;
  let timer: ReturnType<typeof setTimeout> | undefined;
  let typing = false;

  function cancel() {
    sequence++;
    controller?.abort();
    clearTimeout(timer);
  }

  async function fetchResults() {
    typing = false;
    const current = sequence;
    const active = new AbortController();
    controller = active;
    const timeout = setTimeout(() => active.abort(), 12000);
    try {
      const query = serializeSearch(state.value);
      const response = await fetch(`${config.endpoint}?${query}`, {
        signal: active.signal, headers: { Accept: 'application/json' },
      });
      const body = await response.json();
      if (!response.ok) throw new Error(body.error?.message || 'Search is unavailable. Please retry.');
      if (current === sequence) result.value = body;
    } catch (failure) {
      if (current === sequence) error.value = failure instanceof Error && failure.name !== 'AbortError'
        ? failure.message : 'Search timed out. Please retry.';
    } finally {
      clearTimeout(timeout);
      if (current === sequence) loading.value = false;
    }
  }

  function load(mode: 'push' | 'replace' | 'none', delay = 0, preserveLocal = false) {
    if (!preserveLocal) {
      localFilters.value = [];
      localError.value = '';
    }
    if (delay && typing && mode === 'push') mode = 'replace';
    typing = delay > 0;
    cancel();
    result.value = null;
    error.value = '';
    try {
      const normalized = parseSearch(serializeSearch(state.value), config);
      state.value.advanced = normalized.advanced;
      const query = serializeSearch(state.value);
      const url = location.pathname + (query ? `?${query}` : '');
      if (mode !== 'none' && url !== location.pathname + location.search) {
        history[mode === 'push' ? 'pushState' : 'replaceState'](null, '', url);
      }
      loading.value = true;
      timer = setTimeout(fetchResults, delay);
    } catch (failure) {
      error.value = (failure as Error).message;
      loading.value = false;
    }
  }

  function restore() {
    localFilters.value = [];
    localError.value = '';
    typing = false;
    cancel();
    result.value = null;
    loading.value = false;
    try {
      state.value = parseSearch(location.search, config);
      load('replace');
    } catch (failure) { error.value = (failure as Error).message; }
  }

  function update(patch: Partial<SearchState>, delay = 0) {
    const viewOnly = Object.hasOwn(patch, 'view') && Object.keys(patch).every(key => ['view', 'page'].includes(key))
      && (patch.page === undefined || patch.page === state.value.page);
    state.value = { ...state.value, page: viewOnly ? state.value.page : 1, ...patch };
    load('push', delay, viewOnly);
  }

  function reset() { state.value = defaultState(); load('push'); }

  function setLocalFilters(filters: AdvancedFilter[]) {
    try {
      localFilters.value = parseAdvanced(JSON.stringify(filters), config.scores, 'candidate');
      localError.value = '';
    } catch (failure) { localError.value = (failure as Error).message; }
  }

  function promote() {
    if (localError.value || !localFilters.value.length || loading.value) return;
    const advanced = [...state.value.advanced, ...localFilters.value.map(filter => ({ ...filter, scope: 'server' as const }))];
    try {
      parseAdvanced(JSON.stringify(advanced), config.scores);
      update({ advanced });
    } catch (failure) { localError.value = (failure as Error).message; }
  }

  onMounted(() => { restore(); window.addEventListener('popstate', restore); });
  onUnmounted(() => { cancel(); window.removeEventListener('popstate', restore); });
  return { state, result, loading, error, update, reset, retry: restore,
    candidates, visibleItems, localFilters, localError, setLocalFilters, promote };
}
