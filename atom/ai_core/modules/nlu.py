import json
import re
try:
    from transformers import T5ForConditionalGeneration, T5Tokenizer
    import torch
except ImportError:
    print("Warning: transformers/torch not found. Using Mock NLU.")
    T5ForConditionalGeneration = None
    T5Tokenizer = None

try:
    from symspellpy import SymSpell
    import pkg_resources
except ImportError:
    print("Warning: symspellpy not found. Spelling correction disabled.")
    SymSpell = None

# --- Base Intent Class ---
class Intent:
    def __init__(self, name):
        self.name = name

    def match(self, text):
        """Returns True if this intent matches the text."""
        raise NotImplementedError

    def extract(self, text):
        """Returns (instruction_string, json_data_dict)."""
        raise NotImplementedError

    def generate_verbose_instruction(self, app, action_type, target, secondary_target=None):
        """Helper to generate the specific verbose instruction format."""
        # Clean Universal Plan (Relies on platform_open_app in Executor)
        if action_type == "play":
            action_desc = f"navigate to search bar then typr {target} then click on the song then play the song"
        elif action_type == "message":
            action_desc = f"navigate to search bar then typr {target} then click on {target} then click on message bar then typr {secondary_target} then click on send"
        elif action_type == "search":
             action_desc = f"navigate to search bar then typr {target} then click on search"
        elif action_type == "call":
            action_desc = f"navigate to search bar then typr {target} then click on {target} then click call"
        elif action_type == "video_call":
            action_desc = f"navigate to search bar then typr {target} then click on {target} then click on video call"
        elif action_type == "order":
            action_desc = f"navigate to search bar then typr {target} then click on {target} then click order"
        elif action_type == "pay":
            action_desc = f"navigate to search bar then typr {target} then click on {target} then click pay then typr {secondary_target} then click pay"
        elif action_type == "navigate":
            action_desc = f"navigate to search bar then typr {target} then click on {target} then start navigation"
        elif action_type == "open":
            action_desc = "" # Just open
        else:
            action_desc = f"perform action on {target}"

        # Logic: "Open App" is sufficient for Executor to handle platform specifics
        if action_desc:
             return f"open {app} then {action_desc}"
        else:
             return f"open {app}"

# --- Specific Intents ---

class MusicIntent(Intent):
    def __init__(self):
        super().__init__("PlayMusic")
        
    def match(self, text):
        return any(k in text for k in ["play", "listen to", "open spotify", "open youtube", "music", "song", "musi", "musc"])

    def extract(self, text):
        # 1. YouTube Specific
        yt_play = re.search(r"(?:play|listen to) (.+) on youtube", text, re.IGNORECASE)
        yt_open = re.search(r"open youtube and (?:play|listen to) (.+)", text, re.IGNORECASE)
        
        if yt_play or yt_open:
            query = yt_play.group(1).strip() if yt_play else yt_open.group(1).strip()
            return (
                self.generate_verbose_instruction("YouTube", "play", query),
                {"action": "play_music", "app": "YouTube", "query": query}
            )

        # 2. Spotify/Generic
        spot_play = re.search(r"(?:play|listen to) (.+) on spotify", text, re.IGNORECASE)
        spot_open = re.search(r"open spotify and (?:play|listen to) (.+)", text, re.IGNORECASE)
        
        # Generic "play X" (Assumes Spotify/Music app)
        generic_play = re.search(r"(?:play|listen to) (.+)$", text, re.IGNORECASE)
        
        song = ""
        if spot_play: song = spot_play.group(1).strip()
        elif spot_open: song = spot_open.group(1).strip()
        elif generic_play:
             potential_song = generic_play.group(1).strip()
             if " on " not in potential_song:
                 song = potential_song

        # Fix for "play song", "play sond", "play music" -> Generic Play/Resume
        # ALSO Handle standalone "music", "song" AND TYPOS "musi"
        text_lower = text.lower().strip()
        if song in ["song", "music", "audio", "sond", "musi", "musc"] or text_lower in ["music", "song", "musi", "musc"]:
             return (
                 self.generate_verbose_instruction("Spotify", "play", "music"),
                 {"action": "play_music", "app": "Spotify", "song": ""} # Empty/Generic implies resume/shuffle
             )
            
        if song:
            return (
                self.generate_verbose_instruction("Spotify", "play", song),
                {"action": "play_music", "app": "Spotify", "song": song}
            )
            
        # Fallback: If we matched "play" but extracted nothing specific, just open Spotify/Play Music.
        return (
             self.generate_verbose_instruction("Spotify", "play", "music"),
             {"action": "play_music", "app": "Spotify", "song": ""}
        )
        return None

