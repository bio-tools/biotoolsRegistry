<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue';
import { browserRequest, BrowserRequestError } from './browser-auth';
import FunctionEditor from './FunctionEditor.vue';
import UiIcon from './UiIcon.vue';
import { sectionIcon } from './ui-icons';
import MetadataEditor from './MetadataEditor.vue';
import PermissionEditor from './PermissionEditor.vue';
import GithubImport from './GithubImport.vue';
import { applySuggestions } from './github-import';
import { errorLocation, nestedTarget } from './nested-editor';
import { backendErrorsToEditor, editorShapeError, editorToResource, editorToSubmission, newEditorItem,
  resourceToEditor, supportedSchema, type EditorError, type Json, type Resource, type ResourceSchema } from './resource-editor';

type Config = { resource: Resource; revision: string | null; endpoint: string; validateEndpoint?: string; previewEndpoint?: string;
  schema?: ResourceSchema | null; schemaRevision?: string | null; bridgeEndpoint?: string | null;
  editUrl: string | null; detailUrl: string | null; toolTypes: string[]; edamEndpoint: string; draftsEndpoint?: string; metadataOptions?: Record<string, string[]>; canManagePermissions?: boolean; no_changes?: boolean };
const props = defineProps<Config>();
const config = ref<Config>({ ...props });
const draft = ref(resourceToEditor(props.resource));
const baseline = ref(JSON.stringify(props.resource));
const raw = ref(JSON.stringify(editorToResource(draft.value), null, 2));
const rawError = ref('');
const dirty = computed(() => !!rawError.value || JSON.stringify(editorToResource(draft.value)) !== baseline.value);
const savedDraftSnapshot = ref('');
const unstoredChanges = computed(() => dirty.value && (!!rawError.value || JSON.stringify(editorToResource(draft.value)) !== savedDraftSnapshot.value));
type PrivateDraft = { id: string; name: string; target: string; revision: string; recordRevision: string; updated: string };
const privateDrafts = ref<PrivateDraft[]>([]), privateDraft = ref<PrivateDraft | null>(null);
const privateDraftError = ref(''), privateDraftStatus = ref(''), privateDraftPending = ref(false), moreDrafts = ref(false);
let pendingDraftId = '';
const validationMessage = ref('');
const pending = ref(false);
const saved = ref(false);
const errors = ref<EditorError[]>([]);
const errorSummary = ref<HTMLElement>();
const root = ref<HTMLElement>();
const previewHtml = ref('');
const previewSnapshot = ref('');
const previewPending = ref(false);
const previewError = ref('');
const controller = new AbortController();
const schemaReady = computed(() => supportedSchema(config.value.schema, config.value.schemaRevision));
const unavailable = computed(() => pending.value || !schemaReady.value || !!rawError.value);
const snapshot = computed(() => editorToSubmission(draft.value, config.value.schema?.contract));
const fields = computed(() => config.value.schema?.contract.fields || {});
const sections = computed(() => Object.entries(fields.value).filter(([, field]) => field.writable &&
  (field.kind === 'object' || field.item?.kind === 'object')));
const selectedTypes = computed(() => (draft.value.toolType || []).map(item => item.value));
const types = computed(() => {
  const choices = fields.value.toolType?.choices || [];
  return [...choices, ...selectedTypes.value.filter((value): value is string => typeof value === 'string' &&
    !choices.some(item => item.value === value)).map(value => ({ value, label: value + ' (no longer allowed)', help: '' }))];
});
let applyingJSON = false;
let jsonSequence = 0;
let suggestedId = '';
let idEdited = !!props.resource.biotoolsID;
watch(() => draft.value.name, name => {
  if (config.value.revision || applyingJSON || idEdited || (draft.value.biotoolsID && draft.value.biotoolsID !== suggestedId)) return;
  suggestedId = String(name || '').trim().replace(/[^a-zA-Z0-9_. -]/g, '').replace(/ +/g, '_')
    .slice(0, fields.value.biotoolsID?.maxLength || 100);
  draft.value.biotoolsID = suggestedId;
}, { flush: 'sync' });
watch(draft, () => {
  if (!applyingJSON && !rawError.value) raw.value = JSON.stringify(editorToResource(draft.value), null, 2);
}, { deep: true, flush: 'post' });

