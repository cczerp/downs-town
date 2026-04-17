'use strict';

// ── State ──────────────────────────────────────────────────────────────────────
let currentBar = 'ogden';
let mgrBar = 'ogden';
let barData = null;

const BAR_CONFIG = {
  ogden: { name: 'The Ogden Club', tagline: 'Your neighborhood\'s home base' },
  alibi: { name: 'Alibi',          tagline: 'Where regulars become family'   }
};

// ── DOM helpers ────────────────────────────────────────────────────────────────
const $ = id => document.getElementById(id);

function esc(str) {
  const d = document.createElement('div');
  d.textContent = String(str);
  return d.innerHTML;
}

// ── Boot ───────────────────────────────────────────────────────────────────────
async function init() {
  await loadBars();
  await checkAuth();
  switchBar('ogden');
}

async function loadBars() {
  try {
    const res = await fetch('/api/bars');
    barData = await res.json();
  } catch {
    $('menuGrid').innerHTML = '<div class="menu-loading">Could not load menu data.</div>';
  }
}

async function checkAuth() {
  try {
    const res = await fetch('/api/auth');
    const data = await res.json();
    if (data.authenticated) showManagerPanel();
  } catch { /* ignore */ }
}

// ── Bar switching ──────────────────────────────────────────────────────────────
function switchBar(bar) {
  currentBar = bar;
  const cfg = BAR_CONFIG[bar];

  $('heroBarName').textContent = cfg.name;
  $('heroTagline').textContent = cfg.tagline;
  $('heroBg').className = 'hero-bg' + (bar === 'alibi' ? ' alibi' : '');
  $('menuBarLabel').textContent = cfg.name;

  $('tabOgden').classList.toggle('active', bar === 'ogden');
  $('tabAlibi').classList.toggle('active', bar === 'alibi');

  if (barData) {
    renderMenu(barData[bar].menu);
    renderSpecial(barData[bar].special);
  }
}

$('tabOgden').addEventListener('click', () => switchBar('ogden'));
$('tabAlibi').addEventListener('click', () => switchBar('alibi'));

