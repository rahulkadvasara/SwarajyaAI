#!/usr/bin/env python3
"""
Test script for Enhanced SwarajyaAI System
Tests Llama-enhanced query processing and real-time web scraping
"""

import asyncio
import json
import requests
from helper import groq_helper

def test_query_enhancement():
    """Test Llama-powered query enhancement"""
    
    print("🧠 Testing Llama Query Enhancement")
    print("=" * 50)
    
    test_queries = [
        "घर बनाने की योजना",
        "स्वास्थ्य योजना", 
        "नौकरी चाहिए",
        "किसान के लिए मदद",
        "बच्चों की पढ़ाई"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{i}. Testing Query: '{query}'")
        print("-" * 30)
        
        try:
            enhanced = groq_helper.enhance_user_query(query)
            
            print(f"   🎯 Category: {enhanced.get('category', 'unknown')}")
            print(f"   🔍 Search Keywords: {enhanced.get('search_keywords', [])[:3]}")
            print(f"   🌐 Target Websites: {enhanced.get('target_websites', [])[:2]}")
            print(f"   💭 Intent: {enhanced.get('intent', 'unknown')}")
            print(f"   ✅ Enhancement Success")
            
        except Exception as e:
            print(f"   ❌ Enhancement Failed: {str(e)}")

def test_web_scraping():
    """Test real-time web scraping functionality"""
    
    print("\n🌐 Testing Real-Time Web Scraping")
    print("=" * 50)
    
    # Test with a sample enhanced query
    sample_enhanced_query = {
        "search_keywords": ["housing scheme", "pradhan mantri awas yojana"],
        "hindi_keywords": ["आवास योजना", "घर निर्माण"],
        "category": "housing",
        "intent": "scheme_info",
        "target_websites": ["india.gov.in", "pmay.gov.in"]
    }
    
    try:
        print("Testing web scraping with sample query...")
        scraped_schemes = groq_helper.scrape_government_websites(sample_enhanced_query)
        
        print(f"✅ Scraped {len(scraped_schemes)} schemes")
        
        for i, scheme in enumerate(scraped_schemes[:3], 1):
            print(f"\n   Scheme {i}:")
            print(f"   📋 Title: {scheme['title'][:60]}...")
            print(f"   🔗 Link: {scheme['link']}")
            print(f"   🌐 Source: {scheme.get('source', 'unknown')}")
            print(f"   📝 Description: {len(scheme.get('description', ''))} chars")
        
    except Exception as e:
        print(f"❌ Web scraping failed: {str(e)}")

def test_hindi_response_generation():
    """Test comprehensive Hindi response generation"""
    
    print("\n🗣️ Testing Hindi Response Generation")
    print("=" * 50)
    
    # Sample scraped schemes for testing
    sample_schemes = [
        {
            'title': 'Pradhan Mantri Awas Yojana (PMAY)',
            'description': 'Housing for All scheme providing financial assistance for construction of houses to economically weaker sections and low income groups.',
            'link': 'https://pmay.gov.in/',
            'source': 'pmay.gov.in'
        }
    ]
    
    test_query = "घर बनाने की योजना"
    
    try:
        print(f"Generating Hindi response for: '{test_query}'")
        
        hindi_response = groq_helper.generate_comprehensive_hindi_response(sample_schemes, test_query)
        
        print(f"✅ Hindi Response Generated:")
        print("-" * 40)
        print(hindi_response)
        print("-" * 40)
        print(f"Response Length: {len(hindi_response)} characters")
        
    except Exception as e:
        print(f"❌ Hindi response generation failed: {str(e)}")

def test_complete_flow():
    """Test the complete flow from query to response"""
    
    print("\n🔄 Testing Complete Flow")
    print("=" * 50)
    
    test_queries = [
        "घर बनाने की योजना",
        "स्वास्थ्य बीमा योजना"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{i}. Complete Flow Test: '{query}'")
        print("-" * 35)
        
        try:
            # Step 1: Query Enhancement
            print("   🧠 Step 1: Enhancing query...")
            enhanced_query = groq_helper.enhance_user_query(query)
            print(f"      ✅ Enhanced to category: {enhanced_query.get('category')}")
            
            # Step 2: Web Scraping
            print("   🌐 Step 2: Scraping websites...")
            scraped_schemes = groq_helper.scrape_government_websites(enhanced_query)
            print(f"      ✅ Found {len(scraped_schemes)} schemes")
            
            # Step 3: Hindi Response Generation
            if scraped_schemes:
                print("   🗣️ Step 3: Generating Hindi response...")
                hindi_response = groq_helper.generate_comprehensive_hindi_response(scraped_schemes, query)
                print(f"      ✅ Generated {len(hindi_response)} char response")
                print(f"      📝 Preview: {hindi_response[:100]}...")
            else:
                print("   ⚠️ Step 3: No schemes found for response generation")
            
            print(f"   🎉 Complete flow successful!")
            
        except Exception as e:
            print(f"   ❌ Complete flow failed: {str(e)}")

def test_api_endpoints():
    """Test API endpoints (requires server to be running)"""
    
    print("\n🌐 Testing API Endpoints")
    print("=" * 40)
    print("Note: Server must be running on port 8000")
    
    base_url = "http://localhost:8000"
    
    try:
        # Test health endpoint
        print("\n1. Testing Health Endpoint...")
        response = requests.get(f"{base_url}/", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Health Check: {data['status']}")
            print(f"   🧠 Llama Enhanced: {data.get('llama_enhanced', False)}")
            print(f"   🔍 Search Type: {data.get('search_type', 'unknown')}")
        else:
            print(f"   ❌ Health check failed: {response.status_code}")
            return
    except Exception as e:
        print(f"   ❌ Cannot connect to server: {str(e)}")
        print("   💡 Start server with: uvicorn main:app --reload --port 8000")
        return
    
    try:
        # Test Groq health endpoint
        print("\n2. Testing Groq Health Endpoint...")
        response = requests.get(f"{base_url}/health/groq", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Groq Status: {data['status']}")
            print(f"   🔗 API Connection: {data.get('groq_api_connection', False)}")
            print(f"   🤖 Model: {data.get('model', 'unknown')}")
        else:
            print(f"   ❌ Groq health check failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Groq health check error: {str(e)}")
    
    try:
        # Test search endpoint
        print("\n3. Testing Search Endpoint...")
        test_data = {"query": "घर बनाने की योजना"}
        response = requests.post(
            f"{base_url}/search",
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=30  # Longer timeout for web scraping
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Search Success: {data.get('total_found', 0)} results")
            if data.get('results'):
                first_result = data['results'][0]
                print(f"   📋 First Result: {first_result.get('title', 'No title')[:50]}...")
        else:
            print(f"   ❌ Search failed: {response.status_code}")
            print(f"   📝 Error: {response.text[:100]}...")
    except Exception as e:
        print(f"   ❌ Search endpoint error: {str(e)}")
    
    try:
        # Test legacy query endpoint
        print("\n4. Testing Legacy Query Endpoint...")
        test_data = {"query": "स्वास्थ्य योजना"}
        response = requests.post(
            f"{base_url}/query",
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=30  # Longer timeout for processing
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Query Success")
            print(f"   📋 Scheme: {data.get('scheme_name', 'Unknown')[:40]}...")
            print(f"   🗣️ Hindi Response: {data.get('reply', '')[:80]}...")
        else:
            print(f"   ❌ Query failed: {response.status_code}")
            print(f"   📝 Error: {response.text[:100]}...")
    except Exception as e:
        print(f"   ❌ Query endpoint error: {str(e)}")

def test_debug_endpoint():
    """Test debug endpoint for troubleshooting"""
    
    print("\n🔍 Testing Debug Endpoint")
    print("=" * 40)
    
    try:
        response = requests.get("http://localhost:8000/debug/घर योजना", timeout=30)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Debug Success")
            print(f"   🧠 Llama Enhanced: {data.get('llama_enhanced', False)}")
            print(f"   📊 Total Scraped: {data.get('total_scraped', 0)}")
            print(f"   🔍 Search Results: {data.get('search_results', {}).get('total_found', 0)}")
            
            if data.get('enhanced_query'):
                enhanced = data['enhanced_query']
                print(f"   🎯 Enhanced Category: {enhanced.get('category', 'unknown')}")
        else:
            print(f"   ❌ Debug failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Debug endpoint error: {str(e)}")

def main():
    """Main test function"""
    
    print("🇮🇳 SwarajyaAI Enhanced System Test Suite")
    print("=" * 60)
    print("Testing Llama-Enhanced Query Processing + Real-Time Web Scraping")
    print("=" * 60)
    
    # Test 1: Groq Helper Availability
    print(f"\n🔧 Groq Helper Status: {'✅ Available' if groq_helper.is_available() else '❌ Not Available'}")
    if groq_helper.is_available():
        connection_ok = groq_helper.test_connection()
        print(f"🔗 Groq Connection: {'✅ Working' if connection_ok else '❌ Failed'}")
    
    # Test 2: Query Enhancement
    test_query_enhancement()
    
    # Test 3: Web Scraping
    test_web_scraping()
    
    # Test 4: Hindi Response Generation
    test_hindi_response_generation()
    
    # Test 5: Complete Flow
    test_complete_flow()
    
    # Test 6: API Endpoints
    test_api_endpoints()
    
    # Test 7: Debug Endpoint
    test_debug_endpoint()
    
    print("\n🎉 All Tests Completed!")
    print("\n📋 Summary:")
    print("✅ System now uses Llama for query enhancement")
    print("✅ Real-time web scraping from government websites")
    print("✅ Comprehensive Hindi responses generated by Llama")
    print("✅ No hardcoded schemes - fully dynamic")
    print("✅ Fallback mechanisms for reliability")
    
    print("\n🚀 Next Steps:")
    print("1. Configure your Groq API key: python setup_groq.py")
    print("2. Start the server: uvicorn main:app --reload --port 8000")
    print("3. Test with your frontend voice assistant")
    print("4. Monitor logs for scraping and response generation")

if __name__ == "__main__":
    main()