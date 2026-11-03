<script setup lang="ts">
import { computed, nextTick, onMounted, onUnmounted, ref, watch } from 'vue';
import EdamSelector from './EdamSelector.vue';
import ChoiceSelector from './ChoiceSelector.vue';
import { BrowserRequestError, browserRequest } from './browser-auth';
import { connect, readDraft, type Graph, type Step, type IO } from './workflow-graph';

const graph = ref<Graph>({ version: 1, steps: [], connections: [] });
const data = ref<string[]>([]), format = ref<string[]>([]), operation = ref<string[]>([]);
const direction = ref('input'), related = ref(false), includeUnknown = ref(true);
const results = ref<any[]>([]), next = ref<string | null>(null), error = ref(''), status = ref('');
const loading = ref(false), dirty = ref(false), needsReview = ref<string[]>([]), connecting = ref(false);
const unreviewedEdges = ref<string[]>([]);
const from = ref(''), to = ref(''), reason = ref(''), editing = ref('');
const signedIn = ref(!!document.querySelector<HTMLMetaElement>('meta[name="session-user"]')?.content);
const title = ref('Untitled workflow'), drafts = ref<any[]>([]), draftMore = ref(false), draftId = ref(''), revision = ref('');
const shared = ref(false), sharedLoading = ref(false), shareUrl = ref(''), saving = ref(false);
const redactedDraft = ref(false);
const pendingCreate = ref('');
const serverGraph = ref(''), serverTitle = ref('');
const canShare = computed(() => !!draftId.value && JSON.stringify(graph.value) === serverGraph.value && title.value === serverTitle.value);
let searchSequence = 0;
const request = (url: string) => fetch(url, { cache: 'no-store', signal: AbortSignal.timeout(10000) });
async function reconnect() {
  const sessionUrl = document.querySelector<HTMLMetaElement>('meta[name="session-url"]')?.content;
  if (!sessionUrl) throw new Error('The sign-in check is unavailable.');
  let session;
  try { session = await (await browserRequest(sessionUrl)).json(); }
  catch (cause) {
    if (cause instanceof BrowserRequestError && cause.status === 401) {
      signedIn.value = false;
      throw new Error('Your session ended. Sign in and reconnect; your design is unchanged.');
    }
    throw cause;
  }
  const user = document.querySelector<HTMLMetaElement>('meta[name="session-user"]');
  const csrf = document.querySelector<HTMLMetaElement>('meta[name="csrf-token"]');
  if (!user || !csrf || typeof session.userId !== 'string' || typeof session.csrfToken !== 'string' ||
      !/^[a-zA-Z0-9]{64}$/.test(session.csrfToken)) throw new Error('The sign-in check failed.');
  if (user.content && user.content !== session.userId) throw new Error('The account changed. Download your work before reloading.');
  user.content = session.userId; csrf.content = session.csrfToken; signedIn.value = true;
}
async function reconnectAndList() {
  try { await reconnect(); error.value = ''; await listDrafts(); status.value = 'Signed in. Your current design is unchanged.'; }
  catch (cause) { error.value = cause instanceof Error ? cause.message : 'Could not reconnect. Your current design is unchanged.'; }
}
async function api(url: string, method = 'GET', body?: unknown, expected?: string, anonymous = false) {
  if (!anonymous && method !== 'GET') await reconnect();
  const csrf = document.querySelector<HTMLMetaElement>('meta[name="csrf-token"]')?.content || '';
  const user = document.querySelector<HTMLMetaElement>('meta[name="session-user"]')?.content || '';
  const response = await fetch(url, { method, cache: 'no-store', signal: AbortSignal.timeout(10000),
    headers: { Accept: 'application/json', ...(body !== undefined ? { 'Content-Type': 'application/json' } : {}),
      ...(method !== 'GET' ? { 'X-CSRFToken': csrf } : {}), ...(expected ? { 'If-Match': expected } : {}),
      ...(user && !anonymous ? { 'X-Biotools-User': user } : {}) },
    body: body === undefined ? undefined : JSON.stringify(body) });
  const result = await response.json();
  if (!response.ok) {
    if (response.status === 401) signedIn.value = false;
    const notes = result.notes?.map((item: { note: string }) => item.note).filter(Boolean).join('; ');
    throw new Error((result.error?.message || 'The request failed. Your current draft is unchanged.') + (notes ? ` Saved notes: ${notes}` : ''));
  }
  return result;
}
async function listDrafts(append = false) {
  if (!signedIn.value) return;
  try {
    const body = await api('/_workflow/designs/?' + new URLSearchParams({ offset: String(append ? drafts.value.length : 0) }));
    drafts.value = append ? [...drafts.value, ...body.items] : body.items; draftMore.value = body.more;
  }
  catch (cause) { error.value = cause instanceof Error ? cause.message : 'Could not load drafts.'; }
}
async function save(copy = false) {
  if (saving.value) return;
  if (!copy && redactedDraft.value && !window.confirm('This replaces the saved draft with the visible placeholders and discards its hidden snapshots. Save as a new draft to preserve the original. Continue?')) return;
  saving.value = true; error.value = '';
  const savedGraph = JSON.stringify(graph.value), originalTitle = title.value;
  const savedTitle = copy ? `Copy of ${originalTitle}`.slice(0, 120) : originalTitle;
  try {
    const id = copy ? '' : draftId.value;
    if (!id && !pendingCreate.value) pendingCreate.value = crypto.randomUUID();
    const body = await api(id ? `/_workflow/designs/${id}/` : '/_workflow/designs/', id ? 'PUT' : 'POST',
      { title: savedTitle, graph: JSON.parse(savedGraph), ...(!id ? { id: pendingCreate.value } : {}) }, id ? revision.value : undefined);
    draftId.value = body.id; revision.value = body.revision;
    redactedDraft.value = false;
    pendingCreate.value = '';
    serverGraph.value = savedGraph; serverTitle.value = body.title;
    if (copy || title.value === originalTitle) title.value = body.title;
    if (copy) { shared.value = false; needsReview.value = graph.value.steps.map(step => step.id); history.replaceState(null, '', location.pathname); }
    await nextTick();
    dirty.value = JSON.stringify(graph.value) !== savedGraph || title.value !== body.title;
    status.value = dirty.value ? 'Saved a copy; newer edits are still unsaved.' :
      id ? 'Draft saved privately. Any previous sharing link was revoked.' : 'Draft saved privately.';
    shareUrl.value = ''; await listDrafts();
  } catch (cause) { error.value = cause instanceof Error ? cause.message : 'Save failed. Your current draft is unchanged.'; }
  finally { saving.value = false; }
}
async function openDraft(id: string) {
  if (dirty.value && !window.confirm('Replace the current unsaved design? Download it first if you want to keep it.')) return;
  try {
    const body = await api(`/_workflow/designs/${id}/`);
    const nextGraph = readDraft(JSON.stringify(body.graph));
    graph.value = nextGraph; title.value = body.title; draftId.value = body.id; revision.value = body.revision; pendingCreate.value = '';
    redactedDraft.value = body.unresolved.length > 0;
    unreviewedEdges.value = nextGraph.connections.map(edge => edge.id);
    serverGraph.value = JSON.stringify(nextGraph); serverTitle.value = body.title;
    needsReview.value = nextGraph.steps.map(step => step.id); shareUrl.value = ''; error.value = '';
    await nextTick(); dirty.value = false;
    status.value = redactedDraft.value ? 'Some functions are hidden or unavailable. Their details are withheld; the original draft remains stored.' :
      'Draft opened. Review stored function snapshots before adding connections.';
  } catch (cause) { error.value = cause instanceof Error ? cause.message : 'Could not open draft.'; }
}
async function deleteDraft(id: string, expected: string) {
  if (!window.confirm('Delete this saved draft?')) return;
  try {
    await api(`/_workflow/designs/${id}/`, 'DELETE', undefined, expected);
    if (draftId.value === id) { draftId.value = ''; revision.value = ''; pendingCreate.value = ''; serverGraph.value = ''; serverTitle.value = ''; dirty.value = true; shareUrl.value = ''; }
    status.value = 'Saved draft deleted. The current design remains in the browser.'; await listDrafts();
  } catch (cause) { error.value = cause instanceof Error ? cause.message : 'Could not delete draft.'; }
}
async function shareDraft(action: 'create' | 'revoke') {
  if (!draftId.value || (action === 'create' && !canShare.value)) { error.value = 'Save the current draft before creating a sharing link.'; return; }
  try {
    const body = await api(`/_workflow/designs/${draftId.value}/share/`, 'POST', { action }, revision.value);
    revision.value = body.revision;
    shareUrl.value = body.token ? `${location.origin}/workflows/design/#share=${body.token}` : '';
    status.value = body.token ? 'Sharing enabled. Anyone with this link can view the saved design.' : 'Sharing revoked.';
    await listDrafts();
  } catch (cause) { error.value = cause instanceof Error ? cause.message : 'Could not change sharing.'; }
}
async function openShared(token: string) {
  shared.value = true; sharedLoading.value = true;
  try {
    const body = await api('/_workflow/shared/', 'POST', { token }, undefined, true);
    graph.value = readDraft(JSON.stringify(body.graph)); title.value = body.title;
    unreviewedEdges.value = graph.value.connections.map(edge => edge.id);
    needsReview.value = graph.value.steps.map(step => step.id); shared.value = true;
    await nextTick(); dirty.value = false; error.value = '';
  } catch (cause) { error.value = cause instanceof Error ? cause.message : 'The shared design is unavailable.'; shared.value = true; }
  finally { sharedLoading.value = false; }
}
const endpointKey = (step: string, io: string) => JSON.stringify([step, io]);
const outputs = computed(() => graph.value.steps.flatMap(step => step.function.output.map(io => ({ step, io }))));
const inputs = computed(() => graph.value.steps.flatMap(step => step.function.input.map(io => ({ step, io }))));
const termLabel = (term: { uri: string | null; term: string | null } | null) =>
  term ? term.term || (term.uri ? 'Unlabelled EDAM term' : 'Unknown') : 'Unknown';
