import json

try:
    from transformers import T5ForConditionalGeneration, T5Tokenizer
    import torch
except ImportError:
    print("Warning: transformers/torch not found. Using Mock NLU.")
    T5ForConditionalGeneration = None
    T5Tokenizer = None # Ensure T5Tokenizer is also None if transformers fails

try:
    from symspellpy import SymSpell, Verbosity
    import pkg_resources
except ImportError:
    print("Warning: symspellpy not found. Spelling correction disabled.")
    SymSpell = None

class NLUModule:
    def __init__(self, model_path="t5-small", device="cpu"):
        self.mock_mode = True # Default to Mock until we successfully load a model
        self.sym_spell = None
        
        # Initialize SymSpell (Stage 1)
        if SymSpell:
            self.sym_spell = SymSpell(max_dictionary_edit_distance=2, prefix_length=7)
            dictionary_path = pkg_resources.resource_filename(
                "symspellpy", "frequency_dictionary_en_82_765.txt"
            )
            # dictionary_path = "frequency_dictionary_en_82_765.txt" # fallback if needed
            if dictionary_path:
                 self.sym_spell.load_dictionary(dictionary_path, term_index=0, count_index=1)
            print("SymSpell initialized for spelling correction.")

        # Initialize NLU Model (Stage 2)
        if T5ForConditionalGeneration and T5Tokenizer:
            try:
                if device is None: # This check is now redundant if device has a default, but keeping for robustness
                    self.device = "cuda" if torch.cuda.is_available() else "cpu"
                else:
                    self.device = device
                
                print(f"Loading NLU model '{model_path}' on {self.device}...")
                self.tokenizer = T5Tokenizer.from_pretrained(model_path)
                self.model = T5ForConditionalGeneration.from_pretrained(model_path).to(self.device)
                print("NLU model loaded.")
                self.mock_mode = False # Successfully loaded, so disable mock mode
            except Exception as e: # Catch broader exceptions during model loading
                print(f"WARNING: Failed to load NLU model '{model_path}' ({e}). Using Mock Mode.")
                self.mock_mode = True
        else:
            print("WARNING: T5ForConditionalGeneration or T5Tokenizer not available. Using Mock Mode.")
            self.mock_mode = True

    def generate_verbose_instruction(self, app, action_type, target, secondary_target=None):
        """
        Generates the strict verbose instruction format requested by the user.
        Format: "if it is windows click windows buttion... / it it is mack..."
        Includes "typos" (buttion, typr, mack) to match the requested golden dataset style.
        """
        # Common suffix logic based on action
        if action_type == "play":
            # Spotify flow: Navigate Search -> Type Song -> Click Song -> Play
            action_desc = f"navigate to search bar then typr {target} then click on the song then play the song"
        elif action_type == "message":
            # WhatsApp/Message flow: Navigate Search -> Type Contact -> Click Contact -> Message Bar -> Type Msg -> Send
            action_desc = f"navigate to search bar then typr {target} then click on {target} then click on message bar then typr {secondary_target} then click on send"
        elif action_type == "search":
             action_desc = f"navigate to search bar then typr {target} then click on search"
        elif action_type == "call":
            action_desc = f"navigate to search bar then typr {target} then click on {target} then click call"
        elif action_type == "order":
            action_desc = f"navigate to search bar then typr {target} then click on {target} then click order"
        elif action_type == "pay":
            action_desc = f"navigate to search bar then typr {target} then click on {target} then click pay then typr {secondary_target} then click pay"
        elif action_type == "navigate":
            action_desc = f"navigate to search bar then typr {target} then click on {target} then start navigation"
        else:
            action_desc = f"perform action on {target}"

        # Windows Segment - REMOVED the hardcoded search steps to prevent duplication
        win_part = (
            f"if it is windows click windows buttion then search for {app} then open it then {action_desc}"
        )
        
        # Mac Segment
        mac_part = (
            f"it it is mack click Command-Spacebar buttion then search for {app} then open it then {action_desc}"
        )
        
        return f"{win_part}/ {mac_part}"

    def correct_spelling(self, text):
        """
        Stage 1: Spell Correction
        Uses SymSpell to fix typos in the input text.
        """
        if not self.sym_spell or not text:
            return text
            
        suggestions = self.sym_spell.lookup_compound(text, max_edit_distance=2)
        if suggestions:
            corrected = suggestions[0].term
            if corrected != text.lower():
                print(f"Spell Corrected: '{text}' -> '{corrected}'")
            return corrected
        return text

    def predict_action(self, text, image_path=None):
        if not text: return "unknown command", {"action": "unknown"}
        
        # STAGE 1: SPELLING CORRECTION
        text = self.correct_spelling(text)
        
        if self.mock_mode:
            import re
            lower = text.lower()
            print(f"DEBUG: Processing text: '{lower}'")
            
            instruction = ""
            json_data = {}

            # Regex fallback failing -> Use simple string check (Ported from AI/modules/nlu.py)
            if "play " in lower and " on " not in lower:
                parts = lower.split("play ", 1)
                if len(parts) > 1:
                    song = parts[1].strip()
                    if song:
                        instruction = self.generate_verbose_instruction("Spotify", "play", song)
                        json_data = {"action": "play_music", "app": "Spotify", "song": song}
                        return instruction, json_data

            # 1. YOUTUBE
            yt_play = re.search(r"play (.+) on youtube", lower)
            yt_search = re.search(r"search (.+) on youtube", lower)
            yt_open_play = re.search(r"open youtube and play (.+)", lower)
            
            if yt_play or yt_search or yt_open_play:
                if yt_open_play:
                    query = yt_open_play.group(1).strip()
                    action = "play"
                elif yt_play:
                    query = yt_play.group(1).strip()
                    action = "play"
                else:
                    query = yt_search.group(1).strip()
                    action = "search"
                    
                instruction = self.generate_verbose_instruction("YouTube", action, query)
                json_data = {
                    "action": "play_music" if action == "play" else "search_video",
                    "app": "YouTube",
                    "query": query
                }
                return instruction, json_data

            # 2. INSTAGRAM
            insta_msg = re.search(r"message (.+) on instagram", lower)
            insta_search = re.search(r"search (.+) on instagram", lower)
            
            if insta_msg:
                contact = insta_msg.group(1).strip()
                # Assuming empty message for generic "message X" command or use generic text
                instruction = self.generate_verbose_instruction("Instagram", "message", contact, "hello")
                json_data = {"action": "send_message", "app": "Instagram", "contact": contact}
                return instruction, json_data

            if insta_search:
                query = insta_search.group(1).strip()
                instruction = self.generate_verbose_instruction("Instagram", "search", query)
                json_data = {"action": "search", "app": "Instagram", "query": query}
                return instruction, json_data

            # 3. SPOTIFY (Generic Play)
            spotify_play = re.search(r"play (.+) on spotify", lower)
            spotify_open_play = re.search(r"open spotify and play (.+)", lower) # User request format
            
            if spotify_play or spotify_open_play:
                song = spotify_play.group(1).strip() if spotify_play else spotify_open_play.group(1).strip()
                instruction = self.generate_verbose_instruction("Spotify", "play", song)
                json_data = {"action": "play_music", "app": "Spotify", "song": song}
                return instruction, json_data

            # 4. SWIGGY
            swiggy_order = re.search(r"order (.+) from swiggy", lower)
            if swiggy_order:
                item = swiggy_order.group(1).strip()
                instruction = self.generate_verbose_instruction("Swiggy", "order", item)
                json_data = {"action": "order_food", "app": "Swiggy", "item": item}
                return instruction, json_data

            # 5. AMAZON
            amazon_buy = re.search(r"buy (.+) from amazon", lower)
            amazon_search = re.search(r"search (.+) on amazon", lower)
            if amazon_buy or amazon_search:
                item = amazon_buy.group(1).strip() if amazon_buy else amazon_search.group(1).strip()
                instruction = self.generate_verbose_instruction("Amazon", "search", item) # Close enough to 'buy' flow
                json_data = {"action": "search_product", "app": "Amazon", "item": item}
                return instruction, json_data

            # 6. GPAY
            gpay_send = re.search(r"send (\d+)(?: rupees)? to (.+) on gpay", lower)
            gpay_pay = re.search(r"pay (\d+) (?:rupees )?to (.+)", lower)
            
            amt = None
            contact = None
            if gpay_send:
                amt = gpay_send.group(1).strip()
                contact = gpay_send.group(2).strip()
            elif gpay_pay:
                amt = gpay_pay.group(1).strip()
                raw_contact = gpay_pay.group(2).strip()
                contact = raw_contact.split(" on gpay")[0]
            
            if amt and contact:
                instruction = self.generate_verbose_instruction("GPay", "pay", contact, amt)
                json_data = {"action": "payment", "app": "GPay", "amount": amt, "recipient": contact}
                return instruction, json_data

            # 7. MAPS
            maps_nav = re.search(r"navigate to (.+)", lower)
            if maps_nav:
                place = maps_nav.group(1).strip().replace(" on maps", "")
                instruction = self.generate_verbose_instruction("Maps", "navigate", place)
                json_data = {"action": "navigate", "app": "Maps", "destination": place}
                return instruction, json_data

            # 8. WHATSAPP / MESSAGE / GMAIL
            msg_pattern = re.search(r"send (.+) to (.+)", lower)
            tell_pattern = re.search(r"tell (\w+) (.+)", lower)
            ask_msg_pattern = re.search(r"ask message (.+) to (.+)", lower)
            generic_msg_pattern = re.search(r"message (.+) to (.+)", lower)
            
            contact = None
            msg = None
            
            if ask_msg_pattern:
                msg = ask_msg_pattern.group(1).strip()
                contact = ask_msg_pattern.group(2).strip()
            elif generic_msg_pattern:
                msg = generic_msg_pattern.group(1).strip()
                contact = generic_msg_pattern.group(2).strip()
            elif msg_pattern:
                msg = msg_pattern.group(1).strip()
                raw_contact = msg_pattern.group(2).strip()
                contact = raw_contact.split(" on ")[0]
            elif tell_pattern:
                contact = tell_pattern.group(1).strip()
                msg = tell_pattern.group(2).strip()
            
            if contact and msg:
                # Default to WhatsApp for general messaging
                instruction = self.generate_verbose_instruction("WhatsApp", "message", contact, msg)
                json_data = {"action": "send_message", "app": "WhatsApp", "recipient": contact, "message": msg}
                return instruction, json_data
                
            # Fallback removed to allow further regex checks

            # Matches: "video call {contact}"
            video_call_pattern = re.search(r"video call (.+)", lower)
            if video_call_pattern:
                raw_contact = video_call_pattern.group(1).strip()
                contact = raw_contact.split(" on ")[0]
                return (
                    f"if it is windows click windows buttion and search for whatapp and open it then navigate to search bar "
                    f"then click on search and typr {contact} then click on {contact} then click on video call/ "
                    f"if it is mack click Command-Spacebar buttion and search for whatapp and open it then navigate to search bar "
                    f"then click on search and typr {contact} then click on {contact} then click on video call"
                )

            # Template 4: Call
            # Matches: "call {contact}"
            call_pattern = re.search(r"call (.+)", lower)
            if call_pattern:
                raw_contact = call_pattern.group(1).strip()
                contact = raw_contact.split(" on ")[0] # simpler removal
                
                return (
                    f"if it is windows click windows buttion and search for whatapp and open it then navigate to search bar "
                    f"then click on search and typr {contact} then click on {contact} then click on call/ "
                    f"if it is mack click Command-Spacebar buttion and search for whatapp and open it then navigate to search bar "
                    f"then click on search and typr {contact} then click on {contact} then click on call"
                )

            # 9. OPEN -> TYPE -> SAVE (Generic)
            # Matches: "open {app} and type {text} and save it"
            # Regex Note: Non-greedy text capture anchored by " and save it"
            # Regex Note: Flexible spacing after 'type'
            open_type_save = re.search(r"open (.+) and type\s*[\"']?(.+?)[\"']? and save it", lower)
            if open_type_save:
                app = open_type_save.group(1).strip()
                text = open_type_save.group(2).strip()
                
                # Check if "save it" is actually in the original string (implicit by regex match)
                save_step = " then save it" 
                
                # We can reuse the 'typr' typo for consistency
                # Step sequence: search app -> open -> type text -> save
                instruction = (
                    f"if it is windows click windows buttion then search for {app} then open it then typr {text}{save_step}/ "
                    f"it it is mack click Command-Spacebar buttion then search for {app} then open it then typr {text}{save_step}"
                )
                json_data = {"action": "type_save", "app": app, "text": text}
                return instruction, json_data

            # 10. NOTE SHORTCUT
            # Matches: "note {text}" -> Open Notepad, Type, Save
            note_shortcut = re.search(r"^note (.+)", lower)
            if note_shortcut:
                text = note_shortcut.group(1).strip()
                app = "Notepad"
                save_step = " then save it"
                
                instruction = (
                    f"if it is windows click windows buttion then search for {app} then open it then typr {text}{save_step}/ "
                    f"it it is mack click Command-Spacebar buttion then search for {app} then open it then typr {text}{save_step}"
                )
                json_data = {"action": "take_note", "app": app, "text": text}
                return instruction, json_data

            # --- Legacy JSON Mocks (Fallback) ---
            actions = []
            
            if "open" in lower:
                # Extract app name after 'open'
                parts = lower.split("open ")
                if len(parts) > 1:
                    target = parts[1].split(" ")[0]
                    actions.append({"action": "open_app", "target": target})
            
            if "search" in lower:
                 parts = lower.split("search ")
                 if len(parts) > 1:
                     term = parts[1]
                     actions.append({"action": "search", "term": term})
            
            if not actions and "type" in lower:
                 parts = lower.split("type ")
                 if len(parts) > 1:
                     actions.append({"action": "type", "text": parts[1]})
            
            if not actions:
                 return '[{"action": "log", "message": "Mock mode: Pattern not matched."}]'

            return json.dumps(actions)

        # Real Model Inference
        input_text = f"parse command: {text}"
        inputs = self.tokenizer(input_text, return_tensors="pt").to(self.device)
        
        with torch.no_grad():
            outputs = self.model.generate(
                inputs.input_ids, 
                max_length=128, 
                num_beams=4, 
                early_stopping=True
            )
        decoded_output = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        # Return tuple to match signature expected by pipeline
        return decoded_output, {"action": "generated_by_model", "text": decoded_output}

if __name__ == "__main__":
    nlu = NLUModule()
    print("Prediction:", nlu.predict_action("play a song"))
