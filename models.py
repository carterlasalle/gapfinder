from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))  # Increased from 128 to 256

    def __repr__(self):
        return f'<User {self.username}>'

def init_db(app):
    db.init_app(app)
    migrate.init_app(app, db)