const ioLabel = (io: IO) => [termLabel(io.data), io.formats.map(termLabel).join(', ') || 'Unknown format'].join(' / ');
const describeEndpoint = (stepId: string, ioId: string, direction: 'input' | 'output') => {
  const index = graph.value.steps.findIndex(item => item.id === stepId), step = graph.value.steps[index];
  const ioIndex = step?.function[direction].findIndex(item => item.id === ioId) ?? -1;
  const io = step?.function[direction][ioIndex];
  return `${step ? `${index + 1}. ${step.resource.name}` : 'Missing step'}: ${io ? `${direction} ${ioIndex + 1} — ${ioLabel(io)}` : 'Missing annotation'}`;
};
const params = () => ({ direction: direction.value, data: data.value[0] || '', format: format.value[0] || '',
  operation: operation.value[0] || '', mode: related.value ? 'related' : 'exact', include: includeUnknown.value ? 'unknown' : 'matches' });

async function search(cursor?: string) {
  const current = ++searchSequence;
  if (!cursor) { results.value = []; next.value = null; }
  error.value = ''; loading.value = true;
  try {
    const query = new URLSearchParams(params());
    if (cursor) query.set('cursor', cursor);
    const response = await request('/_workflow/matches/?' + query);
    const body = await response.json();
    if (!response.ok) throw new Error(body.error?.message || 'Matching failed. Please retry.');
    if (current !== searchSequence) return;
    results.value.push(...body.items.map((item: any) => ({ ...item, schemaRevision: body.schemaRevision,
      vocabularyRevisions: body.vocabularyRevisions }))); next.value = body.pagination.next;
    status.value = `${results.value.length} candidates found so far. ${body.source.note} ${body.pagination.note}`;
  } catch (cause) { if (current === searchSequence) error.value = cause instanceof Error ? cause.message : 'Matching failed. Please retry.'; }
  finally { if (current === searchSequence) loading.value = false; }
}

