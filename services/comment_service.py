from models.comment import CommentModel
from bson.errors import InvalidId

class CommentService:
    def __init__(self, db):
        self.comment_model = CommentModel(db)

    def serialize_comment(self, comment):
        if not comment:
            return None
        comment['_id'] = str(comment['_id'])
        comment['blog_id'] = str(comment['blog_id'])
        comment['user_id'] = str(comment['user_id'])
        if 'likes' in comment:
            comment['likes'] = [str(uid) for uid in comment['likes']]
        if 'parent_id' in comment and comment['parent_id']:
            comment['parent_id'] = str(comment['parent_id'])
        if 'created_at' in comment:
            comment['created_at'] = comment['created_at'].isoformat()
        return comment

    def add_comment(self, data, user_id):
        blog_id = data.get('blog_id')
        content = data.get('content')
        parent_id = data.get('parent_id')

        if not blog_id or not content:
            return {'error': 'Blog ID and content are required'}, 400

        comment_data = {
            'blog_id': blog_id,
            'user_id': user_id,
            'content': content,
            'parent_id': parent_id
        }

        try:
            comment_id = self.comment_model.create_comment(comment_data)
            return {'message': 'Comment added successfully', 'comment_id': comment_id}, 201
        except InvalidId:
            return {'error': 'Invalid blog or parent ID'}, 400

    def get_comments_for_blog(self, blog_id):
        try:
            comments = self.comment_model.find_by_blog(blog_id)
            serialized = [self.serialize_comment(c) for c in comments]
            
            # Organize into a tree structure for nested replies
            comment_dict = {c['_id']: c for c in serialized}
            tree = []
            for c in serialized:
                p_id = c.get('parent_id')
                if p_id and p_id in comment_dict:
                    if 'replies' not in comment_dict[p_id]:
                        comment_dict[p_id]['replies'] = []
                    comment_dict[p_id]['replies'].append(c)
                else:
                    tree.append(c)
            
            return {'comments': tree}, 200
        except InvalidId:
            return {'error': 'Invalid blog ID'}, 400

    def delete_comment(self, comment_id, user_id):
        try:
            comment = self.comment_model.find_by_id(comment_id)
            if not comment:
                return {'error': 'Comment not found'}, 404
            
            if str(comment['user_id']) != str(user_id):
                return {'error': 'Not authorized to delete this comment'}, 403

            success = self.comment_model.delete_comment(comment_id)
            if success:
                return {'message': 'Comment deleted successfully'}, 200
            return {'error': 'Failed to delete comment'}, 500
        except InvalidId:
            return {'error': 'Invalid comment ID'}, 400

    def toggle_like(self, comment_id, user_id):
        try:
            liked = self.comment_model.toggle_like(comment_id, user_id)
            if liked is None:
                return {'error': 'Comment not found'}, 404
            return {'message': 'Toggled like', 'liked': liked}, 200
        except InvalidId:
            return {'error': 'Invalid comment ID'}, 400
