# Week 2: Story Transformation Agent

A LangChain-based agent that transforms adult stories into children's stories using a multi-step process.

## Features

- Multi-step story transformation process
- FastAPI backend with LangServe integration
- Streamlit frontend
- Comprehensive logging
- Error handling

## Architecture

The project consists of three main components:

1. **Agent** (`agent.py`): The core LangChain implementation that handles the story transformation
2. **API Server** (`main.py`): FastAPI server that exposes the agent via LangServe
3. **Frontend** (`app.py`): Streamlit interface for interacting with the agent

## Setup

1. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up your OpenAI API key in `config.py`

## Running the Application

1. Start the FastAPI server:
   ```bash
   uvicorn main:app --reload
   ```

2. In a separate terminal, start the Streamlit frontend:
   ```bash
   streamlit run app.py
   ```

3. Open your browser to `http://localhost:8501`

## Logging

Logs are stored in the `logs` directory with timestamps. Each run creates a new log file.

## API Endpoints

- `POST /chat/invoke`: Main endpoint for story transformation
- `GET /`: Health check endpoint

## Error Handling

The application includes comprehensive error handling for:
- API requests
- JSON parsing
- Chain execution
- Server errors 