# delete_all_users.py

from pymongo import MongoClient

# Replace with your actual MongoDB connection string
MONGODB_URI = "mongodb://localhost:27017"
DATABASE_NAME = "fido_transactions"

# Connect to MongoDB
client = MongoClient(MONGODB_URI)
db = client[DATABASE_NAME]

# Delete all documents from the 'users' collection
result = db['users'].delete_many({})
print(f"Deleted {result.deleted_count} users.")
