from models.user import UserModel
from models.blog import BlogModel
from bson.errors import InvalidId

class InteractionService:
    def __init__(self, db):
        self.user_model = UserModel(db)
        self.blog_model = BlogModel(db)

    def toggle_like(self, blog_id, user_id):
        try:
            liked = self.blog_model.toggle_like(blog_id, user_id)
            if liked is None:
                return {'error': 'Blog not found'}, 404
            
            message = 'Blog liked' if liked else 'Blog unliked'
            return {'message': message, 'liked': liked}, 200
        except InvalidId:
            return {'error': 'Invalid blog ID'}, 400

    def toggle_favorite(self, user_id, blog_id):
        try:
            # Check if blog exists first
            blog = self.blog_model.find_by_id(blog_id)
            if not blog:
                return {'error': 'Blog not found'}, 404
                
            favorited = self.user_model.toggle_favorite(user_id, blog_id)
            if favorited is None:
                return {'error': 'User not found'}, 404
                
            message = 'Blog added to favorites' if favorited else 'Blog removed from favorites'
            return {'message': message, 'favorited': favorited}, 200
        except InvalidId:
            return {'error': 'Invalid blog ID'}, 400

    def get_user_favorites(self, user_id):
        user = self.user_model.find_by_id(user_id)
        if not user:
            return {'error': 'User not found'}, 404
            
        favorite_ids = user.get('favorite_blogs', [])
        blogs = []
        for b_id in favorite_ids:
            blog = self.blog_model.find_by_id(str(b_id))
            if blog:
                # Basic serialization
                blog['_id'] = str(blog['_id'])
                blog['author_id'] = str(blog['author_id'])
                if 'likes' in blog:
                    blog['likes'] = [str(uid) for uid in blog['likes']]
                if 'created_at' in blog:
                    blog['created_at'] = blog['created_at'].isoformat()
                if 'updated_at' in blog:
                    blog['updated_at'] = blog['updated_at'].isoformat()
                blogs.append(blog)
                
        return {'favorites': blogs}, 200
