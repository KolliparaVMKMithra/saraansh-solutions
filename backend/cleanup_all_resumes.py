#!/usr/bin/env python3
"""
Cleanup Script - Delete all resumes from Azure Blob Storage and Database
This script safely removes all resume data from both storage locations.

Usage:
    python cleanup_all_resumes.py

WARNING: This action cannot be undone. All resume data will be permanently deleted.
"""

import os
import sys
from datetime import datetime

# Load environment variables
import dotenv
dotenv.load_dotenv(verbose=True)

from database import Database
from azure_storage import azure_storage


def main():
    print("\n" + "=" * 70)
    print("RESUME CLEANUP SCRIPT".center(70))
    print("=" * 70)
    print("\n⚠️  WARNING: This will permanently delete ALL resumes from:")
    print("   - Azure Blob Storage")
    print("   - Database")
    print("\n" + "-" * 70)
    
    # Confirmation prompt
    user_input = input("\nType 'DELETE ALL' to confirm deletion: ").strip()
    
    if user_input != "DELETE ALL":
        print("\n❌ Cleanup cancelled. No data was deleted.")
        return False
    
    print("\n" + "=" * 70)
    print("Starting cleanup process...")
    print("=" * 70)
    
    try:
        # Initialize database
        print("\n📦 Connecting to database...")
        db = Database()
        
        # Delete all blobs from Azure
        print("\n🗑️  Deleting blobs from Azure Blob Storage...")
        blobs_deleted = azure_storage.delete_all_blobs()
        print(f"   ✅ Successfully deleted {blobs_deleted} blobs from Azure")
        
        # Delete all records from database
        print("\n🗑️  Deleting records from database...")
        records_deleted = db.delete_all_applicants()
        print(f"   ✅ Successfully deleted {records_deleted} records from database")
        
        print("\n" + "=" * 70)
        print("CLEANUP COMPLETED SUCCESSFULLY".center(70))
        print("=" * 70)
        print(f"\nSummary:")
        print(f"  - Azure Blobs Deleted: {blobs_deleted}")
        print(f"  - Database Records Deleted: {records_deleted}")
        print(f"  - Timestamp: {datetime.now().isoformat()}")
        print("\n✅ All resumes have been permanently deleted.")
        print("=" * 70 + "\n")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error during cleanup: {str(e)}")
        print("   The cleanup process failed. Some data may still exist.")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
