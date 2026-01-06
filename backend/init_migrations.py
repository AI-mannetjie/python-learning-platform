"""
Initialize Flask-Migrate migrations directory
Run this once to set up the migrations folder
"""
from flask_migrate import init, migrate, upgrade
from app import app, db
import os

def initialize_migrations():
    """Initialize migrations if not already initialized"""
    with app.app_context():
        migrations_dir = os.path.join(os.path.dirname(__file__), 'migrations')
        
        if os.path.exists(migrations_dir) and os.path.exists(os.path.join(migrations_dir, 'alembic.ini')):
            print("✅ Migrations already initialized")
            return
        
        print("🔧 Initializing migrations...")
        try:
            # Initialize migrations
            from flask_migrate import Migrate
            migrate_obj = Migrate(app, db)
            
            # This will be done via flask db init command instead
            print("✅ Ready for migrations")
            print("   Run: flask db init")
            print("   Then: flask db migrate -m 'Initial migration'")
            print("   Finally: flask db upgrade")
            
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == '__main__':
    initialize_migrations()
