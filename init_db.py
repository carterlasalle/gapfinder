from gapfinder import create_app
from models import db, User
from werkzeug.security import generate_password_hash
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_database():
    app = create_app()
    with app.app_context():
        db.create_all()
        logger.info("Database tables created.")
        if not User.query.filter_by(username='admin').first():
            admin_user = User(username='admin', password_hash=generate_password_hash('admin123'))
            db.session.add(admin_user)
            db.session.commit()
            logger.info("Admin user created.")
        else:
            logger.info("Admin user already exists.")

if __name__ == '__main__':
    init_database()
