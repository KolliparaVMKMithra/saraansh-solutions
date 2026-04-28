"""
Authentication Manager Module
Handles user authentication and JWT token management
Stores user credentials in Azure Table Storage
"""
import os
import jwt
import bcrypt
import uuid
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from functools import wraps
from flask import request, jsonify

# Import Azure Table Storage
try:
    from azure.data.tables import TableServiceClient
    from azure.core.exceptions import ResourceNotFoundError
except ImportError:
    TableServiceClient = None


class AuthManager:
    """
    Authentication manager using Azure Table Storage for user credentials
    """

    def __init__(self):
        """Initialize Authentication Manager"""
        self.connection_string = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
        self.table_name = 'Users'
        self.jwt_secret = os.getenv('JWT_SECRET', 'your-secret-key-change-in-production')
        self.jwt_algorithm = 'HS256'
        self.token_expiry_hours = 24
        
        self.table_client = None
        self._initialize_table_storage()

    def _initialize_table_storage(self):
        """Initialize Azure Table Storage connection"""
        if not self.connection_string or not TableServiceClient:
            print("⚠️  Azure Table Storage not configured. Auth disabled.")
            return

        try:
            service_client = TableServiceClient.from_connection_string(self.connection_string)
            self.table_client = service_client.get_table_client(self.table_name)

            # Create table if it doesn't exist
            try:
                self.table_client.create_table()
                print(f"✅ Created table: {self.table_name}")
            except Exception:
                print(f"ℹ️  Table already exists: {self.table_name}")

        except Exception as e:
            print(f"⚠️  Failed to initialize Azure Table Storage: {str(e)}")
            self.table_client = None

    def hash_password(self, password: str) -> str:
        """Hash a password using bcrypt"""
        salt = bcrypt.gensalt(rounds=12)
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

    def verify_password(self, password: str, hashed: str) -> bool:
        """Verify a password against its hash"""
        try:
            return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
        except Exception:
            return False

    def signup(self, email: str, password: str, full_name: str) -> Dict[str, Any]:
        """
        Create a new user account

        Args:
            email: User email (will be partition key)
            password: User password (will be hashed)
            full_name: Full name of user

        Returns:
            Dictionary with success status and message
        """
        if not self.table_client:
            return {'success': False, 'message': 'Authentication service not available'}

        try:
            # Check if user already exists
            try:
                existing_user = self.table_client.get_entity(partition_key='USER', row_key=email.lower())
                return {'success': False, 'message': 'User already exists with this email'}
            except ResourceNotFoundError:
                pass

            # Create new user entity
            user_entity = {
                'PartitionKey': 'USER',
                'RowKey': email.lower(),
                'email': email.lower(),
                'fullName': full_name,
                'passwordHash': self.hash_password(password),
                'createdAt': datetime.utcnow().isoformat(),
                'isActive': True
            }

            # Insert user into table
            self.table_client.create_entity(entity=user_entity)
            print(f"✅ User created: {email}")

            return {
                'success': True,
                'message': 'User created successfully',
                'email': email.lower(),
                'fullName': full_name
            }

        except Exception as e:
            print(f"❌ Signup error: {str(e)}")
            return {'success': False, 'message': f'Signup failed: {str(e)}'}

    def login(self, email: str, password: str) -> Dict[str, Any]:
        """
        Authenticate user and generate JWT token

        Args:
            email: User email
            password: User password

        Returns:
            Dictionary with success status, message, and JWT token
        """
        if not self.table_client:
            return {'success': False, 'message': 'Authentication service not available'}

        try:
            # Get user from table
            user = self.table_client.get_entity(partition_key='USER', row_key=email.lower())

            # Verify password
            if not self.verify_password(password, user['passwordHash']):
                return {'success': False, 'message': 'Invalid email or password'}

            # Check if user is active
            if not user.get('isActive', True):
                return {'success': False, 'message': 'User account is inactive'}

            # Generate JWT token
            payload = {
                'email': user['email'],
                'fullName': user['fullName'],
                'exp': datetime.utcnow() + timedelta(hours=self.token_expiry_hours),
                'iat': datetime.utcnow()
            }

            token = jwt.encode(payload, self.jwt_secret, algorithm=self.jwt_algorithm)
            print(f"✅ User logged in: {email}")

            return {
                'success': True,
                'message': 'Login successful',
                'token': token,
                'email': user['email'],
                'fullName': user['fullName']
            }

        except ResourceNotFoundError:
            return {'success': False, 'message': 'Invalid email or password'}
        except Exception as e:
            print(f"❌ Login error: {str(e)}")
            return {'success': False, 'message': f'Login failed: {str(e)}'}

    def verify_token(self, token: str) -> Dict[str, Any]:
        """
        Verify JWT token

        Args:
            token: JWT token

        Returns:
            Dictionary with success status and decoded payload
        """
        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=[self.jwt_algorithm])
            return {'success': True, 'data': payload}
        except jwt.ExpiredSignatureError:
            return {'success': False, 'message': 'Token expired'}
        except jwt.InvalidTokenError:
            return {'success': False, 'message': 'Invalid token'}

    def get_user_from_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Extract user data from JWT token

        Args:
            token: JWT token

        Returns:
            User data dictionary or None if invalid
        """
        result = self.verify_token(token)
        return result['data'] if result['success'] else None


def token_required(f):
    """
    Decorator to require valid JWT token for endpoints
    Accepts token from:
    1. Authorization header (Bearer <token>)
    2. Query parameter (?token=<token>)
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        # Check for token in Authorization header first
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(' ')[1]
            except IndexError:
                return jsonify({'success': False, 'message': 'Invalid token format'}), 401

        # If no token in header, check query parameters
        if not token:
            token = request.args.get('token')

        if not token:
            return jsonify({'success': False, 'message': 'Token is missing'}), 401

        try:
            # Verify token
            from app import auth_manager
            result = auth_manager.verify_token(token)
            if not result['success']:
                return jsonify({'success': False, 'message': result['message']}), 401

            # Pass user data to the route function
            request.user = result['data']
            return f(*args, **kwargs)

        except Exception as e:
            return jsonify({'success': False, 'message': 'Token verification failed'}), 401

    return decorated


# Create global auth manager instance
auth_manager = AuthManager()
