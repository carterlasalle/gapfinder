from gapfinder import create_app
from models import db, User
from werkzeug.security import generate_password_hash
import logging
from supabase import create_client, Client
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

supabase: Client = create_client(os.environ.get('SUPABASE_URL'), os.environ.get('SUPABASE_KEY'))

def init_database():
    app = create_app()
    with app.app_context():
        response = supabase.table('users').select('username').eq('username', 'admin').execute()
        if not response.data:
            admin_user = {
                'username': 'admin',
                'password_hash': generate_password_hash('admin123')
            }
            supabase.table('users').insert(admin_user).execute()
            logger.info("Admin user created.")
        else:
            logger.info("Admin user already exists.")

if __name__ == '__main__':
    init_database()
