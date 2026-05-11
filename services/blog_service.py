from models.blog import BlogModel
from bson.errors import InvalidId

class BlogService:
    def __init__(self, db):
        self.blog_model = BlogModel(db)

    def serialize_blog(self, blog):
        if not blog:
            return None
        blog['_id'] = str(blog['_id'])
        if 'author_id' in blog:
            blog['author_id'] = str(blog['author_id'])
        if 'likes' in blog:
            blog['likes'] = [str(uid) for uid in blog['likes']]
        if 'created_at' in blog:
            blog['created_at'] = blog['created_at'].isoformat()
        if 'updated_at' in blog:
            blog['updated_at'] = blog['updated_at'].isoformat()
        return blog

    def create_blog(self, data, author_id):
        title = data.get('title')
        content = data.get('content')

        if not title or not content:
            return {'error': 'Title and content are required'}, 400

        blog_data = {
            'title': title,
            'content': content,
            'author_id': str(author_id),  # Ensure author_id is stored as string
            'tags': data.get('tags', [])
        }
        
        blog_id = self.blog_model.create_blog(blog_data)
        return {'message': 'Blog created successfully', 'blog_id': blog_id}, 201

    def get_blog(self, blog_id):
        try:
            blog = self.blog_model.find_by_id(blog_id)
            if not blog:
                return {'error': 'Blog not found'}, 404
            return {'blog': self.serialize_blog(blog)}, 200
        except InvalidId:
            return {'error': 'Invalid blog ID'}, 400

    def get_all_blogs(self, page=1, limit=10):
        skip = (page - 1) * limit
        blogs = self.blog_model.find_all(skip=skip, limit=limit)
        serialized_blogs = [self.serialize_blog(b) for b in blogs]
        return {'blogs': serialized_blogs, 'page': page, 'limit': limit}, 200

    def update_blog(self, blog_id, update_data, author_id):
        try:
            blog = self.blog_model.find_by_id(blog_id)
            if not blog:
                return {'error': 'Blog not found'}, 404
            
            if str(blog['author_id']) != str(author_id):
                return {'error': 'Not authorized to update this blog'}, 403

            # Only allow updating specific fields
            allowed_fields = ['title', 'content', 'tags']
            filtered_update = {k: v for k, v in update_data.items() if k in allowed_fields}
            
            if not filtered_update:
                return {'error': 'No valid fields to update'}, 400

            success = self.blog_model.update_blog(blog_id, filtered_update)
            if success:
                return {'message': 'Blog updated successfully'}, 200
            return {'error': 'Failed to update blog'}, 500
        except InvalidId:
            return {'error': 'Invalid blog ID'}, 400

    def delete_blog(self, blog_id, author_id):
        try:
            blog = self.blog_model.find_by_id(blog_id)
            if not blog:
                return {'error': 'Blog not found'}, 404
            
            if str(blog['author_id']) != str(author_id):
                return {'error': 'Not authorized to delete this blog'}, 403

            success = self.blog_model.delete_blog(blog_id)
            if success:
                return {'message': 'Blog deleted successfully'}, 200
            return {'error': 'Failed to delete blog'}, 500
        except InvalidId:
            return {'error': 'Invalid blog ID'}, 400

    def search_blogs(self, query, page=1, limit=10):
        skip = (page - 1) * limit
        blogs = self.blog_model.search_blogs(query, skip=skip, limit=limit)
        serialized_blogs = [self.serialize_blog(b) for b in blogs]
        return {'blogs': serialized_blogs, 'page': page, 'limit': limit}, 200

    def get_blogs_by_author(self, author_id, page=1, limit=10):
        try:
            skip = (page - 1) * limit
            blogs = self.blog_model.find_by_author(author_id, skip=skip, limit=limit)
            serialized_blogs = [self.serialize_blog(b) for b in blogs]
            return {'blogs': serialized_blogs, 'page': page, 'limit': limit}, 200
        except InvalidId:
            return {'error': 'Invalid author ID'}, 400

    def get_blogs_by_tag(self, tag, page=1, limit=10):
        skip = (page - 1) * limit
        blogs = self.blog_model.find_by_tag(tag, skip=skip, limit=limit)
        serialized_blogs = [self.serialize_blog(b) for b in blogs]
        return {'blogs': serialized_blogs, 'page': page, 'limit': limit}, 200