# ... (omitted intermediate classes, they remain unchanged) ...

# --- Router ---

class IntentRouter:
    def __init__(self):
        # Order matters!
        self.intents = [
            SolverIntent(),
            GreetingIntent(),
            HumorIntent(),        # Registered
            SystemIntent(),
            MusicIntent(),        # Moved UP (Priority over Media/Generic)
            MediaIntent(),
            DateIntent(),
            ProductivityIntent(), 
            PaymentIntent(),      
            CommerceIntent(),
            NavigationIntent(),
            SearchIntent(),
            SocialIntent(),       
            GenericActionIntent() 
        ]

    def parse(self, text):
        lower_text = text.lower().strip()
        for intent in self.intents:
            if intent.match(lower_text):
                result = intent.extract(lower_text)
                if result:
                    print(f"[IntentRouter] Matched: {intent.name}")
                    return result
        return "unknown command", {"action": "unknown"}


class SocialIntent(Intent):
    def __init__(self):
        super().__init__("Social")

    def match(self, text):
        keywords = ["message", "send", "tell", "call", "video call"]
        return any(k in text for k in keywords)

    def extract(self, text):
        # 1. Instagram
        insta_msg = re.search(r"message (.+) on instagram", text)
        if insta_msg:
            contact = insta_msg.group(1).strip()
            return (
                self.generate_verbose_instruction("Instagram", "message", contact, "hello"),
                {"action": "send_message", "app": "Instagram", "contact": contact}
            )

        # 2. WhatsApp / Generic Message
        msg_pattern = re.search(r"send (.+) to (.+)", text) # "send hello to mom"
        tell_pattern = re.search(r"tell (\w+) (.+)", text)   # "tell mom hello"
        generic_msg = re.search(r"message (.+) to (.+)", text) # "message hello to mom"
        
        # Check specific "send money" patterns first to avoid conflict (handled by PaymentIntent usually, 
        # but if PaymentIntent misses, we don't want to send "100 rupees" as a text message usually.
        # However, for now, we rely on IntentRouter order.)

        contact = None
        msg = None
        
        if generic_msg:
            msg = generic_msg.group(1).strip()
            contact = generic_msg.group(2).strip()
        elif msg_pattern:
            # Check if it's GPay first? Router logic handles priority.
            if " on gpay" in text: return None # Defer to PaymentIntent
            msg = msg_pattern.group(1).strip()
            raw_contact = msg_pattern.group(2).strip()
            contact = raw_contact.split(" on ")[0]
        elif tell_pattern:
            contact = tell_pattern.group(1).strip()
            msg = tell_pattern.group(2).strip()
            
        if contact and msg:
            return (
                self.generate_verbose_instruction("WhatsApp", "message", contact, msg),
                {"action": "send_message", "app": "WhatsApp", "recipient": contact, "message": msg}
            )

        # 3. Calling
        vid_call = re.search(r"video call (.+)", text)
        if vid_call:
            raw_c = vid_call.group(1).strip().split(" on ")[0]
            # Custom instruction for Call
            return (
               self.generate_verbose_instruction("WhatsApp", "video_call", raw_c).replace("click video call", "click on video call"), # minor adjustment if needed
               {"action": "video_call", "app": "WhatsApp", "contact": raw_c} 
            )

        audio_call = re.search(r"call (.+)", text)
        if audio_call and "video" not in text:
             raw_c = audio_call.group(1).strip().split(" on ")[0]
             return (
                 self.generate_verbose_instruction("WhatsApp", "call", raw_c),
                 {"action": "voice_call", "app": "WhatsApp", "contact": raw_c}
             )

        return None

