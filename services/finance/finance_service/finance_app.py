from flask import Flask
from flask_cors import CORS
from models import db
from routes import bp
import os

def create_app():
    app = Flask(__name__)
    CORS(app)
    
    # Configure database
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DB_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_POOL_SIZE'] = int(os.getenv('DB_POOL_SIZE', 5))
    app.config['SQLALCHEMY_MAX_OVERFLOW'] = int(os.getenv('DB_MAX_OVERFLOW', 10))
    
    db.init_app(app)
    
    with app.app_context():
        db.create_all()
    
    app.register_blueprint(bp)
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000)