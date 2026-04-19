from datetime import datetime
from bson import ObjectId

class BlogModel:
    def __init__(self, db):
        self.collection = db['blogs']
        # Create text index for search
        self.collection.create_index([
            ('title', 'text'),
            ('content', 'text'),
            ('tags', 'text')
        ])

    def search_blogs(self, query, skip=0, limit=10):
        regex_query = {'$regex': query, '$options': 'i'}
        return list(self.collection.find({
            '$or': [
                {'title': regex_query},
                {'content': regex_query},
                {'tags': regex_query}
            ]
        }).sort('created_at', -1).skip(skip).limit(limit))

    def find_by_author(self, author_id, skip=0, limit=10):
        return list(self.collection.find({'author_id': ObjectId(author_id)}).sort('created_at', -1).skip(skip).limit(limit))

    def find_by_tag(self, tag, skip=0, limit=10):
        return list(self.collection.find({'tags': tag}).sort('created_at', -1).skip(skip).limit(limit))

    def create_blog(self, blog_data):
        blog_data['created_at'] = datetime.utcnow()
        blog_data['updated_at'] = datetime.utcnow()
        blog_data['likes'] = []
        blog_data['comments'] = []
        result = self.collection.insert_one(blog_data)
        return str(result.inserted_id)

    def find_by_id(self, blog_id):
        return self.collection.find_one({'_id': ObjectId(blog_id)})

    def find_all(self, skip=0, limit=10):
        return list(self.collection.find().sort('created_at', -1).skip(skip).limit(limit))

    def update_blog(self, blog_id, update_data):
        update_data['updated_at'] = datetime.utcnow()
        result = self.collection.update_one(
            {'_id': ObjectId(blog_id)},
            {'$set': update_data}
        )
        return result.modified_count > 0

    def delete_blog(self, blog_id):
        result = self.collection.delete_one({'_id': ObjectId(blog_id)})
        return result.deleted_count > 0

    def toggle_like(self, blog_id, user_id):
        blog = self.find_by_id(blog_id)
        if not blog:
            return None
        
        user_id_obj = ObjectId(user_id)
        likes = blog.get('likes', [])
        
        if user_id_obj in likes:
            self.collection.update_one(
                {'_id': ObjectId(blog_id)},
                {'$pull': {'likes': user_id_obj}}
            )
            return False # Unliked
        else:
            self.collection.update_one(
                {'_id': ObjectId(blog_id)},
                {'$addToSet': {'likes': user_id_obj}}
            )
            return True # Liked
