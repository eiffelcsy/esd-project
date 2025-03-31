from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import sys
import time
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
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
    password_hash = db.Column(db.String(200), nullable=False)
    
    def __init__(self, username, password):
        self.username = username
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

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
    
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({'error': 'Username and password are required'}), 400
    
    # Check if username already exists
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Username already taken'}), 400
    
    # Create new user
    new_user = User(
        username=data['username'],
        password=data['password']
    )
    
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({
        'message': 'User registered successfully',
        'user_id': new_user.id,
        'username': new_user.username
    }), 201

# Login
@app.route('/api/users/login', methods=['POST'])
def login():
    data = request.get_json()
    
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({'error': 'Username and password are required'}), 400
    
    # Find user by username
    user = User.query.filter_by(username=data['username']).first()
    
    # Check if user exists and password is correct
    if not user or not user.check_password(data['password']):
        return jsonify({'error': 'Invalid username or password'}), 401
    
    return jsonify({
        'message': 'Login successful',
        'user_id': user.id,
        'username': user.username
    }), 200

# Get user
@app.route('/api/users/<int:user_id>')
def get_user(user_id):
    user = User.query.get_or_404(user_id)
    return jsonify({
        'user_id': user.id,
        'username': user.username
    }), 200

# Search users
@app.route('/api/users/search')
def search_users():
    query = request.args.get('q', '')
    users = User.query.filter(User.username.like(f'%{query}%')).all()
    return jsonify([{
        'user_id': user.id,
        'username': user.username
    } for user in users]), 200

if __name__ == '__main__':
    print("*" * 50)
    print("Starting User Service on port 5005")
    print("Try opening: http://127.0.0.1:5005/")
    print("*" * 50)
    app.run(host='0.0.0.0', port=5005, debug=True) 