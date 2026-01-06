import os
from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from dotenv import load_dotenv

from models import db
from routes.auth import auth_bp
from routes.modules import modules_bp
from routes.lessons import lessons_bp
from routes.quizzes import quizzes_bp
from routes.labs import labs_bp
from routes.progress import progress_bp
from routes.admin import admin_bp

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
    'SQLALCHEMY_DATABASE_URI',
    'postgresql://admin:changeme123@db:5432/python_learning'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = 3600  # 1 hour
app.config['JWT_REFRESH_TOKEN_EXPIRES'] = 2592000  # 30 days

# Initialize extensions
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:3000", "http://localhost", "http://localhost:80"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "supports_credentials": True
    }
})
jwt = JWTManager(app)
db.init_app(app)
migrate = Migrate(app, db)

# Register blueprints
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(modules_bp, url_prefix='/api/modules')
app.register_blueprint(lessons_bp, url_prefix='/api/lessons')
app.register_blueprint(quizzes_bp, url_prefix='/api/quizzes')
app.register_blueprint(labs_bp, url_prefix='/api/labs')
app.register_blueprint(progress_bp, url_prefix='/api/progress')
app.register_blueprint(admin_bp, url_prefix='/api/admin')

# Health check endpoint
@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'message': 'Python Learning Platform API is running'
    }), 200

# Root endpoint
@app.route('/', methods=['GET'])
def root():
    return jsonify({
        'message': 'Python Learning Platform API',
        'version': '1.0.0',
        'endpoints': {
            'health': '/api/health',
            'auth': '/api/auth/*',
            'modules': '/api/modules',
            'lessons': '/api/lessons/*',
            'quizzes': '/api/quizzes/*',
            'labs': '/api/labs/*',
            'progress': '/api/progress',
            'admin': '/api/admin/*'
        }
    }), 200

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Resource not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return jsonify({'error': 'Internal server error'}), 500

@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    return jsonify({'error': 'Token has expired'}), 401

@jwt.invalid_token_loader
def invalid_token_callback(error):
    return jsonify({'error': 'Invalid token'}), 401

@jwt.unauthorized_loader
def missing_token_callback(error):
    return jsonify({'error': 'Authorization token is missing'}), 401

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=os.getenv('FLASK_ENV') == 'development')
