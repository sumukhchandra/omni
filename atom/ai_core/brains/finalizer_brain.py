from ai_core.brains.knowledge_brain import KnowledgeBrain
from ai_core.brains.helper_brain import HelperBrain
from ai_core.brains.control_brain import ControlBrain

class FinalizerBrain:
    def __init__(self):
        print("[Finalizer Brain] Initializing The One Above All...")
        self.knowledge = KnowledgeBrain()
        self.helper = HelperBrain()
        self.control = ControlBrain()
        
    def execute(self, user_command):
        """
        Main Loop: User -> Knowledge -> (Optional Helper) -> Finalizer -> Control
        Returns: (success_bool, response_message)
        """
        print(f"[Finalizer] Orchestrating: '{user_command}'")
        
        # 1. Ask Knowledge Brain (What does user want?)
        # Returns: (verbal_instruction, action_dict)
        verbal_plan, action_data = self.knowledge.think(user_command)
        
        if not action_data or action_data.get("action") == "unknown":
            return False, "I didn't understand that command."
            
        if not action_data or action_data.get("action") == "unknown":
            return False, "I didn't understand that command."
            
        print(f"[Finalizer] Intent: {action_data}")
        
        # 2. Refine Plan with Vision (If needed)
        # Check if action requires finding something on screen
        # For MVP, we'll do simple keyword checks or strict action types
        final_actions = []
        
        # --- PLAN REFINEMENT ---
        # --- SCREEN ACTIONS ---
        if action_data.get("action") == "click_text": 
            target_text = action_data.get("target")
            coords = self.helper.find_text_on_screen(target_text)
            if coords:
                final_actions.append({"action": "click_at", "x": coords[0], "y": coords[1]})
            else:
                return False, f"I looked for '{target_text}' but couldn't see it via OCR."

        elif action_data.get("action") == "screen_search":
            query = action_data.get("query")
            # 1. Search for Search Button
            candidates = ["search", "find", "meta ai"]
            coords = None
            for c in candidates:
                coords = self.helper.find_text_on_screen(c)
                if coords: break
            
            if coords:
                print(f"[Finalizer] Orchestrating Search for '{query}'")
                final_actions.append({"action": "click_at", "x": coords[0], "y": coords[1]})
                final_actions.append({"action": "wait", "duration": 0.5}) 
                final_actions.append({"action": "type", "text": query})
                final_actions.append({"action": "wait", "duration": 1.5}) # Wait for results
                
                # 2. Look for the RESULT (The Option)
                # We need a way to perform a mid-stream visual check.
                # Since final_actions is a pre-calculated list, we can't easily perform a check *during* execution 
                # unless ControlBrain supports it or we break execution here.
                # CURRENT LIMITATION: ControlBrain executes a LIST. It doesn't feedback mid-stream.
                # FIX: We must split execution or make ControlBrain smarter. 
                # EASIER FIX FOR MVP: We blindly add a "click_text" action for the query? 
                # No, coordinates are unknown until we type.
                
                # REAL FIX: We need to execute the SEARCH part first, then LOOK, then CLICK.
                # This requires breaking the "plan then act" model slightly or doing it inside execute().
                
                # Execute Part 1 (Search & Type)
                self.control.act(final_actions)
                final_actions = [] # Clear for Part 2
                
                # Part 2: Look for Result
                print(f"[Finalizer] Looking for result option '{query}'...")
                matches = self.helper.find_all_text_on_screen(query)
                target_coords = None
                
                if matches:
                    # Heuristic: Avoid clicking the search bar again.
                    # Usually the search bar is the first match (top of screen).
                    # We pick the second match if available.
                    if len(matches) > 1:
                        target_coords = matches[1]
                        print(f"[Finalizer] Multiple matches found. Picking second match at {target_coords} (avoiding top bar).")
                    else:
                        target_coords = matches[0]
                        
                if target_coords:
                     final_actions.append({"action": "click_at", "x": target_coords[0], "y": target_coords[1]})
                else:
                     print(f"[Finalizer] Result '{query}' not seen. Pressing Enter.")
                     final_actions.append({"action": "press", "key": "enter"})
            else:
                return False, f"I couldn't find a Search or Find button."

        elif action_data.get("action") == "send_message":
            recipient = action_data.get("recipient")
            message = action_data.get("message")
            
            # 1. Search for Recipient
            candidates = ["search", "find", "meta ai"]
            coords = None
            for c in candidates:
                coords = self.helper.find_text_on_screen(c)
                if coords: break
            
            if coords:
                print(f"[Finalizer] Orchestrating Visual Message to {recipient}")
                # Part 1: Open Search & Type
                part1 = [
                    {"action": "click_at", "x": coords[0], "y": coords[1]},
                    {"action": "wait", "duration": 0.5},
                    {"action": "type", "text": recipient},
                    {"action": "wait", "duration": 1.5}
                ]
                self.control.act(part1)
                
                # Part 2: Click Result (The "Option")
                print(f"[Finalizer] Looking for contact '{recipient}'...")
                matches = self.helper.find_all_text_on_screen(recipient)
                res_coords = None
                
                if matches:
                    if len(matches) > 1:
                         res_coords = matches[1]
                    else:
                         res_coords = matches[0]
                
                part2 = []
                if res_coords:
                    part2.append({"action": "click_at", "x": res_coords[0], "y": res_coords[1]})
                else:
                    part2.append({"action": "press", "key": "enter"})
                    
                # Part 3: Type Message
                part2.append({"action": "wait", "duration": 1.0})
                part2.append({"action": "type", "text": message})
                part2.append({"action": "press", "key": "enter"})
                
                # Add to final_actions so it gets executed
                final_actions = part2
                
            else:
                 # Fallback: Try to find Recipient Name directly
                 coords = self.helper.find_text_on_screen(recipient)
                 if coords:
                     final_actions.append({"action": "click_at", "x": coords[0], "y": coords[1]})
                     final_actions.append({"action": "wait", "duration": 0.5})
                     final_actions.append({"action": "type", "text": message})
                     final_actions.append({"action": "press", "key": "enter"})
                 else:
                     return False, f"I couldn't find a way to message '{recipient}'."

        else:
            # Standard "Blind" Actions (Open App, Type, etc.)
            # Just pass the action_data directly if Control knows it, 
            # Or convert verbal_plan? 
            # ControlBrain expects specific keys. KnowledgeBrain returns mapped action_dicts.
            # We trust KnowledgeBrain's action_data output format matches ControlBrain's expectation
            # (See NLU Action Dicts vs ControlBrain checks).
            
            final_actions.append(action_data)
            
        # 3. Execute
        success, logs = self.control.act(final_actions)
        
        # 4. Final Report
        if success:
            return True, f"Done. {verbal_plan}"
        else:
            return False, f"Failed during execution. {logs[-1] if logs else ''}"
