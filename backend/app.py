from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from config import Config
from database import db, migrate
import os

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    CORS(app)
    jwt = JWTManager(app)
    
    # Import models to ensure they're registered
    from models import user, voucher, session, plan
    
    # Import route blueprints after app context is established
    from routes.auth import auth_bp
    from routes.users import users_bp
    from routes.vouchers import vouchers_bp
    from routes.sessions import sessions_bp
    from routes.isp import isp_bp
    from routes.dashboard import dashboard_bp
    
    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(users_bp, url_prefix='/api/users')
    app.register_blueprint(vouchers_bp, url_prefix='/api/vouchers')
    app.register_blueprint(sessions_bp, url_prefix='/api/sessions')
    app.register_blueprint(isp_bp, url_prefix='/api/isp')
    app.register_blueprint(dashboard_bp, url_prefix='/api/dashboard')
    
    @app.route('/api/health')
    def health_check():
        return jsonify({'status': 'healthy', 'service': 'ByteBill Backend'})
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)