function updateJSON(event: Event) {
  raw.value = (event.target as HTMLTextAreaElement).value;
  validationMessage.value = '';
  try {
    const value: unknown = JSON.parse(raw.value);
    const shapeError = editorShapeError(value, config.value.schema?.contract);
    if (shapeError) throw new Error(shapeError);
    const record = value as Record<string, Json>;
    if (Object.hasOwn(record, 'biotoolsID')) idEdited = true;
    applyingJSON = true;
    const current = ++jsonSequence;
    applySuggestions(draft.value, record);
    for (const key of Object.keys(draft.value)) if (!Object.hasOwn(record, key)) Reflect.deleteProperty(draft.value, key);
    rawError.value = '';
    errors.value = [];
    saved.value = false;
    validationMessage.value = '';
    nextTick(() => { if (current === jsonSequence) applyingJSON = false; });
  } catch (error) {
    ++jsonSequence; applyingJSON = false;
    rawError.value = error instanceof SyntaxError ? 'The JSON is incomplete or invalid.'
      : error instanceof Error ? error.message : 'The JSON record could not be read.';
  }
}
function restoreJSON() {
  ++jsonSequence; applyingJSON = false; rawError.value = '';
  raw.value = JSON.stringify(editorToResource(draft.value), null, 2);
}

function changeType(type: string, checked: boolean) {
  const values = draft.value.toolType || [];
  draft.value.toolType = checked ? [...values, newEditorItem(type)] : values.filter(item => item.value !== type);
}

function fieldErrors(field: string) { return errors.value.filter(error => error.wirePath[0] === field).map(error => error.message); }
function errorTarget(error: EditorError) {
  const field = error.wirePath[0];
  return typeof field === 'string' && ['name', 'description', 'homepage', 'biotoolsID', 'toolType'].includes(field)
    ? `editor-${field}` : error.path?.length ? nestedTarget(draft.value, error) : null;
}

function confirmLeave() { return (!unstoredChanges.value && !pending.value && !privateDraftPending.value) || window.confirm('Discard unsaved changes and leave this page?'); }
function beforeUnload(event: BeforeUnloadEvent) {
  if (unstoredChanges.value || pending.value || privateDraftPending.value) { event.preventDefault(); event.returnValue = ''; }
}
function beforeNavigation(event: Event) {
  if (!(event.target instanceof Element)) return;
  if (event.type === 'click') {
    const link = event.target.closest<HTMLAnchorElement>('a[href]');
    if (!link || link.target === '_blank' || link.hasAttribute('download')) return;
    const destination = new URL(link.href, location.href);
    if (destination.pathname === location.pathname && destination.search === location.search && destination.hash) return;
    const mouse = event as MouseEvent;
    if (mouse.button !== 0 || mouse.ctrlKey || mouse.metaKey || mouse.shiftKey || mouse.altKey) return;
  } else if (root.value?.contains(event.target)) return;
  if (!confirmLeave()) { event.preventDefault(); event.stopImmediatePropagation(); }
}
onMounted(() => {
  window.addEventListener('beforeunload', beforeUnload);
  document.addEventListener('click', beforeNavigation, true);
  document.addEventListener('submit', beforeNavigation, true);
  if (config.value.draftsEndpoint) listPrivateDrafts();
});
onBeforeUnmount(() => {
  controller.abort();
  window.removeEventListener('beforeunload', beforeUnload);
  document.removeEventListener('click', beforeNavigation, true);
  document.removeEventListener('submit', beforeNavigation, true);
});

