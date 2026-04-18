'use strict';

const esc = s => String(s)
  .replace(/&/g, '&amp;').replace(/</g, '&lt;')
  .replace(/>/g, '&gt;').replace(/"/g, '&quot;');

// Alibi weekly special schedule — auto-displayed unless manager posts an override
// Index = getDay() result: 0=Sun, 1=Mon, 2=Tue, 3=Wed, 4=Thu, 5=Fri, 6=Sat
const ALIBI_WEEKLY = [
  null, // Sunday
  { title: 'P.B. Bacon Burger & Fries',        description: '',                                              price: '8.95' },
  { title: 'Taco Tuesday',                       description: '2 Tacos  ·  or  ·  Indian Taco · $8.95',      price: '4.50' },
  { title: 'Wednesday Specials',                 description: 'Loaded Nachos · $8.95  or  Gyros To-Go · $5.95', price: ''   },
  { title: 'Italian Beef or French Dip',         description: '',                                              price: '6.95' },
  { title: '2 Cheeseburgers & 12″ Pizza',        description: '3-topping pizza included',                     price: '8.95' },
  null  // Saturday
];

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
  // Manager override takes priority; Alibi falls back to weekly schedule
  let display = (special && special.title) ? special : null;
  if (!display && bar === 'alibi') {
    display = ALIBI_WEEKLY[new Date().getDay()];
  }
  const has = !!display;
  document.getElementById(bar + 'SpecialTitle').textContent = has ? display.title         : 'Check Back Soon';
  document.getElementById(bar + 'SpecialDesc').textContent  = has ? (display.description || '') : "Today\u2019s special hasn\u2019t been posted yet.";
  document.getElementById(bar + 'SpecialPrice').textContent = (has && display.price) ? '$' + display.price : '';
}

function renderEvents(bar, events) {
  const list = document.getElementById(bar + 'EventsList');
  if (!events || !events.length) {
    list.innerHTML = '<div class="home-event-card"><div class="home-event-top"><span class="home-event-title">Check Back Soon</span></div><div class="home-event-desc">No upcoming events posted yet \u2014 check back soon!</div></div>';
    return;
  }
  list.innerHTML = events.map(e => `
    <div class="home-event-card">
      <div class="home-event-top">
        <span class="home-event-title">${esc(e.title)}</span>
        ${e.date ? `<span class="home-event-date">${esc(e.date)}</span>` : ''}
      </div>
      ${e.description ? `<div class="home-event-desc">${esc(e.description)}</div>` : ''}
    </div>`
  ).join('');
}

function updateOpenBadge(id, isOpen) {
  const el = document.getElementById(id);
  if (!el) return;
  el.textContent = isOpen ? 'Open Now' : 'Closed';
  el.className   = 'hours-status ' + (isOpen ? 'is-open' : 'is-closed');
}

function updateHoursStatus() {
  const h   = new Date().getHours();
  // Alibi: 10am – 2am daily (spans midnight)
  updateOpenBadge('alibiOpenStatus', h >= 10 || h < 2);
  // Ogden: 11am – 9pm or later daily (treating 9pm as nominal close)
  updateOpenBadge('ogdenOpenStatus', h >= 11 && h < 21);
}

async function loadBarInfo() {
  try {
    const res  = await fetch('/api/bars');
    const data = await res.json();
    renderSpecial('alibi', data.alibi.special);
    renderSpecial('ogden', data.ogden.special);
    renderEvents('alibi',  data.alibi.events);
    renderEvents('ogden',  data.ogden.events);
  } catch { /* defaults already showing in HTML */ }
  updateHoursStatus();
}

loadBarInfo();
