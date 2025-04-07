import os
import sys
import json
import logging
import psycopg2
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Get database connection details from environment variables
DB_HOST = os.getenv('DB_HOST', 'recommendation-db')
DB_PORT = os.getenv('DB_PORT', '5432')
DB_NAME = os.getenv('DB_NAME', 'recommendation_db')
DB_USER = os.getenv('DB_USER', 'postgres')
DB_PASS = os.getenv('DB_PASS', 'postgres')

def get_db_connection():
    """Create a connection to the database"""
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASS
        )
        logger.info(f"Connected to database {DB_NAME} on {DB_HOST}")
        return conn
    except Exception as e:
        logger.error(f"Error connecting to database: {e}")
        return None

def list_recommendations():
    """List all recommendations in the database"""
    conn = get_db_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, trip_id, created_at, updated_at 
            FROM recommendations 
            ORDER BY id
        """)
        rows = cursor.fetchall()
        
        if not rows:
            logger.info("No recommendations found in the database")
            return True
        
        logger.info(f"Found {len(rows)} recommendations in the database:")
        for row in rows:
            logger.info(f"ID: {row[0]}, Trip ID: {row[1]}, Created: {row[2]}, Updated: {row[3]}")
        
        return True
    except Exception as e:
        logger.error(f"Error listing recommendations: {e}")
        return False
    finally:
        conn.close()

def delete_recommendation(trip_id):
    """Delete a recommendation by trip_id"""
    conn = get_db_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM recommendations WHERE trip_id = %s", (trip_id,))
        recommendation = cursor.fetchone()
        
        if not recommendation:
            logger.info(f"No recommendation found for trip_id: {trip_id}")
            return True
        
        cursor.execute("DELETE FROM recommendations WHERE trip_id = %s", (trip_id,))
        conn.commit()
        
        logger.info(f"Deleted recommendation for trip_id: {trip_id}")
        return True
    except Exception as e:
        logger.error(f"Error deleting recommendation: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def purge_all_recommendations():
    """Purge all recommendations from the database"""
    conn = get_db_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM recommendations")
        count = cursor.fetchone()[0]
        
        confirm = input(f"Are you sure you want to delete all {count} recommendations? (yes/no): ")
        if confirm.lower() != "yes":
            logger.info("Operation cancelled")
            return False
        
        cursor.execute("DELETE FROM recommendations")
        conn.commit()
        
        logger.info(f"Purged {count} recommendations from the database")
        return True
    except Exception as e:
        logger.error(f"Error purging recommendations: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def print_help():
    """Print help information"""
    print("Usage: python migrate_recommendations.py [command]")
    print("Commands:")
    print("  list              - List all recommendations in the database")
    print("  delete <trip_id>  - Delete a recommendation by trip_id")
    print("  purge             - Purge all recommendations from the database")
    print("  help              - Show this help message")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print_help()
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == "list":
        success = list_recommendations()
    elif command == "delete" and len(sys.argv) == 3:
        trip_id = sys.argv[2]
        success = delete_recommendation(trip_id)
    elif command == "purge":
        success = purge_all_recommendations()
    elif command == "help":
        print_help()
        sys.exit(0)
    else:
        print(f"Unknown command: {command}")
        print_help()
        sys.exit(1)
    
    sys.exit(0 if success else 1) 