function discard() {
  if (!window.confirm('Discard your unsaved changes?')) return;
  draft.value = resourceToEditor(JSON.parse(baseline.value));
  suggestedId = '';
  idEdited = !!config.value.revision || !!draft.value.biotoolsID;
  errors.value = [];
  saved.value = false;
  restoreJSON();
  validationMessage.value = '';
}
function exportDraft() {
  const url = URL.createObjectURL(new Blob([rawError.value ? raw.value : JSON.stringify(editorToResource(draft.value), null, 2)], { type: 'application/json' }));
  const link = document.createElement('a');
  link.href = url;
  link.download = `${draft.value.biotoolsID || 'resource'}-draft.json`;
  link.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}

function privateHeaders(extra: Record<string, string> = {}) {
  return { 'X-Biotools-User': document.querySelector<HTMLMetaElement>('meta[name="session-user"]')?.content || '', ...extra };
}
async function listPrivateDrafts(append = false) {
  if (!config.value.draftsEndpoint) return;
  try {
    const query = new URLSearchParams({ target: config.value.revision ? String(config.value.resource.biotoolsID || '') : '', offset: String(append ? privateDrafts.value.length : 0) });
    const response = await browserRequest(`${config.value.draftsEndpoint}?${query}`, { headers: privateHeaders() });
    const body = await response.json(); privateDrafts.value = append ? [...privateDrafts.value, ...body.items] : body.items; moreDrafts.value = body.more;
  } catch { privateDraftError.value = 'Private drafts could not be loaded.'; }
}
async function savePrivateDraft() {
  if (!config.value.draftsEndpoint || privateDraftPending.value || rawError.value) return;
  privateDraftPending.value = true; privateDraftError.value = ''; privateDraftStatus.value = '';
  const resource = editorToResource(draft.value), snapshot = JSON.stringify(resource);
  const target = config.value.revision ? String(config.value.resource.biotoolsID || '') : '';
  try {
    if (!privateDraft.value && !pendingDraftId) pendingDraftId = crypto.randomUUID();
    const current = privateDraft.value;
    const response = await browserRequest(current ? `${config.value.draftsEndpoint}${current.id}/` : config.value.draftsEndpoint, {
      method: current ? 'PUT' : 'POST', headers: privateHeaders({ 'Content-Type': 'application/json', ...(current ? { 'If-Match': current.revision } : {}) }),
      body: JSON.stringify({ ...(!current ? { id: pendingDraftId } : {}), target, recordRevision: current?.recordRevision || config.value.revision || '', resource }),
    });
    privateDraft.value = await response.json(); pendingDraftId = ''; savedDraftSnapshot.value = snapshot;
    privateDraftStatus.value = JSON.stringify(editorToResource(draft.value)) === snapshot ? 'Private draft saved.' : 'Draft saved; newer changes are not saved.';
    await listPrivateDrafts();
  } catch (error) {
    privateDraftError.value = error instanceof BrowserRequestError && error.body && typeof error.body === 'object' && 'detail' in error.body
      ? String(error.body.detail) : 'Private draft could not be saved. Your work is unchanged.';
  } finally { privateDraftPending.value = false; }
}
async function openPrivateDraft(item: PrivateDraft) {
  if (!config.value.draftsEndpoint || privateDraftPending.value || !confirmLeave()) return;
  privateDraftPending.value = true; privateDraftError.value = '';
  try {
    const response = await browserRequest(`${config.value.draftsEndpoint}${item.id}/`, { headers: privateHeaders() });
    const body = await response.json();
    draft.value = resourceToEditor(body.resource); rawError.value = ''; raw.value = JSON.stringify(body.resource, null, 2);
    if (body.target) config.value.revision = body.recordRevision;
    privateDraft.value = body; pendingDraftId = ''; savedDraftSnapshot.value = JSON.stringify(editorToResource(draft.value));
    idEdited = !!body.resource.biotoolsID; errors.value = []; previewHtml.value = ''; privateDraftStatus.value = 'Private draft opened.';
  } catch { privateDraftError.value = 'Private draft could not be opened. Your current work is unchanged.'; }
  finally { privateDraftPending.value = false; }
}
async function deletePrivateDraft(item: PrivateDraft) {
  if (!config.value.draftsEndpoint || privateDraftPending.value || !window.confirm(`Delete private draft “${item.name}”?`)) return;
  privateDraftPending.value = true; privateDraftError.value = '';
  try {
    await browserRequest(`${config.value.draftsEndpoint}${item.id}/`, { method: 'DELETE', headers: privateHeaders({ 'If-Match': item.revision }) });
    if (privateDraft.value?.id === item.id) { privateDraft.value = null; savedDraftSnapshot.value = ''; }
    privateDraftStatus.value = 'Private draft deleted; the current form is unchanged.'; await listPrivateDrafts();
  } catch { privateDraftError.value = 'Draft could not be deleted. It may have changed in another tab.'; }
  finally { privateDraftPending.value = false; }
}