class SearchIntent(Intent):
    def __init__(self):
        super().__init__("Search")

    def match(self, text):
        return "search" in text or "buy" in text

    def extract(self, text):
        # YouTube
        if "youtube" in text:
            m = re.search(r"search (.+) on youtube", text)
            if m:
                q = m.group(1).strip()
                return (
                    self.generate_verbose_instruction("YouTube", "search", q),
                    {"action": "search_video", "app": "YouTube", "query": q}
                )
        
        # Instagram
        if "instagram" in text:
             m = re.search(r"search (.+) on instagram", text)
             if m:
                 q = m.group(1).strip()
                 return (
                     self.generate_verbose_instruction("Instagram", "search", q),
                     {"action": "search", "app": "Instagram", "query": q}
                 )

        # Amazon (Buy or Search)
        amz_buy = re.search(r"buy (.+) from amazon", text)
        amz_search = re.search(r"search (.+) on amazon", text)
        if amz_buy or amz_search:
            item = amz_buy.group(1).strip() if amz_buy else amz_search.group(1).strip()
            return (
                self.generate_verbose_instruction("Amazon", "search", item),
                {"action": "search_product", "app": "Amazon", "item": item}
            )
            
        return None

class CommerceIntent(Intent):
    def __init__(self):
        super().__init__("Commerce")
        
    def match(self, text):
        return "order" in text and "swiggy" in text

    def extract(self, text):
        m = re.search(r"order (.+) from swiggy", text)
        if m:
            item = m.group(1).strip()
            return (
                self.generate_verbose_instruction("Swiggy", "order", item),
                {"action": "order_food", "app": "Swiggy", "item": item}
            )
        return None

class PaymentIntent(Intent):
    def __init__(self):
        super().__init__("Payment")

    def match(self, text):
        return ("pay" in text) or ("gpay" in text)

    def extract(self, text):
        # send 100 to mom on gpay
        gpay_send = re.search(r"send (\d+)(?: rupees)? to (.+) on gpay", text)
        # pay 100 to mom
        gpay_pay = re.search(r"pay (\d+) (?:rupees )?to (.+)", text)

        amt, contact = None, None
        if gpay_send:
            amt = gpay_send.group(1).strip()
            contact = gpay_send.group(2).strip()
        elif gpay_pay:
            amt = gpay_pay.group(1).strip()
            contact = gpay_pay.group(2).strip().split(" on gpay")[0]
            
        if amt and contact:
             return (
                 self.generate_verbose_instruction("GPay", "pay", contact, amt),
                 {"action": "payment", "app": "GPay", "amount": amt, "recipient": contact}
             )
        return None

class NavigationIntent(Intent):
    def __init__(self):
        super().__init__("Navigation")
        
    def match(self, text):
        return "navigate to" in text

    def extract(self, text):
        m = re.search(r"navigate to (.+)", text)
        if m:
            place = m.group(1).strip().replace(" on maps", "")
            return (
                self.generate_verbose_instruction("Maps", "navigate", place),
                {"action": "navigate", "app": "Maps", "destination": place}
            )
        return None

class ProductivityIntent(Intent):
    def __init__(self):
        super().__init__("Productivity")

    def match(self, text):
        return "note" in text or ("type" in text and "save" in text)

    def extract(self, text):
        # Note shortcut
        if text.startswith("note "):
            content = text[5:].strip()
            return (
                self.get_note_instruction("Notepad", content),
                {"action": "take_note", "app": "Notepad", "text": content}
            )
        
        # Generic Type & Save
        m = re.search(r"open (.+) and type\s*[\"']?(.+?)[\"']? and save it", text)
        if m:
            app = m.group(1).strip()
            content = m.group(2).strip()
            return (
                self.get_note_instruction(app, content),
                {"action": "type_save", "app": app, "text": content}
            )
        return None
        
    def get_note_instruction(self, app, text):
        save_step = " then save it"
        win = f"if it is windows click windows buttion then search for {app} then open it then typr {text}{save_step}"
        mac = f"it it is mack click Command-Spacebar buttion then search for {app} then open it then typr {text}{save_step}"
        return f"{win}/ {mac}"

