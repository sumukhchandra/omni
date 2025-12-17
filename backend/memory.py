
import json
import os

MEMORY_FILE = os.path.join(os.path.dirname(__file__), 'memories.json')

class MemoryManager:
    def __init__(self):
        self.memories = self._load_memory()

    def _load_memory(self):
        if not os.path.exists(MEMORY_FILE):
             with open(MEMORY_FILE, 'w') as f:
                 json.dump({}, f)
             return {}
        try:
            with open(MEMORY_FILE, 'r') as f:
                return json.load(f)
        except:
            return {}

    def learn(self, key, value):
        """Saves a new fact."""
        key = key.lower().strip()
        self.memories[key] = value
        with open(MEMORY_FILE, 'w') as f:
            json.dump(self.memories, f, indent=4)
        print(f"[MEMORY] Learned new fact: '{key}'")

    def recall(self, key):
        """Retrieves a fact."""
        return self.memories.get(key.lower().strip())

if __name__ == "__main__":
    m = MemoryManager()
    m.learn("test", "This is a test memory.")
    print(m.recall("test"))
