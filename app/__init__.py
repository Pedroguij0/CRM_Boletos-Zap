from flask import Flask
from app.db.connection import init_db
from app.routes.api import api_bp
from app.routes.views import views_bp
from app.scheduler.tasks import iniciar_scheduler

def create_app():
    app = Flask(__name__, template_folder='templates', static_folder='static')
    app.config['SECRET_KEY'] = 'boletoszap_secret_key_123'
    init_db()
    app.register_blueprint(api_bp)
    app.register_blueprint(views_bp)
    iniciar_scheduler(app)
    return app
