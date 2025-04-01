from flask import request, jsonify, session
from app.models import db, User
from werkzeug.security import generate_password_hash

def register_routes(app):
    # Register a new user
    @app.route('/api/users/register', methods=['POST'])
    def register():
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['username', 'email']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Check if username or email already exists
        if User.query.filter_by(username=data['username']).first():
            return jsonify({'error': 'Username already taken'}), 400
        
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'Email already registered'}), 400
        
        # Create new user without password
        new_user = User(
            username=data['username'],
            email=data['email'],
            first_name=data.get('first_name'),
            last_name=data.get('last_name'),
            profile_picture=data.get('profile_picture')
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        return jsonify({
            'message': 'User registered successfully',
            'user': new_user.to_dict(),
            'user_id': new_user.id
        }), 201
    
    # User login
    @app.route('/api/users/login', methods=['POST'])
    def login():
        data = request.get_json()
        
        # Validate required fields
        if not data or 'username' not in data or 'password' not in data:
            return jsonify({'error': 'Username and password are required'}), 400
        
        # Find user by username
        user = User.query.filter_by(username=data['username']).first()
        
        # Check if user exists and password is correct
        if not user or not user.check_password(data['password']):
            return jsonify({'error': 'Invalid username or password'}), 401
        
        return jsonify({
            'message': 'Login successful',
            'user': user.to_dict(),
            'user_id': user.id
        }), 200
    
    # Get user profile
    @app.route('/api/users/profile/<int:user_id>', methods=['GET'])
    def get_profile(user_id):
        user = User.query.get_or_404(user_id)
        return jsonify(user.to_dict()), 200
    
    # Update user profile
    @app.route('/api/users/profile/<int:user_id>', methods=['PUT'])
    def update_profile(user_id):
        user = User.query.get_or_404(user_id)
        
        data = request.get_json()
        
        # Update user fields if provided
        if 'first_name' in data:
            user.first_name = data['first_name']
        if 'last_name' in data:
            user.last_name = data['last_name']
        if 'profile_picture' in data:
            user.profile_picture = data['profile_picture']
        
        # Update password if provided
        if 'password' in data:
            user.password_hash = generate_password_hash(data['password'])
        
        db.session.commit()
        
        return jsonify({
            'message': 'Profile updated successfully',
            'user': user.to_dict()
        }), 200
    
    # Get user by ID (public profile)
    @app.route('/api/users/<int:user_id>', methods=['GET'])
    def get_user(user_id):
        user = User.query.get_or_404(user_id)
        return jsonify(user.to_public_dict()), 200
    
    # Search users by username
    @app.route('/api/users/search', methods=['GET'])
    def search_users():
        query = request.args.get('q', '')
        if not query:
            return jsonify({'error': 'Query parameter is required'}), 400
        
        users = User.query.filter(User.username.ilike(f'%{query}%')).all()
        return jsonify([user.to_public_dict() for user in users]), 200 