from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError
import sys
from dotenv import load_dotenv
import os

load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")

print("Attempting to connect to MongoDB...")
try:
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000, tlsAllowInvalidCertificates=True)
    # The ismaster command is cheap and does not require auth.
    client.admin.command('ismaster')
    print("Connection Successful!")
except ServerSelectionTimeoutError as e:
    print(f"Connection Failed: Timeout. details: {e}")
except Exception as e:
    print(f"Connection Failed: Error: {e}")
