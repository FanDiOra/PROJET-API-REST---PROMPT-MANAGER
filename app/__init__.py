from flask import Flask
from .config import Config
from flask_jwt_extended import JWTManager

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    jwt = JWTManager(app)

    from app.routes.user import bp as user_bp
    from app.routes.group import bp as group_bp
    from app.routes.prompt import bp as prompt_bp

    app.register_blueprint(user_bp, url_prefix='/api')
    app.register_blueprint(group_bp, url_prefix='/api')
    app.register_blueprint(prompt_bp, url_prefix='/api')

    return app
