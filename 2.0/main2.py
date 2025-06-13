from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import spacy
import requests
import json
from typing import List, Dict, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="PII Detection System", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load spaCy model
try:
    nlp = spacy.load("en_core_web_sm")
    logger.info("spaCy model loaded successfully")
except OSError:
    logger.error("spaCy model not found. Please install it using: python -m spacy download en_core_web_sm")
    raise

# Ollama configuration
OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_MODEL = "llama2"  # Change this to your preferred model

# Pydantic models
class PromptRequest(BaseModel):
    prompt: str

class EntityData(BaseModel):
    text: str
    label: str
    start: int
    end: int
    confidence: float

class APIResponse(BaseModel):
    success: bool
    entities: List[EntityData]
    llm_response: str
    sanitized_prompt: str
    original_prompt: str

def extract_entities(text: str) -> List[EntityData]:
    """Extract named entities using spaCy NER"""
    doc = nlp(text)
    entities = []
    
    for ent in doc.ents:
        # Map spaCy labels to our categories
        entity_type = map_entity_type(ent.label_)
        
        entities.append(EntityData(
            text=ent.text,
            label=entity_type,
            start=ent.start_char,
            end=ent.end_char,
            confidence=round(float(ent._.get("confidence", 0.9)), 2)  # Default confidence
        ))
    
    return entities

def map_entity_type(spacy_label: str) -> str:
    """Map spaCy entity types to our PII categories"""
    mapping = {
        "PERSON": "Person Name",
        "GPE": "Location",
        "LOC": "Location", 
        "ORG": "Organization",
        "PHONE_NUMBER": "Phone Number",
        "EMAIL": "Email Address",
        "DATE": "Date",
        "TIME": "Time",
        "MONEY": "Financial Info",
        "CARDINAL": "Number",
        "ORDINAL": "Number"
    }
    return mapping.get(spacy_label, spacy_label)

def sanitize_prompt(text: str, entities: List[EntityData]) -> str:
    """Replace detected entities with generic placeholders"""
    sanitized = text
    
    # Sort entities by start position in reverse order to avoid index shifting
    sorted_entities = sorted(entities, key=lambda x: x.start, reverse=True)
    
    placeholders = {
        "Person Name": "[PERSON]",
        "Location": "[LOCATION]",
        "Email Address": "[EMAIL]",
        "Phone Number": "[PHONE]",
        "Organization": "[ORG]",
        "Date": "[DATE]",
        "Time": "[TIME]",
        "Financial Info": "[MONEY]",
        "Number": "[NUMBER]"
    }
    
    for entity in sorted_entities:
        placeholder = placeholders.get(entity.label, f"[{entity.label.upper()}]")
        sanitized = sanitized[:entity.start] + placeholder + sanitized[entity.end:]
    
    return sanitized

async def query_ollama(prompt: str) -> str:
    """Query Ollama API with the given prompt"""
    try:
        payload = {
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False
        }
        
        response = requests.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            return result.get("response", "No response from LLM")
        else:
            logger.error(f"Ollama API error: {response.status_code} - {response.text}")
            return f"Error from LLM API: {response.status_code}"
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to connect to Ollama: {str(e)}")
        return f"Failed to connect to LLM: {str(e)}"

# API Routes
@app.post("/api/process", response_model=APIResponse)
async def process_prompt(request: PromptRequest):
    """Main endpoint to process user prompt"""
    try:
        original_prompt = request.prompt
        logger.info(f"Processing prompt: {original_prompt}")
        
        # Step 1: Extract entities using spaCy NER
        entities = extract_entities(original_prompt)
        logger.info(f"Detected entities: {[{'text': e.text, 'label': e.label} for e in entities]}")
        
        # Step 2: Sanitize the prompt for LLM
        sanitized_prompt = sanitize_prompt(original_prompt, entities)
        logger.info(f"Sanitized prompt: {sanitized_prompt}")
        
        # Step 3: Query local LLM
        llm_response = await query_ollama(sanitized_prompt)
        logger.info(f"LLM response: {llm_response[:100]}...")  # Log first 100 chars
        
        # Console output for demonstration
        print("\n" + "="*50)
        print("DETECTED NAMED ENTITIES:")
        print("="*50)
        for entity in entities:
            print(f"• {entity.text} ({entity.label}) - Confidence: {entity.confidence}")
        
        print("\n" + "="*50)
        print("LLM RESPONSE:")
        print("="*50)
        print(llm_response)
        print("="*50 + "\n")
        
        return APIResponse(
            success=True,
            entities=entities,
            llm_response=llm_response,
            sanitized_prompt=sanitized_prompt,
            original_prompt=original_prompt
        )
        
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "ollama_url": OLLAMA_BASE_URL, "model": OLLAMA_MODEL}

# Serve static files (HTML interface)
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def serve_frontend():
    """Serve the main HTML interface"""
    return FileResponse("static/index.html")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)