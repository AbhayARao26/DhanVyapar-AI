#!/usr/bin/env python3
"""
Test script for DhanVyapar AI API
Tests all major endpoints to ensure they work correctly
"""

import requests
import json
import time

# API base URL
BASE_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint"""
    print("🔍 Testing health endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check passed: {data['status']}")
            print(f"📊 Agents available: {data['agents_available']}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_user_creation():
    """Test user creation"""
    print("\n👤 Testing user creation...")
    try:
        user_data = {
            "name": "Test User",
            "phone": "9876543210",
            "village": "Test Village"
        }
        response = requests.post(f"{BASE_URL}/users/create", json=user_data)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ User created: {data['user_id']}")
            return data['user_id']
        else:
            print(f"❌ User creation failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ User creation error: {e}")
        return None

def test_user_operations(user_id):
    """Test user operations"""
    print(f"\n🔧 Testing user operations for {user_id}...")
    
    # Test get user
    try:
        response = requests.get(f"{BASE_URL}/users/{user_id}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ User retrieved: {data['user_data']['full_name']}")
        else:
            print(f"❌ Get user failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Get user error: {e}")
    
    # Test update profile
    try:
        update_data = {
            "user_id": user_id,
            "age": 30,
            "gender": "Male",
            "primary_occupation": "Farmer",
            "monthly_income": 15000
        }
        response = requests.post(f"{BASE_URL}/users/update_profile", json=update_data)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Profile updated: {data['profile_completeness']}")
        else:
            print(f"❌ Profile update failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Profile update error: {e}")

def test_agent_endpoints(user_id):
    """Test agent endpoints"""
    print(f"\n🤖 Testing agent endpoints for {user_id}...")
    
    # Test credit score
    try:
        response = requests.post(f"{BASE_URL}/agents/credit_score", 
                               json={"user_id": user_id})
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Credit score: {data.get('credit_score', 'N/A')}")
        else:
            print(f"❌ Credit score failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Credit score error: {e}")
    
    # Test loan recommendation
    try:
        loan_data = {
            "user_id": user_id,
            "loan_amount": 50000,
            "loan_type": "agriculture",
            "purpose": "Crop cultivation",
            "tenure_months": 12
        }
        response = requests.post(f"{BASE_URL}/agents/loan_recommendation", json=loan_data)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Loan recommendation received")
        else:
            print(f"❌ Loan recommendation failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Loan recommendation error: {e}")
    
    # Test educational content
    try:
        edu_data = {
            "user_id": user_id,
            "topic": "savings"
        }
        response = requests.post(f"{BASE_URL}/agents/educational_content", json=edu_data)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Educational content received")
        else:
            print(f"❌ Educational content failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Educational content error: {e}")
    
    # Test chat
    try:
        chat_data = {
            "user_id": user_id,
            "message": "Hello, I need help with loan application",
            "language": "english"
        }
        response = requests.post(f"{BASE_URL}/agents/chat", json=chat_data)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Chat response received")
        else:
            print(f"❌ Chat failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Chat error: {e}")

def test_mfi_endpoints():
    """Test MFI endpoints"""
    print(f"\n🏦 Testing MFI endpoints...")
    
    # Test create MFI
    try:
        mfi_data = {
            "name": "Test MFI",
            "type": "NBFC",
            "region": "Karnataka",
            "contact_info": {
                "address": "Test Address",
                "phone": "08012345678",
                "email": "test@mfi.com"
            }
        }
        response = requests.post(f"{BASE_URL}/mfi/create", json=mfi_data)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ MFI created: {data['mfi_id']}")
            return data['mfi_id']
        else:
            print(f"❌ MFI creation failed: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ MFI creation error: {e}")
        return None

def test_get_users():
    """Test get all users"""
    print(f"\n📋 Testing get all users...")
    try:
        response = requests.get(f"{BASE_URL}/users")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Found {data['total_users']} users")
            return data['users']
        else:
            print(f"❌ Get users failed: {response.status_code}")
            return []
    except Exception as e:
        print(f"❌ Get users error: {e}")
        return []

def main():
    """Run all tests"""
    print("🚀 Starting DhanVyapar AI API Tests")
    print("=" * 50)
    
    # Test health
    if not test_health():
        print("❌ Health check failed. Make sure the API server is running.")
        return
    
    # Test user creation
    user_id = test_user_creation()
    if not user_id:
        print("❌ User creation failed. Stopping tests.")
        return
    
    # Test user operations
    test_user_operations(user_id)
    
    # Test agent endpoints
    test_agent_endpoints(user_id)
    
    # Test MFI endpoints
    mfi_id = test_mfi_endpoints()
    
    # Test get users
    users = test_get_users()
    
    print("\n" + "=" * 50)
    print("🎉 API Tests Completed!")
    print(f"✅ Created user: {user_id}")
    if mfi_id:
        print(f"✅ Created MFI: {mfi_id}")
    print(f"✅ Total users in system: {len(users)}")
    print("\n📖 Access API documentation at: http://localhost:8000/docs")

if __name__ == "__main__":
    main() 