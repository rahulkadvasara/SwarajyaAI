#!/usr/bin/env python3
"""
Schemes Database Management Script
Helps manage and update the government schemes database
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any

class SchemesManager:
    """Manager class for schemes database operations"""
    
    def __init__(self, db_file: str = "schemes_database.json"):
        self.db_file = db_file
        self.data = self.load_database()
    
    def load_database(self) -> Dict[str, Any]:
        """Load the schemes database from JSON file"""
        try:
            with open(self.db_file, 'r', encoding='utf-8') as file:
                return json.load(file)
        except FileNotFoundError:
            print(f"❌ Database file {self.db_file} not found!")
            return {"metadata": {}, "schemes": {}}
        except json.JSONDecodeError as e:
            print(f"❌ Error parsing JSON: {str(e)}")
            return {"metadata": {}, "schemes": {}}
    
    def save_database(self) -> bool:
        """Save the schemes database to JSON file"""
        try:
            # Update metadata
            self.data["metadata"]["last_updated"] = datetime.now().strftime("%Y-%m-%d")
            self.data["metadata"]["total_categories"] = len(self.data["schemes"])
            
            # Calculate total schemes
            total_schemes = sum(len(schemes) for schemes in self.data["schemes"].values())
            
            with open(self.db_file, 'w', encoding='utf-8') as file:
                json.dump(self.data, file, indent=2, ensure_ascii=False)
            
            print(f"✅ Database saved successfully!")
            print(f"📊 Total categories: {len(self.data['schemes'])}")
            print(f"📊 Total schemes: {total_schemes}")
            return True
            
        except Exception as e:
            print(f"❌ Error saving database: {str(e)}")
            return False
    
    def list_categories(self):
        """List all scheme categories"""
        print("\n📋 Available Categories:")
        print("=" * 40)
        
        for i, (category, schemes) in enumerate(self.data["schemes"].items(), 1):
            print(f"{i}. {category.title()} ({len(schemes)} schemes)")
    
    def list_schemes_in_category(self, category: str):
        """List all schemes in a specific category"""
        if category not in self.data["schemes"]:
            print(f"❌ Category '{category}' not found!")
            return
        
        schemes = self.data["schemes"][category]
        print(f"\n📋 Schemes in '{category.title()}' category:")
        print("=" * 50)
        
        for i, scheme in enumerate(schemes, 1):
            print(f"{i}. {scheme['title']}")
            print(f"   🔗 {scheme['link']}")
            print(f"   📝 {scheme['description'][:100]}...")
            print()
    
    def add_scheme(self, category: str, scheme_data: Dict[str, Any]):
        """Add a new scheme to a category"""
        if category not in self.data["schemes"]:
            self.data["schemes"][category] = []
        
        # Validate required fields
        required_fields = ["title", "description", "link", "keywords"]
        for field in required_fields:
            if field not in scheme_data:
                print(f"❌ Missing required field: {field}")
                return False
        
        self.data["schemes"][category].append(scheme_data)
        print(f"✅ Added scheme '{scheme_data['title']}' to '{category}' category")
        return True
    
    def remove_scheme(self, category: str, scheme_title: str):
        """Remove a scheme from a category"""
        if category not in self.data["schemes"]:
            print(f"❌ Category '{category}' not found!")
            return False
        
        schemes = self.data["schemes"][category]
        for i, scheme in enumerate(schemes):
            if scheme["title"].lower() == scheme_title.lower():
                removed_scheme = schemes.pop(i)
                print(f"✅ Removed scheme '{removed_scheme['title']}' from '{category}' category")
                return True
        
        print(f"❌ Scheme '{scheme_title}' not found in '{category}' category!")
        return False
    
    def search_schemes(self, query: str):
        """Search for schemes containing the query"""
        results = []
        query_lower = query.lower()
        
        for category, schemes in self.data["schemes"].items():
            for scheme in schemes:
                # Search in title, description, and keywords
                searchable_text = (
                    scheme["title"] + " " + 
                    scheme["description"] + " " + 
                    " ".join(scheme["keywords"])
                ).lower()
                
                if query_lower in searchable_text:
                    results.append({
                        "category": category,
                        "scheme": scheme
                    })
        
        print(f"\n🔍 Search results for '{query}':")
        print("=" * 50)
        
        if not results:
            print("❌ No schemes found matching your query.")
            return
        
        for i, result in enumerate(results, 1):
            scheme = result["scheme"]
            print(f"{i}. {scheme['title']} ({result['category'].title()})")
            print(f"   🔗 {scheme['link']}")
            print(f"   📝 {scheme['description'][:100]}...")
            print()
    
    def validate_database(self):
        """Validate the database structure and content"""
        print("\n🔍 Validating database...")
        print("=" * 40)
        
        errors = []
        warnings = []
        
        # Check metadata
        if "metadata" not in self.data:
            errors.append("Missing metadata section")
        
        # Check schemes structure
        if "schemes" not in self.data:
            errors.append("Missing schemes section")
            return errors, warnings
        
        # Validate each category and scheme
        for category, schemes in self.data["schemes"].items():
            if not isinstance(schemes, list):
                errors.append(f"Category '{category}' should contain a list of schemes")
                continue
            
            for i, scheme in enumerate(schemes):
                scheme_id = f"{category}[{i}]"
                
                # Check required fields
                required_fields = ["title", "description", "link", "keywords"]
                for field in required_fields:
                    if field not in scheme:
                        errors.append(f"{scheme_id}: Missing required field '{field}'")
                
                # Check field types
                if "keywords" in scheme and not isinstance(scheme["keywords"], list):
                    errors.append(f"{scheme_id}: 'keywords' should be a list")
                
                # Check for empty values
                if "title" in scheme and not scheme["title"].strip():
                    errors.append(f"{scheme_id}: Empty title")
                
                if "link" in scheme and not scheme["link"].startswith("http"):
                    warnings.append(f"{scheme_id}: Link should start with http/https")
        
        # Print results
        if errors:
            print("❌ Errors found:")
            for error in errors:
                print(f"   • {error}")
        
        if warnings:
            print("⚠️ Warnings:")
            for warning in warnings:
                print(f"   • {warning}")
        
        if not errors and not warnings:
            print("✅ Database validation passed!")
        
        return errors, warnings
    
    def get_statistics(self):
        """Get database statistics"""
        print("\n📊 Database Statistics:")
        print("=" * 40)
        
        total_schemes = sum(len(schemes) for schemes in self.data["schemes"].values())
        
        print(f"📁 Total Categories: {len(self.data['schemes'])}")
        print(f"📄 Total Schemes: {total_schemes}")
        
        if "metadata" in self.data:
            metadata = self.data["metadata"]
            print(f"📅 Last Updated: {metadata.get('last_updated', 'Unknown')}")
            print(f"🔢 Version: {metadata.get('version', 'Unknown')}")
        
        print("\n📋 Schemes per category:")
        for category, schemes in self.data["schemes"].items():
            print(f"   • {category.title()}: {len(schemes)} schemes")

def main():
    """Main interactive menu"""
    manager = SchemesManager()
    
    while True:
        print("\n🇮🇳 SwarajyaAI Schemes Database Manager")
        print("=" * 50)
        print("1. List categories")
        print("2. List schemes in category")
        print("3. Search schemes")
        print("4. Add new scheme")
        print("5. Remove scheme")
        print("6. Validate database")
        print("7. Show statistics")
        print("8. Save database")
        print("9. Reload database")
        print("0. Exit")
        
        choice = input("\n🔢 Enter your choice (0-9): ").strip()
        
        if choice == "1":
            manager.list_categories()
        
        elif choice == "2":
            category = input("📁 Enter category name: ").strip().lower()
            manager.list_schemes_in_category(category)
        
        elif choice == "3":
            query = input("🔍 Enter search query: ").strip()
            if query:
                manager.search_schemes(query)
        
        elif choice == "4":
            print("\n➕ Add New Scheme")
            print("-" * 20)
            category = input("📁 Category: ").strip().lower()
            title = input("📋 Title: ").strip()
            description = input("📝 Description: ").strip()
            link = input("🔗 Link: ").strip()
            keywords_input = input("🏷️ Keywords (comma-separated): ").strip()
            
            if all([category, title, description, link, keywords_input]):
                keywords = [kw.strip() for kw in keywords_input.split(",")]
                
                scheme_data = {
                    "title": title,
                    "description": description,
                    "link": link,
                    "keywords": keywords
                }
                
                manager.add_scheme(category, scheme_data)
            else:
                print("❌ All fields are required!")
        
        elif choice == "5":
            category = input("📁 Category: ").strip().lower()
            title = input("📋 Scheme title to remove: ").strip()
            if category and title:
                manager.remove_scheme(category, title)
        
        elif choice == "6":
            manager.validate_database()
        
        elif choice == "7":
            manager.get_statistics()
        
        elif choice == "8":
            manager.save_database()
        
        elif choice == "9":
            manager.data = manager.load_database()
            print("✅ Database reloaded!")
        
        elif choice == "0":
            print("👋 Goodbye!")
            break
        
        else:
            print("❌ Invalid choice! Please enter 0-9.")

if __name__ == "__main__":
    main()