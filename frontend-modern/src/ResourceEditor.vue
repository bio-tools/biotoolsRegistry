<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, onMounted, ref } from 'vue';
import { browserRequest, BrowserRequestError } from './browser-auth';
import FunctionEditor from './FunctionEditor.vue';
import UiIcon from './UiIcon.vue';
import { sectionIcon } from './ui-icons';
import MetadataEditor from './MetadataEditor.vue';
import PermissionEditor from './PermissionEditor.vue';
import GithubImport from './GithubImport.vue';
import { applySuggestions } from './github-import';
import { errorLocation, nestedTarget } from './nested-editor';
import { backendErrorsToEditor, editorToResource, editorToSubmission, newEditorItem,
  resourceToEditor, supportedSchema, type EditorError, type Resource, type ResourceSchema } from './resource-editor';

type Config = { resource: Resource; revision: string | null; endpoint: string; validateEndpoint?: string;
  schema?: ResourceSchema | null; schemaRevision?: string | null; bridgeEndpoint?: string | null;
  editUrl: string | null; detailUrl: string | null; toolTypes: string[]; edamEndpoint: string; metadataOptions?: Record<string, string[]>; canManagePermissions?: boolean; no_changes?: boolean };
const props = defineProps<Config>();
const config = ref<Config>({ ...props });
const draft = ref(resourceToEditor(props.resource));
const baseline = ref(JSON.stringify(props.resource));
const raw = ref('');
const rawSource = ref('');
const rawLoaded = ref('');
const rawDirty = computed(() => raw.value !== rawLoaded.value);
const dirty = computed(() => rawDirty.value || JSON.stringify(editorToResource(draft.value)) !== baseline.value);
const validationMessage = ref('');
const pending = ref(false);
const saved = ref(false);
const errors = ref<EditorError[]>([]);
const errorSummary = ref<HTMLElement>();
const root = ref<HTMLElement>();
const controller = new AbortController();
const schemaReady = computed(() => supportedSchema(config.value.schema, config.value.schemaRevision));
const unavailable = computed(() => pending.value || !schemaReady.value);
const snapshot = computed(() => editorToSubmission(draft.value, config.value.schema?.contract));
const fields = computed(() => config.value.schema?.contract.fields || {});
const sections = computed(() => Object.entries(fields.value).filter(([, field]) => field.writable &&
  (field.kind === 'object' || field.item?.kind === 'object')));
const selectedTypes = computed(() => (draft.value.toolType || []).map(item => item.value));
const types = computed(() => {
  const choices = fields.value.toolType?.choices || [];
  return [...choices, ...selectedTypes.value.filter((value): value is string => typeof value === 'string' &&
    !choices.some(item => item.value === value)).map(value => ({ value, label: value + ' (no longer allowed)' }))];
});

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

function confirmLeave() { return (!dirty.value && !pending.value) || window.confirm('Discard unsaved changes and leave this page?'); }
function beforeUnload(event: BeforeUnloadEvent) {
  if (dirty.value || pending.value) { event.preventDefault(); event.returnValue = ''; }
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
  errors.value = [];
  saved.value = false;
  raw.value = rawLoaded.value = rawSource.value = '';
  validationMessage.value = '';
}
function exportDraft() {
  const url = URL.createObjectURL(new Blob([rawDirty.value ? raw.value : JSON.stringify(editorToResource(draft.value), null, 2)], { type: 'application/json' }));
  const link = document.createElement('a');
  link.href = url;
  link.download = `${draft.value.biotoolsID || 'resource'}-draft.json`;
  link.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}

function loadRaw() {
  if (rawDirty.value && !window.confirm('Replace the unapplied JSON text with the current draft?')) return;
  rawSource.value = JSON.stringify(editorToResource(draft.value));
  raw.value = rawLoaded.value = JSON.stringify(JSON.parse(rawSource.value), null, 2);
}

