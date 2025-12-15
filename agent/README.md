# X_AI — Cross-Platform AI That Controls Your Entire Screen

X_AI is a cross-platform automation system that allows an AI agent to **see your screen, understand it, and perform actions on any application** exactly the way a human would: by clicking, typing, searching elements on screen, opening apps, playing music, performing WhatsApp video calls, and executing complex workflows.

Users can control the computer using:

1. **Natural language commands** (via the web UI)  
2. **Voice commands with wake-word "bro"** (macOS & Windows support)  
3. **High-level instructions like:**  
   - “bro press command tab”  
   - “open whatsapp and call vinnu video call”  
   - “play hanuman song in spotify”  
   - “press add button on the top of the screen”

X_AI uses screen OCR, template matching, OS automation APIs, and AI command parsing to execute actions exactly as a human would.

---

## Features

### ✔ Full Cross-Platform Support  
Works on:
- macOS  
- Windows  
- Linux (automation subset)

### ✔ AI-Powered Screen Interaction  
The agent can:
- take screenshots  
- locate UI elements  
- click, type, scroll  
- press any keyboard shortcut  
- interact with apps by searching pixels or icons

### ✔ Voice Wake-Word Assistant  
Wake word: **"bro"**  
Examples:
- "bro open spotify"
- "bro press command plus tab"
- "bro do WhatsApp video call with vinnu"

### ✔ Web UI Command Console  
Visit:
http://127.0.0.1:5005/ui/index.html

yaml
Copy code
Enter commands directly.

---

## Folder Structure

X_AI/
│
├── everything_server.py # Main server that automates screen actions
├── background_listener.py # Voice assistant (wake-word + speech recognition)
├── ui/index.html # Web UI for sending text commands
├── requirements.txt # Python dependencies
├── models/ # Vosk speech recognition models
├── screenshots/ # Runtime screenshots (ignored via .gitignore)
└── venv/ # Virtual environment (ignored)

yaml
Copy code

---

# Installation Guide (macOS, Windows, Linux)

## 1. Clone the Repository

```bash
git clone https://github.com/siddikoushik/X_AI.git
cd X_AI
2. Create and Activate Virtual Environment
macOS / Linux
bash
Copy code
python3 -m venv venv
source venv/bin/activate
Windows
powershell
Copy code
python -m venv venv
venv\Scripts\activate
3. Install Dependencies
bash
Copy code
pip install --upgrade pip
pip install -r requirements.txt
4. Install Vosk Model for Voice Commands
Create models folder:

bash
Copy code
mkdir -p models
Download the official model (use browser if curl fails):

Download link:
https://alphacephei.com/vosk/models/vosk-small-en-us-0.15.zip

After downloading:

bash
Copy code
unzip vosk-small-en-us-0.15.zip -d models
Final structure should be:

bash
Copy code
models/vosk-small-en-us-0.15/
5. macOS Required Permissions
Go to:

System Settings → Privacy & Security →
Screen Recording → enable Terminal + Python

Accessibility → enable Terminal + Python

Restart terminal after enabling.

Running the System
Option 1 — Run Only the Automation Server (no voice)
bash
Copy code
cd X_AI
source venv/bin/activate
export EXECUTE=1        # actually click/type
python3 -u everything_server.py
Windows:

powershell
Copy code
set EXECUTE=1
python -u everything_server.py
Open UI in browser:

arduino
Copy code
http://127.0.0.1:5005/ui/index.html
Enter commands like:

sql
Copy code
open spotify
play hanuman song in spotify
open whatsapp and call vinnu video call
press add button
Option 2 — Run the Voice Assistant (wake word "bro")
Terminal 1 — Start automation engine:

bash
Copy code
cd X_AI
source venv/bin/activate
export EXECUTE=1
python3 -u everything_server.py
Terminal 2 — Start voice engine:

bash
Copy code
cd X_AI
source venv/bin/activate
python3 background_listener.py
Say:

pgsql
Copy code
bro open spotify
bro press command plus tab
bro do video call with vinnu in whatsapp
bro press add button on the top of the screen
How Commands Work (Architecture)
pgsql
Copy code
VOICE / TEXT COMMAND
        ↓
Command Parser (NLU)
        ↓
Screenshot → OCR → Template Matching
        ↓
Action Plan Generator
        ↓
OS Automation Layer
        ↓
Click / Type / Open App / Search UI Element
Examples of Supported Commands
App Control
arduino
Copy code
open spotify
open whatsapp
open chrome
Keyboard Automation
arduino
Copy code
press command plus tab
press control plus shift plus t
press enter
press escape
Visual Automation
arduino
Copy code
press add button on top of the screen
click green play button in spotify
scroll down
find search bar and click it
Multi-Step Automation
sql
Copy code
open whatsapp and call vinnu video call
play hanuman song in spotify
Updating the Repository
bash
Copy code
git add .
git commit -m "Update"
git push origin main
If remote rejects push:

bash
Copy code
git pull --rebase origin main
git push origin main
Troubleshooting
UI Not Loading
Check server:

nginx
Copy code
python3 -u everything_server.py
You must see:

nginx
Copy code
SERVER STARTED → http://127.0.0.1:5005
Voice Model Not Found
Place model in:

bash
Copy code
X_AI/models/vosk-small-en-us-0.15
Automation Not Clicking
Check:

Accessibility permissions

Screen Recording permissions

EXECUTE=1

Contribute
Pull requests are welcome.
You may contribute new:

command mappings

automation modules

voice features

screen-understanding models

License
MIT License.

Author
Siddi Koushik
X_AI Project
2025