async function previewRecord() {
  if (!config.value.previewEndpoint || unavailable.value || previewPending.value) return;
  const resource = editorToResource(draft.value);
  const snapshot = JSON.stringify(resource);
  previewPending.value = true;
  previewError.value = '';
  try {
    const response = await browserRequest(config.value.previewEndpoint, { method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ resource, schemaRevision: config.value.schemaRevision }),
      signal: AbortSignal.any([controller.signal, AbortSignal.timeout(30000)]) });
    previewHtml.value = await response.text();
    previewSnapshot.value = snapshot;
  } catch (error) {
    if (!controller.signal.aborted) previewError.value = error instanceof BrowserRequestError && error.body && typeof error.body === 'object' && 'detail' in error.body
      ? String(error.body.detail) : 'Preview could not be loaded. Your draft is unchanged.';
  } finally { previewPending.value = false; }
}

async function save(validateOnly = false) {
  if (unavailable.value || snapshot.value.blockers.length) return;
  const submission = snapshot.value;
  pending.value = true;
  saved.value = false;
  errors.value = [];
  validationMessage.value = '';
  try {
    const response = await browserRequest(validateOnly ? config.value.validateEndpoint! : config.value.endpoint, { method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ resource: submission.payload, revision: config.value.revision, schemaRevision: config.value.schemaRevision }),
      signal: AbortSignal.any([controller.signal, AbortSignal.timeout(30000)]) });
    if (validateOnly) {
      validationMessage.value = 'Validation passed. Nothing was saved.';
      return;
    }
    const result: Config = await response.json();
    config.value = result;
    draft.value = resourceToEditor(result.resource);
    baseline.value = JSON.stringify(result.resource);
    privateDraft.value = null; savedDraftSnapshot.value = ''; pendingDraftId = '';
    if (config.value.draftsEndpoint) await listPrivateDrafts();
    saved.value = true;
    if (result.editUrl) history.replaceState(null, '', result.editUrl);
    document.title = `Edit ${result.resource.name} | bio.tools`;
  } catch (error) {
    if (controller.signal.aborted) return;
    if (error instanceof BrowserRequestError && ['authentication_required', 'csrf_failed'].includes(error.code)) {
      errors.value = [{ path: [], wirePath: [], message: 'Sign in or reconnect above, then save again. Your changes are retained.' }];
    } else if (error instanceof BrowserRequestError && error.body) {
      errors.value = backendErrorsToEditor(error.body, submission);
    }
    if (!errors.value.length) errors.value = [{ path: [], wirePath: [],
      message: 'Save could not be confirmed. Your draft is retained; check the record before retrying.' }];
    await nextTick();
    errorSummary.value?.focus();
  } finally { pending.value = false; }
}
</script>

