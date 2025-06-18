from flask import Blueprint, render_template, request, jsonify

bp = Blueprint('main', __name__)

@bp.route("/")
def index():
    return render_template("index.html")

@bp.route("/api/plants")
def get_plants():
    stage = request.args.get("stage")
    country = request.args.get("country")
    # Replace this with DB query
    return jsonify({
        "stage": stage,
        "country": country,
        "plants": ["Neem", "Tulsi"],
        "molecules": ["Curcumin"]
    })
