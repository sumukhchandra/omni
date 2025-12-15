import os
import sys
import json
from flask import Flask, request, jsonify
from flask_cors import CORS

# Ensure ai_core and executor are in path
sys.path.append(os.path.join(os.path.dirname(__file__), 'ai_core'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'executor'))

try:
    from pipeline import get_pipeline
    from actions import execute_verbose_command
except ImportError as e:
    print(f"Error importing modules: {e}")
    sys.exit(1)

app = Flask(__name__)
CORS(app)

# Initialize the AI Pipeline
pipeline = get_pipeline()

# --- Database Setup ---
from dotenv import load_dotenv
import os
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
try:
    from pymongo import MongoClient
    from pymongo import MongoClient, errors
    from werkzeug.security import generate_password_hash, check_password_hash
    
    # tlsAllowInvalidCertificates=True required for some Windows environments with SSL issues
    mongo_client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000, tlsAllowInvalidCertificates=True) 
    try:
        # Check connection
        mongo_client.admin.command('ismaster')
        print("[DB] Connected to MongoDB Atlas")
        db = mongo_client['bluemind_auth']
        users_collection = db['users']
    except errors.ServerSelectionTimeoutError as err:
        print(f"[DB] Connection failed: IP not whitelisted or Network Error. Details: {err}")
        users_collection = None
except Exception as e:
    print(f"[DB] Generic Error connecting to MongoDB: {e}")
    users_collection = None

# --- Auth Routes ---

@app.route('/api/register', methods=['POST'])
def register():
    if users_collection is None:
        return jsonify({"error": "Database not available"}), 503

    data = request.json
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"error": "Email and password required"}), 400

    # Check if user exists
    if users_collection.find_one({"_id": email}):
        return jsonify({"error": "User already exists"}), 409

    # Hash password
    hashed_pw = generate_password_hash(password)

    user_doc = {
        "_id": email,
        "email": email,
        "password": hashed_pw, # Storing hash
        "name": email.split('@')[0]
    }

    try:
        users_collection.insert_one(user_doc)
        return jsonify({
            "id": email,
            "email": email,
            "name": user_doc["name"]
        }), 201
    except Exception as e:
        print(f"Error registering user: {e}")
        return jsonify({"error": "Registration failed"}), 500

@app.route('/api/login', methods=['POST'])
def login():
    if users_collection is None:
        return jsonify({"error": "Database not available"}), 503
        
    data = request.json
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"error": "Email and password required"}), 400

    user = users_collection.find_one({"_id": email})
    
    if user and check_password_hash(user['password'], password):
        return jsonify({
            "id": user['email'],
            "email": user['email'],
            "name": user['name']
        }), 200
    else:
        return jsonify({"error": "Invalid email or password"}), 401

@app.route('/api/chat', methods=['POST'])
def chat():
    """
    Unified chat endpoint.
    Strict Flow: Input -> AI Plan -> Agent Execute -> Output
    """
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No data provided"}), 400
            
        message = data.get('message', '')
        print(f"[MAIN] Received message: {message}")
        
        # 1. AI BRAIN: Process request (Spell Check + Expand)
        # pipeline returns: success, logs, action_data, strict_instruction_string
        success, logs, action_data, instructions_str = pipeline.processed_request(text_input=message)
        
        execution_logs = []
        response_text = ""

        # 2. AGENT EXECUTOR: Execute the verbose steps
        if instructions_str:
            print(f"[MAIN] Generated Plan: {instructions_str}")
            response_text += f"Plan: {instructions_str}\n\nExecution:\n"
            
            # Execute
            step_logs = execute_verbose_command(instructions_str)
            execution_logs.extend(step_logs)
            
            # Format execution logs for display
            for i, log in enumerate(step_logs):
                response_text += f"{i+1}. {log}\n"
        else:
            response_text = "I could not generate a plan for that command."

        return jsonify({
            "text": response_text,
            "logs": logs + execution_logs,
            "action": action_data
        })

    except Exception as e:
        import traceback
        trace = traceback.format_exc()
        print(f"Error in chat endpoint: {trace}")
        return jsonify({"error": str(e), "trace": trace}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok", "pipeline": "active" if pipeline else "inactive"})

if __name__ == '__main__':
    print("Starting Unified Backend Server on port 5000...")
    app.run(host='0.0.0.0', port=5000, debug=True)
