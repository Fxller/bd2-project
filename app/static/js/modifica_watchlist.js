console.log("Script incluso correttamente!");

document.addEventListener('DOMContentLoaded', () => {
  console.log("JS caricato correttamente!");
  console.log(document.querySelectorAll('.salva-btn'));

function mostraToast(messaggio, success = true) {
  const toastEl = document.getElementById('watchlist-toast');
  if (!toastEl) return;

  const body = toastEl.querySelector('.toast-body');
  if (body) body.textContent = messaggio;

  // Cambia colore in base al tipo
  toastEl.classList.remove('text-bg-success', 'text-bg-danger');
  toastEl.classList.add(success ? 'text-bg-success' : 'text-bg-danger');

  const toast = new bootstrap.Toast(toastEl);
  toast.show();
}

  document.querySelectorAll('.salva-btn').forEach(button => {
    button.addEventListener('click', () => {
      
      const entryId = button.dataset.entryId;
      const parent = button.closest('.watchlist-item');

      const score = parent.querySelector('.score-selector').value;
      const status = parent.querySelector('.status-selector').value;
      const episodes = parent.querySelector('.episodes-selector').value;

      console.log(`Salvo per ID: ${entryId}, punteggio: ${score}, stato: ${status}, episodi: ${episodes}`);

      fetch('/anime/watchlist/update_full', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          entry_id: entryId,
          my_score: parseInt(score),
          stato: status,
          my_watched_episodes: parseInt(episodes)
        })
      })
      .then(res => res.json())
      .then(data => {
        if (data.success) {
          mostraToast("Modifica salvata con successo alla watchlist!", true);
        } else {
          mostraToast("Errore nel salvataggio.", false);
        }
      })
      .catch(err => {
        console.error(err);
        mostraToast("Errore di rete nel salvataggio.");
      });
    });
  });

});
