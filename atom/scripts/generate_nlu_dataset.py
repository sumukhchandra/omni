import json
import random
import os

intents = {
    "PLAY_MUSIC": {
        "templates": [
            "play {song} on {app}",
            "can you play {song}",
            "start playing {song}",
            "play song {song} using {app}",
            "i want to hear {song}"
        ]
    },
    "OPEN_APP": {
        "templates": [
            "open {app}",
            "launch {app}",
            "start {app}",
            "can you open {app}"
        ]
    },
    "CLOSE_APP": {
        "templates": [
            "close {app}",
            "exit {app}",
            "stop {app}"
        ]
    },
    "SEARCH_WEB": {
        "templates": [
            "search {query}",
            "google {query}",
            "find {query} on internet"
        ]
    },
    "SEND_MESSAGE": {
        "templates": [
            "send message to {contact}",
            "text {contact} saying {message}",
            "send {message} to {contact}"
        ]
    }
}

songs = ["baby", "believer", "shape of you", "faded", "despacito", "blinding lights", "levitating", "don't start now"]
apps = ["spotify", "youtube", "chrome", "whatsapp", "telegram", "notepad", "calculator", "calendar"]
contacts = ["siddu", "rahul", "mom", "dad", "alex", "sarah"]
queries = ["weather today", "bitcoin price", "news headlines", "best restaurants nearby", "movie timings"]
messages = ["hello", "i am coming", "call me back", "where are you", "happy birthday"]

def noise(text):
    if random.random() < 0.3:
        text = text.replace("spotify", "spotifi")
    if random.random() < 0.3:
        text = text.replace("play", "ply")
    return text

print("Generating dataset...")

print("Generating dataset...")
dataset = []
count = 0

while len(dataset) < 50000:
    intent = random.choice(list(intents.keys()))
    template = random.choice(intents[intent]["templates"])
    
    # Selection
    s_song = random.choice(songs)
    s_app = random.choice(apps)
    s_contact = random.choice(contacts)
    s_query = random.choice(queries)
    s_message = random.choice(messages)

    # Formatting
    # We only assume the template has unique keys if present.
    text = template.format(
        song=s_song,
        app=s_app,
        contact=s_contact,
        query=s_query,
        message=s_message
    )
    
    # Noise
    text = noise(text)

    sample = {
        "text": text,
        "intent": intent,
        "entities": {}
    }

    if "{song}" in template:
        sample["entities"]["song"] = s_song
    if "{app}" in template:
        sample["entities"]["app"] = s_app
    if "{contact}" in template:
        sample["entities"]["contact"] = s_contact
    if "{query}" in template:
        sample["entities"]["query"] = s_query
    if "{message}" in template:
        sample["entities"]["message"] = s_message

    dataset.append(sample)

output_path = os.path.join("data", "nlu", "nlu_dataset_50k.jsonl")
# Ensure directory exists just in case
os.makedirs(os.path.dirname(output_path), exist_ok=True)

with open(output_path, "w", encoding="utf-8") as f:
    for item in dataset:
        f.write(json.dumps(item) + "\n")

print(f"✅ 50,000 NLU samples generated at {output_path}")
