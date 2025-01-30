from flask import Flask, render_template, request, redirect, url_for, flash
from pymongo import MongoClient
import os

# Configuration Flask
app = Flask(__name__)
app.secret_key = "secret_key_for_flask"

# Connexion à MongoDB
client = MongoClient("mongodb://localhost:27017")  # Remplacez par votre URI si vous utilisez MongoDB Atlas
db = client["games_database"]  # Nom de la base de données
collection = db["games"]       # Nom de la collection

# Dossier pour stocker les fichiers
UPLOAD_FOLDER_GUIDES = "static/guides/"
UPLOAD_FOLDER_IMAGES = "static/images/"
os.makedirs(UPLOAD_FOLDER_GUIDES, exist_ok=True)
os.makedirs(UPLOAD_FOLDER_IMAGES, exist_ok=True)

# Page d'accueil
@app.route("/")
def index():
    return render_template("index.html")

# Ajouter un jeu par un utilisateur
@app.route("/add_game", methods=["GET", "POST"])
def add_game():
    if request.method == "POST":
        # Récupérer les données du formulaire
        name = request.form.get("name")
        description = request.form.get("description")

        # Upload des fichiers
        guide = request.files.get("guide")
        affiche = request.files.get("affiche")

        # Sauvegarde des fichiers
        guide_path = None
        affiche_path = None
        if guide:
            guide_path = os.path.join(UPLOAD_FOLDER_GUIDES, guide.filename)
            guide.save(guide_path)
        if affiche:
            affiche_path = os.path.join(UPLOAD_FOLDER_IMAGES, affiche.filename)
            affiche.save(affiche_path)

        # Ajouter le jeu sans scoring dans MongoDB
        collection.insert_one({
            "name": name,
            "description": description,
            "guide": guide_path,
            "affiche": affiche_path,
            "scoring": None  # Scoring sera ajouté plus tard par le professeur
        })
        flash("Jeu ajouté avec succès !", "success")
        return redirect(url_for("list_games"))

    return render_template("add_game.html")

# Ajouter ou modifier le scoring par le professeur
@app.route("/add_scoring/<game_id>", methods=["GET", "POST"])
def add_scoring(game_id):
    from bson.objectid import ObjectId

    game = collection.find_one({"_id": ObjectId(game_id)})

    if not game:
        flash("Jeu introuvable.", "danger")
        return redirect(url_for("list_games"))

    if request.method == "POST":
        # Récupérer les données du formulaire de scoring
        scoring = {
            "fond": int(request.form.get("fond")),
            "originalite": int(request.form.get("originalite")),
            "cohesion": int(request.form.get("cohesion")),
            "esthetique": int(request.form.get("esthetique")),
            "fun": int(request.form.get("fun"))
        }

        # Mettre à jour le scoring dans MongoDB
        collection.update_one({"_id": ObjectId(game_id)}, {"$set": {"scoring": scoring}})
        flash("Scoring ajouté/modifié avec succès !", "success")
        return redirect(url_for("list_games"))

    return render_template("add_scoring.html", game=game)

# Afficher les jeux
@app.route("/games")
def list_games():
    games = list(collection.find({}))
    return render_template("games.html", games=games)

# Supprimer un jeu
@app.route("/delete_game/<game_id>")
def delete_game(game_id):
    from bson.objectid import ObjectId
    result = collection.delete_one({"_id": ObjectId(game_id)})
    if result.deleted_count > 0:
        flash("Jeu supprimé avec succès.", "success")
    else:
        flash("Erreur lors de la suppression.", "danger")
    return redirect(url_for("list_games"))

if __name__ == "__main__":
    app.run(debug=True)
