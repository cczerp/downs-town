'use strict';

const esc = s => String(s)
  .replace(/&/g, '&amp;').replace(/</g, '&lt;')
  .replace(/>/g, '&gt;').replace(/"/g, '&quot;');

function switchBar(bar) {
  document.body.classList.remove('alibi-theme', 'ogden-theme');
  document.body.classList.add(bar + '-theme');
  document.getElementById('alibiContent').style.display = bar === 'alibi' ? '' : 'none';
  document.getElementById('ogdenContent').style.display = bar === 'ogden' ? '' : 'none';
  document.querySelectorAll('.bar-tab').forEach(btn => {
    btn.classList.toggle('active', btn.dataset.bar === bar);
  });
  document.title = bar === 'alibi' ? 'Alibi — Down-Town' : 'The Ogden Club — Down-Town';
}

document.querySelectorAll('.bar-tab').forEach(btn => {
  btn.addEventListener('click', () => switchBar(btn.dataset.bar));
});

function renderEvents(bar, events) {
  const el = document.getElementById(bar + 'Events');
  if (!el) return;
  if (!events || !events.length) { el.style.display = 'none'; return; }
  el.style.display = '';
  el.innerHTML =
    '<div class="events-label">Events &amp; Announcements</div>' +
    events.map(e => `
      <div class="event-card">
        <div class="event-top">
          <span class="event-title">${esc(e.title)}</span>
          ${e.date ? `<span class="event-date">${esc(e.date)}</span>` : ''}
        </div>
        ${e.description ? `<div class="event-desc">${esc(e.description)}</div>` : ''}
      </div>`
    ).join('');
}

async function loadEvents() {
  try {
    const res  = await fetch('/api/bars');
    const data = await res.json();
    renderEvents('alibi', data.alibi.events);
    renderEvents('ogden', data.ogden.events);
  } catch { /* non-critical — events just won't show */ }
}

loadEvents();
