"""
Resume Parser Module
Extracts structured data from DOCX and PDF files
"""
import re
import os
from pathlib import Path
from typing import Dict, Any
import uuid
from datetime import datetime

try:
    from docx import Document
except ImportError:
    Document = None

try:
    import pdfplumber
except ImportError:
    pdfplumber = None


def parse_docx(filepath: str) -> str:
    """Extract text from DOCX file - comprehensive extraction"""
    if not Document:
        raise ImportError("python-docx not installed. Install with: pip install python-docx")
    
    doc = Document(filepath)
    text_parts = []

    # Extract from paragraphs (including all runs for better formatting)
    for para in doc.paragraphs:
        para_text = para.text.strip()
        if para_text:
            text_parts.append(para_text)

    # Extract from tables
    for table in doc.tables:
        for row in table.rows:
            row_text = []
            for cell in row.cells:
                cell_text = cell.text.strip()
                if cell_text:
                    row_text.append(cell_text)
            if row_text:
                text_parts.append(" | ".join(row_text))

    # Extract from headers/footers
    for section in doc.sections:
        header = section.header
        if header:
            for para in header.paragraphs:
                header_text = para.text.strip()
                if header_text:
                    text_parts.append(header_text)
        footer = section.footer
        if footer:
            for para in footer.paragraphs:
                footer_text = para.text.strip()
                if footer_text:
                    text_parts.append(footer_text)

    # Extract from shapes/textboxes (usually contain important content)
    try:
        for shape in doc.element.body.iter():
            if hasattr(shape, 'text') and shape.text:
                shape_text = shape.text.strip()
                if shape_text and shape_text not in text_parts:
                    text_parts.append(shape_text)
    except Exception:
        pass  # Some shapes may not have text attribute

    full_text = "\n".join(text_parts)
    return full_text


def parse_pdf(filepath: str) -> str:
    """Extract text from PDF file with better handling"""
    if not pdfplumber:
        raise ImportError("pdfplumber not installed. Install with: pip install pdfplumber")
    
    text_parts = []
    try:
        with pdfplumber.open(filepath) as pdf:
            for page_num, page in enumerate(pdf.pages):
                try:
                    page_text = page.extract_text()
                    if page_text and page_text.strip():
                        text_parts.append(page_text.strip())
                except Exception:
                    # Skip pages that fail to extract
                    continue
    except Exception as e:
        raise Exception(f"Error reading PDF: {str(e)}")
    
    return "\n".join(text_parts)


def extract_email(text: str) -> str:
    """Extract email address from text"""
    pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    matches = re.findall(pattern, text)
    return matches[0] if matches else ""


def extract_phone(text: str) -> str:
    """Extract phone number from text"""
    # US and international formats
    patterns = [
        r'\+?1?\s*\(?(\d{3})\)?[-.\s]?(\d{3})[-.\s]?(\d{4})',  # US format
        r'\+\d{1,3}\s?\d{1,14}',  # International format
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, text)
        if matches:
            match = matches[0]
            if isinstance(match, tuple):
                return ''.join(match)
            return match
    return ""


def extract_name(text: str, filename: str) -> str:
    """
    Extract applicant name
    Priority: filename > resume header
    """
    # Try to extract from filename (format: ID_CODE_NAME.ext)
    # Example: 103037724949_1823_4_Michael Welch.docx
    filename_no_ext = os.path.splitext(filename)[0]
    parts = filename_no_ext.split('_')
    
    if len(parts) >= 4:
        # The name is usually the last part(s) after the ID and code
        name = '_'.join(parts[3:]).strip()
        if name:
            return name
    
    # Fallback: try to extract name from first line of resume
    lines = text.split('\n')
    for line in lines[:5]:
        line = line.strip()
        if line and len(line) < 50:  # Names are typically shorter
            return line
    
    return "Unknown"


