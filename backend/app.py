from flask import Flask
from src.api.routes import api
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

app.register_blueprint(api, url_prefix='/api')

if __name__ == '__main__':
    app.run(debug=True)