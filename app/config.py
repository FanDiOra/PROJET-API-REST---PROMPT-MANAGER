import os

class Config:
    DATABASE_URI = os.getenv('DATABASE_URI', 'postgresql://fatee:fatee26ODC@localhost/projet_api_rest_bd')
    SECRET_KEY = os.getenv('SECRET_KEY', 'default_secret_key')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'default_jwt_secret_key')
