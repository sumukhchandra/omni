import unittest
import sys
import os
import json
from unittest.mock import MagicMock, patch

# Setup paths
sys.path.append(os.path.join(os.getcwd(), 'backend', 'ai_core'))
sys.path.append(os.path.join(os.getcwd(), 'backend', 'executor'))

# Mock libraries not available or dangerous to run
sys.modules['pyautogui'] = MagicMock()
sys.modules['cv2'] = MagicMock()
sys.modules['pytesseract'] = MagicMock()

# Import Modules to Test
try:
    from modules.nlu import NLUModule
    from pipeline import ECOPipeline
    import actions
except ImportError as e:
    print(f"CRITICAL: Failed to import backend modules: {e}")
    sys.exit(1)

class TestNLU(unittest.TestCase):
    def setUp(self):
        self.nlu = NLUModule()

    def test_music_intent(self):
        text = "play baby on spotify"
        instr, data = self.nlu.predict_action(text)
        self.assertEqual(data['action'], 'play_music')
        self.assertEqual(data['app'], 'Spotify')
        self.assertIn("click windows", instr) # Loose check for verbose format

    def test_social_intent_whatsapp(self):
        text = "message hello to mom"
        instr, data = self.nlu.predict_action(text)
        self.assertEqual(data['action'], 'send_message')
        self.assertEqual(data['app'], 'WhatsApp')
        self.assertEqual(data['recipient'], 'mom')

    def test_generic_search(self):
        text = "search antigravity"
        instr, data = self.nlu.predict_action(text)
        self.assertEqual(data['action'], 'search')
        self.assertEqual(data['query'], 'antigravity')

    def test_productivity_save(self):
        text = "note buy milk"
        instr, data = self.nlu.predict_action(text)
        self.assertEqual(data['action'], 'take_note')
        self.assertEqual(data['app'], 'Notepad')
        self.assertEqual(data['text'], 'buy milk')

class TestPipeline(unittest.TestCase):
    def setUp(self):
        # Patch init to avoid loading heavyweight models completely if needed
        # But our current pipeline is lightweight enough (Mock NLU)
        self.pipeline = ECOPipeline()

    def test_process_text(self):
        success, logs, action, instr = self.pipeline.processed_request(text_input="open calculator")
        self.assertTrue(success)
        self.assertEqual(action['action'], 'open_app')
        self.assertEqual(action['app'], 'calculator')

class TestExecutorParsing(unittest.TestCase):
    def test_execute_verbose_parsing(self):
        # We test that the parsing logic correctly calls the (mocked) execution functions
        # We rely on the log output or return values since we mocked pyautogui
        
        # Reset mock
        actions.pyautogui.reset_mock()
        
        cmd = "if it is windows click windows buttion then search for notepad then open it"
        logs = actions.execute_verbose_command(cmd)
        
        # Check logs for success messages (our mocked executor returns strings)
        self.assertTrue(any("Pressed Windows key" in log for log in logs))
        self.assertTrue(any("Typed 'notepad'" in log for log in logs))
        self.assertTrue(any("Pressed Enter" in log for log in logs))

if __name__ == '__main__':
    unittest.main()
