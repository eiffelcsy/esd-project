# This file is intentionally minimal to mark directory as Python package

# Trip management microservice package
from app.models import db

# Initialize message_broker as None, it will be set in app.py
message_broker = None

__all__ = ['db', 'message_broker'] 