async function add(item: any) {
  error.value = '';
  try {
    const query = new URLSearchParams({ ref: item.function.token });
    const response = await request('/_workflow/function/?' + query);
    const body = await response.json();
    if (!response.ok) throw new Error(body.error?.message || 'The function could not be loaded.');
    const selected = body.function[item.io.direction].find((io: IO) => io.id === item.io.id);
    const ioChanged = item.io.id === null ? body.function[item.io.direction].length !== 0 :
      !selected || JSON.stringify(selected.data) !== JSON.stringify(item.io.data) ||
      JSON.stringify(selected.formats) !== JSON.stringify(item.io.formats);
    if (ioChanged || body.schemaRevision !== item.schemaRevision || body.resource.revision.token !== item.resource.revision.token ||
        JSON.stringify(body.function.operations) !== JSON.stringify(item.function.operations)) {
      throw new Error('This function changed since the search. Search again before adding it.');
    }
    graph.value.steps.push({ id: crypto.randomUUID(), resource: body.resource, function: body.function, note: '',
      schemaRevision: item.schemaRevision, vocabularyRevisions: item.vocabularyRevisions,
      selection: { direction: item.io.direction, ioId: item.io.id, fingerprint: item.referenceFingerprint, evidence: item.evidence } });
    status.value = `${body.resource.name} added. Its annotations are a snapshot, not a guarantee of compatibility.`;
  } catch (cause) { error.value = cause instanceof Error ? cause.message : 'The function could not be loaded.'; }
}

