from app import app, db
from app.models import User
import sys

print("Checking database connection and tables...")

with app.app_context():
    try:
        # Check connection by executing a simple query
        result = db.session.execute("SELECT 1")
        print("✅ Database connection successful!")
        
        # Check if the users table exists
        result = db.session.execute("SHOW TABLES")
        tables = [row[0] for row in result]
        print(f"Tables in database: {tables}")
        
        if 'users' in tables:
            # Count users
            count = db.session.query(User).count()
            print(f"✅ Users table exists with {count} records")
        else:
            print("❌ Users table does not exist")
            
            # Try to create tables again
            print("Attempting to create tables...")
            db.create_all()
            print("Tables created!")
            
            # Verify again
            result = db.session.execute("SHOW TABLES")
            tables = [row[0] for row in result]
            print(f"Tables in database after creation: {tables}")
        
    except Exception as e:
        print(f"❌ Database error: {e}")
        sys.exit(1)

print("Database check complete!") 