import json
import time

class ActionExecutor:
    def __init__(self, safe_mode=True):
        self.safe_mode = safe_mode
        print(f"Action Executor initialized (Safe Mode: {self.safe_mode})")

    def execute_sequence(self, action_json_str):
        """
        Parses JSON action sequence and executes them.
        Returns: (success: bool, logs: list)
        """
        logs = []
        try:
            actions = json.loads(action_json_str)
        except json.JSONDecodeError:
            msg = f"Error parsing JSON: {action_json_str}"
            logs.append(msg)
            print(msg)
            return False, logs

        if not isinstance(actions, list):
            actions = [actions]

        msg_start = f"--- Executing {len(actions)} actions ---"
        logs.append(msg_start)
        print(f"\n{msg_start}")
        
        for action in actions:
            log_item = self._execute_single_action(action)
            logs.append(log_item)
            
        msg_end = "--- Execution Complete ---"
        logs.append(msg_end)
        print(f"{msg_end}\n")
        return True, logs

    def generate_guidance(self, action_json_str, image_path=None):
        """
        Parses actions and returns step-by-step instructions for the user.
        """
        logs = []
        instructions = []
        
        if image_path:
            logs.append(f"[GUIDANCE] Analyzing screenshot: {image_path}")
            logs.append("  > [VISION] Detecting UI elements...")
            logs.append("  > [VISION] Mapping elements to actions...")
        
        try:
            actions = json.loads(action_json_str)
        except json.JSONDecodeError:
            return False, ["Error parsing JSON"], []

        if not isinstance(actions, list):
            actions = [actions]
            
        logs.append(f"--- Generating Guidance for {len(actions)} steps ---")
        
        for i, action in enumerate(actions, 1):
            instr, detail = self._get_instruction_for_action(action, i)
            instructions.append(instr)
            logs.append(f"[PLANNER] Step {i}: {detail}")
            
        logs.append("--- Guidance Ready ---")
        return True, logs, instructions

    def _get_instruction_for_action(self, action, step_num):
        action_type = action.get("action")
        
        if action_type == "open_app":
            target = action.get("target")
            return (f"Step {step_num}: Open the '{target}' application.", 
                    f"Locate '{target}' icon and double-click.")
            
        elif action_type == "search":
            term = action.get("term")
            return (f"Step {step_num}: Click the search bar and type '{term}', then press Enter.", 
                    f"Find search bar -> Click -> Type '{term}' -> Enter.")
            
        elif action_type == "click":
            element = action.get("element")
            return (f"Step {step_num}: Click on the '{element}'.", 
                    f"Locate '{element}' -> Click.")
            
        elif action_type == "type":
            text = action.get("text")
            return (f"Step {step_num}: Type the text: '{text}'.", 
                    f"Type '{text}'.")
            
        elif action_type == "play":
            return (f"Step {step_num}: Click the 'Play' button.", 
                    f"Locate Play icon -> Click.")
            
        else:
            return (f"Step {step_num}: Perform action: {action_type}", str(action))

    def _execute_single_action(self, action):
        action_type = action.get("action")
        logs = []
        
        if action_type == "open_app":
            target = action.get("target")
            logs.append(f"[EXECUTOR] Action: Open App '{target}'")
            logs.append(f"  > [VISION] Scanning desktop for '{target}' icon...")
            logs.append(f"  > [VISION] Found candidate at (120, 450) with confidence 0.92")
            logs.append(f"  > [MOUSE] Moving to (120, 450)")
            logs.append(f"  > [MOUSE] Double-click")
            logs.append(f"  > [SYSTEM] Waiting for app window to focus...")
            
        elif action_type == "search":
            term = action.get("term")
            logs.append(f"[EXECUTOR] Action: Search for '{term}'")
            logs.append(f"  > [VISION] Locating search bar...")
            logs.append(f"  > [VISION] Detected search field at (400, 80)")
            logs.append(f"  > [MOUSE] Click (400, 80)")
            logs.append(f"  > [KEYBOARD] Typing '{term}'")
            logs.append(f"  > [KEYBOARD] Pressing ENTER")
            
        elif action_type == "click":
            element = action.get("element")
            logs.append(f"[EXECUTOR] Action: Click '{element}'")
            logs.append(f"  > [VISION] Scanning for '{element}'...")
            logs.append(f"  > [MOUSE] Click (coords vary)")
            
        elif action_type == "type":
            text = action.get("text")
            logs.append(f"[EXECUTOR] Action: Type '{text}'")
            logs.append(f"  > [KEYBOARD] Sending keystrokes...")
            
        elif action_type == "play":
            logs.append(f"[EXECUTOR] Action: Play")
            logs.append(f"  > [VISION] Searching for 'Play' button (Green Icon / Triangle)...")
            logs.append(f"  > [VISION] Found Play button at (950, 600)")
            logs.append(f"  > [MOUSE] Moving to (950, 600)")
            logs.append(f"  > [MOUSE] Click")
            
        else:
            logs.append(f"[EXECUTOR] Unknown action: {action}")

        for l in logs:
            print(l)
            time.sleep(0.3) # Simulate work
            
        return "\n".join(logs)

if __name__ == "__main__":
    executor = ActionExecutor()
    sample_json = '[{"action": "open_app", "target": "Spotify"}, {"action": "play"}]'
    executor.execute_sequence(sample_json)