<template>
  <div ref="root" class="resource-editor">
    <div class="editor-heading">
      <div><h1>{{ config.revision ? 'Edit tool' : 'Register a tool' }}</h1>
        <p v-if="config.revision" class="editor-id">biotools:{{ draft.biotoolsID }}</p></div>
      <a v-if="config.detailUrl" :href="config.detailUrl">View record</a>
    </div>
    <section v-if="config.draftsEndpoint" class="editor-card private-drafts" aria-label="Private drafts">
      <h2>Private drafts</h2>
      <p>Save unfinished work privately. A draft becomes public only when you publish the record.</p>
      <button type="button" class="secondary" :disabled="pending || privateDraftPending || !!rawError" @click="savePrivateDraft">{{ privateDraft ? 'Update private draft' : 'Save private draft' }}</button>
      <span role="status">{{ privateDraftStatus }}</span><p v-if="privateDraftError" role="alert">{{ privateDraftError }}</p>
      <details v-if="privateDrafts.length"><summary>Open a private draft</summary>
        <ul><li v-for="item in privateDrafts" :key="item.id"><span>{{ item.name }}</span>
          <button type="button" class="secondary" :disabled="privateDraftPending" @click="openPrivateDraft(item)">Open</button>
          <button type="button" class="secondary" :disabled="privateDraftPending" @click="deletePrivateDraft(item)">Delete</button></li></ul>
        <button v-if="moreDrafts" type="button" class="secondary" @click="listPrivateDrafts(true)">More drafts</button>
      </details>
    </section>
    <section v-if="config.previewEndpoint" class="editor-preview" aria-label="Record preview">
      <div class="preview-heading">
        <button type="button" class="secondary" :disabled="unavailable || previewPending" @click="previewRecord">{{ previewPending ? 'Loading preview...' : previewHtml ? 'Refresh preview' : 'Preview record' }}</button>
        <button v-if="previewHtml" type="button" class="secondary" :disabled="previewPending" @click="previewHtml = ''">Close preview</button>
        <span v-if="previewHtml && JSON.stringify(editorToResource(draft)) !== previewSnapshot" role="status">Draft changed. Refresh the preview to see the latest changes.</span>
      </div>
      <p v-if="previewError" role="alert">{{ previewError }}</p>
      <template v-if="previewHtml">
        <p>Preview of your draft. Live publication metrics are omitted. Save changes to publish the record.</p>
        <iframe title="Preview of the tool record" :srcdoc="previewHtml" sandbox="" />
      </template>
    </section>
    <div v-if="errors.length" ref="errorSummary" tabindex="-1" role="alert" class="message error editor-errors">
      <h2>Changes not saved</h2>
      <ul><li v-for="(error, index) in errors" :key="index">
        <a v-if="errorTarget(error)" :href="`#${errorTarget(error)}`">{{ error.wirePath.length ? errorLocation(draft, error) + ': ' : '' }}{{ error.message }}</a>
        <span v-else>{{ error.wirePath.length ? errorLocation(draft, error) + ': ' : '' }}{{ error.message }}</span>
      </li></ul>
    </div>
    <div v-if="schemaReady && snapshot.blockers.length" role="alert" class="message error editor-errors">
      <h2>This record cannot yet be saved here</h2>
      <ul><li v-for="(blocker, index) in snapshot.blockers" :key="index">{{ blocker.path[0] }}: {{ blocker.reason === 'removed-choice' ? 'A stored choice is no longer allowed. Correct it before saving; it remains in your draft.' : 'An unsupported field must be retained in the exported draft.' }}</li></ul>
    </div>
    <p v-if="!schemaReady" role="alert" class="message error">Schema metadata is unavailable or unsupported. Editing is disabled; your record can still be exported.</p>
    <GithubImport v-if="schemaReady && config.schema && config.bridgeEndpoint" :endpoint="config.bridgeEndpoint" :schema="config.schema"
      :current="editorToResource(draft)" :identifier="config.revision ? String(draft.biotoolsID) : null" :disabled="unavailable"
      @apply="applySuggestions(draft, $event)" />
    <p v-else-if="schemaReady">GitHub import is unavailable. You can enter metadata manually.</p>
    <details class="editor-json-panel">
      <summary>JSON record <span class="editor-help" tabindex="0" role="img" aria-label="The current record in JSON format. Changes in the form and JSON are synchronized; save to publish them." title="The current record in JSON format. Changes in the form and JSON are synchronized; save to publish them.">ⓘ</span></summary>
      <p>This is the current record in JSON format. Form and JSON changes update each other. Save changes to publish them.</p>
      <label for="editor-json">Resource JSON</label><textarea id="editor-json" :value="raw" rows="14" :disabled="pending" :readonly="!schemaReady" spellcheck="false" @input="updateJSON" />
    </details>
    <div v-if="rawError" role="alert" class="json-error"><p>{{ rawError }} Correct the JSON or restore the last valid form values. Form editing and saving are paused.</p>
      <button type="button" class="secondary" @click="restoreJSON">Restore JSON from form</button></div>
    <p v-if="validationMessage" role="status" aria-label="Validation status">{{ validationMessage }}</p>
    <form @submit.prevent="save()" :aria-busy="pending">
      <nav class="editor-sections" aria-label="Editor sections">
        <span class="editor-sections-title">Sections</span>
        <a href="#editor-name"><UiIcon name="object" />Basic information</a><a href="#metadata-labels"><UiIcon name="topic" />Labels</a>
        <a v-for="[name, field] in sections" :key="name" :href="`#nested-${name}`"><UiIcon :name="sectionIcon(field.path, field.kind)" />{{ field.label }}</a>
        <a href="#nested-editPermission"><UiIcon name="lock" />Editing permissions</a>
      </nav>
      <div class="editor-content">
      <section class="editor-card"><fieldset :disabled="unavailable" class="editor-fields">
        <legend>Basic information</legend>
        <div class="editor-pair">
          <div><label for="editor-name">{{ fields.name?.label || 'Name' }}</label><span v-if="fields.name?.required" class="required-label" aria-hidden="true">(required)</span>
            <input id="editor-name" v-model="draft.name" type="text" :required="fields.name?.required" :maxlength="fields.name?.maxLength" :aria-invalid="fieldErrors('name').length > 0" aria-describedby="error-name">
            <p id="error-name" class="editor-field-error">{{ fieldErrors('name').join(' ') }}</p></div>
          <div><label for="editor-biotoolsID">{{ fields.biotoolsID?.label || 'bio.tools ID' }}</label><span v-if="fields.biotoolsID?.required" class="required-label" aria-hidden="true">(required)</span>
            <input id="editor-biotoolsID" v-model="draft.biotoolsID" type="text" :required="fields.biotoolsID?.required" :maxlength="fields.biotoolsID?.maxLength" :readonly="!!config.revision" :aria-invalid="fieldErrors('biotoolsID').length > 0" aria-describedby="error-biotoolsID" @input="idEdited = true">
            <p id="error-biotoolsID" class="editor-field-error">{{ fieldErrors('biotoolsID').join(' ') }}</p></div>
        </div>
        <label for="editor-homepage">{{ fields.homepage?.label || 'Homepage' }}</label><span v-if="fields.homepage?.required" class="required-label" aria-hidden="true">(required)</span>
        <input id="editor-homepage" v-model="draft.homepage" type="text" inputmode="url" :required="fields.homepage?.required" :maxlength="fields.homepage?.maxLength" :aria-invalid="fieldErrors('homepage').length > 0" aria-describedby="error-homepage">
        <p id="error-homepage" class="editor-field-error">{{ fieldErrors('homepage').join(' ') }}</p>
        <label for="editor-description">{{ fields.description?.label || 'Description' }}</label><span v-if="fields.description?.required" class="required-label" aria-hidden="true">(required)</span>
        <textarea id="editor-description" v-model="draft.description" :required="fields.description?.required" :minlength="fields.description?.minLength" :maxlength="fields.description?.maxLength" rows="6" :aria-invalid="fieldErrors('description').length > 0" aria-describedby="error-description" />
        <p id="error-description" class="editor-field-error">{{ fieldErrors('description').join(' ') }}</p>
        <fieldset id="editor-toolType" class="editor-types" tabindex="-1" aria-describedby="error-toolType">
          <legend>{{ fields.toolType?.label || 'Tool type' }}</legend>
          <div v-for="type in types" :key="type.value" class="editor-type-choice">
            <label><input type="checkbox" :value="type.value" :checked="selectedTypes.includes(type.value)" @change="changeType(type.value, ($event.target as HTMLInputElement).checked)">{{ type.label }}</label>
            <details v-if="type.help" class="editor-type-help"><summary :aria-label="`About ${type.label}`">ⓘ</summary><p>{{ type.help }}</p></details>
          </div>
        </fieldset>
        <p id="error-toolType" class="editor-field-error">{{ fieldErrors('toolType').join(' ') }}</p>
      </fieldset></section>
      <FunctionEditor v-model="draft.function" :schema="fields.function" :endpoint="config.edamEndpoint" :errors="errors" :disabled="unavailable" />
      <MetadataEditor :draft="draft" :fields="fields" :endpoint="config.edamEndpoint" :errors="errors" :disabled="unavailable" />
      <PermissionEditor v-model="draft.editPermission" :can-manage="config.canManagePermissions === true" :errors="errors" :disabled="unavailable" />
      <div class="editor-actions">
        <button type="submit" :disabled="unavailable || privateDraftPending || !!snapshot.blockers.length">{{ pending ? 'Working...' : config.revision ? 'Save changes' : 'Publish tool' }}</button>
        <button v-if="config.validateEndpoint" type="button" class="secondary" :disabled="unavailable || !!snapshot.blockers.length" @click="save(true)">Validate without saving</button>
        <button type="button" class="secondary" :disabled="pending || !dirty" @click="discard">Discard changes</button>
        <button type="button" class="secondary" @click="exportDraft">Export draft</button>
        <span role="status" aria-label="Save status">{{ pending ? 'Saving changes...' : dirty ? (unstoredChanges ? 'Unsaved changes' : 'Saved privately; not published') : saved ? (config.no_changes ? 'No changes detected.' : 'Changes saved.') : 'No unsaved changes' }}</span>
      </div>
      </div>
    </form>
  </div>
