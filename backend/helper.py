"""
SwarajyaAI Helper Module
Handles Groq API integration and prompt management for Hindi response generation
"""

import os
import logging
import requests
from bs4 import BeautifulSoup
from typing import Optional, Dict, Any, List
from groq import Groq
from dotenv import load_dotenv
from urllib.parse import urljoin, quote
import re
import time

# Load environment variables
load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)

class GroqHelper:
    """
    Helper class for Groq API integration with Llama models
    Handles query enhancement, web scraping assistance, and Hindi response generation
    """
    
    def __init__(self):
        """Initialize Groq client with API key from environment"""
        self.client = None
        self.model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
        self.temperature = float(os.getenv("GROQ_TEMPERATURE", "0.3"))
        self.max_tokens = int(os.getenv("GROQ_MAX_TOKENS", "300"))
        
        # Initialize Groq client
        self._initialize_client()
    
    def _initialize_client(self) -> None:
        """Initialize Groq client with error handling"""
        try:
            api_key = os.getenv("GROQ_API_KEY")
            if not api_key or api_key == "your-groq-api-key-here":
                logger.warning("Groq API key not found or not configured properly")
                return
            
            self.client = Groq(api_key=api_key)
            logger.info("Groq client initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Groq client: {str(e)}")
            self.client = None
    
    def is_available(self) -> bool:
        """Check if Groq client is available and ready to use"""
        return self.client is not None
    
    def generate_hindi_response(self, scheme: Dict[str, Any], user_query: str) -> str:
        """
        Generate natural Hindi response for government scheme using Llama
        
        Args:
            scheme: Dictionary containing scheme information
            user_query: Original user query
            
        Returns:
            Natural Hindi response string
        """
        
        if not self.is_available():
            return self._get_fallback_response(scheme, user_query)
        
        try:
            # Generate the prompt for Llama
            prompt = self._create_scheme_prompt(scheme, user_query)
            
            # Call Groq API with Llama model
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": self._get_system_prompt()
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                model=self.model,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                top_p=0.9
            )
            
            hindi_response = chat_completion.choices[0].message.content.strip()
            logger.info(f"Generated Hindi response using Llama for scheme: {scheme['title']}")
            
            return hindi_response
            
        except Exception as e:
            logger.error(f"Error generating Hindi response with Llama: {str(e)}")
            return self._get_fallback_response(scheme, user_query)
    
    def _get_system_prompt(self) -> str:
        """
        Get the system prompt for Llama model
        
        Returns:
            System prompt string in Hindi
        """
        return """आप एक विशेषज्ञ भारतीय सरकारी योजना सलाहकार हैं। आपका काम है:

1. हमेशा हिंदी में सरल और स्पष्ट उत्तर देना
2. आम लोगों की भाषा का उपयोग करना
3. जटिल शब्दों से बचना
4. व्यावहारिक और उपयोगी जानकारी देना
5. योजना के लाभ और आवेदन प्रक्रिया को समझाना

आपके उत्तर में भरोसा और सहायता की भावना होनी चाहिए।"""
    
    def _create_scheme_prompt(self, scheme: Dict[str, Any], user_query: str) -> str:
        """
        Create a detailed prompt for scheme information
        
        Args:
            scheme: Dictionary containing scheme information
            user_query: Original user query
            
        Returns:
            Formatted prompt string
        """
        
        prompt = f"""उपयोगकर्ता ने "{user_query}" के बारे में पूछा है।

योजना की जानकारी:
नाम: {scheme['title']}
विवरण: {scheme['description']}
आधिकारिक वेबसाइट: {scheme['link']}

कृपया इस योजना के बारे में एक सरल, स्पष्ट और उपयोगी उत्तर दें। उत्तर में निम्नलिखित बातें शामिल करें:

1. योजना का नाम और मुख्य लाभ क्या है
2. कौन से लोग इस योजना के लिए आवेदन कर सकते हैं
3. आवेदन कैसे करें (सरल चरणों में)
4. कहाँ से अधिक जानकारी मिल सकती है

महत्वपूर्ण निर्देश:
- उत्तर पूरी तरह हिंदी में दें
- बहुत सरल भाषा का उपयोग करें जो गांव के लोग भी समझ सकें
- तकनीकी शब्दों से बचें
- उत्तर 120-180 शब्दों में दें
- उत्साहजनक और सहायक टोन रखें
- "आप" का उपयोग करके व्यक्तिगत बनाएं"""

        return prompt
    
    def _get_fallback_response(self, scheme: Dict[str, Any], user_query: str) -> str:
        """
        Generate fallback Hindi response when Groq API is not available
        
        Args:
            scheme: Dictionary containing scheme information
            user_query: Original user query
            
        Returns:
            Simple Hindi response string
        """
        
        # Create a simple but informative Hindi response
        response = f"{scheme['title']} योजना आपके लिए उपलब्ध है। "
        
        # Add description if available
        if scheme.get('description'):
            # Simplify the description
            desc = scheme['description'][:150]
            response += f"इस योजना के तहत {desc}... "
        
        # Add application guidance
        response += "आवेदन करने के लिए दिए गए लिंक पर जाएं या अपने नजदीकी सरकारी कार्यालय में संपर्क करें। "
        response += "अधिक जानकारी के लिए आधिकारिक वेबसाइट देखें।"
        
        logger.info(f"Using fallback Hindi response for scheme: {scheme['title']}")
        return response
    
    def test_connection(self) -> bool:
        """
        Test Groq API connection with a simple query
        
        Returns:
            True if connection successful, False otherwise
        """
        
        if not self.is_available():
            return False
        
        try:
            # Test with a simple Hindi query
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "आप एक सहायक हैं। हिंदी में उत्तर दें।"
                    },
                    {
                        "role": "user",
                        "content": "नमस्ते! क्या आप हिंदी में बात कर सकते हैं?"
                    }
                ],
                model=self.model,
                temperature=0.3,
                max_tokens=50
            )
            
            response = chat_completion.choices[0].message.content
            logger.info(f"Groq API test successful. Response: {response[:50]}...")
            return True
            
        except Exception as e:
            logger.error(f"Groq API test failed: {str(e)}")
            return False
    
    def enhance_user_query(self, user_query: str) -> Dict[str, Any]:
        """
        Use Llama to enhance and understand user query for better web scraping
        
        Args:
            user_query: Original user query from user
            
        Returns:
            Dictionary with enhanced query information
        """
        
        if not self.is_available():
            # Fallback query enhancement without Llama
            return self._fallback_query_enhancement(user_query)
        
        try:
            enhancement_prompt = f"""
आप एक भारतीय सरकारी योजना खोज विशेषज्ञ हैं। उपयोगकर्ता ने "{user_query}" पूछा है।

कृपया इस query को समझकर निम्नलिखित जानकारी JSON format में दें:

1. search_keywords: वेब सर्च के लिए बेहतर English keywords (array)
2. hindi_keywords: हिंदी में खोज शब्द (array)  
3. category: मुख्य श्रेणी (housing/employment/education/health/agriculture/pension/women)
4. intent: उपयोगकर्ता क्या चाहता है (scheme_info/application_process/eligibility/benefits)
5. target_websites: खोजने के लिए सरकारी websites (array)

उदाहरण:
{{
  "search_keywords": ["housing scheme", "pradhan mantri awas yojana", "home construction"],
  "hindi_keywords": ["आवास योजना", "घर निर्माण", "प्रधानमंत्री आवास"],
  "category": "housing",
  "intent": "scheme_info",
  "target_websites": ["pmay.gov.in", "india.gov.in", "myscheme.gov.in"]
}}

केवल JSON response दें, कोई अतिरिक्त text नहीं।
"""

            chat_completion = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "आप एक JSON response generator हैं। केवल valid JSON format में उत्तर दें।"
                    },
                    {
                        "role": "user",
                        "content": enhancement_prompt
                    }
                ],
                model=self.model,
                temperature=0.2,  # Lower temperature for more consistent JSON
                max_tokens=400
            )
            
            response_text = chat_completion.choices[0].message.content.strip()
            
            # Extract JSON from response
            import json
            try:
                # Try to find JSON in the response
                json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                if json_match:
                    enhanced_query = json.loads(json_match.group())
                    logger.info(f"Enhanced query using Llama: {enhanced_query}")
                    return enhanced_query
                else:
                    raise ValueError("No JSON found in response")
            except (json.JSONDecodeError, ValueError) as e:
                logger.warning(f"Failed to parse JSON from Llama response: {e}")
                return self._fallback_query_enhancement(user_query)
                
        except Exception as e:
            logger.error(f"Error enhancing query with Llama: {str(e)}")
            return self._fallback_query_enhancement(user_query)
    
    def _fallback_query_enhancement(self, user_query: str) -> Dict[str, Any]:
        """
        Fallback query enhancement without Llama
        
        Args:
            user_query: Original user query
            
        Returns:
            Basic enhanced query information
        """
        
        query_lower = user_query.lower()
        
        # Basic keyword mapping
        if any(word in query_lower for word in ["घर", "आवास", "house", "housing", "मकान"]):
            return {
                "search_keywords": ["housing scheme", "pradhan mantri awas yojana", "home construction"],
                "hindi_keywords": ["आवास योजना", "घर निर्माण"],
                "category": "housing",
                "intent": "scheme_info",
                "target_websites": ["pmay.gov.in", "india.gov.in", "myscheme.gov.in"]
            }
        elif any(word in query_lower for word in ["नौकरी", "काम", "employment", "job", "रोजगार"]):
            return {
                "search_keywords": ["employment scheme", "job guarantee", "mgnrega"],
                "hindi_keywords": ["रोजगार योजना", "नौकरी"],
                "category": "employment",
                "intent": "scheme_info",
                "target_websites": ["nrega.nic.in", "pmkvyofficial.org", "india.gov.in"]
            }
        elif any(word in query_lower for word in ["स्वास्थ्य", "इलाज", "health", "medical", "hospital"]):
            return {
                "search_keywords": ["health scheme", "ayushman bharat", "medical insurance"],
                "hindi_keywords": ["स्वास्थ्य योजना", "इलाज"],
                "category": "health",
                "intent": "scheme_info",
                "target_websites": ["pmjay.gov.in", "nhm.gov.in", "india.gov.in"]
            }
        else:
            return {
                "search_keywords": [user_query, "government scheme"],
                "hindi_keywords": [user_query],
                "category": "general",
                "intent": "scheme_info",
                "target_websites": ["india.gov.in", "myscheme.gov.in"]
            }
    
    def scrape_government_websites(self, enhanced_query: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Scrape official government websites for scheme information
        
        Args:
            enhanced_query: Enhanced query information from Llama
            
        Returns:
            List of scraped scheme information
        """
        
        schemes = []
        search_keywords = enhanced_query.get("search_keywords", [])
        target_websites = enhanced_query.get("target_websites", ["india.gov.in"])
        
        # Government website configurations
        website_configs = {
            "india.gov.in": {
                "search_url": "https://www.india.gov.in/search/site",
                "selectors": {
                    "container": ".search-result, .view-content .views-row",
                    "title": "h3 a, .views-field-title a, h2 a",
                    "description": ".search-snippet, .views-field-body, p",
                    "link": "h3 a, .views-field-title a, h2 a"
                }
            },
            "myscheme.gov.in": {
                "search_url": "https://www.myscheme.gov.in/search",
                "selectors": {
                    "container": ".scheme-card, .search-result-item",
                    "title": ".scheme-title, h3, .card-title",
                    "description": ".scheme-description, .card-text, p",
                    "link": "a"
                }
            },
            "pmay.gov.in": {
                "search_url": "https://pmay.gov.in",
                "selectors": {
                    "container": ".content-area, .main-content",
                    "title": "h1, h2, h3",
                    "description": "p, .description",
                    "link": "a"
                }
            }
        }
        
        for keyword in search_keywords[:3]:  # Limit to 3 keywords to avoid too many requests
            for website in target_websites[:2]:  # Limit to 2 websites per keyword
                try:
                    website_schemes = self._scrape_single_website(
                        website, keyword, website_configs.get(website, website_configs["india.gov.in"])
                    )
                    schemes.extend(website_schemes)
                    
                    # Add delay to be respectful to servers
                    time.sleep(1)
                    
                except Exception as e:
                    logger.warning(f"Failed to scrape {website} for keyword '{keyword}': {str(e)}")
                    continue
        
        # Remove duplicates and limit results
        unique_schemes = self._remove_duplicate_schemes(schemes)
        return unique_schemes[:5]  # Return top 5 results
    
    def _scrape_single_website(self, website: str, keyword: str, config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Scrape a single government website
        
        Args:
            website: Website domain
            keyword: Search keyword
            config: Website configuration
            
        Returns:
            List of scraped schemes
        """
        
        schemes = []
        
        try:
            # Construct search URL
            search_url = f"{config['search_url']}?q={quote(keyword)}"
            
            # Set up headers to mimic a real browser
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            }
            
            # Make request with timeout
            response = requests.get(search_url, headers=headers, timeout=10)
            response.raise_for_status()
            
            # Parse HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract schemes using selectors
            containers = soup.select(config['selectors']['container'])
            
            for container in containers[:3]:  # Limit to 3 results per website
                scheme = self._extract_scheme_from_container(container, config['selectors'], website)
                if scheme and self._is_valid_scheme(scheme, keyword):
                    schemes.append(scheme)
            
            logger.info(f"Scraped {len(schemes)} schemes from {website} for keyword '{keyword}'")
            
        except Exception as e:
            logger.error(f"Error scraping {website}: {str(e)}")
        
        return schemes
    
    def _extract_scheme_from_container(self, container, selectors: Dict[str, str], base_website: str) -> Optional[Dict[str, Any]]:
        """
        Extract scheme information from HTML container
        
        Args:
            container: BeautifulSoup container element
            selectors: CSS selectors for different elements
            base_website: Base website for relative URLs
            
        Returns:
            Scheme dictionary or None
        """
        
        try:
            # Extract title
            title_element = container.select_one(selectors['title'])
            if not title_element:
                return None
            
            title = title_element.get_text(strip=True)
            if not title or len(title) < 10:
                return None
            
            # Extract link
            link_element = title_element if title_element.name == 'a' else container.select_one(selectors['link'])
            link = ""
            if link_element and link_element.get('href'):
                href = link_element.get('href')
                if href.startswith('http'):
                    link = href
                elif href.startswith('/'):
                    link = f"https://{base_website}{href}"
                else:
                    link = f"https://{base_website}/{href}"
            
            # Extract description
            description = ""
            desc_element = container.select_one(selectors['description'])
            if desc_element:
                description = desc_element.get_text(strip=True)
                # Clean up description
                description = re.sub(r'\s+', ' ', description)
                description = description[:300]  # Limit length
            
            return {
                "title": title,
                "description": description,
                "link": link,
                "source": base_website
            }
            
        except Exception as e:
            logger.error(f"Error extracting scheme from container: {str(e)}")
            return None
    
    def _is_valid_scheme(self, scheme: Dict[str, Any], keyword: str) -> bool:
        """
        Check if scraped scheme is valid and relevant
        
        Args:
            scheme: Scheme dictionary
            keyword: Search keyword
            
        Returns:
            True if scheme is valid and relevant
        """
        
        # Check if title and description exist
        if not scheme.get('title') or not scheme.get('description'):
            return False
        
        # Check relevance to keyword
        text_to_check = (scheme['title'] + ' ' + scheme['description']).lower()
        keyword_lower = keyword.lower()
        
        # Simple relevance check
        keyword_words = keyword_lower.split()
        relevant_words = [word for word in keyword_words if len(word) > 2]
        
        if not any(word in text_to_check for word in relevant_words):
            return False
        
        # Check if it looks like a government scheme
        govt_indicators = ['scheme', 'yojana', 'योजना', 'government', 'pradhan mantri', 'ministry', 'भारत सरकार']
        if not any(indicator in text_to_check for indicator in govt_indicators):
            return False
        
        return True
    
    def _remove_duplicate_schemes(self, schemes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Remove duplicate schemes based on title similarity
        
        Args:
            schemes: List of scheme dictionaries
            
        Returns:
            List of unique schemes
        """
        
        unique_schemes = []
        seen_titles = set()
        
        for scheme in schemes:
            title_lower = scheme['title'].lower()
            
            # Simple duplicate detection
            is_duplicate = False
            for seen_title in seen_titles:
                if self._calculate_similarity(title_lower, seen_title) > 0.8:
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                unique_schemes.append(scheme)
                seen_titles.add(title_lower)
        
        return unique_schemes
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate similarity between two texts
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Similarity score between 0 and 1
        """
        
        words1 = set(text1.split())
        words2 = set(text2.split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union)
    
    def generate_comprehensive_hindi_response(self, schemes: List[Dict[str, Any]], user_query: str) -> str:
        """
        Generate comprehensive Hindi response from multiple scraped schemes
        
        Args:
            schemes: List of scraped scheme dictionaries
            user_query: Original user query
            
        Returns:
            Comprehensive Hindi response
        """
        
        if not schemes:
            return self.generate_error_response(user_query, "no_results")
        
        if not self.is_available():
            return self._generate_fallback_comprehensive_response(schemes, user_query)
        
        try:
            # Prepare schemes data for Llama
            schemes_text = ""
            for i, scheme in enumerate(schemes[:3], 1):  # Limit to top 3 schemes
                schemes_text += f"""
योजना {i}:
नाम: {scheme['title']}
विवरण: {scheme['description'][:200]}...
वेबसाइट: {scheme['link']}
स्रोत: {scheme['source']}
"""
            
            comprehensive_prompt = f"""
उपयोगकर्ता ने "{user_query}" के बारे में पूछा है। मैंने सरकारी वेबसाइटों से निम्नलिखित योजनाएं खोजी हैं:

{schemes_text}

कृपया इन योजनाओं के आधार पर एक विस्तृत और सरल हिंदी उत्तर दें जिसमें:

1. सबसे उपयुक्त योजना का नाम और मुख्य लाभ
2. पात्रता की शर्तें (कौन आवेदन कर सकता है)
3. आवेदन की प्रक्रिया (सरल चरणों में)
4. आवश्यक दस्तावेज
5. संपर्क जानकारी या वेबसाइट

महत्वपूर्ण निर्देश:
- उत्तर पूरी तरह हिंदी में दें
- बहुत सरल भाषा का उपयोग करें
- तकनीकी शब्दों से बचें
- उत्तर 200-300 शब्दों में दें
- व्यावहारिक और उपयोगी जानकारी दें
- उत्साहजनक टोन रखें
"""

            chat_completion = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": self._get_system_prompt()
                    },
                    {
                        "role": "user",
                        "content": comprehensive_prompt
                    }
                ],
                model=self.model,
                temperature=0.3,
                max_tokens=500,
                top_p=0.9
            )
            
            hindi_response = chat_completion.choices[0].message.content.strip()
            logger.info(f"Generated comprehensive Hindi response for {len(schemes)} schemes")
            
            return hindi_response
            
        except Exception as e:
            logger.error(f"Error generating comprehensive Hindi response: {str(e)}")
            return self._generate_fallback_comprehensive_response(schemes, user_query)
    
    def _generate_fallback_comprehensive_response(self, schemes: List[Dict[str, Any]], user_query: str) -> str:
        """
        Generate fallback comprehensive response without Llama
        
        Args:
            schemes: List of scheme dictionaries
            user_query: Original user query
            
        Returns:
            Simple comprehensive Hindi response
        """
        
        if not schemes:
            return f"'{user_query}' के लिए कोई सरकारी योजना नहीं मिली। कृपया अलग शब्दों में खोजें।"
        
        main_scheme = schemes[0]
        response = f"{main_scheme['title']} आपके लिए एक उपयुक्त योजना है। "
        
        if main_scheme.get('description'):
            response += f"{main_scheme['description'][:150]}... "
        
        response += f"अधिक जानकारी के लिए {main_scheme['link']} पर जाएं। "
        
        if len(schemes) > 1:
            response += f"इसके अलावा {len(schemes)-1} और योजनाएं भी उपलब्ध हैं। "
        
        response += "आवेदन करने के लिए संबंधित वेबसाइट पर जाएं या नजदीकी सरकारी कार्यालय में संपर्क करें।"
        
        return response
    
    def generate_error_response(self, query: str, error_type: str = "no_results") -> str:
        """
        Generate appropriate Hindi error responses
        
        Args:
            query: User's search query
            error_type: Type of error (no_results, server_error, etc.)
            
        Returns:
            Hindi error message
        """
        
        error_responses = {
            "no_results": f"'{query}' के लिए कोई सरकारी योजना नहीं मिली। कृपया अलग शब्दों में खोजें जैसे 'घर', 'नौकरी', 'शिक्षा', 'स्वास्थ्य', या 'किसान'।",
            "server_error": "सरकारी योजनाओं की जानकारी लेने में कुछ समस्या हो रही है। कृपया कुछ देर बाद कोशिश करें।",
            "invalid_query": "कृपया अपना सवाल स्पष्ट रूप से पूछें। उदाहरण: 'घर बनाने की योजना' या 'नौकरी की योजना'।"
        }
        
        return error_responses.get(error_type, error_responses["server_error"])

# Create a global instance for easy import
groq_helper = GroqHelper()

# Convenience functions for backward compatibility
def generate_hindi_response_with_llama(scheme: Dict[str, Any], user_query: str) -> str:
    """
    Convenience function to generate Hindi response using Groq helper
    
    Args:
        scheme: Dictionary containing scheme information
        user_query: Original user query
        
    Returns:
        Natural Hindi response string
    """
    return groq_helper.generate_hindi_response(scheme, user_query)

def test_groq_connection() -> bool:
    """
    Convenience function to test Groq API connection
    
    Returns:
        True if connection successful, False otherwise
    """
    return groq_helper.test_connection()

def is_groq_available() -> bool:
    """
    Convenience function to check if Groq is available
    
    Returns:
        True if Groq client is available, False otherwise
    """
    return groq_helper.is_available()