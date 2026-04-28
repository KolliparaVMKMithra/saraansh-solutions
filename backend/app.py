from flask import Flask, request, jsonify, send_file, after_this_request
from flask_cors import CORS
import os
import sys
from datetime import datetime
from resume_parser import parse_resume
from database import Database

# Load environment variables from .env file BEFORE importing azure_storage
import dotenv
dotenv.load_dotenv(verbose=True)

print(f"[APP] .env loaded", flush=True)
print(f"[APP] Azure Connection: {os.getenv('AZURE_STORAGE_CONNECTION_STRING', 'NOT SET')[:50]}...", flush=True)

from azure_storage import azure_storage
from auth_manager import auth_manager, token_required

# Initialize Flask app
app = Flask(__name__)
# Enable CORS for frontend applications
CORS(app, resources={
    r"/api/*": {
        "origins": [
            "https://yellow-hill-06120a607.azurestaticapps.net",
            "http://localhost:3000",
            "http://localhost:5000",
            "*"
        ],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# Initialize database connection
db = Database()

# Ensure upload directory exists
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size


@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'ok', 'message': 'Backend is running'}), 200


@app.route('/api/auth/signup', methods=['POST'])
def signup():
    """User signup endpoint"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'message': 'No data provided'}), 400
        
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        full_name = data.get('fullName', '').strip()
        
        # Validate input
        if not email or not password or not full_name:
            return jsonify({'success': False, 'message': 'Email, password, and full name are required'}), 400
        
        if len(password) < 6:
            return jsonify({'success': False, 'message': 'Password must be at least 6 characters'}), 400
        
        # Check email format
        if '@' not in email or '.' not in email:
            return jsonify({'success': False, 'message': 'Invalid email format'}), 400
        
        result = auth_manager.signup(email, password, full_name)
        
        if result['success']:
            return jsonify(result), 201
        else:
            return jsonify(result), 400
    
    except Exception as e:
        print(f"Signup error: {str(e)}")
        return jsonify({'success': False, 'message': f'Signup failed: {str(e)}'}), 500


@app.route('/api/auth/login', methods=['POST'])
def login():
    """User login endpoint"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'message': 'No data provided'}), 400
        
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        
        if not email or not password:
            return jsonify({'success': False, 'message': 'Email and password are required'}), 400
        
        result = auth_manager.login(email, password)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 401
    
    except Exception as e:
        print(f"Login error: {str(e)}")
        return jsonify({'success': False, 'message': f'Login failed: {str(e)}'}), 500


@app.route('/api/auth/verify', methods=['GET'])
def verify_token():
    """Verify JWT token endpoint"""
    try:
        token = None
        
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(' ')[1]
            except IndexError:
                return jsonify({'success': False, 'message': 'Invalid token format'}), 401
        
        if not token:
            return jsonify({'success': False, 'message': 'Token is missing'}), 401
        
        result = auth_manager.verify_token(token)
        
        if result['success']:
            return jsonify({'success': True, 'user': result['data']}), 200
        else:
            return jsonify(result), 401
    
    except Exception as e:
        return jsonify({'success': False, 'message': f'Verification failed: {str(e)}'}), 500


@app.route('/api/upload', methods=['POST'])
@token_required
def upload_resumes():
    """Handle resume uploads and parsing - Requires authentication"""
    print("\n" + "="*60, flush=True)
    print("[UPLOAD] New upload request started", flush=True)
    print(f"[UPLOAD] User: {request.user.get('email')}", flush=True)
    print("="*60, flush=True)
    
    try:
        if 'files' not in request.files:
            print("[UPLOAD] ERROR: No 'files' key in request", flush=True)
            return jsonify({'success': False, 'message': 'No files provided'}), 400

        files = request.files.getlist('files')
        print(f"[UPLOAD] Received {len(files)} file(s)", flush=True)
        
        if not files or all(f.filename == '' for f in files):
            print("[UPLOAD] ERROR: All files have empty filenames", flush=True)
            return jsonify({'success': False, 'message': 'No valid files selected'}), 400

        parsed_data = []
        errors = []
        created_by = request.user.get('fullName', request.user.get('email'))

        for idx, file in enumerate(files, 1):
            print(f"\n[UPLOAD] [{idx}] Processing: {file.filename}", flush=True)
            
            if file.filename == '':
                print(f"[UPLOAD] [{idx}] Skipping empty filename", flush=True)
                continue

            try:
                # Save file temporarily
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
                file.save(filepath)
                print(f"[UPLOAD] [{idx}] Saved to: {filepath}", flush=True)
                
                # Check file exists and size
                if os.path.exists(filepath):
                    size = os.path.getsize(filepath)
                    print(f"[UPLOAD] [{idx}] File size: {size} bytes", flush=True)
                else:
                    raise Exception("File was not saved")

                # Upload to Azure Blob Storage
                print(f"[UPLOAD] [{idx}] Uploading to Azure...", flush=True)
                blob_url = azure_storage.upload_file(filepath, file.filename)
                print(f"[UPLOAD] [{idx}] Azure URL: {blob_url}", flush=True)

                # Parse resume
                print(f"[UPLOAD] [{idx}] Parsing resume...", flush=True)
                applicant_data = parse_resume(filepath)
                print(f"[UPLOAD] [{idx}] Name: {applicant_data.get('applicantName')}", flush=True)
                print(f"[UPLOAD] [{idx}] Email: {applicant_data.get('emailAddress')}", flush=True)
                print(f"[UPLOAD] [{idx}] Job Title: {applicant_data.get('jobTitle')}", flush=True)

                # Add blob URL and createdBy to applicant data
                applicant_data['blobUrl'] = blob_url
                applicant_data['createdBy'] = created_by

                # Add to database
                print(f"[UPLOAD] [{idx}] Inserting to database...", flush=True)
                result = db.insert_applicant(applicant_data)
                print(f"[UPLOAD] [{idx}] SUCCESS: {result}", flush=True)
                
                parsed_data.append(result)
                
                # Clean up
                try:
                    os.remove(filepath)
                    print(f"[UPLOAD] [{idx}] Cleaned up temp file", flush=True)
                except:
                    pass

            except Exception as e:
                error_msg = f"{file.filename}: {str(e)}"
                print(f"[UPLOAD] [{idx}] ERROR: {error_msg}", flush=True)
                import traceback
                traceback.print_exc()
                errors.append({'file': file.filename, 'error': str(e)})

        print(f"\n[UPLOAD] Summary - Successful: {len(parsed_data)}, Failed: {len(errors)}", flush=True)
        
        response_msg = f"Processed {len(parsed_data)} resumes successfully"
        if errors:
            response_msg += f". Errors: {len(errors)} - " + "; ".join([f"{e['file']}: {e['error']}" for e in errors])
        
        print(f"[UPLOAD] Response: {response_msg}", flush=True)
        print("="*60 + "\n", flush=True)
        
        return jsonify({
            'success': len(parsed_data) > 0,
            'message': response_msg,
            'data': {
                'parsed': parsed_data,
                'errors': errors
            }
        }), 200

    except Exception as e:
        error_msg = str(e)
        print(f"[UPLOAD] CRITICAL ERROR: {error_msg}", flush=True)
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': f'Upload failed: {error_msg}'}), 500


@app.route('/api/search', methods=['POST'])
@token_required
def search_applicants():
    """Search for applicants based on filters - Requires authentication"""
    try:
        filters = request.get_json()
        
        # Add createdBy filter to only show user's own resumes
        created_by = request.user.get('fullName', request.user.get('email'))
        filters['createdBy'] = created_by
        
        results = db.search_applicants(filters)
        
        return jsonify({
            'success': True,
            'count': len(results),
            'data': results
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/applicants', methods=['GET'])
@token_required
def get_all_applicants():
    """Get all applicants - Requires authentication"""
    try:
        skip = request.args.get('skip', 0, type=int)
        limit = request.args.get('limit', 100, type=int)
        
        # Get only resumes created by the current user
        created_by = request.user.get('fullName', request.user.get('email'))
        
        results = db.get_all_applicants(skip, limit, created_by)
        
        return jsonify({
            'success': True,
            'count': len(results),
            'data': results
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/applicants/<applicant_id>', methods=['GET'])
@token_required
def get_applicant(applicant_id):
    """Get specific applicant by ID - Requires authentication"""
    try:
        applicant = db.get_applicant(applicant_id)
        
        if not applicant:
            return jsonify({'success': False, 'message': 'Applicant not found'}), 404
        
        return jsonify({
            'success': True,
            'data': applicant
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/applicants/<applicant_id>', methods=['PUT'])
@token_required
def update_applicant(applicant_id):
    """Update applicant information - Requires authentication"""
    try:
        data = request.get_json()
        
        result = db.update_applicant(applicant_id, data)
        
        if not result:
            return jsonify({'success': False, 'message': 'Applicant not found'}), 404
        
        return jsonify({
            'success': True,
            'message': 'Applicant updated successfully',
            'data': result
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/applicants/<applicant_id>/download', methods=['GET'])
@token_required
def download_resume(applicant_id):
    """Download resume file from Azure Blob Storage - Requires authentication"""
    try:
        applicant = db.get_applicant(applicant_id)
        if not applicant:
            return jsonify({'success': False, 'message': 'Applicant not found'}), 404

        blob_url = applicant.get('blobUrl')
        
        # Debug logging
        print(f"Applicant: {applicant.get('applicantName')}")
        print(f"Blob URL: {blob_url}")
        print(f"Applicant data: {applicant}")
        
        if not blob_url:
            return jsonify({'success': False, 'message': 'Resume file not found. Please re-upload the resume.'}), 404

        file_extension = os.path.splitext(blob_url)[1] or '.pdf'
        safe_name = applicant['applicantName'].replace(' ', '_')
        filename = f"{safe_name}_resume{file_extension}"
        download_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

        if not azure_storage.download_file(blob_url, download_path):
            return jsonify({'success': False, 'message': 'Failed to download resume from Azure'}), 500

        @after_this_request
        def cleanup(response):
            try:
                if os.path.exists(download_path):
                    os.remove(download_path)
            except Exception:
                pass
            return response

        return send_file(download_path, as_attachment=False, download_name=filename)

    except Exception as e:
        print(f"Download error: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/applicants/<applicant_id>', methods=['DELETE'])
@token_required
def delete_applicant(applicant_id):
    """Delete applicant - Requires authentication"""
    try:
        # Get applicant data first to delete blob
        applicant = db.get_applicant(applicant_id)
        
        if applicant and applicant.get('blobUrl'):
            # Delete from Azure Blob Storage
            azure_storage.delete_file(applicant['blobUrl'])
        
        result = db.delete_applicant(applicant_id)
        
        if not result:
            return jsonify({'success': False, 'message': 'Applicant not found'}), 404
        
        return jsonify({
            'success': True,
            'message': 'Applicant deleted successfully'
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/admin/delete-all-resumes', methods=['DELETE'])
@token_required
def delete_all_resumes():
    """Delete all resumes from both Azure and database - Requires authentication"""
    try:
        # Delete all blobs from Azure
        blobs_deleted = azure_storage.delete_all_blobs()
        
        # Delete all records from database
        records_deleted = db.delete_all_applicants()
        
        return jsonify({
            'success': True,
            'message': f'Successfully deleted all resumes',
            'data': {
                'blobs_deleted': blobs_deleted,
                'records_deleted': records_deleted
            }
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


if __name__ == '__main__':
    # Create database tables
    db.create_tables()
    
    # Run Flask app
    app.run(host='0.0.0.0', port=5000, debug=True)
