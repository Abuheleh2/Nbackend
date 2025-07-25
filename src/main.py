import os
import sys
from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS

# Add the parent directory to the path to allow imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from src.models.user import db
from src.routes.user import user_bp
from src.routes.generate_copy import generate_copy_bp

# Initialize Flask app
app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = '9IpDjXzQ9EgYNMh9pbEkmEk3c-PrhqudOrCGdRIgygA'

# Enable CORS for all routes
CORS(app, origins="*")

# =============================================================
# DATABASE CONFIGURATION - CORRECTED FORMAT
# =============================================================
# IMPORTANT: Database URL must be a single continuous string
# Use SQLite for deployment to avoid PostgreSQL connection issues
import os
if os.getenv('DATABASE_URL'):
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///neonadsai.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db.init_app(app)

# =============================================================
# DATABASE INITIALIZATION WITH ERROR HANDLING
# =============================================================
def initialize_database():
    """Safe database initialization with error handling and logging"""
    try:
        with app.app_context():
            print("Attempting to connect to database...")
            print(f"Using database URL: {app.config['SQLALCHEMY_DATABASE_URI']}")
            
            # Test connection first
            connection = db.engine.connect()
            connection.close()
            print("Database connection successful!")
            
            # Create tables
            db.create_all()
            print("Database tables created successfully")
            
        return True
    except Exception as e:
        print(f"!!! DATABASE INITIALIZATION FAILED !!!")
        print(f"Error: {str(e)}")
        print("Please verify your database configuration")
        return False

# Initialize database tables on startup
with app.app_context():
    try:
        db.create_all()
        print("Database tables created successfully")
    except Exception as e:
        print(f"Database initialization error: {e}")

# =============================================================
# BLUEPRINT REGISTRATION
# =============================================================
app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(generate_copy_bp, url_prefix='/api')

# =============================================================
# HEALTH CHECK ENDPOINT
# =============================================================
@app.route('/health')
def health_check():
    """Endpoint to verify database connectivity"""
    try:
        # Simple database check
        db.session.execute(db.text('SELECT 1'))
        return jsonify({
            'status': 'healthy',
            'database': 'connected',
            'app': 'neonadsai-backend'
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'database': 'connection failed',
            'error': str(e)
        }), 500

# =============================================================
# STATIC FILE SERVING (REACT APP)
# =============================================================
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
        return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return "index.html not found", 404

# =============================================================
# APPLICATION STARTUP
# =============================================================
# Export the app for deployment
__all__ = ['app']
