from flask import Flask, jsonify
from flask_cors import CORS
import os
from app.models import db
from app.routes import register_routes
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Configure database
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DB_URL', 'postgresql://postgres:postgres@finance-db:5432/finance_db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database
db.init_app(app)

# Register routes
register_routes(app)

# Health check
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "service": "finance"}), 200

# Create tables if they don't exist
with app.app_context():
    try:
        # First check if the tables exist
        db.create_all()
        
        # Then check for and add the payees_json column if needed
        from sqlalchemy import text
        try:
            logger.info("Checking if payees_json column exists")
            # Check if column exists
            result = db.session.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name='expenses' AND column_name='payees_json'"))
            column_exists = bool(result.fetchone())
            
            if not column_exists:
                logger.info("Adding payees_json column to expenses table")
                # Add the column if it doesn't exist
                db.session.execute(text("ALTER TABLE expenses ADD COLUMN payees_json TEXT"))
                
                # Update existing records
                logger.info("Updating existing expenses with payees_json data")
                db.session.execute(text("""
                    UPDATE expenses
                    SET payees_json = CASE 
                        WHEN payee_id IS NULL OR payee_id = 'all' THEN '["all"]'
                        ELSE json_build_array(payee_id)::TEXT
                    END
                    WHERE payees_json IS NULL
                """))
                
                db.session.commit()
                logger.info("Database schema update completed successfully")
        except Exception as e:
            logger.error(f"Error updating schema: {str(e)}")
            db.session.rollback()
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5008)