async function addConnection() {
  if (connecting.value) return;
  connecting.value = true;
  error.value = '';
  try {
    const [fromStep, fromIo] = JSON.parse(from.value), [toStep, toIo] = JSON.parse(to.value);
    const editId = editing.value, connectionReason = reason.value;
    if (needsReview.value.includes(fromStep) || needsReview.value.includes(toStep)) throw new Error('Review the imported step snapshots first.');
    const source = graph.value.steps.find(step => step.id === fromStep), target = graph.value.steps.find(step => step.id === toStep);
    if (!source || !target) throw new Error('Choose existing steps.');
    try { await Promise.all([validateSnapshot(source), validateSnapshot(target)]); }
    catch (cause) { needsReview.value = [...new Set([...needsReview.value, fromStep, toStep])]; throw cause; }
    const withoutCurrent = { ...graph.value, connections: graph.value.connections.filter(edge => edge.id !== editId) };
    const edge = connect(withoutCurrent, { step: fromStep, io: fromIo }, { step: toStep, io: toIo }, connectionReason, editId || crypto.randomUUID());
    const sourceSnapshot = JSON.stringify(source), targetSnapshot = JSON.stringify(target);
    const output = source.function.output.find(io => io.id === fromIo)!, input = target.function.input.find(io => io.id === toIo)!;
    const comparison = await api('/_workflow/compare/', 'POST', { output: { data: output.data, formats: output.formats },
      input: { data: input.data, formats: input.formats } }, undefined, true);
    for (const step of [source, target]) {
      if (comparison.schemaRevision !== step.schemaRevision || Object.entries(step.vocabularyRevisions).some(([scope, revision]) =>
          comparison.vocabularyRevisions[scope] && comparison.vocabularyRevisions[scope] !== revision)) {
        needsReview.value = [...new Set([...needsReview.value, fromStep, toStep])];
        throw new Error('The schema or EDAM vocabulary changed during the check. Review the steps and try again.');
      }
    }
    if (comparison.state !== 'exact' && !connectionReason.trim()) throw new Error('Explain why you want to connect these annotations.');
    if (JSON.stringify(graph.value.steps.find(step => step.id === fromStep)) !== sourceSnapshot ||
        JSON.stringify(graph.value.steps.find(step => step.id === toStep)) !== targetSnapshot ||
        (editId && !graph.value.connections.some(item => item.id === editId))) throw new Error('The design changed during the check. Try again.');
    connect({ ...graph.value, connections: graph.value.connections.filter(item => item.id !== editId) }, edge.from, edge.to, connectionReason, edge.id);
    edge.evidence = comparison.state; edge.dimensions = comparison.dimensions;
    edge.schemaRevision = comparison.schemaRevision; edge.vocabularyRevisions = comparison.vocabularyRevisions;
    const index = graph.value.connections.findIndex(item => item.id === editId);
    if (index < 0) graph.value.connections.push(edge); else graph.value.connections.splice(index, 1, edge);
    unreviewedEdges.value = unreviewedEdges.value.filter(id => id !== edge.id);
    editing.value = ''; reason.value = ''; status.value = 'Connection saved. Matching annotations do not guarantee execution.';
  } catch (cause) { error.value = cause instanceof Error ? cause.message : 'Choose an output and an input.'; }
  finally { connecting.value = false; }
}

