from flask import Blueprint, render_template, request, redirect, url_for, flash
from bson.objectid import ObjectId
from .db import get_db
from flask import session
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()

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
    generi = db.anime.distinct("genre")
    
    return render_template('home.html', anime=anime_list, total_pages=total_pages, current_page=page, generi = generi)

@main.route('/watchlist/add', methods=['GET', 'POST'])
def add_to_watchlist():
    db = get_db()

    preselected_id = request.args.get('preselected_id', type=int)

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
    return render_template("add_watchlist.html", anime_list=anime_list, preselected_id=preselected_id)

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

@main.route('/anime/<int:anime_id>')
def anime_detail(anime_id):
    db = get_db()
    anime = db.anime.find_one({"anime_id": anime_id})
    if not anime:
        return "Anime non trovato", 404
    return render_template("anime_detail.html", anime=anime)

@main.route('/register', methods=['GET', 'POST'])
def register():
    db = get_db()

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # verifica se l'utente esiste già
        if db.users.find_one({"username": username}):
            flash("Username già esistente", "danger")
            return redirect(url_for('main.register'))

        hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')
        db.users.insert_one({"username": username, "password": hashed_pw})
        flash("Registrazione completata. Ora puoi effettuare il login!", "success")
        return redirect(url_for('main.login'))

    return render_template('register.html')


@main.route('/login', methods=['GET', 'POST'])
def login():
    db = get_db()

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = db.users.find_one({"username": username})
        print("Utente nel DB:", user)

        if user and bcrypt.check_password_hash(user['password'], password):
            session['username'] = username
            flash("Login effettuato!", "success")
            return redirect(url_for('main.user_profile', username=username))
        else:
            flash("Credenziali non valide", "danger")

    return render_template('login.html')

@main.route('/logout')
def logout():
    session.pop('username', None)
    flash("Logout effettuato.", "info")
    return redirect(url_for('main.login'))

@main.route('/user/<username>')
def user_profile(username):
    db = get_db()
    user = db.users.find_one({"username": username})
    if not user:
        return "Utente non trovato", 404

    watchlist = db.user_anime_list.find({"username": username})
    enriched_watchlist = []
    for entry in watchlist:
        anime = db.anime.find_one({"anime_id": entry["anime_id"]})
        if anime:
            entry["anime_info"] = anime
            enriched_watchlist.append(entry)

    return render_template("user.html", username=username, watchlist=enriched_watchlist)

@main.route('/account')
def account():
    if 'username' not in session:
        flash("Devi essere loggato!", "danger")
        return redirect(url_for('main.login'))

    db = get_db()
    user = db.users.find_one({"username": session['username']})
    if not user:
        flash("Utente non trovato!", "danger")
        return redirect(url_for('main.login'))

    return render_template('account.html', user=user)

@main.route('/account/edit', methods=['GET', 'POST'])
def edit_account():
    if 'username' not in session:
        flash("Devi essere loggato!", "danger")
        return redirect(url_for('main.login'))

    db = get_db()
    user = db.users.find_one({"username": session['username']})

    if request.method == 'POST':
        email = request.form['email']
        gender = request.form['gender']
        location = request.form['location']
        birth_date = request.form['birth_date']

        db.users.update_one(
            {"username": session['username']},
            {"$set": {
                "email": email,
                "gender": gender,
                "location": location,
                "birth_date": birth_date
            }}
        )
        flash("Dati aggiornati con successo!", "success")
        return redirect(url_for('main.account'))

    return render_template('edit_account.html', user=user)