class GenericActionIntent(Intent):
    """Handles generic Open, Search, Type commands using standardized verbose flow."""
    def __init__(self):
        super().__init__("GenericAction")
        # Optimization: Known apps for fuzzy matching
        self.known_apps = [
            "notepad", "calculator", "spotify", "chrome", "edge", "discord", 
            "slack", "files", "settings", "camera", "word", "excel", "powerpoint", 
            "explorer", "terminal", "cmd", "paint", "vlc"
        ]
    
    def match(self, text):
        return any(k in text for k in ["open", "search", "type", "run"])
    
    def extract(self, text):
        # Open App
        if text.startswith("open ") or text.startswith("run "):
            app = text.replace("open ", "").replace("run ", "").strip()
            
            # --- FUZZY LOGIC (ACCURACY) ---
            import difflib
            if app not in self.known_apps:
                matches = difflib.get_close_matches(app, self.known_apps, n=1, cutoff=0.6)
                if matches:
                    print(f"[NLU] Typos Detected! Correcting '{app}' -> '{matches[0]}'")
                    app = matches[0]

            return (
                self.generate_verbose_instruction(app, "open", app),
                {"action": "open_app", "app": app}
            )
            
        # Search Generic
        if text.startswith("search ") and " on " not in text:
             query = text[7:].strip()
             # Default to browser search if no app specified
             return (
                 self.generate_verbose_instruction("Browser", "search", query),
                 {"action": "search", "query": query}
             )

        return None
        
    def generate_verbose_instruction(self, app, action_type, target):
        # Optimized for speed
        win = f"if it is windows click windows buttion then search for {target} then open it"
        mac = f"it it is mack click Command-Spacebar buttion then search for {target} then open it"
        return f"{win}/ {mac}"

class SystemIntent(Intent):
    def __init__(self):
        super().__init__("System")
        
    def match(self, text):
        return any(k in text for k in ["volume", "mute", "unmute", "battery", "cpu", "ram", "memory", "check", "clean temp"])
        
    def extract(self, text):
        if "volume" in text:
            if "up" in text: return "press volume_up", {"action": "system", "type": "volume_up"}
            if "down" in text: return "press volume_down", {"action": "system", "type": "volume_down"}
            if "mute" in text: return "press volume_mute", {"action": "system", "type": "volume_mute"}
        
        # New System Admin Commands
        if "battery" in text: return "check battery", {"action": "system", "type": "battery"}
        if "cpu" in text: return "check cpu", {"action": "system", "type": "cpu"}
        if "memory" in text or "ram" in text: return "check memory", {"action": "system", "type": "memory"}
        if "clean temp" in text: return "clean temp", {"action": "system", "type": "clean"}
            
        return "press volume_mute", {"action": "system", "type": "mute"} # Default safety

class MediaIntent(Intent):
    def __init__(self):
        super().__init__("Media")
        
    def match(self, text):
        return any(k in text for k in ["pause", "resume", "next song", "previous song", "skip song"])
        
    def extract(self, text):
        if "pause" in text or "resume" in text or "stop" in text:
            return "press playpause", {"action": "media", "command": "playpause"}
        if "next" in text or "skip" in text:
            return "press nexttrack", {"action": "media", "command": "nexttrack"}
        if "previous" in text or "back" in text:
            return "press prevtrack", {"action": "media", "command": "prevtrack"}
        return None

