from gapfinder import app, db
from models import User
from werkzeug.security import generate_password_hash
from flask_migrate import upgrade

def init_database():
    with app.app_context():
        upgrade()
        if not User.query.filter_by(username='admin').first():
            admin_user = User(username='admin', password_hash=generate_password_hash('admin123'))
            db.session.add(admin_user)
            db.session.commit()

if __name__ == '__main__':
    init_database()