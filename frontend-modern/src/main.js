import htmx from 'htmx.org';
import './home-search.js';
import CounterDemo from './CounterDemo.vue';
import SearchWorkspace from './SearchWorkspace.vue';
import EdamField from './EdamField.vue';
import SessionCheck from './SessionCheck.vue';
import ResourceEditor from './ResourceEditor.vue';
import DomainEditors from './DomainEditors.vue';
import WorkflowDesigner from './WorkflowDesigner.vue';
import { installBrowserAuth, handleHtmxAuthError } from './browser-auth';
import { createIslandRuntime } from './islands';

htmx.config.allowEval = false;
htmx.config.allowScriptTags = false;
htmx.config.selfRequestsOnly = true;
htmx.config.timeout = 10000;
// Restore canonical pages without retaining potentially private HTML in storage.
htmx.config.historyCacheSize = 0;
htmx.config.refreshOnHistoryMiss = true;
htmx.config.historyRestoreAsHxRequest = false;

installBrowserAuth();
createIslandRuntime({ 'counter-demo': CounterDemo, 'search-workspace': SearchWorkspace, 'edam-field': EdamField, 'session-check': SessionCheck, 'resource-editor': ResourceEditor, 'domain-editors': DomainEditors, 'workflow-designer': WorkflowDesigner }).start();

function imageFailure(image) {
  image.closest('.workflow')?.querySelector('[data-workflow-error]')?.removeAttribute('hidden');
  image.closest('.workflow-image')?.querySelectorAll('.workflow-region').forEach(region => region.hidden = true);
}
document.addEventListener('error', event => {
  if (event.target instanceof HTMLImageElement && event.target.hasAttribute('data-workflow-image')) imageFailure(event.target);
}, true);
document.querySelectorAll('[data-workflow-image]').forEach(image => {
  if (image.complete && !image.naturalWidth) imageFailure(image);
});

document.addEventListener('htmx:beforeRequest', () => {
  document.getElementById('request-error').hidden = true;
});
for (const event of ['htmx:responseError', 'htmx:sendError', 'htmx:timeout', 'htmx:swapError']) {
  document.addEventListener(event, ({ detail }) => {
    if (detail?.xhr && handleHtmxAuthError(detail.xhr)) return;
    document.getElementById('request-error').hidden = false;
  });
}