class DateIntent(Intent):
    def __init__(self):
        super().__init__("Date")
        
    def match(self, text):
        return "time" in text or "date" in text
        
    def extract(self, text):
        from datetime import datetime
        now = datetime.now()
        if "time" in text:
            t_str = now.strftime("%I:%M %p")
            return f"inform The time is {t_str}", {"action": "info", "text": f"The time is {t_str}"}
        if "date" in text:
            d_str = now.strftime("%A, %B %d, %Y")
            return f"inform The date is {d_str}", {"action": "info", "text": f"The date is {d_str}"}
        return None


class GreetingIntent(Intent):
    def __init__(self):
        super().__init__("Greeting")
        
    def match(self, text):
        return any(k in text for k in ["hello", "hi ", "hey "])
        
    def extract(self, text):
        return "inform Hello! How can I help you?", {"action": "info", "text": "Hello! How can I help you?"}

class HumorIntent(Intent):
    def __init__(self):
        super().__init__("Humor")
        
    def match(self, text):
        return "joke" in text or "funny" in text
        
    def extract(self, text):
        # A simple placeholder. In a real system, this would fetch from a DB or API.
        return "inform Why did the robot go to school? To get smarter!", {"action": "info", "text": "Why did the robot go to school? To get smarter!"}

class SolverIntent(Intent):
    def __init__(self):
        super().__init__("Solver")
        
    def match(self, text):
        math_words = ["plus", "minus", "times", "divided by", "+", "-", "*", "/"]
        return any(w in text for w in math_words) and any(c.isdigit() for c in text)
        
    def extract(self, text):
        # Basic Safety: only allow digits and math ops
        import re
        try:
            # Clean text to just math expression
            expr = text.lower().replace("plus", "+").replace("minus", "-").replace("times", "*").replace("divided by", "/")
            expr = re.sub(r'[^0-9+\-*/.]', '', expr)
            if not expr: return None
            
            result = eval(expr) # Safe-ish constraint above
            ans = f"The result is {result}"
            return f"inform {ans}", {"action": "info", "text": ans}
        except:
            return None

# --- Router ---



# --- Main Module ---

