"""
Reset applicants database - clears old records to allow fresh upload with improved parser
"""
import sqlite3
import os

db_path = 'applicants.db'

if os.path.exists(db_path):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Delete all applicants
        cursor.execute("DELETE FROM Applicants")
        conn.commit()
        
        print(f"✅ Database cleared successfully!")
        print(f"   All old applicant records have been deleted.")
        print(f"   Ready for fresh resume upload with full text extraction.")
        
        conn.close()
    except Exception as e:
        print(f"❌ Error: {str(e)}")
else:
    print(f"ℹ️  Database not found at {db_path}")
    print(f"   A new database will be created on first upload.")
