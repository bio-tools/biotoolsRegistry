(() => {
  const target = document.querySelector('.header-search-count');
  if (!target) return;
  const show = count => {
    if (!Number.isSafeInteger(count) || count < 0) return;
    target.textContent = `${count.toLocaleString()} tools`;
    target.hidden = false;
  };
  try {
    const cached = JSON.parse(sessionStorage.getItem('biotools-tool-count') || 'null');
    if (cached && Date.now() - cached.time < 300000) { show(cached.count); return; }
  } catch { /* Search remains usable when browser storage is unavailable. */ }
  fetch(`${target.dataset.countUrl}?per_page=10`, { headers: { Accept: 'application/json' }, signal: AbortSignal.timeout(5000) })
    .then(response => response.ok ? response.json() : null)
    .then(data => {
      if (!Number.isSafeInteger(data?.count) || data.count < 0) return;
      show(data.count);
      try { sessionStorage.setItem('biotools-tool-count', JSON.stringify({ count: data.count, time: Date.now() })); } catch { /* Optional cache. */ }
    }).catch(() => {});
})();
