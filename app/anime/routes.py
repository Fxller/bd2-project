from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.extensions import mongo
from bson.objectid import ObjectId
from flask import jsonify, session
import pandas as pd
import pickle
from sklearn.metrics.pairwise import cosine_distances

anime_bp = Blueprint('anime', __name__, template_folder='templates')

df = pd.read_csv('datasets/anime_suggestions.csv')

with open('matrice_X.pkl', 'rb') as f:
    X = pickle.load(f)

def get_suggerimenti(titolo, n=6):
    anime_corrente = df[df['title'].str.lower() == titolo.lower()]

    if anime_corrente.empty:
        return []

    indice_anime = anime_corrente.index[0]
    cluster_corrente = anime_corrente['cluster'].values[0]
    cluster_anime = df[df['cluster'] == cluster_corrente]
    cluster_indices = cluster_anime.index
    X_cluster = X[cluster_indices]
    anime_feature = X[indice_anime].reshape(1, -1)
    distanze = cosine_distances(anime_feature, X_cluster)[0]
    cluster_anime = cluster_anime.copy()
    cluster_anime['distanza'] = distanze
    suggerimenti = cluster_anime[cluster_anime['title'].str.lower() != titolo.lower()]
    suggerimenti = suggerimenti.sort_values('distanza').head(n)
    
    return suggerimenti[['title', 'score', 'episodes']].to_dict(orient='records')


@anime_bp.route('/<string:anime_id>')
def anime_detail(anime_id):
    anime = mongo.db.anime.find_one({"_id": ObjectId(anime_id)})
    if not anime:
        return "Anime non trovato", 404

    titolo = anime['title']
    suggerimenti = get_suggerimenti(titolo)

    suggerimenti_mongo = []
    for s in suggerimenti:
        suggerito = mongo.db.anime.find_one({"title": s['title']})
        if suggerito:
            suggerimenti_mongo.append({
                "_id": suggerito["_id"],
                "title": suggerito["title"],
                "image_url": suggerito.get("image_url", ""),
                "score": suggerito.get("score", ""),
                "episodes": suggerito.get("episodes", "")
            })

    return render_template("anime_detail.html", anime=anime, suggerimenti=suggerimenti_mongo)


@anime_bp.route('/watchlist/add', methods=['POST'])
def add_to_watchlist():
    if 'username' not in session:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json()
    anime_id = data.get("anime_id")

    if not anime_id:
        return jsonify({"error": "Anime ID mancante"}), 400

    user = mongo.db.users.find_one({"username": session['username']})
    if not user:
        return jsonify({"error": "Utente non trovato"}), 404

    esiste = mongo.db.user_anime_list.find_one({
        "user_id": user["_id"],
        "anime_id": ObjectId(anime_id)
    })

    if esiste:
        return jsonify({"message": "Questo anime è già presente nella tua watchlist."}), 200
    
    entry = {
        "username": session['username'],
        "user_id": user['_id'],
        "anime_id": ObjectId(anime_id),
        "my_watched_episodes": 0,
        "my_score": 0,
        "terminato": False,
        "stato": "watching"
    }

    mongo.db.user_anime_list.insert_one(entry)
    return jsonify({"message": "Anime aggiunto con successo alla watchlist!"}), 200


@anime_bp.route('/watchlist/edit/<entry_id>', methods=['GET', 'POST'])
def edit_watchlist(entry_id):
    entry = mongo.db.user_anime_list.find_one({"_id": ObjectId(entry_id)})

    if request.method == 'POST':
        mongo.db.user_anime_list.update_one(
            {"_id": ObjectId(entry_id)},
            {"$set": {
                "score": int(request.form['score']),
                "status": request.form['status']
            }}
        )
        flash("Voce modificata con successo!", "info")
        return redirect(url_for('users.user_profile', username=entry['username']))

    anime = mongo.db.anime.find_one({"anime_id": entry['anime_id']})
    return render_template("edit_watchlist.html", entry=entry, anime=anime)

@anime_bp.route('/watchlist/delete/<entry_id>', methods=['POST'])
def delete_watchlist(entry_id):
    entry = mongo.db.user_anime_list.find_one({"_id": ObjectId(entry_id)})
    if entry:
        mongo.db.user_anime_list.delete_one({"_id": ObjectId(entry_id)})
        flash("Voce eliminata dalla watchlist.", "danger")
        return redirect(url_for('users.user_profile', username=entry['username']))
    return "Voce non trovata", 404

@anime_bp.route('/watchlist/update_full', methods=['POST'])
def update_watchlist_full():
    data = request.get_json()

    entry_id = data['entry_id']
    my_score = data['my_score']
    stato = data['stato']
    my_watched_episodes = data['my_watched_episodes']

    mongo.db.user_anime_list.update_one(
        { "_id": ObjectId(entry_id) },
        { "$set": {
            "my_score": my_score,
            "stato": stato,
            "my_watched_episodes": my_watched_episodes
        }}
    )

    return jsonify({ "success": True })