def extract_name_from_filename(filename: str) -> str:
    """Extract name from filename pattern"""
    filename_no_ext = os.path.splitext(filename)[0]
    parts = filename_no_ext.split('_')
    
    if len(parts) >= 4:
        name = '_'.join(parts[3:]).replace('_', ' ').strip()
        return name
    
    return ""


def extract_location(text: str) -> tuple:
    """Extract city and state from text"""
    # Look for city, state patterns
    # Common US states abbreviations
    us_states = {
        'AL': 'Alabama', 'AK': 'Alaska', 'AZ': 'Arizona', 'AR': 'Arkansas',
        'CA': 'California', 'CO': 'Colorado', 'CT': 'Connecticut', 'DE': 'Delaware',
        'FL': 'Florida', 'GA': 'Georgia', 'HI': 'Hawaii', 'ID': 'Idaho',
        'IL': 'Illinois', 'IN': 'Indiana', 'IA': 'Iowa', 'KS': 'Kansas',
        'KY': 'Kentucky', 'LA': 'Louisiana', 'ME': 'Maine', 'MD': 'Maryland',
        'MA': 'Massachusetts', 'MI': 'Michigan', 'MN': 'Minnesota', 'MS': 'Mississippi',
        'MO': 'Missouri', 'MT': 'Montana', 'NE': 'Nebraska', 'NV': 'Nevada',
        'NH': 'New Hampshire', 'NJ': 'New Jersey', 'NM': 'New Mexico', 'NY': 'New York',
        'NC': 'North Carolina', 'ND': 'North Dakota', 'OH': 'Ohio', 'OK': 'Oklahoma',
        'OR': 'Oregon', 'PA': 'Pennsylvania', 'RI': 'Rhode Island', 'SC': 'South Carolina',
        'SD': 'South Dakota', 'TN': 'Tennessee', 'TX': 'Texas', 'UT': 'Utah',
        'VT': 'Vermont', 'VA': 'Virginia', 'WA': 'Washington', 'WV': 'West Virginia',
        'WI': 'Wisconsin', 'WY': 'Wyoming'
    }
    
    city = ""
    state = ""
    
    # Search for state abbreviations
    for abbrev, full_name in us_states.items():
        if abbrev in text or full_name in text:
            state = abbrev
            break
    
    # Try to extract city (usually before state)
    pattern = r'([A-Z][a-z]+),\s*([A-Z]{2})'
    match = re.search(pattern, text)
    if match:
        city = match.group(1)
        state = match.group(2)
    
    return city, state


