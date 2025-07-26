"""
SwarajyaAI Backend - FastAPI Server
Voice-based assistant for Indian government welfare schemes

This backend provides reliable scheme search functionality using:
- Curated database of real government schemes for reliability
- Llama-enhanced Hindi responses for natural conversation
- Fast and reliable results without web scraping issues
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import logging
from typing import List
import os
import json
from helper import groq_helper

# Initialize FastAPI app
app = FastAPI(
    title="SwarajyaAI API",
    description="Voice-based assistant for Indian government welfare schemes",
    version="1.0.0"
)

# Enable CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Request and Response Models
class QueryRequest(BaseModel):
    query: str

class SchemeResult(BaseModel):
    title: str
    description: str = ""
    link: str

class SearchResponse(BaseModel):
    results: List[SchemeResult]
    total_found: int = 0
    search_query: str = ""

class QueryResponse(BaseModel):
    reply: str
    link: str
    scheme_name: str = ""

# Load schemes database from JSON file
def load_schemes_database():
    """Load government schemes from JSON file"""
    try:
        with open('schemes_database.json', 'r', encoding='utf-8') as file:
            data = json.load(file)
            logger.info(f"Loaded schemes database: {data['metadata']['total_categories']} categories, {sum(len(schemes) for schemes in data['schemes'].values())} total schemes")
            return data['schemes']
    except FileNotFoundError:
        logger.error("schemes_database.json file not found!")
        return {}
    except json.JSONDecodeError as e:
        logger.error(f"Error parsing schemes_database.json: {str(e)}")
        return {}
    except Exception as e:
        logger.error(f"Error loading schemes database: {str(e)}")
        return {}

# Load schemes database at startup
CURATED_SCHEMES_DB = load_schemes_database()

# Configuration
SEARCH_CONFIG = {
    "max_results": 10,
    "min_query_length": 2
}

def calculate_relevance_score(scheme: dict, query_words: list) -> float:
    """Calculate relevance score for a scheme based on query words"""
    score = 0.0
    
    # Combine all searchable text
    searchable_text = (
        scheme['title'] + ' ' + 
        scheme['description'] + ' ' + 
        ' '.join(scheme['keywords'])
    ).lower()
    
    for word in query_words:
        if len(word) < 2:  # Skip very short words
            continue
            
        # Exact match in keywords (highest score)
        if word in [kw.lower() for kw in scheme['keywords']]:
            score += 10.0
        # Exact match in title (high score)
        elif word in scheme['title'].lower():
            score += 5.0
        # Exact match in description (medium score)
        elif word in scheme['description'].lower():
            score += 2.0
        # Partial match (low score)
        elif any(word in text_part for text_part in searchable_text.split()):
            score += 0.5
    
    return score

def search_government_schemes(query: str) -> SearchResponse:
    """Search government schemes using curated database with relevance scoring"""
    
    if not query or len(query.strip()) < SEARCH_CONFIG['min_query_length']:
        logger.warning(f"Query too short: '{query}'")
        return SearchResponse(results=[], total_found=0, search_query=query)
    
    logger.info(f"Searching schemes for query: '{query}'")
    
    try:
        matching_schemes = []
        query_lower = query.lower().strip()
        query_words = query_lower.split()
        
        # Search through all scheme categories
        for category, schemes in CURATED_SCHEMES_DB.items():
            for scheme in schemes:
                relevance_score = calculate_relevance_score(scheme, query_words)
                
                if relevance_score > 0:
                    matching_schemes.append({
                        'scheme': scheme,
                        'score': relevance_score
                    })
        
        # Sort by relevance score (highest first)
        matching_schemes.sort(key=lambda x: x['score'], reverse=True)
        
        # Convert to SearchResponse format
        results = []
        for match in matching_schemes[:SEARCH_CONFIG['max_results']]:
            scheme = match['scheme']
            results.append(SchemeResult(
                title=scheme['title'],
                description=scheme['description'],
                link=scheme['link']
            ))
        
        logger.info(f"Found {len(results)} matching schemes for query: '{query}'")
        
        return SearchResponse(
            results=results,
            total_found=len(results),
            search_query=query
        )
        
    except Exception as e:
        logger.error(f"Error in search: {str(e)}")
        return SearchResponse(
            results=[],
            total_found=0,
            search_query=query
        )

def convert_to_legacy_format(search_results: SearchResponse) -> QueryResponse:
    """Convert SearchResponse to legacy QueryResponse format with Llama-enhanced Hindi"""
    
    if not search_results.results:
        error_message = groq_helper.generate_error_response(search_results.search_query, "no_results")
        raise HTTPException(status_code=404, detail=error_message)
    
    # Use the first (most relevant) result
    first_result = search_results.results[0]
    
    # Create scheme data for Groq helper
    scheme_data = {
        'title': first_result.title,
        'description': first_result.description,
        'link': first_result.link
    }
    
    # Generate natural Hindi response using Llama
    hindi_reply = groq_helper.generate_hindi_response(scheme_data, search_results.search_query)
    
    return QueryResponse(
        reply=hindi_reply,
        link=first_result.link,
        scheme_name=first_result.title
    )

# API Endpoints
@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "SwarajyaAI API is running!", 
        "status": "healthy",
        "groq_available": groq_helper.is_available(),
        "search_type": "curated_database",
        "llama_enhanced": True,
        "total_schemes": sum(len(schemes) for schemes in CURATED_SCHEMES_DB.values())
    }

@app.get("/health/groq")
async def groq_health():
    """Health check endpoint for Groq API integration"""
    try:
        is_available = groq_helper.is_available()
        connection_test = groq_helper.test_connection() if is_available else False
        
        return {
            "groq_client_initialized": is_available,
            "groq_api_connection": connection_test,
            "model": os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
            "status": "healthy" if (is_available and connection_test) else "degraded",
            "fallback_available": True,
            "message": "Groq integration working properly" if connection_test else "Using fallback Hindi responses"
        }
    except Exception as e:
        logger.error(f"Groq health check failed: {str(e)}")
        return {
            "groq_client_initialized": False,
            "groq_api_connection": False,
            "status": "error",
            "error": str(e),
            "fallback_available": True,
            "message": "Groq integration failed, using fallback responses"
        }

@app.post("/search", response_model=SearchResponse)
async def search_schemes(request: QueryRequest):
    """Search endpoint returning structured scheme results"""
    
    try:
        if not request.query or len(request.query.strip()) == 0:
            raise HTTPException(status_code=400, detail="Query cannot be empty")
        
        logger.info(f"Search request received: '{request.query}'")
        
        search_results = search_government_schemes(request.query)
        
        logger.info(f"Search completed: {search_results.total_found} results found")
        
        return search_results
        
    except Exception as e:
        logger.error(f"Error in search endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error during search")

@app.post("/query", response_model=QueryResponse)
async def query_schemes(request: QueryRequest):
    """Legacy endpoint for frontend compatibility with Llama-enhanced Hindi responses"""
    
    try:
        if not request.query or len(request.query.strip()) == 0:
            raise HTTPException(status_code=400, detail="Query cannot be empty")
        
        logger.info(f"Legacy query received: '{request.query}'")
        
        # Search for schemes
        search_results = search_government_schemes(request.query)
        
        # Convert to legacy format with Hindi response
        response = convert_to_legacy_format(search_results)
        
        logger.info(f"Legacy query processed: '{request.query}' -> '{response.scheme_name}'")
        
        return response
        
    except HTTPException:
        # Re-raise HTTP exceptions (like 404 when no results found)
        raise
        
    except Exception as e:
        logger.error(f"Error in legacy query endpoint: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail="सरकारी योजनाओं की जानकारी लेने में कुछ समस्या हो रही है। कृपया कुछ देर बाद कोशिश करें।"
        )

@app.get("/debug/{query}")
async def debug_search(query: str):
    """Debug endpoint for troubleshooting search functionality"""
    try:
        logger.info(f"Debug search for query: '{query}'")
        
        search_results = search_government_schemes(query)
        
        debug_info = {
            "query": query,
            "groq_available": groq_helper.is_available(),
            "search_results": search_results.dict(),
            "database_info": {
                "total_categories": len(CURATED_SCHEMES_DB),
                "categories": list(CURATED_SCHEMES_DB.keys()),
                "total_schemes": sum(len(schemes) for schemes in CURATED_SCHEMES_DB.values())
            }
        }
        
        return debug_info
        
    except Exception as e:
        logger.error(f"Debug search failed: {str(e)}")
        return {"error": f"Debug failed: {str(e)}"}

@app.get("/schemes")
async def list_schemes():
    """List available scheme categories"""
    return {
        "message": "Available government scheme categories",
        "categories": list(CURATED_SCHEMES_DB.keys()),
        "total_schemes": sum(len(schemes) for schemes in CURATED_SCHEMES_DB.values()),
        "note": "Use the /search or /query endpoint to find specific schemes"
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)