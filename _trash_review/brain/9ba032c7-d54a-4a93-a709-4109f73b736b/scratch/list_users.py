import pymongo

uri = "mongodb+srv://mr_bharath_foods:demo12345@cluster0.2swejbu.mongodb.net/?appName=Cluster0"
client = pymongo.MongoClient(uri)
db = client["mr_bharath_foods"]

col = db["customers"]
print(f"Total users: {col.count_documents({})}")
for u in col.find({}, {"email": 1, "phone": 1, "personal_details": 1, "auth": 1}):
    print(f"ID: {u.get('_id')}")
    print(f"Email: {u.get('email')}")
    print(f"Phone: {u.get('phone')}")
    print(f"Role: {u.get('auth', {}).get('role') if u.get('auth') else None}")
    print("-" * 30)