</template>

<style scoped>
.resource-editor { max-width: 1200px; }
.editor-heading { display: flex; justify-content: space-between; align-items: baseline; gap: 16px; margin-bottom: 24px; }
.editor-heading a { white-space: nowrap; }
.editor-preview { margin-bottom: 20px; }
.preview-heading { display: flex; align-items: center; flex-wrap: wrap; gap: 12px; }
.editor-preview iframe { width: 100%; height: 75vh; min-height: 500px; border: 1px solid #dce8ed; border-radius: 8px; background: white; }
.editor-id { color: #575757; margin: 0; overflow-wrap: anywhere; }
.editor-card, .editor-json-panel { min-width: 0; padding: 16px; border: 1px solid var(--line); border-radius: 8px; background: #fff; }
.private-drafts { margin-bottom: 20px; }
.private-drafts p { margin-bottom: 12px; }
.private-drafts ul { padding: 0; list-style: none; }
.private-drafts li { display: flex; align-items: center; flex-wrap: wrap; gap: 8px; margin-block: 8px; }
.editor-json-panel { margin-bottom: 20px; }
.editor-json-panel summary { color: #005472; font-weight: 700; }
.editor-json-panel > p { margin: 12px 0 16px; color: #526d79; }
.editor-json-panel textarea { min-height: 240px; font-family: ui-monospace, SFMono-Regular, Consolas, monospace; font-size: var(--text-ui); }
.editor-help { color: #526d79; margin-left: 4px; cursor: help; }
.json-error { margin-top: 12px; padding: 12px; border-left: 3px solid #a94442; background: #fff4f2; color: #842b29; }
.json-error p { margin-bottom: 10px; }
.resource-editor form { display: grid; grid-template-columns: 220px minmax(0, 1fr); gap: 24px; align-items: start; }
.editor-sections { position: sticky; top: 16px; display: flex; flex-direction: column; align-items: stretch; gap: 0; padding: 12px; margin: 0; border: 1px solid var(--line); border-radius: 8px; background: #fff; font-size: var(--text-ui); }
.editor-sections a { display: flex; align-items: center; gap: 8px; padding: 6px 8px; text-decoration: none; border-radius: 4px; }
.editor-sections a:hover { background: #e5f1f5; text-decoration: underline; }
.editor-sections-title { padding: 6px 8px; color: #425f6b; font-weight: 700; }
.editor-content { min-width: 0; }
.required-label { color: #526d79; font-size: var(--text-caption); font-weight: 400; }
.editor-fields label:has(+ .required-label) { display: inline-block; margin-right: 4px; }
.editor-fields { border: 0; padding: 0; margin: 0; min-width: 0; }
.editor-fields > legend { font-size: var(--text-heading); font-weight: 600; margin-bottom: 16px; padding: 0; }
.editor-pair { display: grid; grid-template-columns: 1fr 1fr; gap: 24px; }
.editor-pair > div { min-width: 0; }
textarea { width: 100%; min-height: 160px; resize: vertical; padding: 12px; border: 1px solid #767676; border-radius: 4px; font: inherit; }
input[readonly] { background: #f4f4f4; color: #575757; }
.editor-field-error { color: #a94442; min-height: 8px; margin: 4px 0 20px; overflow-wrap: anywhere; }
.editor-types { border: 0; padding: 0; margin: 0; display: grid; grid-template-columns: 1fr 1fr; gap: 0 24px; min-width: 0; }
.editor-types legend { font-weight: 600; margin-bottom: 8px; padding: 0; }
.editor-types label { display: flex; align-items: center; gap: 10px; min-height: 36px; font-weight: 400; margin: 0; }
.editor-type-choice { display: flex; align-items: flex-start; gap: 8px; }
.editor-type-help { position: relative; }
.editor-type-help summary { color: #286090; list-style: none; min-height: 36px; }
.editor-type-help p { position: absolute; z-index: 2; width: min(320px, 70vw); margin: 0; padding: 12px; border: 1px solid #d6e2e7; border-radius: 6px; background: white; box-shadow: 0 4px 12px #173e4b22; }
.editor-types input { width: 18px; height: 18px; min-height: 18px; flex: 0 0 18px; accent-color: #337ab7; }
.editor-actions { border-top: 1px solid var(--line); padding: 16px; margin-top: 24px; display: flex; align-items: center; flex-wrap: wrap; gap: 12px; background: #fff; border-radius: 8px; }
.editor-actions span { color: #575757; }
.editor-errors { overflow-wrap: anywhere; }
.editor-errors h2 { font-size: 18px; margin-bottom: 8px; }
.editor-errors ul { margin: 0; padding-left: 20px; }
@media (min-width: 761px) {
  .editor-actions { position: sticky; bottom: 0; z-index: 2; box-shadow: 0 -4px 16px #173e4b14; }
}
@media (max-width: 760px) {
  .resource-editor form { grid-template-columns: minmax(0, 1fr); gap: 20px; }
  .editor-sections { position: static; flex-direction: row; flex-wrap: wrap; gap: 4px; }
  .editor-sections-title { width: 100%; }
}
@media (max-width: 600px) {
  .editor-pair { grid-template-columns: 1fr; gap: 0; }
  .editor-types { grid-template-columns: 1fr; }
  .editor-heading { flex-wrap: wrap; }
}
</style>
