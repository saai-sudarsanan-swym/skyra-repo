from flask import Blueprint
from .health import health_bp
from .generate import generate_bp

def register_routes(app):
    app.register_blueprint(health_bp)
    app.register_blueprint(generate_bp)