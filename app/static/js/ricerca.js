document.addEventListener('DOMContentLoaded', function () {
    const campoRicerca = document.getElementById('ricercaTitolo');
    const listaAnime = document.getElementById('listaAnime');
    let timer;

    if (campoRicerca) {
        campoRicerca.addEventListener('input', function () {
            clearTimeout(timer);

            timer = setTimeout(() => {
                const titolo = campoRicerca.value.trim();
                const genere = campoRicerca.getAttribute('data-genere');
                const min_score = campoRicerca.getAttribute('data-min-score');

                const params = new URLSearchParams();
                if (titolo) params.append('title', titolo);
                if (genere) params.append('genre', genere);
                if (min_score) params.append('min_score', min_score);

                fetch(`/ricerca_live?${params.toString()}`)
                    .then(response => response.text())
                    .then(html => {
                        listaAnime.innerHTML = html;
                    })
                    .catch(err => console.error('Errore durante la ricerca:', err));
            }, 400); // Debounce di 400ms
        });
    }
});
