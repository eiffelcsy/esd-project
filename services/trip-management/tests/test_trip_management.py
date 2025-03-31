import unittest
from datetime import datetime, timedelta
from app import app, db
from app.models import Trip
import json

class TestTripManagement(unittest.TestCase):
    def setUp(self):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['TESTING'] = True
        self.client = app.test_client()
        with app.app_context():
            db.create_all()

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_health_check(self):
        response = self.client.get('/health')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'healthy')
        self.assertEqual(data['service'], 'trip-management')

    def test_create_trip(self):
        # Test data
        start_date = datetime.utcnow()
        end_date = start_date + timedelta(days=5)
        trip_data = {
            'user_id': 1,
            'city': 'Paris',
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat()
        }

        # Create trip
        response = self.client.post('/trips',
                                  data=json.dumps(trip_data),
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data['city'], 'Paris')
        self.assertEqual(data['user_id'], 1)

    def test_get_trip(self):
        # Create a trip first
        with app.app_context():
            trip = Trip(
                user_id=1,
                city='London',
                start_date=datetime.utcnow(),
                end_date=datetime.utcnow() + timedelta(days=3)
            )
            db.session.add(trip)
            db.session.commit()
            trip_id = trip.id

        # Get the trip
        response = self.client.get(f'/trips/{trip_id}')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['city'], 'London')
        self.assertEqual(data['user_id'], 1)

    def test_get_user_trips(self):
        # Create multiple trips for a user
        with app.app_context():
            user_id = 1
            trips = [
                Trip(
                    user_id=user_id,
                    city='Rome',
                    start_date=datetime.utcnow(),
                    end_date=datetime.utcnow() + timedelta(days=3)
                ),
                Trip(
                    user_id=user_id,
                    city='Berlin',
                    start_date=datetime.utcnow() + timedelta(days=10),
                    end_date=datetime.utcnow() + timedelta(days=15)
                )
            ]
            db.session.add_all(trips)
            db.session.commit()

        # Get all trips for the user
        response = self.client.get(f'/users/{user_id}/trips')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data), 2)
        cities = [trip['city'] for trip in data]
        self.assertIn('Rome', cities)
        self.assertIn('Berlin', cities)

if __name__ == '__main__':
    unittest.main() 