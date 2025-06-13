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
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI()

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
except OSError:
    print("Downloading spaCy model...")
    spacy.cli.download("en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

class PromptRequest(BaseModel):
    text: str

class Entity(BaseModel):
    text: str
    label: str
    start: int
    end: int

class PromptResponse(BaseModel):
    entities: List[Entity]
    llm_response: str
    error: str = None

def check_ollama_status():
    try:
        response = requests.get("http://localhost:11434/api/tags")
        return response.status_code == 200
    except requests.exceptions.ConnectionError:
        return False

@app.get("/")
async def read_root():
    return FileResponse("static/index.html")

@app.post("/api/process", response_model=PromptResponse)
async def process_prompt(request: PromptRequest):
    try:
        # Process with spaCy
        doc = nlp(request.text)
        entities = [
            Entity(
                text=ent.text,
                label=ent.label_,
                start=ent.start_char,
                end=ent.end_char
            )
            for ent in doc.ents
        ]

        # Log detected entities
        logger.info("Detected Entities:")
        for entity in entities:
            logger.info(f"- {entity.text} ({entity.label})")

        # Check if Ollama is running
        if not check_ollama_status():
            logger.error("Ollama is not running. Please start Ollama first.")
            return PromptResponse(
                entities=entities,
                llm_response="",
                error="Ollama is not running. Please start Ollama first."
            )

        # Process with Ollama
        try:
            ollama_response = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": "llama2",
                    "prompt": request.text,
                    "stream": False
                },
                timeout=30  # Add timeout
            )
            
            if ollama_response.status_code != 200:
                error_msg = f"Ollama API error: {ollama_response.text}"
                logger.error(error_msg)
                return PromptResponse(
                    entities=entities,
                    llm_response="",
                    error=error_msg
                )
            
            llm_response = ollama_response.json()["response"]
            
            # Log LLM response
            logger.info("\nLLM Response:")
            logger.info(llm_response)

            return PromptResponse(
                entities=entities,
                llm_response=llm_response
            )

        except requests.exceptions.Timeout:
            error_msg = "Ollama request timed out. Please try again."
            logger.error(error_msg)
            return PromptResponse(
                entities=entities,
                llm_response="",
                error=error_msg
            )
        except requests.exceptions.RequestException as e:
            error_msg = f"Error connecting to Ollama: {str(e)}"
            logger.error(error_msg)
            return PromptResponse(
                entities=entities,
                llm_response="",
                error=error_msg
            )

    except Exception as e:
        error_msg = f"Error processing request: {str(e)}"
        logger.error(error_msg)
        return PromptResponse(
            entities=[],
            llm_response="",
            error=error_msg
        ) 