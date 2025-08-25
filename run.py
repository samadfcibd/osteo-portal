from flask import Flask
from app.routes import bp
from flask_cors import CORS

app = Flask(__name__, static_folder="app/static", template_folder="app/templates")
app.register_blueprint(bp)
CORS(app)

if __name__ == "__main__":
    app.run(debug=True)
