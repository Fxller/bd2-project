console.log("Script incluso correttamente!");
document.addEventListener('DOMContentLoaded', () => {
  console.log("JS caricato correttamente!");
  console.log(document.querySelectorAll('.salva-btn'));


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
          alert("Modifica salvata con successo!");
        } else {
          alert("Errore nel salvataggio.");
        }
      })
      .catch(err => {
        console.error(err);
        alert("Errore di rete nel salvataggio.");
      });
    });
  });

});
