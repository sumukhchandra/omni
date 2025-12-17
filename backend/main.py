import os
import sys
import json
from flask import Flask, request, jsonify
from flask_cors import CORS

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

try:
    from ai_core.pipeline import get_pipeline
except ImportError as e:
    print(f"Error importing AI Brain: {e}. Fallback to Regex.")
    get_pipeline = None

app = Flask(__name__)
CORS(app)

# Initialize the AI Pipeline
# --- Fallback Logic for when AI is missing ---
# Fallback removed in favor of atom/ai_core integration

# Initialize the AI Pipeline (or Fallback)
pipeline = None
if get_pipeline:
    try:
        pipeline = get_pipeline()
        print("[MAIN] AI Pipeline Loaded successfully.")
    except Exception as e:
        print(f"Failed to initialize pipeline: {e}")

if not pipeline:
    print("[MAIN] Using Fallback Regex Pipeline.")
    pipeline = FallbackPipeline()

# --- Database Setup ---
from dotenv import load_dotenv
import os
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
        
        message = data.get('message', '')
        print(f"[MAIN] Received message: {message}")
        
        # --- MULTI-BRAIN ARCHITECTURE ---
        # 1. ATOM (Rule-Based, Fast)
        atom_plan = None
        atom_data = {}
        atom_logs = []
        if pipeline:
            s, l, d, p = pipeline.processed_request(text_input=message)
            if s and p != "unknown command":
                atom_plan = p
                atom_data = d
                atom_logs = l
        
        # 2. DEEP BRAIN (Generative, Slower)
        deep_plan = None
        deep_data = {}
        deep_logs = []
        if deep_brain:
             s, l, d, p = deep_brain.process_request(message)
             if s:
                 deep_plan = p
                 deep_data = d
                 deep_logs = l

        # 3. THE AGENT SELECTOR (Voting Logic)
        final_plan = None
        final_data = {}
        logs = atom_logs + deep_logs
        
        if atom_plan and not deep_plan:
            final_plan = atom_plan
            final_data = atom_data
            logs.append(f"[SELECTOR] Chosen: ATOM (DeepBrain failed)")
        elif deep_plan and not atom_plan:
            final_plan = deep_plan
            final_data = deep_data
            logs.append(f"[SELECTOR] Chosen: DEEP BRAIN (Atom failed)")
        elif atom_plan and deep_plan:
            # Conflict Resolution
            # Atom is preferred for System Control (Speed)
            # Deep Brain is preferred for Conversation (Richness)
            if atom_data.get('action') in ["system", "media"]:
                final_plan = atom_plan
                final_data = atom_data
                logs.append(f"[SELECTOR] Chosen: ATOM (Preferred for System Control)")
            elif "hello" in message.lower():
                final_plan = deep_plan # Let the LLM be polite
                final_data = deep_data
                logs.append(f"[SELECTOR] Chosen: DEEP BRAIN (Preferred for Conversation)")
            else:
                final_plan = atom_plan # Default to speed
                logs.append(f"[SELECTOR] Chosen: ATOM (Default optimized path)")
        else:
            final_plan = None
            logs.append(f"[SELECTOR] Both Brains failed.")

        instructions_str = final_plan
        action_data = final_data
        success = True if final_plan else False
            
        execution_logs = []
        response_text = ""

        # 2. AGENT EXECUTOR: Execute the verbose steps
        if instructions_str and instructions_str != "unknown command":
            print(f"[MAIN] Generated Plan: {instructions_str}")
            response_text += f"Plan: {instructions_str}\n\nExecution:\n"
            
            # Execute
            step_logs = execute_verbose_command(instructions_str)
            execution_logs.extend(step_logs)
            
            # Format execution logs for display
            for i, log in enumerate(step_logs):
                response_text += f"{i+1}. {log}\n"
        else:
            # Check if action_data has info (like Time/Date)
            if action_data.get("action") == "info":
                 texto = action_data.get("text", "")
                 response_text = texto
                 logs.append(f"Info response: {texto}")
            else:
                 response_text = "I'm listening, but I didn't understand that command."

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
