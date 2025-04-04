from flask import request, jsonify
from app.models import db, Recommendation
from app.openai_service import get_recommendations, get_openai_client
from datetime import datetime
import json
import logging

# Configure logging
logger = logging.getLogger(__name__)

def register_routes(app):
    # Get recommendations based on trip details
    @app.route('/api/recommendations', methods=['POST'])
    def create_recommendation():
        logger.info("Received direct API request to create recommendation")
        data = request.get_json()
        
        required_fields = ['trip_id', 'destination', 'start_date', 'end_date']
        for field in required_fields:
            if field not in data:
                logger.error(f"Missing required field: {field}")
                return jsonify({'error': f'{field} is required'}), 400
        
        try:
            start_date = datetime.fromisoformat(data['start_date']).date()
            end_date = datetime.fromisoformat(data['end_date']).date()
        except ValueError as e:
            logger.error(f"Invalid date format: {e}")
            return jsonify({'error': 'Invalid date format. Use ISO format (YYYY-MM-DD)'}), 400
        
        # Get recommendations from OpenAI
        logger.info(f"Calling OpenAI for recommendations for trip_id={data['trip_id']}, destination={data['destination']}")
        recommendations = get_recommendations(data['destination'], start_date, end_date)
        logger.info(f"Received recommendations from OpenAI for trip_id={data['trip_id']}")
        
        # Check if a recommendation for this trip already exists
        existing_recommendation = Recommendation.query.filter_by(trip_id=data['trip_id']).first()
        
        if existing_recommendation:
            # Update existing record
            logger.info(f"Updating existing recommendation for trip_id={data['trip_id']}")
            existing_recommendation.recommendations = recommendations
            db.session.commit()
            return jsonify(existing_recommendation.to_dict()), 200
        else:
            # Create new recommendation record
            logger.info(f"Creating new recommendation for trip_id={data['trip_id']}")
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
        logger.info(f"Fetching recommendation for trip_id={trip_id}")
        recommendation = Recommendation.query.filter_by(trip_id=trip_id).first()
        
        if not recommendation:
            logger.warning(f"Recommendation not found for trip_id={trip_id}")
            return jsonify({'error': 'Recommendation not found'}), 404
            
        logger.info(f"Found recommendation for trip_id={trip_id}")
        return jsonify(recommendation.to_dict()), 200
        
    # Get all recommendations
    @app.route('/api/recommendations', methods=['GET'])
    def get_recommendations_list():
        logger.info("Fetching all recommendations")
        recommendations = Recommendation.query.all()
        logger.info(f"Found {len(recommendations)} recommendations")
        return jsonify([recommendation.to_dict() for recommendation in recommendations]), 200
        
    # Test endpoint for OpenAI integration
    @app.route('/api/test/openai', methods=['GET'])
    def test_openai():
        logger.info("Testing OpenAI integration")
        client = get_openai_client()
        
        if not client:
            logger.error("OpenAI client initialization failed")
            return jsonify({
                'status': 'error',
                'message': 'Failed to initialize OpenAI client - check API key configuration'
            }), 500
            
        try:
            # Test with minimal request
            test_destination = request.args.get('destination', 'Paris')
            test_start_date = datetime.now().date()
            test_end_date = test_start_date
            
            logger.info(f"Testing OpenAI with destination: {test_destination}")
            
            # Call OpenAI service
            recommendations = get_recommendations(test_destination, test_start_date, test_end_date)
            
            # Check if there's an error in the response
            if 'error' in recommendations:
                logger.error(f"OpenAI test error: {recommendations['error']}")
                return jsonify({
                    'status': 'error',
                    'message': 'Error from OpenAI API',
                    'details': recommendations
                }), 500
                
            logger.info("OpenAI integration test successful")
            return jsonify({
                'status': 'success',
                'message': 'OpenAI integration test successful',
                'sample_data': recommendations
            }), 200
            
        except Exception as e:
            logger.error(f"OpenAI test error: {e}")
            return jsonify({
                'status': 'error',
                'message': f'Error testing OpenAI integration: {str(e)}'
            }), 500
            
    # Test endpoint for RabbitMQ connectivity
    @app.route('/api/test/rabbitmq', methods=['GET'])
    def test_rabbitmq():
        logger.info("Testing RabbitMQ connectivity")
        from app.message_broker import connect_to_rabbitmq
        
        try:
            # Try to connect to RabbitMQ
            connection, channel = connect_to_rabbitmq()
            
            # Declare the queues to verify connectivity
            request_queue = 'recommendation_requests'
            response_queue = 'recommendation_responses'
            
            channel.queue_declare(queue=request_queue, durable=True)
            channel.queue_declare(queue=response_queue, durable=True)
            
            # Close the connection
            connection.close()
            
            logger.info("RabbitMQ connectivity test successful")
            return jsonify({
                'status': 'success',
                'message': 'Successfully connected to RabbitMQ',
                'queues_declared': [request_queue, response_queue]
            }), 200
            
        except Exception as e:
            logger.error(f"RabbitMQ test error: {e}")
            return jsonify({
                'status': 'error',
                'message': f'Error connecting to RabbitMQ: {str(e)}'
            }), 500 