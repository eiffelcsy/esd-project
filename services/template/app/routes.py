from flask import request, jsonify
from app.models import db, Item

def register_routes(app):
    # Create a new item
    @app.route('/api/items', methods=['POST'])
    def create_item():
        data = request.get_json()
        
        if not data or 'name' not in data:
            return jsonify({'error': 'Name is required'}), 400
        
        new_item = Item(
            name=data['name'],
            description=data.get('description')
        )
        
        db.session.add(new_item)
        db.session.commit()
        
        return jsonify(new_item.to_dict()), 201
    
    # Get all items
    @app.route('/api/items', methods=['GET'])
    def get_items():
        items = Item.query.all()
        return jsonify([item.to_dict() for item in items]), 200
    
    # Get a specific item by ID
    @app.route('/api/items/<int:item_id>', methods=['GET'])
    def get_item(item_id):
        item = Item.query.get_or_404(item_id)
        return jsonify(item.to_dict()), 200
    
    # Update an item
    @app.route('/api/items/<int:item_id>', methods=['PUT'])
    def update_item(item_id):
        item = Item.query.get_or_404(item_id)
        data = request.get_json()
        
        if 'name' in data:
            item.name = data['name']
        if 'description' in data:
            item.description = data['description']
        
        db.session.commit()
        
        return jsonify(item.to_dict()), 200
    
    # Delete an item
    @app.route('/api/items/<int:item_id>', methods=['DELETE'])
    def delete_item(item_id):
        item = Item.query.get_or_404(item_id)
        
        db.session.delete(item)
        db.session.commit()
        
        return jsonify({'message': f'Item {item_id} deleted successfully'}), 200 