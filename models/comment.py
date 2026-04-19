from datetime import datetime
from bson import ObjectId

class CommentModel:
    def __init__(self, db):
        self.collection = db['comments']

    def create_comment(self, comment_data):
        comment_data['created_at'] = datetime.utcnow()
        comment_data['likes'] = []
        
        # Convert IDs to ObjectId
        comment_data['blog_id'] = ObjectId(comment_data['blog_id'])
        comment_data['user_id'] = ObjectId(comment_data['user_id'])
        
        if 'parent_id' in comment_data and comment_data['parent_id']:
            comment_data['parent_id'] = ObjectId(comment_data['parent_id'])
        else:
            comment_data['parent_id'] = None
        
        result = self.collection.insert_one(comment_data)
        return str(result.inserted_id)

    def find_by_blog(self, blog_id):
        return list(self.collection.find({'blog_id': ObjectId(blog_id)}).sort('created_at', 1))

    def find_by_id(self, comment_id):
        return self.collection.find_one({'_id': ObjectId(comment_id)})

    def delete_comment(self, comment_id):
        result = self.collection.delete_one({'_id': ObjectId(comment_id)})
        return result.deleted_count > 0

    def toggle_like(self, comment_id, user_id):
        comment = self.find_by_id(comment_id)
        if not comment:
            return None
        
        user_id_obj = ObjectId(user_id)
        likes = comment.get('likes', [])
        
        if user_id_obj in likes:
            self.collection.update_one(
                {'_id': ObjectId(comment_id)},
                {'$pull': {'likes': user_id_obj}}
            )
            return False # Unliked
        else:
            self.collection.update_one(
                {'_id': ObjectId(comment_id)},
                {'$addToSet': {'likes': user_id_obj}}
            )
            return True # Liked
