import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    # SQLALCHEMY_DATABASE_URI = (
    # 'mssql+pyodbc://esign_user:12345@DESKTOP-D36DLIS\\SQLEXPRESS/Esign_db'
    # '?driver=ODBC+Driver+17+for+SQL+Server'
    # )
    SQLALCHEMY_DATABASE_URI = 'sqlite:///../instance/app.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # File upload configuration
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'uploads')
    ALLOWED_DOCUMENT_EXTENSIONS = {'pdf', 'docx', 'doc'}
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size

    # Email configuration
    MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'smtp.gmail.com'
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')

    # Flask URL generation for background threads
    SERVER_NAME = os.environ.get('SERVER_NAME') or '127.0.0.1:8000'
    PREFERRED_URL_SCHEME = os.environ.get('PREFERRED_URL_SCHEME') or 'http'

