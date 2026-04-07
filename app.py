import os
from flask import Flask, redirect, url_for, send_from_directory, request, jsonify
from flask_jwt_extended import JWTManager, verify_jwt_in_request, get_jwt_identity
from flask_jwt_extended.exceptions import NoAuthorizationError, InvalidHeaderError, WrongTokenError, RevokedTokenError, FreshTokenRequired, CSRFError
from jwt import ExpiredSignatureError
from flask_cors import CORS
from config import config_by_name
from database.models import db


def create_app(config_name='development'):
    """Application factory pattern."""
    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])

    # Ensure required directories exist
    os.makedirs(app.config.get('UPLOAD_FOLDER', 'uploads'), exist_ok=True)
    os.makedirs(app.config.get('SCREENSHOT_FOLDER', 'screenshots'), exist_ok=True)
    os.makedirs(app.config.get('RECORDING_FOLDER', 'recordings'), exist_ok=True)

    # Initialize extensions
    db.init_app(app)
    jwt = JWTManager(app)
    CORS(app)

    # JWT error handlers - redirect to login for web requests
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        # Check if it's an API request (expects JSON)
        if request.is_json or request.path.startswith('/api/'):
            return jsonify({"msg": "Token has expired"}), 401
        # Web request - redirect to login
        return redirect(url_for('auth.login_page'))

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        if request.is_json or request.path.startswith('/api/'):
            return jsonify({"msg": "Invalid token"}), 401
        return redirect(url_for('auth.login_page'))

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        if request.is_json or request.path.startswith('/api/'):
            return jsonify({"msg": "Authorization required"}), 401
        return redirect(url_for('auth.login_page'))

    @jwt.needs_fresh_token_loader
    def token_not_fresh_callback(jwt_header, jwt_payload):
        if request.is_json or request.path.startswith('/api/'):
            return jsonify({"msg": "Fresh token required"}), 401
        return redirect(url_for('auth.login_page'))

    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwt_payload):
        if request.is_json or request.path.startswith('/api/'):
            return jsonify({"msg": "Token has been revoked"}), 401
        return redirect(url_for('auth.login_page'))

    # Register blueprints
    from routes.auth_routes import auth_bp
    from routes.student_routes import student_bp
    from routes.lecturer_routes import lecturer_bp
    from routes.exam_routes import exam_bp
    from routes.analytics_routes import analytics_bp
    from routes.admin_routes import admin_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(student_bp)
    app.register_blueprint(lecturer_bp)
    app.register_blueprint(exam_bp)
    app.register_blueprint(analytics_bp)
    app.register_blueprint(admin_bp)

    # Root route — serve landing page
    @app.route('/')
    def index():
        return send_from_directory('landing', 'index.html')

    # Serve landing page static assets (style.css, script.js)
    @app.route('/landing/<path:filename>')
    def landing_static(filename):
        return send_from_directory('landing', filename)

    # Serve uploaded files
    @app.route('/uploads/<path:filename>')
    def uploaded_file(filename):
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

    # Serve proctoring screenshots
    @app.route('/screenshots/<path:filename>')
    def screenshot_file(filename):
        return send_from_directory(app.config['SCREENSHOT_FOLDER'], filename)

    # Serve proctoring recordings
    @app.route('/recordings/<path:filename>')
    def recording_file(filename):
        return send_from_directory(app.config['RECORDING_FOLDER'], filename)

    # Initialize database
    from database.db_init import init_database
    init_database(app)

    return app


if __name__ == '__main__':
    env = os.getenv('FLASK_ENV', 'development')
    app = create_app(env)
    app.run(host='0.0.0.0', port=5000, debug=(env == 'development'))
