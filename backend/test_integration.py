#!/usr/bin/env python3
"""
Test script for SwarajyaAI Groq integration
Tests the complete flow from query to Hindi response generation
"""

import asyncio
import json
from helper import groq_helper
from main import search_real_government_schemes, convert_search_to_legacy_format

def test_complete_flow():
    """Test the complete flow from search to Hindi response"""
    
    print("🧪 Testing Complete SwarajyaAI Flow")
    print("=" * 50)
    
    # Test queries from frontend examples
    test_queries = [
        "घर बनाने की योजना",
        "स्वास्थ्य योजना", 
        "रोजगार की योजना",
        "शिक्षा योजना",
        "किसान के लिए योजना"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{i}. Testing Query: '{query}'")
        print("-" * 30)
        
        try:
            # Step 1: Search for schemes
            search_results = search_real_government_schemes(query)
            print(f"   📊 Found {search_results.total_found} schemes")
            
            if search_results.results:
                # Step 2: Convert to legacy format (generates Hindi response)
                legacy_response = convert_search_to_legacy_format(search_results)
                
                print(f"   🎯 Scheme: {legacy_response.scheme_name}")
                print(f"   🔗 Link: {legacy_response.link}")
                print(f"   💬 Hindi Response:")
                print(f"      {legacy_response.reply[:100]}...")
                print(f"   ✅ Success")
            else:
                print(f"   ❌ No schemes found")
                
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
    
    print(f"\n🏁 Test completed!")

def test_groq_helper():
    """Test the Groq helper module specifically"""
    
    print("\n🔧 Testing Groq Helper Module")
    print("=" * 40)
    
    # Test availability
    print(f"Groq Available: {groq_helper.is_available()}")
    
    if groq_helper.is_available():
        # Test connection
        connection_ok = groq_helper.test_connection()
        print(f"Connection Test: {'✅ Pass' if connection_ok else '❌ Fail'}")
        
        if connection_ok:
            # Test Hindi response generation
            test_scheme = {
                "title": "Test Scheme",
                "description": "This is a test government scheme for demonstration.",
                "link": "https://example.gov.in"
            }
            
            response = groq_helper.generate_hindi_response(test_scheme, "test query")
            print(f"Hindi Response Generated: {'✅ Yes' if response else '❌ No'}")
            print(f"Response Length: {len(response)} characters")
    else:
        print("❌ Groq not available - will use fallback responses")

def test_api_endpoints():
    """Test API endpoints (requires server to be running)"""
    
    print("\n🌐 Testing API Endpoints")
    print("=" * 30)
    print("Note: This requires the FastAPI server to be running on port 8000")
    
    import requests
    
    try:
        # Test health endpoint
        response = requests.get("http://localhost:8000/")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Main Health Check: {data['status']}")
            print(f"   Groq Available: {data.get('groq_available', 'Unknown')}")
        else:
            print(f"❌ Main Health Check Failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Cannot connect to server: {str(e)}")
        print("   Make sure to run: uvicorn main:app --reload --port 8000")
        return
    
    try:
        # Test Groq health endpoint
        response = requests.get("http://localhost:8000/health/groq")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Groq Health Check: {data['status']}")
            print(f"   Connection: {data.get('groq_api_connection', 'Unknown')}")
        else:
            print(f"❌ Groq Health Check Failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Groq health check error: {str(e)}")
    
    try:
        # Test query endpoint
        test_data = {"query": "घर बनाने की योजना"}
        response = requests.post(
            "http://localhost:8000/query",
            json=test_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Query Endpoint: Success")
            print(f"   Scheme: {data.get('scheme_name', 'Unknown')}")
            print(f"   Response: {data.get('reply', '')[:50]}...")
        else:
            print(f"❌ Query Endpoint Failed: {response.status_code}")
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"❌ Query endpoint error: {str(e)}")

def main():
    """Main test function"""
    
    print("🇮🇳 SwarajyaAI Integration Test Suite")
    print("=" * 60)
    
    # Test 1: Groq Helper Module
    test_groq_helper()
    
    # Test 2: Complete Flow
    test_complete_flow()
    
    # Test 3: API Endpoints (if server is running)
    test_api_endpoints()
    
    print("\n🎉 All tests completed!")
    print("\n📋 Next Steps:")
    print("1. If Groq is not available, run: python setup_groq.py")
    print("2. Start the server: uvicorn main:app --reload --port 8000")
    print("3. Test your frontend with the voice assistant")

if __name__ == "__main__":
    main()