from openai import OpenAI
from dotenv import load_dotenv
import httpx
from logging_config import logger
import traceback
import os

# Load environment variables
load_dotenv()

# Try to get API key from environment first, fall back to config if not found
try:
    from config import OPENAI_API_KEY
    api_key = os.getenv("OPENAI_API_KEY", OPENAI_API_KEY)
except ImportError:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY not found in environment variables")

def chat(messages, model="gpt-4", temperature=0.7):
    try:
        logger.debug("Creating httpx client")
        http_client = httpx.Client()
        
        logger.debug("Creating OpenAI client")
        client = OpenAI(http_client=http_client)
        
        logger.info(f"Sending request to OpenAI with model {model}")
        response = client.chat.completions.create(
            model=model,
            temperature=temperature,
            messages=messages
        )
        logger.debug("Successfully received response from OpenAI")
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"Error in chat function: {str(e)}")
        logger.error(f"Stack trace: {traceback.format_exc()}")
        raise

def run_agent(story_title="", story_text=""):
    try:
        logger.info(f"Starting run_agent with title: {story_title}")
        context = []

        # Step 1: Get archetypes
        logger.debug("Step 1: Getting archetypes")
        prompt1 = """List common archetypes and story structures used in children's books. Include examples like 'The Hero's Journey', 'Overcoming the Monster', 'Rags to Riches', and explain each in 1-2 sentences."""
        context.append({"role": "user", "content": prompt1})
        archetypes = chat(context)
        context.append({"role": "assistant", "content": archetypes})

        # Step 2: Get or use adult story summary
        logger.debug("Step 2: Getting story summary")
        if story_text.strip():
            logger.debug("Using provided story text")
            summary = story_text.strip()
        elif story_title.strip():
            logger.debug(f"Getting summary for title: {story_title}")
            prompt2 = f"""Provide a brief plot summary of the story: {story_title}. If it's in the public domain, include key elements and themes."""
            context.append({"role": "user", "content": prompt2})
            summary = chat(context)
            context.append({"role": "assistant", "content": summary})
        else:
            logger.error("No story title or text provided")
            return "Error: You must provide either a story title or full story text."

        # Step 3: Match to children's archetype
        logger.debug("Step 3: Matching to archetype")
        prompt3 = f"""Given the following adult story summary:\n---\n{summary}\n---\nAnd the following children's story archetypes:\n---\n{archetypes}\n---\nAnalyze the structure of the adult story and select the children's archetype it most closely resembles. Explain your reasoning."""
        context.append({"role": "user", "content": prompt3})
        matched_archetype = chat(context)
        context.append({"role": "assistant", "content": matched_archetype})

        # Step 4: Transform mature elements
        logger.debug("Step 4: Transforming mature elements")
        prompt4 = f"""Using the following adult story summary:\n---\n{summary}\n---\nTransform the more mature or dark elements into metaphors or themes suitable for young children, while retaining the emotional or thematic essence."""
        context.append({"role": "user", "content": prompt4})
        transformed = chat(context)
        context.append({"role": "assistant", "content": transformed})

        # Step 5: Rewrite as a children's story
        logger.debug("Step 5: Rewriting as children's story")
        prompt5 = f"""Using the transformed elements below:\n---\n{transformed}\n---\nWrite a children's story version of the original adult tale. The story should be appropriate for kids aged 5–8, spanning 10–20 pages of 1–2 sentences each. Format the output as a list of short pages."""
        context.append({"role": "user", "content": prompt5})
        child_story = chat(context)

        logger.info("Successfully completed story transformation")
        return child_story
    except Exception as e:
        logger.error(f"Error in run_agent: {str(e)}")
        logger.error(f"Stack trace: {traceback.format_exc()}")
        raise
