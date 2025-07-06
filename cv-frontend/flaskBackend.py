from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app, origins=['http://localhost:3000'])

latest_improvements = None
latest_job_rankings = None

def clear_endpoints():
    """Clear both endpoints by setting global variables to empty objects"""
    global latest_improvements, latest_job_rankings
    latest_improvements = {}
    latest_job_rankings = {}
    print("Endpoints cleared successfully")

@app.route('/api/improvements', methods=['POST'])
def post_improvements():
    global latest_improvements
    latest_improvements = request.json
    return jsonify({"message": "Improvements stored successfully"}), 200

@app.route('/api/improvements', methods=['GET'])
def get_improvements():
    return jsonify(latest_improvements or {})

@app.route('/api/jobrankings', methods=['POST'])
def post_job_rankings():
    global latest_job_rankings
    latest_job_rankings = request.json
    return jsonify({"message": "Job rankings stored successfully"}), 200

@app.route('/api/jobrankings', methods=['GET'])
def get_job_rankings():
    if latest_job_rankings is None:
        return jsonify([])
    return jsonify(latest_job_rankings)

if __name__ == '__main__':
    print("Starting Flask backend...")
    print("Clearing endpoints...")
    clear_endpoints()
    print("Starting server on port 5002...")
    app.run(port=5002)