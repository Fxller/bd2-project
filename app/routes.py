from flask import Blueprint, render_template, request, redirect, url_for, flash
from bson.objectid import ObjectId
from .db import get_db

main = Blueprint('main', __name__)

@main.route('/')
def home():
    db = get_db()
    query = {}

    title = request.args.get('title')
    genre = request.args.get('genre')
    min_score = request.args.get('min_score')
    page = int(request.args.get('page', 1))
    per_page = 12

    if title:
        query["title"] = {"$regex": title, "$options": "i"}
    if genre:
        query["genre"] = {"$regex": genre, "$options": "i"}
    if min_score:
        try:
            query["score"] = {"$gte": float(min_score)}
        except ValueError:
            pass

    skip = (page - 1) * per_page
    anime_list = db.anime.find(query).skip(skip).limit(per_page)
    total_anime = db.anime.count_documents(query)
    total_pages = (total_anime + per_page - 1) // per_page

    return render_template('home.html', anime=anime_list, total_pages=total_pages, current_page=page)

@main.route('/watchlist/add', methods=['GET', 'POST'])
def add_to_watchlist():
    db = get_db()

    if request.method == 'POST':
        entry = {
            "username": request.form['username'],
            "anime_id": int(request.form['anime_id']),
            "score": int(request.form['score']),
            "status": request.form['status']
        }
        db.user_anime_list.insert_one(entry)
        flash("Anime aggiunto con successo alla watchlist!", "success")
        return redirect(url_for('main.user_profile', username=entry['username']))

    anime_list = db.anime.find({}, {"anime_id": 1, "title": 1}).limit(100)
    return render_template("add_watchlist.html", anime_list=anime_list)

@main.route('/watchlist/edit/<entry_id>', methods=['GET', 'POST'])
def edit_watchlist(entry_id):
    db = get_db()
    entry = db.user_anime_list.find_one({"_id": ObjectId(entry_id)})

    if request.method == 'POST':
        db.user_anime_list.update_one(
            {"_id": ObjectId(entry_id)},
            {"$set": {
                "score": int(request.form['score']),
                "status": request.form['status']
            }}
        )
        flash("Voce modificata con successo!", "info")
        return redirect(url_for('main.user_profile', username=entry['username']))

    anime = db.anime.find_one({"anime_id": entry['anime_id']})
    return render_template("edit_watchlist.html", entry=entry, anime=anime)

@main.route('/watchlist/delete/<entry_id>', methods=['POST'])
def delete_watchlist(entry_id):
    db = get_db()
    entry = db.user_anime_list.find_one({"_id": ObjectId(entry_id)})
    if entry:
        db.user_anime_list.delete_one({"_id": ObjectId(entry_id)})
        flash("Voce eliminata dalla watchlist.", "danger")
        return redirect(url_for('main.user_profile', username=entry['username']))
    return "Voce non trovata", 404

@main.route('/dashboard')
def dashboard():
    db = get_db()

    # Media punteggio globale degli anime
    avg_score = db.anime.aggregate([
        {"$match": {"score": {"$ne": None}}},
        {"$group": {"_id": None, "media_score": {"$avg": "$score"}}}
    ])
    avg_score_list = list(avg_score)
    avg_score_value = round(avg_score_list[0]["media_score"], 2) if avg_score_list else "N/D"

    # Totale utenti
    total_users = db.users.count_documents({})

    # Totale voci nella watchlist
    total_watchlist = db.user_anime_list.count_documents({})

    # Top 5 anime più popolari nella watchlist
    top_anime = db.user_anime_list.aggregate([
        {"$group": {"_id": "$anime_id", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 5},
        {"$lookup": {
            "from": "anime",
            "localField": "_id",
            "foreignField": "anime_id",
            "as": "anime_info"
        }},
        {"$unwind": "$anime_info"}
    ])

    return render_template("dashboard.html",
        avg_score=avg_score_value,
        total_users=total_users,
        total_watchlist=total_watchlist,
        top_anime=top_anime
    )
