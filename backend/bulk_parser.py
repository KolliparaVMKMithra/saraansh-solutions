"""
Bulk Resume Parser
Parses all resumes in the Sample Resumes directory and imports them to database
"""
import os
import sys
from pathlib import Path
from resume_parser import parse_resume
from database import Database
import json


def bulk_parse_resumes(resumes_directory: str, output_file: str = "parsed_resumes.json"):
    """
    Parse all resumes in a directory
    """
    # Initialize database
    db = Database()
    db.create_tables()
    
    # Get all resume files
    resume_files = []
    resumes_path = Path(resumes_directory)
    
    if not resumes_path.exists():
        print(f"Error: Directory not found: {resumes_directory}")
        return
    
    # Find all DOCX and PDF files
    for ext in ['*.pdf', '*.docx', '*.doc']:
        resume_files.extend(resumes_path.glob(ext))
    
    print(f"Found {len(resume_files)} resume files")
    print("-" * 80)
    
    parsed_data = []
    failed_resumes = []
    
    for idx, resume_path in enumerate(resume_files, 1):
        try:
            print(f"[{idx}/{len(resume_files)}] Parsing: {resume_path.name}")
            
            # Parse resume
            applicant_data = parse_resume(str(resume_path))
            
            # Insert into database
            result = db.insert_applicant(applicant_data)
            
            parsed_data.append(applicant_data)
            print(f"  ✓ Success: {applicant_data['applicantName']}")
            
        except Exception as e:
            failed_resumes.append({
                'file': resume_path.name,
                'error': str(e)
            })
            print(f"  ✗ Failed: {str(e)}")
    
    print("-" * 80)
    print(f"\nSummary:")
    print(f"  Total Processed: {len(resume_files)}")
    print(f"  Successfully Parsed: {len(parsed_data)}")
    print(f"  Failed: {len(failed_resumes)}")
    
    # Save parsed data to JSON
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            'total': len(resume_files),
            'successful': len(parsed_data),
            'failed': len(failed_resumes),
            'data': parsed_data,
            'errors': failed_resumes
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\nParsed data saved to: {output_file}")
    
    if failed_resumes:
        print("\nFailed resumes:")
        for failed in failed_resumes:
            print(f"  - {failed['file']}: {failed['error']}")
    
    db.close()


if __name__ == '__main__':
    # Get the sample resumes directory
    # This should be run from the backend directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Look for Sample Resumes directory in parent directories
    sample_resumes_dir = None
    
    # Check various possible locations
    possible_paths = [
        os.path.join(current_dir, '..', '..', 'Sample Resumes'),
        os.path.join(current_dir, 'Sample Resumes'),
        r'c:\Users\DELL\Documents\Personals\Saraansh solutions\Sample Resumes',
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            sample_resumes_dir = path
            break
    
    if not sample_resumes_dir:
        print("Error: Could not find Sample Resumes directory")
        print(f"Current directory: {current_dir}")
        print("Please provide the path as an argument:")
        print(f"  python {sys.argv[0]} <path_to_sample_resumes>")
        
        if len(sys.argv) > 1:
            sample_resumes_dir = sys.argv[1]
        else:
            sys.exit(1)
    
    print(f"Using Sample Resumes directory: {sample_resumes_dir}")
    bulk_parse_resumes(sample_resumes_dir)
