# Authentication Implementation - Quick Start Guide

## What's Been Implemented

### Backend Changes
1. ✅ Created `auth_manager.py` - Complete authentication system with:
   - Azure Table Storage integration for user credentials
   - Password hashing with bcrypt (12 rounds)
   - JWT token generation and validation
   - Decorator for protecting endpoints: `@token_required`

2. ✅ Updated `app.py` with:
   - `/api/auth/signup` - Register new users
   - `/api/auth/login` - Authenticate users and get JWT tokens
   - `/api/auth/verify` - Verify token validity
   - Protected all applicant endpoints with `@token_required`
   - Automatic "createdBy" field population from JWT token

3. ✅ Updated `requirements.txt` with:
   - PyJWT==2.8.0 - JWT token handling
   - bcrypt==4.0.1 - Password hashing
   - azure-data-tables==12.4.0 - Azure Table Storage support

4. ✅ Updated `.env` with JWT_SECRET variable

### Frontend Changes
1. ✅ Created `context/AuthContext.tsx` - Global authentication state:
   - User data management
   - Token persistence in localStorage
   - `useAuth` hook for easy access in components

2. ✅ Created `pages/login.tsx` - Beautiful login page:
   - Email and password input
   - Error handling
   - Auto-redirect if already authenticated
   - Link to signup page

3. ✅ Created `pages/signup.tsx` - Registration page:
   - Full name, email, password fields
   - Password confirmation
   - Input validation
   - Auto-redirect to login on success

4. ✅ Created `components/ProtectedRoute.tsx` - Route protection:
   - Checks authentication status
   - Redirects to login if not authenticated
   - Shows loading state

5. ✅ Updated `components/Layout.tsx` with:
   - User's full name display
   - Logout button
   - Conditional navbar based on auth status
   - Link to login/signup for unauthenticated users

6. ✅ Updated all API-calling components with JWT tokens:
   - `components/Upload.tsx` - Includes token in upload request
   - `components/Search.tsx` - Includes token in search requests
   - `components/StoredResumes.tsx` - Includes token in all requests (fetch, delete, download)

7. ✅ Protected pages with ProtectedRoute:
   - `pages/upload.tsx`
   - `pages/search.tsx`
   - `pages/resumes.tsx`

8. ✅ Updated `pages/_app.tsx` to wrap app with AuthProvider

## How to Test

### 1. Install Backend Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 2. Start the Backend
```bash
cd backend
python app.py
```
Should output:
```
[APP] .env loaded
[APP] Azure Connection: https://sarransh...
* Running on http://0.0.0.0:5000
```

### 3. Start the Frontend (in another terminal)
```bash
cd frontend
npm install  # if not already installed
npm run dev
```
Should output:
```
> ready - started server on 0.0.0.0:3000, url: http://localhost:3000
```

### 4. Test the Application

#### Step 1: Sign Up
1. Go to `http://localhost:3000`
2. Click "Sign Up" in the navigation bar
3. Fill in:
   - Full Name: John Doe
   - Email: john@example.com
   - Password: password123
   - Confirm Password: password123
4. Click "Create Account"
5. You should be redirected to login page

#### Step 2: Log In
1. You're now on the login page
2. Enter the email and password you just created
3. Click "Sign In"
4. You should be redirected to home page with your name shown in the navbar

#### Step 3: Test Protected Routes
1. Click on "Upload" - should open upload page
2. Click on "Search" - should open search page
3. Click on "Resumes" - should open resumes page
4. Try uploading a resume - it will now be tagged with your name in "createdBy" field
5. Click "Logout" - you'll be redirected to login

#### Step 4: Try Unauthorized Access
1. Clear localStorage: Open DevTools → Application → LocalStorage → Remove authToken
2. Try to access /upload directly
3. You should be redirected to login

## Data Storage Architecture

### User Credentials (Azure Table Storage)
- **Location**: Azure Table Storage
- **Table Name**: Users
- **Partition Key**: USER
- **Row Key**: user email (lowercase)
- **Fields**:
  - email
  - fullName
  - passwordHash (bcrypt hashed)
  - createdAt (ISO timestamp)
  - isActive (boolean)

### Applicant Data (Azure SQL / SQLite)
- **Location**: SQL Database (Azure SQL or local SQLite)
- **New Field**: `createdBy` - automatically populated with user's full name
- **Updated**: When user uploads resumes, the creator's name is stored

### Resume Files (Azure Blob Storage)
- **Location**: Azure Blob Storage
- **Container**: resumes
- **Storage**: Unchanged from previous implementation

## JWT Token Details

- **Algorithm**: HS256
- **Expiration**: 24 hours
- **Secret**: Set in `.env` as `JWT_SECRET`
- **Storage**: Browser localStorage
- **Sent In**: Authorization header as `Bearer <token>`

## Files Created/Modified

### Created Files:
- `backend/auth_manager.py`
- `frontend/context/AuthContext.tsx`
- `frontend/pages/login.tsx`
- `frontend/pages/signup.tsx`
- `frontend/components/ProtectedRoute.tsx`
- `AUTH_DOCUMENTATION.md`

### Modified Files:
- `backend/app.py` - Added auth routes and token_required decorator
- `backend/requirements.txt` - Added JWT and bcrypt dependencies
- `backend/.env` - Added JWT_SECRET
- `frontend/pages/_app.tsx` - Added AuthProvider wrapper
- `frontend/components/Layout.tsx` - Added user info and logout
- `frontend/components/Upload.tsx` - Added token in headers
- `frontend/components/Search.tsx` - Added token in headers
- `frontend/components/StoredResumes.tsx` - Added token in headers
- `frontend/pages/upload.tsx` - Added ProtectedRoute wrapper
- `frontend/pages/search.tsx` - Added ProtectedRoute wrapper
- `frontend/pages/resumes.tsx` - Added ProtectedRoute wrapper

## Important Notes

⚠️ **Production Considerations**:
1. Change JWT_SECRET to a strong random value
2. Store secrets in secure environment management
3. Use HTTPS instead of HTTP
4. Consider using httpOnly cookies instead of localStorage
5. Implement rate limiting on auth endpoints
6. Add password strength requirements
7. Implement password reset functionality
8. Add email verification

✅ **Security Features Implemented**:
1. Bcrypt password hashing (12 rounds)
2. JWT token-based stateless authentication
3. Azure Table Storage for secure credential storage
4. Protected route components
5. Automatic token validation on app load
6. Token expiration (24 hours)

## Troubleshooting

### Issue: "Azure Table Storage not configured"
**Solution**: 
- Verify AZURE_STORAGE_CONNECTION_STRING in backend/.env
- Check that Azure Storage Account exists and is accessible

### Issue: "Token is missing" errors
**Solution**:
- Make sure you're logged in
- Check browser console for errors
- Try logging out and back in

### Issue: Backend won't start
**Solution**:
- Run `pip install -r requirements.txt` to install all dependencies
- Check that Python 3.8+ is installed
- Verify Azure connection string is valid

### Issue: Frontend won't start
**Solution**:
- Run `npm install` to install all dependencies
- Check that Node.js 16+ is installed
- Make sure port 3000 is not in use

## Next Steps

1. Test the complete authentication flow (done above)
2. Review the AUTH_DOCUMENTATION.md for detailed information
3. Create a few test accounts to verify multi-user functionality
4. Test that different users can only see/modify their own data
5. Deploy to production with security considerations in place

## Support

For detailed information about:
- Authentication flow
- API endpoints
- Security considerations
- Deployment instructions

See: `AUTH_DOCUMENTATION.md`
