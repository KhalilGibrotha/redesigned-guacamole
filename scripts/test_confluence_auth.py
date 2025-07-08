#!/usr/bin/env python3
"""
Test Confluence authentication and API access
"""

import base64
import requests
import sys

# Your credentials from vars.yml
confluence_url = "https://alexgambino22.atlassian.net/wiki"
confluence_space = "Ansible"
confluence_auth = "YWxleGdhbWJpbm8yMkBnbWFpbC5jb206QVRBVFQzeEZmR0Ywcm9qcXdIS0JWbHhDVVZCYzc4N0oyaDhuNUJ6Tld2dmc2RmtGX1lRYkxPamVXOGFzVm1xbGhtT3hINUFVR2RsLWRVeVN3VkF5VEVYc3R1WWFYamFES0RIaWtKN255SjF4UHdZYTY1ZVNvQlFtRE5LMlM5Um9Wa0t3U3daOUU1WnlYajVWMFRrVzh1NFo3NGJveUVTUmk3aGdLSExPWVRNcS1UYm1WcFdzWU13PTYwQTM3RTA5"

def test_confluence_auth():
    """Test basic Confluence API access"""
    
    print("🔍 Testing Confluence Authentication...")
    print(f"URL: {confluence_url}")
    print(f"Space: {confluence_space}")
    print(f"Auth (first 20 chars): {confluence_auth[:20]}...")
    
    # Test basic API access
    headers = {
        "Authorization": f"Basic {confluence_auth}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    # Test 1: Check if we can access the API at all
    try:
        response = requests.get(
            f"{confluence_url}/rest/api/user/current",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            user_info = response.json()
            print(f"✅ Authentication successful!")
            print(f"   User: {user_info.get('displayName', 'Unknown')}")
            print(f"   Email: {user_info.get('email', 'Unknown')}")
        else:
            print(f"❌ Authentication failed: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False
    
    # Test 2: Check space access
    try:
        response = requests.get(
            f"{confluence_url}/rest/api/space/{confluence_space}",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            space_info = response.json()
            print(f"✅ Space access successful!")
            print(f"   Space: {space_info.get('name', 'Unknown')}")
            print(f"   Key: {space_info.get('key', 'Unknown')}")
        else:
            print(f"❌ Space access failed: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"❌ Space access error: {e}")
        return False
    
    # Test 3: Try to search for existing pages
    try:
        response = requests.get(
            f"{confluence_url}/rest/api/content",
            headers=headers,
            params={
                "spaceKey": confluence_space,
                "limit": 5
            },
            timeout=10
        )
        
        if response.status_code == 200:
            content_info = response.json()
            print(f"✅ Content search successful!")
            print(f"   Found {len(content_info.get('results', []))} pages")
            for page in content_info.get('results', [])[:3]:
                print(f"   - {page.get('title', 'Unknown')}")
        else:
            print(f"❌ Content search failed: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"❌ Content search error: {e}")
        return False
    
    print("\n🎉 All tests passed! Your Confluence setup is working.")
    return True

if __name__ == "__main__":
    if test_confluence_auth():
        sys.exit(0)
    else:
        sys.exit(1)
