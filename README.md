# Progetto NoSQL: AnimeList Database

## 📌 Descrizione generale

Questo progetto nasce come prova pratica per l'esame del corso di **Basi di Dati 2** e consiste nella progettazione e implementazione di un database NoSQL orientato ai documenti, basato su dati provenienti da **MyAnimeList**.

Utilizzando **MongoDB**, si intende costruire un sistema che permetta di esplorare, modificare e analizzare informazioni relative ad **anime**, **utenti** e alle loro **attività di visione**, rispettando i vincoli previsti dal paradigma NoSQL e dal **teorema CAP**.

---

## 🧠 Miniworld del progetto

Il dominio applicativo è il mondo degli anime e della community MyAnimeList. Il miniworld include:

* Anime: informazioni dettagliate su ogni serie
* Utenti: profili pubblici, abitudini e interessi
* Interazioni: liste di visione, valutazioni e stati

---

## 🗂️ Struttura del database

### Collection principali

#### 1. `anime`

Contiene informazioni sugli anime.
Campi principali:

* `anime_id`
* `title`, `type`, `genre`, `studio`
* `episodes`, `score`, `rating`

#### 2. `users`

Contiene informazioni di profilo sugli utenti.
Campi principali:

* `user_id`
* `username`, `gender`, `location`, `stats`

#### 3. `user_anime_list`

Relazione tra utenti e anime (watchlist/voti).
Campi principali:

* `user_id`, `anime_id`
* `watched_episodes`, `score`, `status`, `rewatching`

---

## 🔗 Collegamenti tra entità

* `user_anime_list.anime_id` ⇒ `anime.anime_id`
* `user_anime_list.user_id` ⇒ `users.user_id`

---

## 🔄 Operazioni supportate (CRUD)

* **C**: Aggiunta nuovo anime / utente / voce nella watchlist
* **R**: Ricerca e filtraggio per genere, punteggio, stato
* **U**: Modifica dei voti o dello stato di visione
* **D**: Rimozione di elementi dalla watchlist

---

## 🤝 JOIN e aggregazioni

Le JOIN saranno implementate tramite l'operatore `$lookup` di MongoDB per collegare:

* utenti e anime nella loro lista
* anime correlati (sequel, adattamenti...)

Saranno inoltre effettuate **query di aggregazione** per:

* calcolo punteggio medio per anime
* numero medio di episodi visti per utente

---

## 🖥️ Interfaccia utente

Il sistema prevederà lo sviluppo di una semplice **interfaccia web** (Flask/Express) che permetta:

* visualizzazione del catalogo anime
* gestione della lista personale
* inserimento di nuovi utenti e aggiornamento stati

---

## ⚖️ Teorema CAP e proprietà BASE

Il progetto rispetta il teorema CAP scegliendo:

* **Availability**
* **Partition Tolerance**

E segue le proprietà **BASE**:

* Basically Available
* Soft-state
* Eventually Consistent

---

## 📄 Struttura documentazione finale (da completare)

1. Introduzione
2. Descrizione del Miniworld
3. Contesto applicativo
4. Soluzione proposta
5. Metodologia di sviluppo
6. Query, esempi e interfaccia
7. Considerazioni su CAP e BASE
8. Demo finale

