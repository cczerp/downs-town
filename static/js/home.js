'use strict';

function switchBar(bar) {
  // Swap the full-page theme
  document.body.classList.remove('alibi-theme', 'ogden-theme');
  document.body.classList.add(bar + '-theme');

  // Show only the selected bar's content
  document.getElementById('alibiContent').style.display = bar === 'alibi' ? '' : 'none';
  document.getElementById('ogdenContent').style.display = bar === 'ogden' ? '' : 'none';

  // Update toggle button active states
  document.querySelectorAll('.bar-tab').forEach(btn => {
    btn.classList.toggle('active', btn.dataset.bar === bar);
  });

  // Update browser tab title
  document.title = bar === 'alibi' ? 'Alibi — Down-Town' : 'The Ogden Club — Down-Town';
}

document.querySelectorAll('.bar-tab').forEach(btn => {
  btn.addEventListener('click', () => switchBar(btn.dataset.bar));
});
