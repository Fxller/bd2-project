from flask import Blueprint, render_template, request
from app.extensions import mongo

main_bp = Blueprint('main', __name__, template_folder='templates')

@main_bp.route('/')
def home():
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
    anime_list = mongo.db.anime.find(query).skip(skip).limit(per_page)
    total_anime = mongo.db.anime.count_documents(query)
    total_pages = (total_anime + per_page - 1) // per_page
    generi = mongo.db.anime.distinct("genre")
    
    return render_template('home.html', anime=anime_list, total_pages=total_pages, current_page=page, generi=generi)

@main_bp.route('/dashboard')
def dashboard():
    avg_score = mongo.db.anime.aggregate([
        {"$match": {"score": {"$ne": None}}},
        {"$group": {"_id": None, "media_score": {"$avg": "$score"}}}
    ])
    avg_score_list = list(avg_score)
    avg_score_value = round(avg_score_list[0]["media_score"], 2) if avg_score_list else "N/D"

    total_users = mongo.db.users.count_documents({})
    total_watchlist = mongo.db.user_anime_list.count_documents({})

    top_anime = mongo.db.user_anime_list.aggregate([
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
