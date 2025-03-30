import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
from unittest.mock import patch, mock_open
from flask import Flask
from flask_testing import TestCase
from itinerary_service import app, itineraries

class ItineraryServiceTest(TestCase, unittest.TestCase):  # Ensure it inherits from unittest.TestCase
    def create_app(self):
        app.config['TESTING'] = True
        return app

    def setUp(self):
        self.client = self.app.test_client()
        self.trip_id = "test_trip"
        itineraries[self.trip_id] = {
            "tripId": self.trip_id,
            "destination": "Test Destination",
            "startDate": "2023-01-01",
            "endDate": "2023-01-10",
            "dailyActivities": {
                "2023-01-01": [
                    {
                        "time": "10:00",
                        "description": "Test Activity",
                        "location": "Test Location"
                    }
                ]
            }
        }

    def tearDown(self):
        itineraries.clear()

    @patch('itinerary_service.requests.get')
    def test_get_itinerary(self, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            "tripId": self.trip_id,
            "destination": "Test Destination",
            "startDate": "2023-01-01",
            "endDate": "2023-01-10",
            "activities": [
                {
                    "date": "2023-01-01",
                    "time": "10:00",
                    "description": "Test Activity",
                    "location": "Test Location"
                }
            ]
        }
        response = self.client.get(f'/itinerary/{self.trip_id}')
        self.assertEqual(response.status_code, 200)
        self.assertIn("Test Destination", response.json['destination'])

    @patch('itinerary_service.requests.get')
    def test_get_itinerary_not_found(self, mock_get):
        mock_get.return_value.status_code = 404
        response = self.client.get('/itinerary/non_existent_trip')
        self.assertEqual(response.status_code, 404)

    @patch('itinerary_service.requests.post')
    @patch('builtins.open', new_callable=mock_open)
    @patch('os.path.exists', return_value=True)
    def test_export_to_calendar(self, mock_exists, mock_open, mock_post):
        mock_post.return_value.status_code = 200
        response = self.client.post(f'/itinerary/{self.trip_id}/export')
        self.assertEqual(response.status_code, 200)
        self.assertIn('attachment', response.headers['Content-Disposition'])

    def test_add_activity(self):
        new_activity = {
            "date": "2023-01-02",
            "time": "14:00",
            "description": "New Test Activity",
            "location": "New Test Location"
        }
        response = self.client.put(f'/itinerary/{self.trip_id}/activities', json=new_activity)
        self.assertEqual(response.status_code, 200)
        self.assertIn("Activity added successfully", response.json['message'])
        self.assertIn(new_activity, itineraries[self.trip_id]['dailyActivities']['2023-01-02'])

    def test_add_activity_itinerary_not_found(self):
        new_activity = {
            "date": "2023-01-02",
            "time": "14:00",
            "description": "New Test Activity",
            "location": "New Test Location"
        }
        response = self.client.put('/itinerary/non_existent_trip/activities', json=new_activity)
        self.assertEqual(response.status_code, 404)
        self.assertIn("Itinerary not found", response.json['error'])

if __name__ == '__main__':
    unittest.main()
