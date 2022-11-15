from flask import Flask
from flask_qrcode import QRcode
import os
from .Routes.FrontGate import FrontG
from .ext import db, migrate, bcrypt, login_manager


def create_app():
    app = Flask(__name__)
    env_dir = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..'))
    app.config.from_pyfile(f"{env_dir}/.env")

    db.init_app(app)
    migrate.init_app(app,db)
    bcrypt.init_app(app)
    QRcode(app)
    login_manager.init_app(app)
    login_manager.login_view = 'FrontG.login'
    login_manager.login_message_category = 'info'

    app.register_blueprint(FrontG)

    return app