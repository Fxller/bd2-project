from flask import Blueprint, render_template, request
from app.extensions import mongo

main_bp = Blueprint('main', __name__, template_folder='templates')

@main_bp.route('/')
def home():
    query = {}

    genre = request.args.get('genre')
    min_score = request.args.get('min_score')
    page = int(request.args.get('page', 1))
    per_page = 12

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

@main_bp.route('/ricerca_live')
def ricerca_live():
    titolo = request.args.get('title', '')
    genere = request.args.get('genre', '')
    min_score = request.args.get('min_score', '')

    query = {}
    if titolo:
        query["title"] = {"$regex": titolo, "$options": "i"}
    if genere:
        query["genre"] = {"$regex": genere, "$options": "i"}
    if min_score:
        try:
            query["score"] = {"$gte": float(min_score)}
        except ValueError:
            pass

    anime_filtrati = mongo.db.anime.find(query).limit(20)

    html_card = ""
    for a in anime_filtrati:
        generi = ', '.join(a['genre']) if isinstance(a['genre'], list) else a['genre']
        html_card += f"""
        <div class="col-md-4 col-lg-3 mb-4">
            <div class="card h-100 anime-card">
                <img src="{a.get('image_url', '/static/default_anime.jpg')}" class="card-img-top anime-img" alt="Locandina">
                <div class="card-body d-flex flex-column justify-content-between">
                    <h5 class="card-title text-center">{a['title']}</h5>
                    <p><strong>Tipo:</strong> {a.get('type', '')}</p>
                    <p><strong>Punteggio:</strong> {a.get('score', '')}</p>
                    <p><strong>Genere:</strong> {generi}</p>
                    <a href="/anime/{a['_id']}" class="btn btn-primary mt-2 w-100">Dettagli</a>
                </div>
            </div>
        </div>
        """

    return html_card