function removeStep(id: string) {
  graph.value.steps = graph.value.steps.filter(step => step.id !== id);
  graph.value.connections = graph.value.connections.filter(edge => edge.from.step !== id && edge.to.step !== id);
  needsReview.value = needsReview.value.filter(item => item !== id);
}
function editConnection(edge: Graph['connections'][number]) {
  from.value = endpointKey(edge.from.step, edge.from.io); to.value = endpointKey(edge.to.step, edge.to.io);
  reason.value = edge.reason; editing.value = edge.id;
  document.getElementById('workflow-from')?.focus();
}
function move(index: number, offset: number) {
  const target = index + offset;
  if (target < 0 || target >= graph.value.steps.length) return;
  [graph.value.steps[index], graph.value.steps[target]] = [graph.value.steps[target], graph.value.steps[index]];
}
function findNext(io: IO, stepId?: string) {
  if (stepId) from.value = endpointKey(stepId, io.id);
  const canonical = (uri: string | null | undefined, scope: 'data' | 'format') =>
    !!uri && new RegExp(`^http://edamontology\\.org/${scope}_[0-9]{4}$`).test(uri);
  const formats = io.formats.filter(item => canonical(item.uri, 'format'));
  const unavailable = (!!io.data && !canonical(io.data.uri, 'data')) || formats.length !== io.formats.length;
  direction.value = 'input'; data.value = canonical(io.data?.uri, 'data') ? [io.data!.uri!] : [];
  format.value = formats[0]?.uri ? [formats[0].uri] : [];
  operation.value = [];
  status.value = !data.value.length && !format.value.length
    ? 'This output has no usable EDAM data type or format. Choose one to search for the next tool.'
    : `Output selected for an input search.${formats.length > 1 ? ' The first output format is selected; you can choose another.' : ''}${unavailable ? ' Some annotations lack usable EDAM identifiers; review the search fields.' : ''} Choose an operation if desired, then search.`;
}
function selectOutput(value: string) {
  if (!value) return;
  try {
    const [stepId, ioId] = JSON.parse(value);
    const io = graph.value.steps.find(step => step.id === stepId)?.function.output.find(item => item.id === ioId);
    if (io) findNext(io);
  } catch { /* An invalid or removed endpoint leaves the search unchanged. */ }
}
function download() {
  const blob = new Blob([JSON.stringify({ ...graph.value, title: title.value }, null, 2)], { type: 'application/json' });
  const url = URL.createObjectURL(blob), link = document.createElement('a');
  link.href = url; link.download = 'biotools-workflow-design.json'; link.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000); dirty.value = false;
}
async function restore(event: Event) {
  const input = event.target as HTMLInputElement, file = input.files?.[0];
  if (!file) return;
  try {
    if (file.size > 1_000_000) throw new Error('The draft is too large.');
    const text = await file.text(), restored = readDraft(text), imported = JSON.parse(text);
    if (imported.title !== undefined && (typeof imported.title !== 'string' || !imported.title.trim() || imported.title.length > 120)) {
      throw new Error('The draft title is invalid.');
    }
    graph.value = restored; needsReview.value = restored.steps.map(step => step.id);
    unreviewedEdges.value = restored.connections.map(edge => edge.id);
    if (imported.title !== undefined) title.value = imported.title;
    draftId.value = ''; revision.value = ''; pendingCreate.value = ''; serverGraph.value = ''; serverTitle.value = ''; shareUrl.value = '';
    redactedDraft.value = false;
    status.value = 'Draft restored. Review each stored function against the current registry before adding connections.';
    error.value = '';
  } catch (cause) { error.value = cause instanceof Error ? cause.message : 'The draft could not be restored.'; }
  input.value = '';
}
async function validateSnapshot(step: Step) {
    const response = await request('/_workflow/function/?' + new URLSearchParams({ ref: step.function.token }));
    const current = await response.json();
    if (!response.ok || current.schemaRevision !== step.schemaRevision || current.resource.revision.token !== step.resource.revision.token ||
        JSON.stringify(current.function) !== JSON.stringify(step.function)) {
      throw new Error('This function changed or is unavailable. Keep this snapshot for reference and add a current function after reviewing it.');
    }
    for (const [scope, revision] of Object.entries(step.vocabularyRevisions)) {
      const vocabulary = await request('/_edam/terms/?' + new URLSearchParams({ scope }));
      const body = await vocabulary.json();
      if (!vocabulary.ok || body.vocabulary?.revision !== revision) throw new Error('The EDAM vocabulary changed or is unavailable. Review the snapshot and search again.');
    }
}
async function review(step: Step) {
  try {
    await validateSnapshot(step);
    needsReview.value = needsReview.value.filter(id => id !== step.id); status.value = `${step.resource.name} matches its stored snapshot.`;
  } catch (cause) { error.value = cause instanceof Error ? cause.message : 'The function could not be reviewed.'; }
}
watch(graph, () => { dirty.value = true; }, { deep: true });
watch(title, () => { dirty.value = true; });
watch([data, format, operation, direction, related, includeUnknown], () => { searchSequence++; loading.value = false; next.value = null; results.value = []; });
function beforeUnload(event: BeforeUnloadEvent) { if (dirty.value) { event.preventDefault(); event.returnValue = ''; } }
onMounted(() => {
  window.addEventListener('beforeunload', beforeUnload);
  const token = new URLSearchParams(location.hash.slice(1)).get('share');
  if (token) openShared(token); else listDrafts();
});
onUnmounted(() => window.removeEventListener('beforeunload', beforeUnload));
</script>

