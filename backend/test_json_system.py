#!/usr/bin/env python3
"""
Test script for JSON-based schemes system
Verifies that the schemes database loads correctly and search works
"""

import json
import sys
from main import load_schemes_database, search_government_schemes, calculate_relevance_score

def test_json_loading():
    """Test loading schemes from JSON file"""
    print("🧪 Testing JSON Database Loading")
    print("=" * 40)
    
    try:
        schemes_db = load_schemes_database()
        
        if not schemes_db:
            print("❌ Failed to load schemes database")
            return False
        
        total_schemes = sum(len(schemes) for schemes in schemes_db.values())
        
        print(f"✅ Successfully loaded schemes database")
        print(f"📁 Categories: {len(schemes_db)}")
        print(f"📄 Total schemes: {total_schemes}")
        
        # List categories
        print(f"\n📋 Available categories:")
        for category, schemes in schemes_db.items():
            print(f"   • {category}: {len(schemes)} schemes")
        
        return True
        
    except Exception as e:
        print(f"❌ Error loading database: {str(e)}")
        return False

def test_search_functionality():
    """Test search functionality with JSON database"""
    print("\n🧪 Testing Search Functionality")
    print("=" * 40)
    
    test_queries = [
        "घर बनाने की योजना",
        "स्वास्थ्य योजना",
        "employment",
        "किसान",
        "pension"
    ]
    
    success_count = 0
    
    for query in test_queries:
        try:
            print(f"\n🔍 Testing query: '{query}'")
            
            search_results = search_government_schemes(query)
            
            print(f"   📊 Found: {search_results.total_found} results")
            
            if search_results.results:
                first_result = search_results.results[0]
                print(f"   🎯 Top result: {first_result.title[:50]}...")
                success_count += 1
            else:
                print(f"   ⚠️ No results found")
            
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
    
    print(f"\n📊 Search test results: {success_count}/{len(test_queries)} queries successful")
    return success_count == len(test_queries)

def test_relevance_scoring():
    """Test relevance scoring algorithm"""
    print("\n🧪 Testing Relevance Scoring")
    print("=" * 40)
    
    # Sample scheme for testing
    test_scheme = {
        "title": "Pradhan Mantri Awas Yojana (PMAY)",
        "description": "Housing for All scheme providing financial assistance",
        "keywords": ["housing", "house", "awas", "ghar", "मकान", "घर बनाने की योजना"]
    }
    
    test_cases = [
        (["घर", "बनाने"], "Should match keywords"),
        (["housing", "scheme"], "Should match title and keywords"),
        (["pradhan", "mantri"], "Should match title"),
        (["xyz", "abc"], "Should not match"),
        (["awas", "yojana"], "Should match keywords and title")
    ]
    
    for query_words, expected in test_cases:
        score = calculate_relevance_score(test_scheme, query_words)
        print(f"   Query: {query_words} -> Score: {score:.1f} ({expected})")
    
    return True

def test_json_structure():
    """Test JSON file structure and validation"""
    print("\n🧪 Testing JSON Structure")
    print("=" * 40)
    
    try:
        with open('schemes_database.json', 'r', encoding='utf-8') as file:
            data = json.load(file)
        
        # Check required sections
        required_sections = ["metadata", "schemes"]
        for section in required_sections:
            if section not in data:
                print(f"❌ Missing required section: {section}")
                return False
            else:
                print(f"✅ Found section: {section}")
        
        # Check metadata
        metadata = data["metadata"]
        required_metadata = ["version", "last_updated", "total_categories"]
        for field in required_metadata:
            if field in metadata:
                print(f"✅ Metadata field '{field}': {metadata[field]}")
            else:
                print(f"⚠️ Missing metadata field: {field}")
        
        # Check schemes structure
        schemes = data["schemes"]
        print(f"✅ Found {len(schemes)} scheme categories")
        
        # Validate a few schemes
        sample_count = 0
        for category, scheme_list in schemes.items():
            if sample_count >= 2:  # Check only first 2 categories
                break
                
            print(f"✅ Category '{category}': {len(scheme_list)} schemes")
            
            if scheme_list:  # Check first scheme in category
                scheme = scheme_list[0]
                required_fields = ["title", "description", "link", "keywords"]
                
                for field in required_fields:
                    if field in scheme:
                        print(f"   ✅ Field '{field}': Present")
                    else:
                        print(f"   ❌ Field '{field}': Missing")
            
            sample_count += 1
        
        return True
        
    except FileNotFoundError:
        print("❌ schemes_database.json file not found!")
        return False
    except json.JSONDecodeError as e:
        print(f"❌ JSON parsing error: {str(e)}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return False

def test_integration():
    """Test complete integration"""
    print("\n🧪 Testing Complete Integration")
    print("=" * 40)
    
    try:
        # Test the complete flow
        query = "घर बनाने की योजना"
        print(f"🔍 Testing complete flow with query: '{query}'")
        
        # Step 1: Load database
        schemes_db = load_schemes_database()
        if not schemes_db:
            print("❌ Failed to load database")
            return False
        print("✅ Database loaded")
        
        # Step 2: Search
        search_results = search_government_schemes(query)
        if not search_results.results:
            print("❌ No search results")
            return False
        print(f"✅ Search completed: {search_results.total_found} results")
        
        # Step 3: Check result structure
        first_result = search_results.results[0]
        required_fields = ["title", "description", "link"]
        
        for field in required_fields:
            if hasattr(first_result, field) and getattr(first_result, field):
                print(f"✅ Result field '{field}': Present")
            else:
                print(f"❌ Result field '{field}': Missing or empty")
                return False
        
        print(f"✅ Integration test successful!")
        print(f"📋 Top result: {first_result.title}")
        print(f"🔗 Link: {first_result.link}")
        
        return True
        
    except Exception as e:
        print(f"❌ Integration test failed: {str(e)}")
        return False

def main():
    """Run all tests"""
    print("🇮🇳 SwarajyaAI JSON System Test Suite")
    print("=" * 60)
    
    tests = [
        ("JSON Loading", test_json_loading),
        ("JSON Structure", test_json_structure),
        ("Search Functionality", test_search_functionality),
        ("Relevance Scoring", test_relevance_scoring),
        ("Complete Integration", test_integration)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🧪 Running {test_name} Test...")
        try:
            if test_func():
                print(f"✅ {test_name} test PASSED")
                passed += 1
            else:
                print(f"❌ {test_name} test FAILED")
        except Exception as e:
            print(f"❌ {test_name} test ERROR: {str(e)}")
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! JSON system is working correctly.")
        return 0
    else:
        print("⚠️ Some tests failed. Please check the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())