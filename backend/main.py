import os
import sys
import json
import subprocess
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

# Ensure root path is accessible to import siblings
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(os.path.join(ROOT_DIR, 'atom'))
sys.path.append(os.path.join(ROOT_DIR, 'agent'))
sys.path.append(ROOT_DIR) # Allow importing 'AI' folder

# Decoupled Imports to allow partial functionality
try:
    from executor.actions import execute_verbose_command
except ImportError as e:
    print(f"Error importing executor: {e}")
    execute_verbose_command = None

# Import Deep Brain Shim
try:
    from AI.deep_brain_shim import DeepBrainShim
    deep_brain = DeepBrainShim()
    print("[MAIN] Deep Brain Loaded.")
except Exception as e:
    print(f"Error loading Deep Brain: {e}")
    deep_brain = None

app = Flask(__name__)
CORS(app)

# Initialize the AI Pipeline (4-Brain Architecture)
finalizer = None
try:
    from ai_core.brains.finalizer_brain import FinalizerBrain
    finalizer = FinalizerBrain()
    print("[MAIN] Finalizer Brain Loaded (4-Brain Architecture).")
except ImportError as e:
    print(f"Failed to initialize Finalizer Brain: {e}")
    finalizer = None

# --- Database Setup ---
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")
try:
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

# Global Agent Process Handle
AGENT_PROCESS = None

@app.route('/api/agent/status', methods=['GET'])
def agent_status():
    global AGENT_PROCESS
    if AGENT_PROCESS and AGENT_PROCESS.poll() is None:
        return jsonify({"status": "running", "pid": AGENT_PROCESS.pid})
    return jsonify({"status": "stopped"})

@app.route('/api/agent/start', methods=['POST'])
def start_agent():
    global AGENT_PROCESS
    if AGENT_PROCESS and AGENT_PROCESS.poll() is None:
        return jsonify({"status": "already_running", "pid": AGENT_PROCESS.pid})
    
    try:
        # Launch atom/main.py as a separate process
        atom_script = os.path.join(ROOT_DIR, 'atom', 'main.py')
        
        # Redirect stdout/stderr to a log file for debugging
        log_file = open(os.path.join(ROOT_DIR, 'agent_debug.log'), 'w')
        
        AGENT_PROCESS = subprocess.Popen(
            [sys.executable, atom_script], 
            cwd=ROOT_DIR,
            stdout=log_file,
            stderr=subprocess.STDOUT
        )
        return jsonify({"status": "started", "pid": AGENT_PROCESS.pid})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/agent/stop', methods=['POST'])
def stop_agent():
    global AGENT_PROCESS
    if AGENT_PROCESS and AGENT_PROCESS.poll() is None:
        AGENT_PROCESS.terminate()
        AGENT_PROCESS = None
        return jsonify({"status": "stopped"})
    return jsonify({"status": "not_running"})

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
        
        # --- 4-BRAIN ARCHITECTURE ---
        # 1. FINALIZER BRAIN (The Orchestrator)
        finalizer_response = None
        success = False
        execution_logs = []
        action_data = {}
        logs = [] # Initialize logs for the new structure
        response_text = ""

        if finalizer:
            # Finalizer executes the whole flow: Knowledge -> Vision -> Control
            # It returns (success, response_string)
            success, response_text = finalizer.execute(message)
            logs.append(f"[FINALIZER] Execution Success: {success}")
            logs.append(f"[FINALIZER] Response: {response_text}")
            
        else:
             response_text = "I am lobotomized (Finalizer Brain Missing)."
             logs.append("[ERROR] Finalizer Brain not loaded.")

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
    return jsonify({"status": "ok", "pipeline": "active" if finalizer else "inactive"})

if __name__ == '__main__':
    print("Starting Unified Backend Server on port 5000...")
    app.run(host='0.0.0.0', port=5000, debug=True)
