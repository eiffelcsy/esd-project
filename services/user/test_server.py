from flask import Flask, jsonify

# Create a minimal test app
app = Flask(__name__)

@app.route('/')
def hello():
    return jsonify({"message": "Hello World!"})

@app.route('/test')
def test():
    return jsonify({"status": "Test endpoint working"})

if __name__ == '__main__':
    print("Starting test server on port 5002...")
    # Use a different port to avoid conflicts
    app.run(host='0.0.0.0', port=5002, debug=True) 