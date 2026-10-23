window.addEventListener('DOMContentLoaded', () => {
  fetch('/rides')
    .then(r => r.json())
    .then(data => {
      const box = document.getElementById('rides');
      box.innerHTML = data
        .map(item => `<div class="card"><strong>#${item.id}</strong> ${item.client_name} — ${item.status}</div>`)
        .join('');
    });
});