class NLUModule:
    def __init__(self, model_path="t5-small", device=None):
        self.router = IntentRouter()
        self.sym_spell = None
        self.dataset_cache = {}
        
        # Load Dataset
        self.load_dataset()
        
        # Initialize SymSpell
        if SymSpell:
            self.sym_spell = SymSpell(max_dictionary_edit_distance=2, prefix_length=7)
            try:
                dictionary_path = pkg_resources.resource_filename("symspellpy", "frequency_dictionary_en_82_765.txt")
                self.sym_spell.load_dictionary(dictionary_path, term_index=0, count_index=1)
                print("SymSpell initialized.")
            except:
                print("SymSpell dictionary load failed.")

        self.use_model = False 

    def load_dataset(self):
        try:
            import os
            # Locate dataset relative to this file
            base_dir = os.path.dirname(os.path.abspath(__file__)) # atom/ai_core/modules
            # Path: atom/data/nlu/nlu_dataset_50k.jsonl
            # modules -> ai_core -> atom -> data (So ../../../data)
            data_path = os.path.join(base_dir, "..", "..", "..", "atom", "data", "nlu", "nlu_dataset_50k.jsonl")
            
            # Helper to find if above path is wrong (depending heavily on where 'atom' folder is)
            if not os.path.exists(data_path):
                 # Try finding 'atom' root in path
                 parts = base_dir.split(os.sep)
                 if "atom" in parts:
                     atom_index = parts.index("atom")
                     atom_root = os.sep.join(parts[:atom_index+1])
                     data_path = os.path.join(atom_root, "data", "nlu", "nlu_dataset_50k.jsonl")
            
            if os.path.exists(data_path):
                print(f"[NLU] Loading dataset from {data_path}...")
                with open(data_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        if not line.strip(): continue
                        try:
                            record = json.loads(line)
                            # Normalize key: lower, stripped, no punctuation?
                            # For now: simple lower/strip matching as requested ("compair every question")
                            key = record['text'].lower().strip()
                            self.dataset_cache[key] = record
                        except:
                            pass
                print(f"[NLU] Loaded {len(self.dataset_cache)} commands.")
            else:
                print(f"[NLU] Warning: Dataset not found at {data_path}")
        except Exception as e:
            print(f"[NLU] Error loading dataset: {e}")

    def lookup_dataset(self, text):
        # 1. Direct Match
        record = self.dataset_cache.get(text)
        if not record: return None
        
        intent = record.get("intent")
        entities = record.get("entities", {})
        
        # MAP DATASET INTENTS TO PLANS
        # "PLAY_MUSIC" -> keys: song, app
        if intent == "PLAY_MUSIC":
            song = entities.get("song", "")
            app = entities.get("app", "Spotify") # Default to Spotify
            base_intent = MusicIntent()
            return (
                base_intent.generate_verbose_instruction(app, "play", song),
                {"action": "play_music", "app": app, "song": song}
            )
            
        # "OPEN_APP" -> keys: app
        if intent == "OPEN_APP":
            app = entities.get("app", "")
            base_intent = GenericActionIntent()
            return (
                base_intent.generate_verbose_instruction(app, "open", app),
                {"action": "open_app", "app": app}
            )
            
        # "CLOSE_APP" -> keys: app
        if intent == "CLOSE_APP":
            app = entities.get("app", "")
            # We don't have a specific Close instruction locally, but GenericAction can handle process termination if we added it.
            # For now, fallback to generic open? No, that's bad. 
            # We will generate a "force close" instruction if executor supports it, or just inform.
            # Actually, let's map it to "clean temp" style logic or just ignore for now if Executor lacks it.
            # Or better: "close {app}" and let executor fail gracefully if unknown.
            return (
                f"close {app}", # Executor needs to handle this!
                {"action": "close_app", "app": app}
            )

        # "SEARCH_WEB" -> query
        if intent == "SEARCH_WEB":
            query = entities.get("query", "")
            base_intent = GenericActionIntent()
            return (
                base_intent.generate_verbose_instruction("Browser", "search", query),
                {"action": "search", "query": query}
            )
            
        # "SEND_MESSAGE" -> contact, message
        if intent == "SEND_MESSAGE":
            contact = entities.get("contact", "")
            msg = entities.get("message", "hello")
            # Default to WhatsApp? Or generic?
            app = "WhatsApp" 
            return (
                 SocialIntent().generate_verbose_instruction(app, "message", contact, msg),
                 {"action": "send_message", "app": app, "recipient": contact, "message": msg}
            )

        return None

    def correct_spelling(self, text):
        if not self.sym_spell or not text: return text
        suggestions = self.sym_spell.lookup_compound(text, max_edit_distance=2)
        if suggestions:
            return suggestions[0].term
        return text

    def preprocess_text(self, text):
        """Strips filler phrases to extract main points."""
        fillers = ["hey atom", "hay atom", "ok atom", "please", "can you", "could you", "just", "would you", "kindly"]
        text_lower = text.lower()
        for f in fillers:
             text_lower = text_lower.replace(f, "")
        return text_lower.strip()

    def predict_action(self, text, image_path=None):
        if not text: return "unknown command", {"action": "unknown"}
        
        # 1. Preprocessing (Main Point Extraction)
        text_processed = self.preprocess_text(text)
        
        # --- DATASET LOOKUP (PRIORITY) ---
        # We check both: raw text (if user was brief) and processed text (without "hey atom")
        db_match = self.lookup_dataset(text.lower().strip())
        if not db_match:
             db_match = self.lookup_dataset(text_processed)
             
        if db_match:
            print(f"[NLU] Dataset Match Found for: '{text}'!")
            return db_match
        
        # 2. Cleaning & Spell Check
        text_final = self.correct_spelling(text_processed)
        
        # 3. Intent Routing
        return self.router.parse(text_final)

if __name__ == "__main__":
    nlu = NLUModule()
    print("Test 1:", nlu.predict_action("play baby song"))
    print("Test 2:", nlu.predict_action("open calculator"))
