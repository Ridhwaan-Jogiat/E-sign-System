# clear_db.py
from app import create_app  # Import your app factory function
from app.models import db, User, Document, Signature  # Import db and models
import os

UPLOAD_DIRS = [
    os.path.join(os.path.dirname(__file__), 'static', 'uploads', 'signatures'),
    os.path.join(os.path.dirname(__file__), 'static', 'uploads', 'documents'),
]

def clear_database():
    # Create the Flask app instance
    app = create_app()

    with app.app_context():  # Required for database operations
        print("🗑️ Dropping all tables...")
        db.drop_all()  # Deletes all tables
        print("🔄 Recreating tables...")
        db.create_all()  # Recreates empty tables
        print("✅ Database cleared successfully!")

    # Clear static uploaded files
    for dir_path in UPLOAD_DIRS:
        if os.path.exists(dir_path):
            for filename in os.listdir(dir_path):
                file_path = os.path.join(dir_path, filename)
                try:
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                except Exception as e:
                    print(f"Error deleting {file_path}: {e}")
    print("🧹 Static uploaded files cleared!")


if __name__ == "__main__":
    clear_database()