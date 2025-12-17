import re

class RuleBasedNLU:
    def __init__(self):
        self.intents = {
            "PLAY_MUSIC": [
                r"play (?P<song>.+) on (?P<app>.+)",
                r"play (?P<song>.+)",
                r"start playing (?P<song>.+)"
            ],
            "OPEN_APP": [
                r"open (?P<app>.+)",
                r"launch (?P<app>.+)",
                r"start (?P<app>.+)"
            ],
            "CLOSE_APP": [
                r"close (?P<app>.+)",
                r"exit (?P<app>.+)"
            ],
            "SEARCH_WEB": [
                r"search (?P<query>.+)",
                r"google (?P<query>.+)",
                r"find (?P<query>.+)"
            ],
            "SEND_MESSAGE": [
                r"send message to (?P<contact>.+) saying (?P<message>.+)",
                r"text (?P<contact>.+) (?P<message>.+)"
            ]
        }

    def parse(self, text):
        text = text.lower().strip()
        
        for intent, patterns in self.intents.items():
            for pattern in patterns:
                match = re.search(pattern, text)
                if match:
                    entities = match.groupdict()
                    return {
                        "intent": intent,
                        "entities": entities,
                        "confidence": 1.0
                    }
        
        # Default fallback
        return {
            "intent": "UNKNOWN",
            "entities": {},
            "confidence": 0.0
        }

if __name__ == "__main__":
    nlu = RuleBasedNLU()
    print(nlu.parse("play believer on spotify"))
    print(nlu.parse("open youtube"))
