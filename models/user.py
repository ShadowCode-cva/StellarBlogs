from datetime import datetime
from bson import ObjectId

class UserModel:
    def __init__(self, db):
        if db is None:
            self.collection = None
        else:
            self.collection = db['users']
            # Ensure unique email and username
            try:
                self.collection.create_index('email', unique=True)
                self.collection.create_index('username', unique=True)
            except Exception as e:
                pass  # Index creation failed, but collection is available

    def create_user(self, user_data):
        user_data['created_at'] = datetime.utcnow()
        user_data['favorite_blogs'] = []
        result = self.collection.insert_one(user_data)
        return str(result.inserted_id)

    def find_by_email(self, email):
        return self.collection.find_one({'email': email})

    def find_by_username(self, username):
        return self.collection.find_one({'username': username})

    def find_by_id(self, user_id):
        return self.collection.find_one({'_id': ObjectId(user_id)})

    def toggle_favorite(self, user_id, blog_id):
        user = self.find_by_id(user_id)
        if not user:
            return None
        
        blog_id_obj = ObjectId(blog_id)
        favorites = user.get('favorite_blogs', [])
        
        if blog_id_obj in favorites:
            self.collection.update_one(
                {'_id': ObjectId(user_id)},
                {'$pull': {'favorite_blogs': blog_id_obj}}
            )
            return False # Removed
        else:
            self.collection.update_one(
                {'_id': ObjectId(user_id)},
                {'$addToSet': {'favorite_blogs': blog_id_obj}}
            )
            return True # Added
