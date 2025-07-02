from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.extensions import mongo
from flask_bcrypt import Bcrypt
from bson import ObjectId
from datetime import datetime

bcrypt = Bcrypt()

users_bp = Blueprint('users', __name__, template_folder='templates')

@users_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        gender = request.form['gender']
        location = request.form['location']
        birth_date = request.form['birth_date']

        if mongo.db.users.find_one({"username": username}):
            flash("Username già esistente", "danger")
            return redirect(url_for('users.register'))

        hashed_pw = bcrypt.generate_password_hash(password, rounds=10).decode('utf-8')
        nuovo_utente = {
            "_id": ObjectId(),
            "username": username,
            "gender": gender,
            "location": location,
            "birth_date": birth_date,
            "join_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "last_online": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "password": hashed_pw,
            "email": email
        }
        mongo.db.users.insert_one(nuovo_utente)

        flash("Registrazione completata. Ora puoi effettuare il login!", "success")
        return redirect(url_for('users.login'))

    return render_template('register.html')

@users_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = mongo.db.users.find_one({"username": username})

        if user and bcrypt.check_password_hash(user['password'], password):
            session['username'] = username
            flash("Login effettuato!", "success")
            return redirect(url_for('users.user_profile', username=username))
        else:
            flash("Credenziali non valide", "danger")

    return render_template('login.html')

@users_bp.route('/logout')
def logout():
    session.pop('username', None)
    flash("Logout effettuato.", "info")
    return redirect(url_for('users.login'))

@users_bp.route('/user/<username>')
def user_profile(username):
    user = mongo.db.users.find_one({"username": username})
    if not user:
        return "Utente non trovato", 404
    
    user_id = user["_id"]

    watchlist = mongo.db.user_anime_list.aggregate([
         {"$match": {"user_id": user_id}},
        {"$lookup": {
            "from": "anime",
            "localField": "anime_id",
            "foreignField": "_id",
            "as": "anime_info"
        }},
         {"$unwind": {"path": "$anime_info", "preserveNullAndEmptyArrays": True}} 
    ])

    enriched_watchlist = list(watchlist)

    return render_template("user.html", username=username, watchlist=enriched_watchlist)

@users_bp.route('/account')
def account():
    if 'username' not in session:
        flash("Devi essere loggato!", "danger")
        return redirect(url_for('users.login'))

    user = mongo.db.users.find_one({"username": session['username']})
    if not user:
        flash("Utente non trovato!", "danger")
        return redirect(url_for('users.login'))

    return render_template('account.html', user=user)

@users_bp.route('/account/edit', methods=['GET', 'POST'])
def edit_account():
    if 'username' not in session:
        flash("Devi essere loggato!", "danger")
        return redirect(url_for('users.login'))

    user = mongo.db.users.find_one({"username": session['username']})

    if request.method == 'POST':
        email = request.form['email']
        gender = request.form['gender']
        location = request.form['location']
        birth_date = request.form['birth_date']

        mongo.db.users.update_one(
            {"username": session['username']},
            {"$set": {
                "email": email,
                "gender": gender,
                "location": location,
                "birth_date": birth_date
            }}
        )
        flash("Dati aggiornati con successo!", "success")
        return redirect(url_for('users.account'))

    return render_template('edit_account.html', user=user)
