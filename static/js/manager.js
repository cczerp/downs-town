'use strict';

const $ = id => document.getElementById(id);

let barData = null;
let mgrBar  = 'ogden';

// ── Boot ───────────────────────────────────────────────────────────────
async function init() {
  try {
    const res = await fetch('/api/auth');
    if ((await res.json()).authenticated) {
      await loadBarData();
      showPanel();
    }
  } catch { /* start at login */ }
}

async function loadBarData() {
  const res = await fetch('/api/bars');
  barData   = await res.json();
}

// ── Login ──────────────────────────────────────────────────────────────
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
      await loadBarData();
      showPanel();
    } else {
      $('loginError').textContent = 'Invalid password.';
    }
  } catch {
    $('loginError').textContent = 'Network error — try again.';
  }
});

$('mgrPassword').addEventListener('keydown', e => {
  if (e.key === 'Enter') $('loginBtn').click();
});

function showPanel() {
  $('loginView').style.display    = 'none';
  $('managerPanel').style.display = '';
  syncSpecial();
  renderMenuEditor();
}

// ── Bar tabs ───────────────────────────────────────────────────────────
document.querySelectorAll('.mgr-tab').forEach(tab => {
  tab.addEventListener('click', () => {
    mgrBar = tab.dataset.mgrBar;
    document.querySelectorAll('.mgr-tab').forEach(t => t.classList.remove('active'));
    tab.classList.add('active');
    syncSpecial();
    renderMenuEditor();
  });
});

// ── Special editor ─────────────────────────────────────────────────────
function syncSpecial() {
  const s = (barData[mgrBar] && barData[mgrBar].special) || {};
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
      flash('specialFeedback', 'Special saved!');
    }
  } catch {
    flash('specialFeedback', 'Error — check connection.');
  }
});

// ── Menu editor ────────────────────────────────────────────────────────
function renderMenuEditor() {
  const editor = $('mgrMenuEditor');
  editor.innerHTML = '';
  Object.entries(barData[mgrBar].menu).forEach(([cat, items]) => {
    editor.appendChild(buildCatBlock(cat, items));
  });
}

function buildCatBlock(catName, items) {
  const block      = document.createElement('div');
  block.className  = 'mgr-category-block';

  // Header row with editable category name and delete button
  const hdr       = document.createElement('div');
  hdr.className   = 'mgr-category-header';

  const nameIn        = document.createElement('input');
  nameIn.className    = 'mgr-cat-name-input';
  nameIn.value        = catName;
  nameIn.placeholder  = 'Category name';

  const delCat        = document.createElement('button');
  delCat.className    = 'mgr-cat-delete';
  delCat.textContent  = '✕';
  delCat.title        = 'Remove category';
  delCat.addEventListener('click', () => block.remove());

  hdr.appendChild(nameIn);
  hdr.appendChild(delCat);

  // Item rows
  const itemsDiv = document.createElement('div');
  items.forEach(item => itemsDiv.appendChild(buildItemRow(item)));

  // Add item button
  const addBtn        = document.createElement('button');
  addBtn.className    = 'mgr-add-item-btn';
  addBtn.textContent  = '+ Add item';
  addBtn.addEventListener('click', () => {
    itemsDiv.appendChild(buildItemRow({ name: '', description: '', price: '' }));
  });

  // Expose data-collection method for Save
  block._getData = () => ({
    name:  nameIn.value.trim(),
    items: Array.from(itemsDiv.querySelectorAll('.mgr-item-row')).map(row => {
      const ins = row.querySelectorAll('.mgr-item-input');
      return {
        name:        ins[0].value.trim(),
        description: ins[1].value.trim(),
        price:       ins[2].value.trim()
      };
    }).filter(i => i.name)
  });

  block.appendChild(hdr);
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
    const inp       = document.createElement('input');
    inp.className   = 'mgr-item-input';
    inp.placeholder = ph;
    inp.value       = val || '';
    row.appendChild(inp);
  });

  const del       = document.createElement('button');
  del.className   = 'mgr-item-delete';
  del.textContent = '✕';
  del.title       = 'Remove item';
  del.addEventListener('click', () => row.remove());
  row.appendChild(del);

  return row;
}

$('addCategoryBtn').addEventListener('click', () => {
  $('mgrMenuEditor').appendChild(buildCatBlock('New Category', []));
});

$('saveMenuBtn').addEventListener('click', async () => {
  const blocks = $('mgrMenuEditor').querySelectorAll('.mgr-category-block');
  const menu   = {};
  blocks.forEach(b => {
    if (!b._getData) return;
    const { name, items } = b._getData();
    if (name) menu[name] = items;
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
      flash('menuFeedback', 'Menu saved!');
    }
  } catch {
    flash('menuFeedback', 'Error — check connection.');
  }
});

// ── Logout ─────────────────────────────────────────────────────────────
$('logoutBtn').addEventListener('click', async () => {
  await fetch('/api/logout', { method: 'POST' });
  $('managerPanel').style.display = 'none';
  $('loginView').style.display    = '';
  $('mgrPassword').value          = '';
});

// ── Utility ────────────────────────────────────────────────────────────
function flash(id, msg) {
  const el    = $(id);
  el.textContent = msg;
  setTimeout(() => { el.textContent = ''; }, 3000);
}

init();
