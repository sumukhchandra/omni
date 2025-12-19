from ai_core.modules.nlu import NLUModule

class KnowledgeBrain:
    def __init__(self):
        print("[Knowledge Brain] Initializing...")
        self.nlu = NLUModule()

    def think(self, text):
        """
        Processes text and returns an intent and action data.
        Returns: (verbose_instruction_string, action_data_dict)
        """
        print(f"[Knowledge Brain] Thinking about: '{text}'")
        return self.nlu.predict_action(text)
