import pyautogui
import time
import json

class ControlBrain:
    def __init__(self):
        print("[Control Brain] Initializing Muscles...")
        # Safety defaults
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.5 

    def act(self, action_plan):
        """
        Executes a list of actions.
        Args:
            action_plan (list or dict): JSON-like action instructions.
        """
        print(f"[Control Brain] Received orders: {action_plan}")
        
        if not isinstance(action_plan, list):
            action_plan = [action_plan]
            
        logs = []
        for action in action_plan:
            try:
                self._execute_single_action(action)
                logs.append(f"Executed: {action}")
            except Exception as e:
                err = f"Failed {action}: {e}"
                print(f"[Control Brain] ERROR: {err}")
                logs.append(err)
                return False, logs
                
        return True, logs
        
    def _execute_single_action(self, action):
        kind = action.get("action")
        
        if kind == "open_app":
            app = action.get("app")
            # Windows Key -> Type -> Enter
            pyautogui.press("win")
            time.sleep(0.5)
            pyautogui.write(app)
            time.sleep(0.5)
            pyautogui.press("enter")
            # Wait for app to open
            time.sleep(2.0)
            
        elif kind == "type":
            text = action.get("text")
            pyautogui.write(text, interval=0.05)
            
        elif kind == "press":
            keys = action.get("keys") # e.g. "enter" or ["ctrl", "t"]
            if isinstance(keys, list):
                pyautogui.hotkey(*keys)
            else:
                pyautogui.press(keys)
                
        elif kind == "click_at":
            # For Vision Integration
            x = action.get("x")
            y = action.get("y")
            if x and y:
                pyautogui.click(x, y)
                
        elif kind == "scroll":
            amount = action.get("amount", 0)
            pyautogui.scroll(amount)
            
        # --- PREVIOUS NLU MAPPING SUPPORT ---
        # "search" -> Browser/App search logic usually handled by verbose plan "click search then type"
        # But if we get a raw "search" action:
        elif kind == "search":
             # Assuming generic "Type and Enter" if focused
             query = action.get("query")
             pyautogui.write(query)
             pyautogui.press("enter")
             
        elif kind == "play_music":
             # Fallback if no specific click coords provided
             # Just hit Space (often play/pause) or Media Key
             pyautogui.press("playpause")
             
        # Add more mappings as needed
