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
                alert(data.message);
            }
        })
        .catch(error => {
            console.error("Errore:", error);
        });
    });
});
