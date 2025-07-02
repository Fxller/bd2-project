document.addEventListener("DOMContentLoaded", () => {
    const addBtn = document.getElementById("add-watchlist-btn");
    if (!addBtn) return;

    addBtn.addEventListener("click", () => {
        const animeId = addBtn.dataset.animeId;

        const payload = { anime_id: animeId };

        fetch("/anime/watchlist/add", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        })
        .then(response => {
            if (response.status === 401) {
                window.location.href = "/users/login";
                return;
            }
            return response.json();
        })
        .then(data => {
            if (data && data.message) {
                const toastElement = document.getElementById('watchlist-toast');
                const toastBody = toastElement.querySelector('.toast-body');
                
                toastBody.textContent = data.message;

                // Prima rimuovi eventuali classi di colore vecchie
                toastElement.classList.remove('text-bg-success', 'text-bg-warning');

                // Se l'anime è già presente, metti il toast giallo
                if (data.message.toLowerCase().includes("già")) {
                    toastElement.classList.add('text-bg-warning');
                } else {
                    toastElement.classList.add('text-bg-success');
                }

                const toast = new bootstrap.Toast(toastElement);
                toast.show();
            }
        })
        .catch(error => {
            console.error("Errore:", error);
        });
    });
});
