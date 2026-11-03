(() => {
  const form = document.querySelector('[data-home-search]');
  if (!form) return;
  const input = form.querySelector('#home-query');
  const list = form.querySelector('#home-suggestions');
  const status = form.querySelector('#home-suggestion-status');
  const scopes = [
    ['topic', 'Topic', 'topicID'], ['operation', 'Operation', 'operationID'],
    ['data', 'Data type', 'dataTypeID'], ['format', 'Format', 'dataFormatID'],
  ];
  let timer, controller, timeout, sequence = 0, active = -1;
  input.setAttribute('role', 'combobox');
  input.setAttribute('aria-autocomplete', 'list');
  input.setAttribute('aria-controls', list.id);
  input.setAttribute('aria-expanded', 'false');
  input.setAttribute('autocomplete', 'off');
  function close() {
    list.hidden = true;
    input.setAttribute('aria-expanded', 'false');
    input.removeAttribute('aria-activedescendant');
    active = -1;
  }
  function cancel() {
    sequence++;
    clearTimeout(timer); clearTimeout(timeout);
    controller?.abort();
  }
  function highlight(index) {
    const choices = [...list.querySelectorAll('[role="option"]')];
    if (!choices.length) return;
    active = (index + choices.length) % choices.length;
    choices.forEach((choice, position) => choice.setAttribute('aria-selected', String(position === active)));
    input.setAttribute('aria-activedescendant', choices[active].id);
    choices[active].scrollIntoView({ block: 'nearest' });
  }
  async function lookup(query, current) {
    controller = new AbortController();
    timeout = setTimeout(() => controller.abort(), 8000);
    const signal = controller.signal;
    const results = await Promise.allSettled(scopes.map(async ([scope, label, key]) => {
      const url = new URL(form.dataset.edamUrl, location.href);
      url.search = new URLSearchParams({ scope, q: query });
      const response = await fetch(url, { signal, headers: { Accept: 'application/json' } });
      if (!response.ok) throw new Error('Lookup unavailable');
      const body = await response.json();
      if (!Array.isArray(body.items)) throw new Error('Invalid lookup');
      return body.items.slice(0, 3).flatMap(item => {
        const match = typeof item.uri === 'string' && item.uri.match(new RegExp(`^http://edamontology\\.org/(${scope}_[0-9]{4})$`));
        return match && typeof item.term === 'string' ? [{ id: match[1], term: item.term, label, key }] : [];
      });
    }));
    clearTimeout(timeout);
    if (current !== sequence) return;
    list.replaceChildren(); active = -1;
    const items = results.flatMap(result => result.status === 'fulfilled' ? result.value : []);
    for (const [index, item] of items.entries()) {
      const li = document.createElement('li');
      const link = document.createElement('a');
      const category = document.createElement('span');
      const text = document.createElement('strong');
      const identifier = document.createElement('small');
      li.setAttribute('role', 'presentation');
      link.id = `home-suggestion-${index}`;
      link.setAttribute('role', 'option');
      link.setAttribute('aria-selected', 'false');
      link.tabIndex = -1;
      link.href = '/t?' + new URLSearchParams({ [item.key]: `"${item.id}"` });
      category.className = 'suggestion-category'; category.textContent = item.label;
      text.textContent = item.term; identifier.textContent = item.id;
      link.append(category, text, identifier); li.append(link); list.append(li);
    }
    const failures = results.filter(result => result.status === 'rejected').length;
    status.textContent = failures ? 'Some concept suggestions are unavailable. You can still search by text.'
      : items.length ? `${items.length} EDAM suggestions available.` : 'No EDAM suggestions. You can still search by text.';
    list.hidden = !items.length;
    input.setAttribute('aria-expanded', String(!!items.length));
  }
  input.addEventListener('input', () => {
    cancel(); close(); list.replaceChildren(); status.textContent = '';
    const query = input.value.trim();
    if (query.length < 2 || query.length > 128 || /[\x00-\x1f\x7f]/.test(query)) return;
    const current = sequence;
    timer = setTimeout(() => lookup(query, current), 350);
  });
  input.addEventListener('keydown', event => {
    if (event.key === 'Escape') { cancel(); close(); status.textContent = ''; }
    else if (!list.hidden && (event.key === 'ArrowDown' || event.key === 'ArrowUp')) {
      event.preventDefault(); highlight(active < 0 && event.key === 'ArrowUp' ? -1 : active + (event.key === 'ArrowDown' ? 1 : -1));
    } else if (!list.hidden && event.key === 'Enter' && active >= 0) {
      event.preventDefault(); list.querySelectorAll('[role="option"]')[active]?.click();
    }
  });
  list.addEventListener('mousedown', event => event.preventDefault());
  input.addEventListener('blur', () => { cancel(); close(); });
})();
