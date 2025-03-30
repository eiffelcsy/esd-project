from flask import Flask

# Create the absolute simplest Flask app
app = Flask(__name__)

@app.route('/')
def home():
    return "Hello! This is working."

if __name__ == '__main__':
    print("*" * 50)
    print("STARTING FLASK TEST SERVER")
    print("If you see this, the server is starting")
    print("Try opening: http://127.0.0.1:5000/")
    print("*" * 50)
    # Use the default port 5000 since it might be a port conflict
    app.run(host='127.0.0.1', port=5000, debug=True) 