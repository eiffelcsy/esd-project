from flask import request, jsonify
from app.models import db, Recommendation
from app.openai_service import get_recommendations
from datetime import datetime
import json

def register_routes(app):
    # Get recommendations based on trip details
    @app.route('/api/recommendations', methods=['POST'])
    def create_recommendation():
        data = request.get_json()
        
        required_fields = ['trip_id', 'destination', 'start_date', 'end_date']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        try:
            start_date = datetime.fromisoformat(data['start_date']).date()
            end_date = datetime.fromisoformat(data['end_date']).date()
        except ValueError:
            return jsonify({'error': 'Invalid date format. Use ISO format (YYYY-MM-DD)'}), 400
        
        # Get recommendations from OpenAI
        recommendations = get_recommendations(data['destination'], start_date, end_date)
        
        # Check if a recommendation for this trip already exists
        existing_recommendation = Recommendation.query.filter_by(trip_id=data['trip_id']).first()
        
        if existing_recommendation:
            # Update existing record
            existing_recommendation.recommendations = recommendations
            db.session.commit()
            return jsonify(existing_recommendation.to_dict()), 200
        else:
            # Create new recommendation record
            new_recommendation = Recommendation(
                trip_id=data['trip_id'],
                recommendations=recommendations
            )
            
            db.session.add(new_recommendation)
            db.session.commit()
            
            return jsonify(new_recommendation.to_dict()), 201
    
    # Get recommendation by trip ID
    @app.route('/api/recommendations/<trip_id>', methods=['GET'])
    def get_recommendation(trip_id):
        recommendation = Recommendation.query.filter_by(trip_id=trip_id).first()
        
        if not recommendation:
            return jsonify({'error': 'Recommendation not found'}), 404
            
        return jsonify(recommendation.to_dict()), 200
        
    # Get all recommendations
    @app.route('/api/recommendations', methods=['GET'])
    def get_recommendations_list():
        recommendations = Recommendation.query.all()
        return jsonify([recommendation.to_dict() for recommendation in recommendations]), 200 