# Authentication System Documentation

## Overview
The Applicant Database application now includes a comprehensive authentication system with the following features:

### Features
1. **User Registration (Signup)** - Users can create new accounts with email and password
2. **User Authentication (Login)** - Users can log in with their credentials
3. **JWT Token-based Authentication** - Secure token-based API access
4. **Azure Table Storage** - User credentials stored securely in Azure
5. **Protected Routes** - Frontend pages require authentication
6. **User Tracking** - Each applicant entry is tracked with "createdBy" field showing who uploaded the resume

## Backend Setup

### Prerequisites
- Python 3.8+
- Azure Storage Account (for both Blob Storage and Table Storage)
- pip for package management

### Installation

1. **Install Dependencies**
```bash
cd backend
pip install -r requirements.txt
```

2. **Environment Variables** (.env file)
```
AZURE_STORAGE_CONNECTION_STRING=your-azure-connection-string
AZURE_CONTAINER_NAME=resumes
JWT_SECRET=your-secret-key-change-in-production
FLASK_ENV=development
FLASK_DEBUG=1
```

### Running the Backend
```bash
cd backend
python app.py
```

The server will run on `http://localhost:5000`

## Frontend Setup

### Prerequisites
- Node.js 16+
- npm or yarn

### Installation

1. **Install Dependencies**
```bash
cd frontend
npm install
```

2. **Create .env.local file** (optional, for custom API URLs)
```
# Backend API URL
NEXT_PUBLIC_API_URL=http://localhost:5000
```

### Running the Frontend
```bash
cd frontend
npm run dev
```

The application will run on `http://localhost:3000`

## Authentication Flow

### User Registration
1. User clicks "Sign Up" button
2. Fills in email, password, and full name
3. Backend validates and stores credentials in Azure Table Storage (hashed)
4. User is redirected to login page

### User Login
1. User navigates to login page or clicks "Login"
2. Enters email and password
3. Backend verifies credentials against Azure Table Storage
4. If valid, backend generates JWT token
5. Token is stored in browser localStorage
6. User is redirected to home page

### Protected Routes
1. When user tries to access protected pages (Upload, Search, Resumes)
2. ProtectedRoute component checks for valid token
3. If no token or invalid token, user is redirected to login
4. If valid token, user can access the page

### API Requests
All API endpoints (except health check) require JWT token in Authorization header:
```
Authorization: Bearer <token>
```

Token is automatically included in all API requests by the components.

## API Endpoints

### Authentication Endpoints (No authentication required)
- `POST /api/auth/signup` - Create new account
- `POST /api/auth/login` - Login and get JWT token
- `GET /api/auth/verify` - Verify JWT token validity

### Protected Endpoints (JWT token required)
- `POST /api/upload` - Upload resumes (requires authentication)
- `GET /api/applicants` - Get all applicants
- `GET /api/applicants/<id>` - Get specific applicant
- `PUT /api/applicants/<id>` - Update applicant
- `GET /api/applicants/<id>/download` - Download resume
- `DELETE /api/applicants/<id>` - Delete applicant
- `POST /api/search` - Search applicants

## User Data Storage

### Azure Table Storage
User credentials are stored in Azure Table Storage in the "Users" table with the following structure:
- **PartitionKey**: "USER"
- **RowKey**: user email (lowercase)
- **email**: user email
- **fullName**: user full name
- **passwordHash**: bcrypt hashed password (12 rounds)
- **createdAt**: account creation timestamp
- **isActive**: boolean flag for account status

## Applicant Data Tracking

When resumes are uploaded, the "createdBy" field is automatically populated with:
- User's full name (if available)
- Or user's email (if full name not available)

This allows tracking which user uploaded each resume.

## Security Considerations

1. **Password Hashing**: Passwords are hashed using bcrypt with 12 rounds
2. **JWT Tokens**: 
   - Tokens expire after 24 hours
   - Tokens use HS256 algorithm with a secret key
   - Tokens are stored in localStorage (accessible to XSS attacks)
   - Consider using httpOnly cookies for production
3. **Azure Security**:
   - Connection strings stored in environment variables
   - Never commit .env files to version control
4. **CORS**: Enabled for development (should be restricted in production)

## Demo Account

For testing purposes, you can use:
- Email: `user@example.com`
- Password: `password123`

(This account must be created first through the signup process)

## Troubleshooting

### Backend Issues
1. **"Azure Table Storage not configured" message**
   - Verify AZURE_STORAGE_CONNECTION_STRING in .env
   - Ensure Azure Storage Account has Table Storage enabled
   - Check internet connection to Azure

2. **JWT Token errors**
   - Ensure JWT_SECRET is set in .env
   - Token might have expired (try logging in again)
   - Clear localStorage and try again

### Frontend Issues
1. **"Token is missing" errors**
   - Make sure you're logged in
   - Check browser console for errors
   - Try logging out and logging back in
   - Clear localStorage: `localStorage.removeItem('authToken')`

2. **Redirects to login unexpectedly**
   - Token might have expired
   - Backend server might be down
   - Check if backend is running on http://localhost:5000

## Production Deployment

### Security Changes for Production
1. Change JWT_SECRET to a strong random string
2. Use HTTPS instead of HTTP
3. Store secrets in secure environment management (AWS Secrets Manager, Azure Key Vault, etc.)
4. Consider using httpOnly cookies instead of localStorage
5. Implement CSRF protection
6. Set proper CORS headers (restrict to specific domains)
7. Implement rate limiting on auth endpoints
8. Add account lockout after failed login attempts
9. Implement password reset functionality
10. Use HTTPS for Azure connections

### Azure Configuration
- Ensure Azure Storage Account is properly secured
- Use connection strings with limited access
- Enable firewall rules on Azure resources
- Monitor access logs regularly

## File Structure

```
backend/
  auth_manager.py          - Authentication logic and JWT handling
  app.py                   - Flask application with auth routes
  database.py              - Database operations
  azure_storage.py         - Azure Blob Storage operations
  requirements.txt         - Python dependencies
  .env                     - Environment variables (DO NOT COMMIT)

frontend/
  context/
    AuthContext.tsx        - React context for authentication state
  components/
    ProtectedRoute.tsx     - Route protection component
    Layout.tsx             - Updated with user info and logout
    Upload.tsx             - Updated with token in headers
    Search.tsx             - Updated with token in headers
    StoredResumes.tsx      - Updated with token in headers
  pages/
    login.tsx              - Login page
    signup.tsx             - Signup page
    _app.tsx               - App wrapper with AuthProvider
    upload.tsx             - Protected upload page
    search.tsx             - Protected search page
    resumes.tsx            - Protected resumes page
```

## Future Enhancements

1. **Social Login** - Add Google/Microsoft OAuth
2. **Two-Factor Authentication** - Enhanced security
3. **Role-Based Access Control** - Different user roles (Admin, Manager, Viewer)
4. **Audit Logging** - Track all user actions
5. **Email Verification** - Verify email addresses on signup
6. **Password Reset** - Forgot password functionality
7. **User Management** - Admin panel to manage users
8. **API Rate Limiting** - Prevent abuse
