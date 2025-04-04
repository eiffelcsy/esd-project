import json
import logging
import os
import traceback
from app.models import Recommendation

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class RecommendationService:
    @staticmethod
    def get_recommendations(trip_data):
        """
        Get recommendations for a trip from the database.
        Recommendations are requested via RabbitMQ message broker
        and stored in the database when received.
        """
        try:
            trip_id = trip_data['tripId']
            logger.info(f"Looking up recommendations for trip_id: {trip_id}")
            
            # Query the database for recommendations
            recommendation = Recommendation.query.filter_by(trip_id=trip_id).first()
            
            if recommendation:
                logger.info(f"Retrieved recommendations from database for trip_id: {trip_id}")
                return True, recommendation.to_dict()
            else:
                logger.info(f"No recommendations found for trip_id: {trip_id}. Recommendations will be processed asynchronously.")
                
                # Request recommendations via message broker if not found
                try:
                    from app import message_broker
                    if message_broker and message_broker.connection and message_broker.connection.is_open:
                        # Format data for recommendation service
                        destination = trip_data.get('destination', '')
                        start_date = trip_data.get('startDate', '')
                        end_date = trip_data.get('endDate', '')
                        
                        # Send recommendation request
                        message_broker.send_recommendation_request(
                            trip_id=trip_id,
                            destination=destination,
                            start_date=start_date,
                            end_date=end_date
                        )
                        logger.info(f"Sent recommendation request for trip_id: {trip_id}")
                    else:
                        logger.warning("Message broker not available, cannot request recommendations")
                except Exception as e:
                    logger.error(f"Error requesting recommendations via message broker: {e}")
                    logger.error(traceback.format_exc())
                
                return False, {"message": "Recommendations are being processed asynchronously and will be available soon."}
        except Exception as e:
            logger.error(f"Error in get_recommendations: {e}")
            logger.error(traceback.format_exc())
            return False, {"error": f"Error getting recommendations: {str(e)}"}
    
    @staticmethod
    def retrieve_recommendations(trip_id):
        """Retrieve recommendations for a specific trip from the database."""
        try:
            logger.info(f"Retrieving recommendations for trip_id: {trip_id}")
            
            recommendation = Recommendation.query.filter_by(trip_id=trip_id).first()
            
            if not recommendation:
                logger.warning(f"No recommendations found in database for trip_id: {trip_id}")
                
                # Try to request recommendations if not found
                try:
                    from app import message_broker
                    if message_broker and message_broker.connection and message_broker.connection.is_open:
                        # Get trip details from itinerary
                        from app.models import Itinerary
                        itinerary = Itinerary.query.get(trip_id)
                        
                        if itinerary:
                            # Send recommendation request
                            message_broker.send_recommendation_request(
                                trip_id=trip_id,
                                destination=itinerary.destination,
                                start_date=itinerary.start_date.isoformat(),
                                end_date=itinerary.end_date.isoformat()
                            )
                            logger.info(f"Sent recommendation request for trip_id: {trip_id}")
                except Exception as e:
                    logger.error(f"Error requesting recommendations via message broker: {e}")
                    logger.error(traceback.format_exc())
                
                return False, {"message": "No recommendations found for this trip. They may still be processing."}
            
            logger.info(f"Retrieved recommendations from database for trip_id: {trip_id}")
            return True, recommendation.to_dict()
        except Exception as e:
            logger.error(f"Error in retrieve_recommendations: {e}")
            logger.error(traceback.format_exc())
            return False, {"error": f"Error retrieving recommendations: {str(e)}"} 