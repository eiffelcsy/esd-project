from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import sys
import time
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

# Add more verbose output at startup
print("=== Starting User Service ===")

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Configure the database
database_url = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@user-db:5432/user_db')
app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
print("✅ Database configured")

# Initialize the database
db = SQLAlchemy(app)
print("✅ SQLAlchemy initialized")

# Simple User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    
    def __init__(self, username, email):
        self.username = username
        self.email = email

print("✅ User model defined")

# Create tables with retry mechanism
def create_tables_with_retry(max_retries=5, retry_delay=5):
    for attempt in range(max_retries):
        try:
            with app.app_context():
                db.create_all()
            print("✅ Database tables created successfully")
            return True
        except Exception as e:
            print(f"❌ Attempt {attempt + 1}/{max_retries} failed to create database tables: {e}")
            if attempt < max_retries - 1:
                print(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                print("❌ Failed to create database tables after all retries")
                return False

# Create tables
create_tables_with_retry()

# Root route for basic testing
@app.route('/')
def home():
    return "User service is running. Try /health for status check."

# Health check
@app.route('/health')
def health_check():
    return jsonify({"status": "healthy", "service": "user"}), 200

# Register user
@app.route('/api/users/register', methods=['POST'])
def register():
    data = request.get_json()
    
    if not data or 'username' not in data or 'email' not in data:
        return jsonify({'error': 'Username and email are required'}), 400
    
    # Check if username already exists
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Username already taken'}), 400
        
    # Check if email already exists
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already registered'}), 400
    
    # Create new user
    new_user = User(
        username=data['username'],
        email=data['email']
    )
    
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({
        'message': 'User registered successfully',
        'user_id': new_user.id,
        'username': new_user.username,
        'email': new_user.email
    }), 201

# Get user
@app.route('/api/users/<int:user_id>')
def get_user(user_id):
    user = User.query.get_or_404(user_id)
    return jsonify({
        'user_id': user.id,
        'username': user.username,
        'email': user.email
    }), 200

# Search users
@app.route('/api/users/search')
def search_users():
    query = request.args.get('q', '')
    users = User.query.filter(User.username.like(f'%{query}%')).all()
    return jsonify([{
        'user_id': user.id,
        'username': user.username,
        'email': user.email
    } for user in users]), 200

if __name__ == '__main__':
    print("*" * 50)
    print("Starting User Service on port 5005")
    print("Try opening: http://127.0.0.1:5005/")
    print("*" * 50)
    app.run(host='0.0.0.0', port=5005, debug=True) 