def extract_job_title(text: str) -> str:
    """Extract job title from resume"""
    # Common job title keywords
    title_keywords = [
        'Software Engineer', 'Data Engineer', 'Data Scientist', 'Full Stack',
        'Frontend', 'Backend', 'Python Developer', 'Java Developer',
        'DevOps', 'Cloud Architect', 'Solutions Architect', 'Product Manager',
        'QA Engineer', 'Business Analyst', 'System Administrator',
        'Database Administrator', 'Network Engineer', 'Security Engineer'
    ]
    
    text_lower = text.lower()
    
    for title in title_keywords:
        if title.lower() in text_lower:
            return title
    
    # If no exact match, try to find "Job Title:" or similar patterns
    pattern = r'(?:job\s*title|position|role)[\s:]*([^\n]+)'
    match = re.search(pattern, text, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    
    return "Senior Professional"


def extract_work_authorization(text: str) -> str:
    """Extract work authorization status"""
    auth_keywords = {
        'US Citizen': ['us citizen', 'u.s. citizen'],
        'Green Card Holder': ['green card', 'permanent resident'],
        'H-1B': ['h-1b', 'h1b'],
        'L-1': ['l-1', 'l1'],
        'O-1': ['o-1', 'o1'],
        'F-1': ['f-1', 'f1', 'optional practical training', 'opt'],
        'TN': ['tn visa', 'tn'],
        'Willing to Sponsor': ['willing to sponsor', 'require sponsorship'],
    }
    
    text_lower = text.lower()
    
    for auth_type, keywords in auth_keywords.items():
        for keyword in keywords:
            if keyword in text_lower:
                return auth_type
    
    return "Not Specified"


def extract_skills(text: str) -> str:
    """Extract technology skills from resume text"""
    skills_section = []
    text_lower = text.lower()

    # Known keywords for tech skills and tools
    skill_keywords = [
        'python', 'java', 'javascript', 'react', 'angular', 'vue', 'node',
        'express', 'django', 'flask', 'c++', 'c#', 'ruby', 'php', 'sql',
        'mysql', 'postgresql', 'mongodb', 'azure', 'aws', 'gcp', 'docker',
        'kubernetes', 'linux', 'git', 'gitlab', 'github', 'jira', 'confluence',
        'html', 'css', 'tailwind', 'bootstrap', 'rest api', 'graphql',
        'machine learning', 'data science', 'pandas', 'numpy', 'tensorflow',
        'pytorch', 'spark', 'hadoop', 'power bi', 'tableau', 'salesforce',
        'sap', 'oracle', 'microservices', 'devops', 'ci/cd', 'junit', 'selenium',
        'typescript', 'swift', 'objective-c', 'kotlin', 'android', 'ios',
        'animation', 'after effects', 'maya', 'blender', 'unity', 'unreal',
        'ui/ux', 'problem solving', 'agile', 'scrum'
    ]

    # Find explicit Skills section lines
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    for idx, line in enumerate(lines):
        if re.search(r'\b(skills?|technical skills|tools|technologies)\b', line, re.IGNORECASE):
            following_lines = lines[idx:idx + 6]
            for section_line in following_lines:
                skills_section.extend(re.split(r'[,:;\|\-\/]', section_line))
            break

    found_skills = set()
    for keyword in skill_keywords:
        if keyword in text_lower:
            found_skills.add(keyword.title())

    for part in skills_section:
        part_text = part.strip().lower()
        for keyword in skill_keywords:
            if keyword in part_text:
                found_skills.add(keyword.title())

    return ', '.join(sorted(found_skills)) if found_skills else 'Not Specified'


def parse_resume(filepath: str) -> Dict[str, Any]:
    """
    Parse resume file and extract structured data
    
    Args:
        filepath: Path to resume file (DOCX or PDF)
    
    Returns:
        Dictionary with extracted applicant data
    """
    try:
        file_ext = Path(filepath).suffix.lower()
        filename = os.path.basename(filepath)
        
        # Extract text based on file type
        if file_ext in ['.docx', '.doc']:
            text = parse_docx(filepath)
        elif file_ext == '.pdf':
            text = parse_pdf(filepath)
        else:
            raise ValueError(f"Unsupported file type: {file_ext}")
        
        # Extract structured data
        applicant_data = {
            'applicantId': str(uuid.uuid4()),
            'applicantName': extract_name_from_filename(filename) or extract_name(text, filename),
            'emailAddress': extract_email(text),
            'mobileNumber': extract_phone(text),
            'city': extract_location(text)[0],
            'state': extract_location(text)[1],
            'applicantStatus': 'Active',
            'jobTitle': extract_job_title(text),
            'ownership': 'Internal',
            'workAuthorization': extract_work_authorization(text),
            'source': 'Resume Upload',
            'createdBy': 'System',
            'createdOn': datetime.now().isoformat(),
            'techSkills': extract_skills(text),
            'resumeText': text,
        }
        
        return applicant_data
        
    except Exception as e:
        raise Exception(f"Error parsing resume: {str(e)}")


if __name__ == '__main__':
    # Test parsing
    test_file = 'test_resume.pdf'
    if os.path.exists(test_file):
        result = parse_resume(test_file)
        print("Parsed Resume Data:")
        for key, value in result.items():
            print(f"  {key}: {value}")
