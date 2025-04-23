from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from agent import run_agent
from logging_config import logger
import traceback

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Server starting up...")
    yield
    logger.info("Server shutting down...")

app = FastAPI(
    title="Story Transformation API",
    version="1.0",
    description="A simple API server for transforming adult stories into children's stories",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/chat")
async def transform_story(request: Request):
    try:
        logger.info("Received chat request")
        data = await request.json()
        story_title = data.get("story_title", "")
        story_text = data.get("story_text", "")
        
        logger.info(f"Processing story with title: {story_title}")
        result = run_agent(story_title=story_title, story_text=story_text)
        logger.info("Successfully processed story")
        return {"output": result}
    except Exception as e:
        logger.error(f"Error in transform_story endpoint: {str(e)}")
        logger.error(f"Stack trace: {traceback.format_exc()}")
        raise

@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Request: {request.method} {request.url}")
    response = await call_next(request)
    logger.info(f"Response status: {response.status_code}")
    return response

@app.get("/")
async def root():
    logger.info("Root endpoint accessed")
    return {"message": "Welcome to the Story Transformation API"}