"""
Test the API endpoints
"""
import requests
import json

BASE_URL = "http://localhost:5000"

def test_health():
    """Test health check endpoint"""
    print("Testing health check...")
    response = requests.get(f"{BASE_URL}/api/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}\n")

def test_get_all_applicants():
    """Test get all applicants"""
    print("Testing get all applicants...")
    response = requests.get(f"{BASE_URL}/api/applicants?limit=5")
    data = response.json()
    print(f"Status: {response.status_code}")
    print(f"Count: {data.get('count')}")
    if data.get('data'):
        print(f"First applicant: {data['data'][0]}\n")

def test_search():
    """Test search functionality"""
    print("Testing search with keywords 'Engineer'...")
    payload = {
        'keywords': 'Engineer',
        'jobTitle': '',
        'city': '',
        'state': 'United States'
    }
    response = requests.post(f"{BASE_URL}/api/search", json=payload)
    data = response.json()
    print(f"Status: {response.status_code}")
    print(f"Found: {data.get('count')} results")
    if data.get('data'):
        for i, applicant in enumerate(data['data'][:3], 1):
            print(f"  {i}. {applicant['applicantName']} - {applicant['jobTitle']}")
    print()

def test_search_by_job_title():
    """Test search by job title"""
    print("Testing search with Job Title 'Data Engineer'...")
    payload = {
        'keywords': '',
        'jobTitle': 'Engineer',
        'city': '',
        'state': 'United States'
    }
    response = requests.post(f"{BASE_URL}/api/search", json=payload)
    data = response.json()
    print(f"Status: {response.status_code}")
    print(f"Found: {data.get('count')} results\n")

if __name__ == '__main__':
    print("=" * 80)
    print("API ENDPOINT TESTS")
    print("=" * 80 + "\n")
    
    test_health()
    test_get_all_applicants()
    test_search()
    test_search_by_job_title()
    
    print("=" * 80)
    print("Tests completed!")
    print("=" * 80)
