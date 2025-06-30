from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.extensions import mongo
from bson.objectid import ObjectId
from flask import jsonify, session

anime_bp = Blueprint('anime', __name__, template_folder='templates')

@anime_bp.route('/<string:anime_id>')
def anime_detail(anime_id):
    anime = mongo.db.anime.find_one({"_id": ObjectId(anime_id)})
    if not anime:
        return "Anime non trovato", 404
    return render_template("anime_detail.html", anime=anime)


@anime_bp.route('/watchlist/add', methods=['POST'])
def add_to_watchlist():
    if 'username' not in session:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json()
    anime_id = data.get("anime_id")

    if not anime_id:
        return jsonify({"error": "Anime ID mancante"}), 400

    # Recupera l'utente completo per ottenere l'_id
    user = mongo.db.users.find_one({"username": session['username']})
    if not user:
        return jsonify({"error": "Utente non trovato"}), 404

# Controllo se è già presente nella watchlist
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