async function applyRaw() {
  if (unavailable.value || !config.value.validateEndpoint) return;
  const text = raw.value;
  validationMessage.value = '';
  if (JSON.stringify(editorToResource(draft.value)) !== rawSource.value) {
    validationMessage.value = 'The form draft changed. Export your JSON text, then load the current draft before applying it.';
    return;
  }
  pending.value = true;
  try {
    const value = JSON.parse(text);
    const candidate = resourceToEditor(value as Resource);
    const submission = editorToSubmission(candidate, config.value.schema?.contract);
    if (submission.blockers.length) throw new Error('Unsupported fields or values remain in the JSON text. Correct them before applying.');
    await browserRequest(config.value.validateEndpoint, { method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ resource: submission.payload, revision: config.value.revision, schemaRevision: config.value.schemaRevision }),
      signal: AbortSignal.any([controller.signal, AbortSignal.timeout(30000)]) });
    if (text !== raw.value || JSON.stringify(editorToResource(draft.value)) !== rawSource.value) {
      throw new Error('The draft changed during validation. Review it and apply again.');
    }
    applySuggestions(draft.value, value);
    for (const key of Object.keys(draft.value)) if (!(key in value)) Reflect.deleteProperty(draft.value, key);
    rawLoaded.value = raw.value;
    rawSource.value = JSON.stringify(editorToResource(draft.value));
    saved.value = false;
    errors.value = [];
    validationMessage.value = 'JSON applied to the draft. Nothing was saved.';
  } catch (error) {
    if (!controller.signal.aborted) validationMessage.value = error instanceof BrowserRequestError && error.body
      ? JSON.stringify(error.body) : error instanceof Error ? error.message : 'JSON validation failed. Your text is retained.';
  } finally { pending.value = false; }
}

