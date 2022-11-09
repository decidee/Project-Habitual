from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from random_word import RandomWords
from flask_bcrypt import Bcrypt


db = SQLAlchemy()
migrate = Migrate()
rand = RandomWords()
bcrypt = Bcrypt()
login_manager = LoginManager()

