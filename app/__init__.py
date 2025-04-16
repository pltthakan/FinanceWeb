from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_caching import Cache

# Uygulama oluşturuluyor ve yapılandırılıyor
app = Flask(__name__)
app.config.from_object('app.config.Config')

db = SQLAlchemy(app)
migrate = Migrate(app, db)
cache = Cache(app)
cache.clear()

# Modeller, yardımcı fonksiyonlar, admin ve route’leri içe aktarın
from app import models, utils, admin
from app.routes import main, auth, comments, profile

# Blueprint’leri içe aktarın ve kaydedin
from app.routes.main import assets_bp
app.register_blueprint(assets_bp)