async function save(validateOnly = false) {
  if (unavailable.value || rawDirty.value || snapshot.value.blockers.length) return;
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
    <details>
      <summary>Raw JSON draft</summary>
      <p>Load the current draft, edit its JSON, then validate and apply it. Saving remains a separate action. Invalid text stays available for export.</p>
      <button type="button" class="secondary" :disabled="unavailable" @click="loadRaw">Load current draft as JSON</button>
      <label for="editor-json">Resource JSON</label><textarea id="editor-json" v-model="raw" rows="14" :disabled="pending" spellcheck="false" />
      <button type="button" :disabled="unavailable || !rawDirty || !config.validateEndpoint" @click="applyRaw">Validate and apply JSON</button>
    </details>
    <p v-if="validationMessage" role="status" aria-label="Validation status">{{ validationMessage }}</p>
    <p v-if="rawDirty">Unapplied JSON text. Apply it or reload the current draft before saving the form.</p>
    <form @submit.prevent="save()" :aria-busy="pending">
      <nav class="editor-sections" aria-label="Editor sections">
        <span class="editor-sections-title">Sections</span>
        <a href="#editor-name"><UiIcon name="object" />Basic information</a><a href="#metadata-labels"><UiIcon name="topic" />Labels</a>
        <a v-for="[name, field] in sections" :key="name" :href="`#nested-${name}`"><UiIcon :name="sectionIcon(field.path, field.kind)" />{{ field.label }}</a>
        <a href="#nested-editPermission"><UiIcon name="lock" />Editing permissions</a>
      </nav>
      <div class="editor-content">
      <fieldset :disabled="unavailable" class="editor-fields">
        <legend>Basic information</legend>
        <div class="editor-pair">
          <div><label for="editor-name">{{ fields.name?.label || 'Name' }}</label><span v-if="fields.name?.required" class="required-label" aria-hidden="true">(required)</span>
            <input id="editor-name" v-model="draft.name" type="text" :required="fields.name?.required" :maxlength="fields.name?.maxLength" :aria-invalid="fieldErrors('name').length > 0" aria-describedby="error-name">
            <p id="error-name" class="editor-field-error">{{ fieldErrors('name').join(' ') }}</p></div>
          <div><label for="editor-biotoolsID">{{ fields.biotoolsID?.label || 'bio.tools ID' }}</label><span v-if="fields.biotoolsID?.required" class="required-label" aria-hidden="true">(required)</span>
            <input id="editor-biotoolsID" v-model="draft.biotoolsID" type="text" :required="fields.biotoolsID?.required" :maxlength="fields.biotoolsID?.maxLength" :readonly="!!config.revision" :aria-invalid="fieldErrors('biotoolsID').length > 0" aria-describedby="error-biotoolsID">
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
          <label v-for="type in types" :key="type.value"><input type="checkbox" :value="type.value" :checked="selectedTypes.includes(type.value)" @change="changeType(type.value, ($event.target as HTMLInputElement).checked)">{{ type.label }}</label>
        </fieldset>
        <p id="error-toolType" class="editor-field-error">{{ fieldErrors('toolType').join(' ') }}</p>
      </fieldset>
      <FunctionEditor v-model="draft.function" :schema="fields.function" :endpoint="config.edamEndpoint" :errors="errors" :disabled="unavailable" />
      <MetadataEditor :draft="draft" :fields="fields" :endpoint="config.edamEndpoint" :errors="errors" :disabled="unavailable" />
      <PermissionEditor v-model="draft.editPermission" :can-manage="config.canManagePermissions === true" :errors="errors" :disabled="unavailable" />
      <div class="editor-actions">
        <button type="submit" :disabled="unavailable || rawDirty || !!snapshot.blockers.length">{{ pending ? 'Working...' : 'Save changes' }}</button>
        <button v-if="config.validateEndpoint" type="button" class="secondary" :disabled="unavailable || rawDirty || !!snapshot.blockers.length" @click="save(true)">Validate without saving</button>
        <button type="button" class="secondary" :disabled="pending || !dirty" @click="discard">Discard changes</button>
        <button type="button" class="secondary" @click="exportDraft">Export draft</button>
        <span role="status" aria-label="Save status">{{ pending ? 'Saving changes...' : dirty ? 'Unsaved changes' : saved ? (config.no_changes ? 'No changes detected.' : 'Changes saved.') : 'No unsaved changes' }}</span>
      </div>
      </div>
    </form>
  </div>
</template>

<style scoped>
.resource-editor { max-width: 1200px; }
.editor-heading { display: flex; justify-content: space-between; align-items: baseline; gap: 16px; margin-bottom: 24px; }
.editor-heading a { white-space: nowrap; }
.editor-id { color: #575757; margin: 0; overflow-wrap: anywhere; }
.resource-editor form { display: grid; grid-template-columns: 220px minmax(0, 1fr); gap: 28px; align-items: start; }
.editor-sections { position: sticky; top: 16px; display: flex; flex-direction: column; align-items: stretch; gap: 0; padding: 12px; margin: 0; border: 1px solid #dce8ec; border-radius: 8px; background: #f5f9fa; font-size: var(--text-ui); }
.editor-sections a { display: flex; align-items: center; gap: 8px; padding: 6px 8px; text-decoration: none; border-radius: 4px; }
.editor-sections a:hover { background: #e5f1f5; text-decoration: underline; }
.editor-sections-title { padding: 6px 8px; color: #425f6b; font-weight: 700; }
.editor-content { min-width: 0; }
.required-label { color: #526d79; font-size: var(--text-caption); font-weight: 400; }
.editor-fields label:has(+ .required-label) { display: inline-block; margin-right: 4px; }
.editor-fields { border: 0; padding: 0; margin: 0; min-width: 0; }
.editor-fields > legend { font-size: 20px; font-weight: 600; margin-bottom: 20px; padding: 0; }
.editor-pair { display: grid; grid-template-columns: 1fr 1fr; gap: 24px; }
.editor-pair > div { min-width: 0; }
textarea { width: 100%; min-height: 160px; resize: vertical; padding: 12px; border: 1px solid #767676; border-radius: 4px; font: inherit; }
input[readonly] { background: #f4f4f4; color: #575757; }
.editor-field-error { color: #a94442; min-height: 8px; margin: 4px 0 20px; overflow-wrap: anywhere; }
.editor-types { border: 0; padding: 0; margin: 0; display: grid; grid-template-columns: 1fr 1fr; gap: 0 24px; min-width: 0; }
.editor-types legend { font-weight: 600; margin-bottom: 8px; padding: 0; }
.editor-types label { display: flex; align-items: center; gap: 10px; min-height: 36px; font-weight: 400; margin: 0; }
.editor-types input { width: 18px; height: 18px; min-height: 18px; flex: 0 0 18px; accent-color: #337ab7; }
.editor-actions { border-top: 1px solid #d6e2e7; padding: 16px; margin-top: 24px; display: flex; align-items: center; flex-wrap: wrap; gap: 12px; background: #f5f9fa; border-radius: 8px; }
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
