import os
import sys
import unittest
from datetime import datetime, timedelta, UTC
import json

# Add the project root to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Now we can import from app
from app import create_app, db
from app.models import Trip

class TestTripManagement(unittest.TestCase):
    def setUp(self):
        print("\n=== Setting up test environment ===")
        try:
            self.app = create_app(testing=True)
            self.client = self.app.test_client()
            with self.app.app_context():
                db.create_all()
            print("✓ Test database initialized")
        except Exception as e:
            print(f"❌ Failed to set up test environment: {str(e)}")
            raise

    def tearDown(self):
        print("\n=== Cleaning up test environment ===")
        try:
            with self.app.app_context():
                db.session.remove()
                db.drop_all()
            print("✓ Test database cleaned up")
        except Exception as e:
            print(f"❌ Failed to clean up test environment: {str(e)}")
            raise

    def test_health_check(self):
        print("\n=== Testing Health Check Endpoint ===")
        try:
            response = self.client.get('/health')
            self.assertEqual(response.status_code, 200, 
                f"❌ Expected status code 200, but got {response.status_code}")
            
            data = json.loads(response.data)
            try:
                self.assertEqual(data['status'], 'healthy')
                self.assertEqual(data['service'], 'trip-management')
                print(f"✓ Health check response: {data}")
            except AssertionError:
                print(f"❌ Invalid health check response: Expected 'healthy' status and 'trip-management' service")
                print(f"❌ Actual response: {data}")
                raise
        except Exception as e:
            print(f"❌ Health check test failed: {str(e)}")
            raise

    def test_create_trip(self):
        print("\n=== Testing Trip Creation ===")
        # Test data
        start_date = datetime.now(UTC)
        end_date = start_date + timedelta(days=5)
        trip_data = {
            'user_id': 1,
            'city': 'Paris',
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat()
        }
        print(f"Creating trip with data: {trip_data}")

        try:
            # Create trip
            response = self.client.post('/trips',
                                    data=json.dumps(trip_data),
                                    content_type='application/json')
            
            self.assertEqual(response.status_code, 201,
                f"❌ Expected status code 201, but got {response.status_code}")
            
            data = json.loads(response.data)
            try:
                self.assertEqual(data['city'], 'Paris')
                self.assertEqual(data['user_id'], 1)
                print(f"✓ Trip created successfully: {data}")
            except AssertionError:
                print(f"❌ Trip creation response does not match expected data")
                print(f"❌ Expected: city='Paris', user_id=1")
                print(f"❌ Actual: {data}")
                raise
        except Exception as e:
            print(f"❌ Trip creation test failed: {str(e)}")
            if hasattr(e, 'response'):
                print(f"❌ Response: {e.response.data}")
            raise

    def test_get_trip(self):
        print("\n=== Testing Get Trip Details ===")
        try:
            # Create a trip first
            with self.app.app_context():
                trip = Trip(
                    user_id=1,
                    city='London',
                    start_date=datetime.now(UTC),
                    end_date=datetime.now(UTC) + timedelta(days=3)
                )
                db.session.add(trip)
                db.session.commit()
                trip_id = trip.id
                print(f"Created test trip with ID: {trip_id}")

            # Get the trip
            print(f"Fetching trip details for ID: {trip_id}")
            response = self.client.get(f'/trips/{trip_id}')
            
            self.assertEqual(response.status_code, 200,
                f"❌ Expected status code 200, but got {response.status_code}")
            
            data = json.loads(response.data)
            try:
                self.assertEqual(data['city'], 'London')
                self.assertEqual(data['user_id'], 1)
                print(f"✓ Trip details retrieved successfully: {data}")
            except AssertionError:
                print(f"❌ Retrieved trip details do not match expected data")
                print(f"❌ Expected: city='London', user_id=1")
                print(f"❌ Actual: {data}")
                raise
        except Exception as e:
            print(f"❌ Get trip test failed: {str(e)}")
            if hasattr(e, 'response'):
                print(f"❌ Response: {e.response.data}")
            raise

    def test_get_user_trips(self):
        print("\n=== Testing Get User Trips ===")
        try:
            # Create multiple trips for a user
            with self.app.app_context():
                user_id = 1
                trips = [
                    Trip(
                        user_id=user_id,
                        city='Rome',
                        start_date=datetime.now(UTC),
                        end_date=datetime.now(UTC) + timedelta(days=3)
                    ),
                    Trip(
                        user_id=user_id,
                        city='Berlin',
                        start_date=datetime.now(UTC) + timedelta(days=10),
                        end_date=datetime.now(UTC) + timedelta(days=15)
                    )
                ]
                db.session.add_all(trips)
                db.session.commit()
                print(f"Created test trips for user {user_id}: Rome and Berlin")

            # Get all trips for the user
            print(f"Fetching all trips for user {user_id}")
            response = self.client.get(f'/users/{user_id}/trips')
            
            self.assertEqual(response.status_code, 200,
                f"❌ Expected status code 200, but got {response.status_code}")
            
            data = json.loads(response.data)
            try:
                self.assertEqual(len(data), 2,
                    f"❌ Expected 2 trips, but got {len(data)}")
                cities = [trip['city'] for trip in data]
                self.assertIn('Rome', cities)
                self.assertIn('Berlin', cities)
                print(f"✓ Retrieved {len(data)} trips for user: {cities}")
            except AssertionError as e:
                print(f"❌ Retrieved trips do not match expected data")
                print(f"❌ Expected cities: ['Rome', 'Berlin']")
                print(f"❌ Actual cities: {cities}")
                raise
        except Exception as e:
            print(f"❌ Get user trips test failed: {str(e)}")
            if hasattr(e, 'response'):
                print(f"❌ Response: {e.response.data}")
            raise

if __name__ == '__main__':
    print("\n=== Starting Trip Management Tests ===")
    try:
        unittest.main(verbosity=2)
    except Exception as e:
        print(f"\n❌ Tests failed with error: {str(e)}")
        sys.exit(1) 