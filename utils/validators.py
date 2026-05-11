import re
from typing import Dict, Any, Tuple

class InputValidator:
    """Validates and sanitizes user input"""
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def validate_password(password: str) -> Tuple[bool, str]:
        """Validate password strength"""
        if len(password) < 8:
            return False, "Password must be at least 8 characters"
        if not re.search(r'[A-Z]', password):
            return False, "Password must contain uppercase letter"
        if not re.search(r'[a-z]', password):
            return False, "Password must contain lowercase letter"
        if not re.search(r'[0-9]', password):
            return False, "Password must contain number"
        return True, "Valid"
    
    @staticmethod
    def sanitize_string(text: str, max_length: int = 5000) -> str:
        """Sanitize string input"""
        if not isinstance(text, str):
            return ""
        # Remove HTML tags
        text = re.sub(r'<[^>]*>', '', text)
        # Limit length
        return text[:max_length].strip()
    
    @staticmethod
    def validate_blog_data(data: Dict[str, Any]) -> Tuple[bool, str]:
        """Validate blog creation/update data"""
        if not data:
            return False, "No data provided"
        
        title = data.get('title', '').strip()
        content = data.get('content', '').strip()
        
        if not title or len(title) < 3:
            return False, "Title must be at least 3 characters"
        
        if not content or len(content) < 10:
            return False, "Content must be at least 10 characters"
        
        if len(title) > 200:
            return False, "Title must be less than 200 characters"
        
        if len(content) > 50000:
            return False, "Content must be less than 50000 characters"
        
        return True, "Valid"