<template>
  <section v-if="shared" aria-labelledby="shared-title">
    <h2 id="shared-title">{{ title }}</h2>
    <p>This shared design is read-only. Its stored annotations may have changed and do not guarantee that tools will run together.</p>
    <p v-if="sharedLoading" role="status">Loading shared design…</p>
    <p v-if="error" role="alert">{{ error }}</p>
    <ol><li v-for="step in graph.steps" :key="step.id">
      <h3>{{ step.resource.name }}</h3><a v-if="step.resource.id" :href="'/' + encodeURIComponent(step.resource.id)">View tool</a>
      <p>Operations: {{ step.function.operations.map(termLabel).join(', ') || 'Unknown' }}</p>
      <p v-for="io in step.function.input" :key="io.id">Input: {{ ioLabel(io) }}</p>
      <p v-for="io in step.function.output" :key="io.id">Output: {{ ioLabel(io) }}</p>
      <p v-if="step.note">{{ step.note }}</p>
    </li></ol>
    <ol aria-label="Shared connections"><li v-for="edge in graph.connections" :key="edge.id">
      {{ describeEndpoint(edge.from.step, edge.from.io, 'output') }} → {{ describeEndpoint(edge.to.step, edge.to.io, 'input') }}: stored {{ edge.evidence }}<template v-if="edge.reason"> — {{ edge.reason }}</template>
    </li></ol>
    <button v-if="signedIn && !error && !sharedLoading" type="button" :disabled="saving" @click="save(true)">Copy to my drafts</button>
    <p v-else-if="!signedIn"><a href="/login" target="_blank" rel="noopener">Sign in</a> to copy this design to your drafts. <button type="button" class="secondary" @click="reconnectAndList">Reconnect</button></p>
    <p><a href="/workflows/design/">Start a new design</a></p>
  </section>
  <template v-else>
  <div class="workflow-workspace">
  <section class="workflow-finder" aria-labelledby="workflow-find"><h2 id="workflow-find">Find a tool function</h2>
    <p>Choose a data type and/or format, and optionally an operation. Matches are suggestions for review, not executable workflows.</p>
    <label for="workflow-direction">Find functions that</label><select id="workflow-direction" v-model="direction"><option value="input">Accept input</option><option value="output">Produce output</option></select>
    <div class="selectors">
      <EdamSelector v-model="data" scope="data" label="Data type" endpoint="/_edam/terms/" :multiple="false" />
      <EdamSelector v-model="format" scope="format" label="Format" endpoint="/_edam/terms/" :multiple="false" />
      <EdamSelector v-model="operation" scope="operation" label="Operation" endpoint="/_edam/terms/" :multiple="false" />
    </div>
    <label title="Also include broader and narrower EDAM terms. Related terms are suggestions and do not guarantee compatibility."><input v-model="related" type="checkbox"> Include related EDAM terms <span tabindex="0" role="img" aria-label="Includes broader and narrower terms; compatibility still needs review." title="Includes broader and narrower EDAM terms; compatibility still needs review.">ⓘ</span></label>
    <label title="Include tools with missing, obsolete or unrecognized annotations, which may not match. Results can take several pages."><input v-model="includeUnknown" type="checkbox"> Include missing or uncertain annotations <span tabindex="0" role="img" aria-label="Includes tools with missing, obsolete or unrecognized annotations; they may not match." title="Includes tools with missing, obsolete or unrecognized annotations; they may not match.">ⓘ</span></label>
    <p><button type="button" :disabled="loading || (!data.length && !format.length)" @click="search()">Search functions</button></p>
    <p role="status">{{ status }}</p><p v-if="error" role="alert">{{ error }}</p>
    <ol class="candidate-list"><li v-for="item in results" :key="item.referenceFingerprint">
      <strong>{{ item.resource.name }}</strong> — {{ ioLabel(item.io) }}
      <span v-for="(evidence, scope) in item.evidence" :key="scope"> · {{ scope }}: {{ evidence.state }}<template v-if="evidence.obsolete"> (obsolete)</template><template v-if="evidence.relation"> ({{ evidence.relation.replaceAll('_', ' ') }})</template><template v-if="evidence.reasons"> ({{ evidence.reasons.join(', ') }})</template></span>
      <p>Operations: {{ item.function.operations.map(termLabel).join(', ') || 'Unknown' }}</p>
      <button type="button" @click="add(item)">Add tool to workflow</button> <a :href="'/' + encodeURIComponent(item.resource.id)">View tool</a>
    </li></ol>
    <button v-if="next" type="button" class="secondary" :disabled="loading" @click="search(next)">More results</button>
  </section>
  <section class="workflow-draft" aria-labelledby="workflow-draft"><h2 id="workflow-draft">Your workflow design</h2>
    <p>This design does not run tools or contain analysis data. Download it or sign in to save it privately.</p>
    <label for="workflow-title">Design title</label><input id="workflow-title" v-model="title" maxlength="120">
    <template v-if="signedIn">
      <button type="button" :disabled="saving" @click="save()">Save private draft</button>
      <button v-if="draftId" type="button" class="secondary" :disabled="saving" @click="save(true)">Save as a new draft</button>
      <button v-if="draftId" type="button" :disabled="saving || !canShare" @click="shareDraft('create')">Create sharing link</button>
      <button v-if="draftId" type="button" class="secondary" :disabled="saving" @click="shareDraft('revoke')">Revoke sharing</button>
      <label v-if="shareUrl" for="workflow-share-url">Read-only sharing link</label><input v-if="shareUrl" id="workflow-share-url" :value="shareUrl" readonly @focus="($event.target as HTMLInputElement).select()">
      <p v-if="shareUrl">Anyone with this link can view the saved design until you revoke or replace the link.</p>
      <details><summary>Saved drafts</summary><button type="button" class="secondary" @click="listDrafts()">Refresh drafts</button>
        <ul><li v-for="draft in drafts" :key="draft.id">{{ draft.title }}<template v-if="draft.shared"> (shared)</template>
          <button type="button" class="secondary" @click="openDraft(draft.id)">Open</button>
          <button type="button" class="secondary" @click="deleteDraft(draft.id, draft.revision)">Delete</button>
        </li></ul><button v-if="draftMore" type="button" class="secondary" @click="listDrafts(true)">More saved drafts</button>
      </details>
    </template>
    <p v-else><a href="/login" target="_blank" rel="noopener">Sign in</a> to save and share drafts. Your current design stays here. <button type="button" class="secondary" @click="reconnectAndList">Reconnect</button></p>
    <p v-if="needsReview.length" role="status">Some stored function snapshots need review. Their displayed connection evidence may be out of date.</p>
    <p v-if="redactedDraft" role="status">Hidden or unavailable functions are shown as placeholders. Save as a new draft to preserve the original stored snapshots.</p>
    <button type="button" @click="download">Download draft</button>
    <label>Restore draft <input type="file" accept="application/json,.json" @change="restore"></label>
    <p v-if="!graph.steps.length" class="workflow-empty">Your design is empty. Search for a tool function and add it to begin.</p>
    <p v-if="graph.steps.length" class="diagram-hint">Scroll the diagram horizontally to see the connections.</p>
    <div v-if="graph.steps.length" class="diagram" role="region" tabindex="0" aria-label="Workflow diagram, scroll horizontally to see connections">
      <svg :viewBox="`0 0 800 ${graph.steps.length * 90}`" role="img" aria-label="Connections between workflow steps; details and controls follow">
        <defs><marker id="workflow-arrow" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0 0 L8 4 L0 8 Z" /></marker></defs>
        <path v-for="(edge, index) in graph.connections" :key="edge.id" :d="`M 300 ${graph.steps.findIndex(s => s.id === edge.from.step) * 90 + 40} C ${Math.min(760, 420 + index * 28)} ${graph.steps.findIndex(s => s.id === edge.from.step) * 90 + 40}, ${Math.min(760, 420 + index * 28)} ${graph.steps.findIndex(s => s.id === edge.to.step) * 90 + 40}, 300 ${graph.steps.findIndex(s => s.id === edge.to.step) * 90 + 40}`" fill="none" stroke="#276390" stroke-width="3" marker-end="url(#workflow-arrow)" />
        <g v-for="(step, index) in graph.steps" :key="step.id"><rect x="5" :y="index * 90 + 10" width="290" height="60" rx="6" fill="#e8f2f8" stroke="#276390"/><text x="18" :y="index * 90 + 45">{{ index + 1 }}. {{ step.resource.name.slice(0, 35) }}</text></g>
      </svg>
    </div>
    <ol class="steps-list"><li v-for="(step, index) in graph.steps" :key="step.id">
      <h3>{{ step.resource.name }}</h3><a v-if="step.resource.id" :href="'/' + encodeURIComponent(step.resource.id)">View tool</a>
      <p v-if="needsReview.includes(step.id)" role="status">Stored snapshot needs review. <button type="button" @click="review(step)">Review current function</button></p>
      <p class="workflow-operation">Operations: {{ step.function.operations.map(termLabel).join(', ') || 'Unknown' }}</p>
      <p>Selected {{ step.selection.direction }} evidence:
        <span v-for="(evidence, scope) in step.selection.evidence" :key="scope"> {{ scope }}: {{ evidence.state }}<template v-if="evidence.obsolete"> (obsolete)</template><template v-if="evidence.relation"> ({{ evidence.relation.replaceAll('_', ' ') }})</template><template v-if="evidence.reasons"> ({{ evidence.reasons.join(', ') }})</template>;</span>
      </p>
      <p v-if="!step.function.input.length">No input annotation recorded.</p>
      <p v-for="io in step.function.input" :key="io.id" class="workflow-io">Input: {{ ioLabel(io) }}</p>
      <p v-if="!step.function.output.length">No output annotation recorded.</p>
      <p v-for="io in step.function.output" :key="io.id" class="workflow-io">Output: {{ ioLabel(io) }} <button type="button" class="secondary" @click="findNext(io, step.id)">Find next tool</button></p>
      <label :for="'note-' + step.id">Notes for step {{ index + 1 }}</label><textarea :id="'note-' + step.id" v-model="step.note" maxlength="1000" />
      <button type="button" class="secondary" :aria-label="`Move step ${index + 1} up`" :disabled="index === 0" @click="move(index, -1)">Move up</button>
      <button type="button" class="secondary" :aria-label="`Move step ${index + 1} down`" :disabled="index === graph.steps.length - 1" @click="move(index, 1)">Move down</button>
      <button type="button" class="secondary" :aria-label="`Remove step ${index + 1}`" @click="removeStep(step.id)">Remove step</button>
    </li></ol>
    <fieldset :disabled="connecting"><legend>Connect steps</legend>
      <label for="workflow-from">Output</label><ChoiceSelector v-if="outputs.length > 20" id="workflow-from" v-model="from" label="Output" :choices="outputs.map(entry => ({ value: endpointKey(entry.step.id, entry.io.id), label: describeEndpoint(entry.step.id, entry.io.id, 'output') }))" @update:model-value="selectOutput" />
      <select v-else id="workflow-from" v-model="from" @change="selectOutput(($event.target as HTMLSelectElement).value)"><option value="">Choose output</option><option v-for="entry in outputs" :key="endpointKey(entry.step.id, entry.io.id)" :value="endpointKey(entry.step.id, entry.io.id)">{{ describeEndpoint(entry.step.id, entry.io.id, 'output') }}</option></select>
      <label for="workflow-to">Input</label><ChoiceSelector v-if="inputs.length > 20" id="workflow-to" v-model="to" label="Input" :choices="inputs.map(entry => ({ value: endpointKey(entry.step.id, entry.io.id), label: describeEndpoint(entry.step.id, entry.io.id, 'input') }))" />
      <select v-else id="workflow-to" v-model="to"><option value="">Choose input</option><option v-for="entry in inputs" :key="endpointKey(entry.step.id, entry.io.id)" :value="endpointKey(entry.step.id, entry.io.id)">{{ describeEndpoint(entry.step.id, entry.io.id, 'input') }}</option></select>
      <label for="workflow-reason">Reason for an uncertain connection</label><input id="workflow-reason" v-model="reason" maxlength="1000">
      <button type="button" @click="addConnection">{{ editing ? 'Update connection' : 'Connect' }}</button>
      <button v-if="editing" type="button" class="secondary" @click="editing = ''; reason = ''">Cancel edit</button>
    </fieldset>
    <p v-if="graph.connections.length">For related terms, “requested” refers to the output and “annotated” to the input. The evidence does not guarantee that tools work together.</p>
    <ol aria-label="Connections"><li v-for="(edge, index) in graph.connections" :key="edge.id">
      {{ describeEndpoint(edge.from.step, edge.from.io, 'output') }} → {{ describeEndpoint(edge.to.step, edge.to.io, 'input') }}: <template v-if="unreviewedEdges.includes(edge.id) || needsReview.includes(edge.from.step) || needsReview.includes(edge.to.step)">unreviewed snapshot, stored evidence </template>{{ edge.evidence }}<template v-if="edge.reason"> — {{ edge.reason }}</template>
      <span v-for="(detail, scope) in edge.dimensions" :key="scope"> · {{ scope }}: {{ detail.state }}<template v-if="detail.relation"> ({{ detail.relation.replaceAll('_', ' ') }})</template><template v-if="detail.reasons"> ({{ detail.reasons.join(', ') }})</template></span>
      <button type="button" class="secondary" :aria-label="`Edit connection ${index + 1}`" @click="editConnection(edge)">Edit connection</button>
      <button type="button" class="secondary" :aria-label="`Remove connection ${index + 1}`" @click="graph.connections = graph.connections.filter(item => item.id !== edge.id)">Remove connection</button>
    </li></ol>
  </section>
  </div>
  </template>
