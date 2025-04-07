# This file is intentionally minimal to mark directory as Python package

# Itinerary microservice package
from app.models import db

# message_broker is initialized in app.py and assigned here later
message_broker = None

__all__ = ['db', 'message_broker'] 