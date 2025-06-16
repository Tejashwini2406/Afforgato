import os
from urllib.parse import quote_plus

class Config:
    # MariaDB Configuration
    DB_HOST = 'localhost'
    DB_PORT = 3306
    DB_NAME = 'afforgato_cafe'
    DB_USER = 'afforgato_user'
    DB_PASSWORD = 'wini'
    
    # SQLAlchemy URI for MariaDB
    SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://{DB_USER}:{quote_plus(DB_PASSWORD)}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
    
    # Other settings
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here'
    UPLOAD_FOLDER = 'static/uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024 