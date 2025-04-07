from flask import Flask, jsonify
from flask_cors import CORS
import os
from app.models import db
from app.routes import register_routes


app = Flask(__name__)
# Enable CORS for all domains and routes
CORS(app, supports_credentials=True)

# Configure the database
database_url = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@calendar-db:5432/calendar_db')
app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database
db.init_app(app)

# Register routes
register_routes(app)

# Error handler for all exceptions
@app.errorhandler(Exception)
def handle_error(error):
    print(f"Error occurred: {str(error)}")
    return jsonify({
        "error": "Internal server error",
        "message": str(error)
    }), 500

# Health check
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "service": "calendar"}), 200

# Create tables if they don't exist
with app.app_context():
    try:
        db.create_all()
        print("Database tables created successfully")
    except Exception as e:
        print(f"Error creating database tables: {e}")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5004, debug=True) 