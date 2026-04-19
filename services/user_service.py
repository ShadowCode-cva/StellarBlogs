from models.user import UserModel
from utils.security import hash_password, check_password, generate_jwt

class UserService:
    def __init__(self, db):
        self.user_model = UserModel(db)

    def signup(self, data):
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        role = data.get('role', 'user') # default to 'user'

        if not username or not email or not password:
            return {"error": "Missing required fields"}, 400

        if self.user_model.find_by_email(email):
            return {"error": "Email already exists"}, 400

        if self.user_model.find_by_username(username):
            return {"error": "Username already exists"}, 400

        user_data = {
            "username": username,
            "email": email,
            "password_hash": hash_password(password),
            "role": role if role in ['user', 'author'] else 'user'
        }

        user_id = self.user_model.create_user(user_data)
        
        # Generate token immediately after signup
        token = generate_jwt(user_id, user_data['role'])

        return {
            "message": "User created successfully",
            "token": token,
            "user": {
                "id": user_id,
                "username": username,
                "email": email,
                "role": user_data['role']
            }
        }, 201

    def login(self, data):
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return {"error": "Missing email or password"}, 400

        user = self.user_model.find_by_email(email)
        if not user or not check_password(password, user['password_hash']):
            return {"error": "Invalid email or password"}, 401

        token = generate_jwt(str(user['_id']), user['role'])

        return {
            "message": "Login successful",
            "token": token,
            "user": {
                "id": str(user['_id']),
                "username": user['username'],
                "email": user['email'],
                "role": user['role']
            }
        }, 200