// ── Menu render ────────────────────────────────────────────────────────────────
function renderMenu(menu) {
  const grid = $('menuGrid');
  if (!menu || !Object.keys(menu).length) {
    grid.innerHTML = '<div class="menu-loading">No menu items yet.</div>';
    return;
  }
  grid.innerHTML = Object.entries(menu).map(([cat, items]) => `
    <div class="menu-category">
      <div class="menu-category-name">${esc(cat)}</div>
      <div class="menu-items">
        ${items.map(item => `
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

// ── Special banner ─────────────────────────────────────────────────────────────
function renderSpecial(special) {
  const banner = $('specialBanner');
  if (!special || !special.title) {
    banner.style.display = 'none';
    return;
  }
  banner.style.display = '';
  $('specialTitle').textContent = special.title;
  $('specialDesc').textContent  = special.description;
  $('specialPrice').textContent = special.price ? '$' + special.price : '';
}

// ── Manager modal ──────────────────────────────────────────────────────────────
$('mgrToggle').addEventListener('click', () => $('mgrModal').classList.add('open'));
$('modalClose').addEventListener('click', closeModal);
$('mgrModal').addEventListener('click', e => { if (e.target === $('mgrModal')) closeModal(); });

function closeModal() { $('mgrModal').classList.remove('open'); }

// Login
$('loginBtn').addEventListener('click', async () => {
  const pw = $('mgrPassword').value;
  $('loginError').textContent = '';
  if (!pw) return;
  try {
    const res  = await fetch('/api/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ password: pw })
    });
    const data = await res.json();
    if (data.success) {
      showManagerPanel();
    } else {
      $('loginError').textContent = 'Invalid password.';
    }
  } catch {
    $('loginError').textContent = 'Network error. Try again.';
  }
});

$('mgrPassword').addEventListener('keydown', e => { if (e.key === 'Enter') $('loginBtn').click(); });

function showManagerPanel() {
  $('loginView').style.display    = 'none';
  $('managerPanel').style.display = '';
  syncMgrSpecial();
  renderMgrMenu();
}

function showLoginView() {
  $('managerPanel').style.display = 'none';
  $('loginView').style.display    = '';
  $('mgrPassword').value          = '';
  $('loginError').textContent     = '';
}

// Manager bar tabs
document.querySelectorAll('.mgr-tab').forEach(tab => {
  tab.addEventListener('click', () => {
    mgrBar = tab.dataset.mgrBar;
    document.querySelectorAll('.mgr-tab').forEach(t => t.classList.remove('active'));
    tab.classList.add('active');
    syncMgrSpecial();
    renderMgrMenu();
  });
});

// ── Special editor ─────────────────────────────────────────────────────────────
function syncMgrSpecial() {
  if (!barData) return;
  const s = barData[mgrBar].special || {};
  $('specialTitleInput').value = s.title       || '';
  $('specialDescInput').value  = s.description || '';
  $('specialPriceInput').value = s.price       || '';
}

$('saveSpecialBtn').addEventListener('click', async () => {
  const payload = {
    title:       $('specialTitleInput').value.trim(),
    description: $('specialDescInput').value.trim(),
    price:       $('specialPriceInput').value.trim()
  };
  try {
    const res  = await fetch(`/api/bars/${mgrBar}/special`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    const data = await res.json();
    if (data.success) {
      barData[mgrBar].special = data.special;
      if (mgrBar === currentBar) renderSpecial(barData[mgrBar].special);
      flashFeedback('specialFeedback', 'Special saved!');
    }
  } catch {
    flashFeedback('specialFeedback', 'Error saving special.');
  }
});

// ── Menu editor ────────────────────────────────────────────────────────────────
function renderMgrMenu() {
  if (!barData) return;
  const editor = $('mgrMenuEditor');
  editor.innerHTML = '';
  Object.entries(barData[mgrBar].menu).forEach(([cat, items]) => {
    editor.appendChild(buildCategoryBlock(cat, items));
  });
}

function buildCategoryBlock(catName, items) {
  const block = document.createElement('div');
  block.className = 'mgr-category-block';

  const header    = document.createElement('div');
  header.className = 'mgr-category-header';

  const nameInput = document.createElement('input');
  nameInput.className   = 'mgr-cat-name-input';
  nameInput.value       = catName;
  nameInput.placeholder = 'Category name';

  const delBtn      = document.createElement('button');
  delBtn.className  = 'mgr-cat-delete';
  delBtn.textContent = '✕';
  delBtn.addEventListener('click', () => block.remove());

  header.appendChild(nameInput);
  header.appendChild(delBtn);

  const itemsDiv      = document.createElement('div');
  items.forEach(item => itemsDiv.appendChild(buildItemRow(item)));

  const addBtn      = document.createElement('button');
  addBtn.className  = 'mgr-add-item-btn';
  addBtn.textContent = '+ Add item';
  addBtn.addEventListener('click', () => {
    itemsDiv.appendChild(buildItemRow({ name: '', description: '', price: '' }));
  });

  block._getCategory = () => ({
    name:  nameInput.value.trim(),
    items: Array.from(itemsDiv.querySelectorAll('.mgr-item-row')).map(row => {
      const inputs = row.querySelectorAll('.mgr-item-input');
      return { name: inputs[0].value, description: inputs[1].value, price: inputs[2].value };
    }).filter(i => i.name.trim())
  });

  block.appendChild(header);
  block.appendChild(itemsDiv);
  block.appendChild(addBtn);
  return block;
}

function buildItemRow(item) {
  const row      = document.createElement('div');
  row.className  = 'mgr-item-row';

  [
    { ph: 'Name',        val: item.name        },
    { ph: 'Description', val: item.description },
    { ph: 'Price',       val: item.price        }
  ].forEach(({ ph, val }) => {
    const input       = document.createElement('input');
    input.className   = 'mgr-item-input';
    input.placeholder = ph;
    input.value       = val || '';
    row.appendChild(input);
  });

  const del      = document.createElement('button');
  del.className  = 'mgr-item-delete';
  del.textContent = '✕';
  del.addEventListener('click', () => row.remove());
  row.appendChild(del);
  return row;
}

$('addCategoryBtn').addEventListener('click', () => {
  $('mgrMenuEditor').appendChild(buildCategoryBlock('New Category', []));
});

$('saveMenuBtn').addEventListener('click', async () => {
  const blocks = $('mgrMenuEditor').querySelectorAll('.mgr-category-block');
  const menu   = {};
  blocks.forEach(block => {
    if (block._getCategory) {
      const { name, items } = block._getCategory();
      if (name) menu[name] = items;
    }
  });
  try {
    const res  = await fetch(`/api/bars/${mgrBar}/menu`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ menu })
    });
    const data = await res.json();
    if (data.success) {
      barData[mgrBar].menu = menu;
      if (mgrBar === currentBar) renderMenu(barData[mgrBar].menu);
      flashFeedback('menuFeedback', 'Menu saved!');
    }
  } catch {
    flashFeedback('menuFeedback', 'Error saving menu.');
  }
});

// Logout
$('logoutBtn').addEventListener('click', async () => {
  await fetch('/api/logout', { method: 'POST' });
  showLoginView();
});

// ── Utilities ──────────────────────────────────────────────────────────────────
function flashFeedback(id, msg) {
  const el = $(id);
  el.textContent = msg;
  setTimeout(() => { el.textContent = ''; }, 3000);
}

// ── Start ──────────────────────────────────────────────────────────────────────
init();
