'use strict';

// BAR is set inline in each menu page: <script>const BAR = 'alibi';</script>

const $ = id => document.getElementById(id);

function esc(str) {
  const d = document.createElement('div');
  d.textContent = String(str);
  return d.innerHTML;
}

async function init() {
  try {
    const res     = await fetch('/api/bars');
    const allBars = await res.json();
    const data    = allBars[BAR];
    renderSpecial(data.special);
    renderMenu(data.menu);
  } catch {
    $('menuGrid').innerHTML = '<div class="menu-loading">Could not load menu data.</div>';
  }
}

function renderSpecial(special) {
  if (!special || !special.title) return;
  $('specialBanner').style.display = '';
  $('specialTitle').textContent = special.title;
  $('specialDesc').textContent  = special.description || '';
  $('specialPrice').textContent = special.price ? '$' + special.price : '';
}

function renderMenu(menu) {
  const grid   = $('menuGrid');
  const filter = $('categoryFilter');

  if (!menu || !Object.keys(menu).length) {
    grid.innerHTML = '<div class="menu-loading">No menu items yet.</div>';
    return;
  }

  const cats = Object.keys(menu);

  // Add a filter button per category
  cats.forEach(cat => {
    const btn        = document.createElement('button');
    btn.className    = 'cat-btn';
    btn.dataset.cat  = cat;
    btn.textContent  = cat;
    btn.addEventListener('click', () => setFilter(cat));
    filter.appendChild(btn);
  });

  // Wire the All button
  filter.querySelector('[data-cat="all"]').addEventListener('click', () => setFilter('all'));

  // Build menu cards
  grid.innerHTML = cats.map(cat => `
    <div class="menu-category" data-cat="${esc(cat)}">
      <div class="menu-category-name">${esc(cat)}</div>
      <div class="menu-items">
        ${menu[cat].map(item => `
          <div class="menu-item">
            <div class="menu-item-top">
              <span class="menu-item-name">${esc(item.name)}</span>
              <span class="menu-item-price">$${esc(item.price)}</span>
            </div>
            ${item.description ? `<div class="menu-item-desc">${esc(item.description)}</div>` : ''}
          </div>
        `).join('')}
      </div>
    </div>
  `).join('');
}

function setFilter(activeCat) {
  document.querySelectorAll('.cat-btn').forEach(btn => {
    btn.classList.toggle('active', btn.dataset.cat === activeCat);
  });
  document.querySelectorAll('.menu-category').forEach(card => {
    card.classList.toggle('hidden', activeCat !== 'all' && card.dataset.cat !== activeCat);
  });
}

init();
