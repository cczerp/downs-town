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

function renderSpecial(bar, special) {
  const wrap  = document.getElementById(bar + 'Special');
  if (!special || !special.title) { wrap.style.display = 'none'; return; }
  document.getElementById(bar + 'SpecialTitle').textContent = special.title;
  document.getElementById(bar + 'SpecialDesc').textContent  = special.description || '';
  document.getElementById(bar + 'SpecialPrice').textContent = special.price ? '$' + special.price : '';
  wrap.style.display = '';
}

function renderEvents(bar, events) {
  const wrap = document.getElementById(bar + 'Events');
  const list = document.getElementById(bar + 'EventsList');
  if (!events || !events.length) { wrap.style.display = 'none'; return; }
  list.innerHTML = events.map(e => `
    <div class="home-event-card">
      <div class="home-event-top">
        <span class="home-event-title">${esc(e.title)}</span>
        ${e.date ? `<span class="home-event-date">${esc(e.date)}</span>` : ''}
      </div>
      ${e.description ? `<div class="home-event-desc">${esc(e.description)}</div>` : ''}
    </div>`
  ).join('');
  wrap.style.display = '';
}

async function loadBarInfo() {
  try {
    const res  = await fetch('/api/bars');
    const data = await res.json();
    renderSpecial('alibi', data.alibi.special);
    renderSpecial('ogden', data.ogden.special);
    renderEvents('alibi',  data.alibi.events);
    renderEvents('ogden',  data.ogden.events);
  } catch { /* non-critical */ }
}

loadBarInfo();