</template>

<style scoped>
.workflow-workspace { display: grid; grid-template-columns: minmax(280px, 0.8fr) minmax(0, 1.2fr); gap: 24px; align-items: start; }
.workflow-finder, .workflow-draft { min-width: 0; margin: 0; padding: 24px; border: 1px solid #d6e5eb; border-radius: 10px; background: #fff; }
.workflow-finder { background: #f4f9fb; }
.workflow-finder > h2, .workflow-draft > h2 { color: #173e4b; }
.workflow-empty { padding: 20px; background: #f4f9fb; border: 1px dashed #a9cbd7; border-radius: 8px; color: #425f6b; }
.workflow-operation, .workflow-io { padding: 8px 10px; border-left: 3px solid #88b3c3; background: #f5fafb; }
.workflow-operation { border-color: #005472; background: #e5f2f7; }
.workflow-draft input[type="file"] { display: block; max-width: 100%; }
.selectors { display: flex; flex-wrap: wrap; gap: 1rem; margin: 1rem 0; }
.diagram { overflow-x: auto; max-width: 100%; }
.diagram svg { display: block; width: 800px; max-width: none; }
.diagram-hint { display: none; }
@media (max-width: 840px) { .diagram-hint { display: block; } }
@media (max-width: 850px) { .workflow-workspace { grid-template-columns: minmax(0, 1fr); } }
section { margin-block: 2rem; }
.candidate-list > li, .steps-list > li { background: #f5f9fc; border: 1px solid #c9dce9; border-radius: 6px; padding: 1rem; overflow-wrap: anywhere; }
.steps-list h3 { margin-top: 0; }
.steps-list button, .candidate-list button { margin: .2rem; }
fieldset select { max-width: 100%; }
li { margin-block: 1rem; }
fieldset { margin-block: 1.5rem; }
</style>
