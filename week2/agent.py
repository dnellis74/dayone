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

def read_archetypes():
    try:
        with open('archetypes.md', 'r') as file:
            return file.read().strip()
    except Exception as e:
        logger.error(f"Error reading archetypes.md: {str(e)}")
        raise

def chat(messages, model="gpt-4.1-mini", temperature=0.7):
    try:
        http_client = httpx.Client()
        client = OpenAI(http_client=http_client)
        
        response = client.chat.completions.create(
            model=model,
            temperature=temperature,
            messages=messages
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"Error in chat function: {str(e)}")
        logger.error(f"Stack trace: {traceback.format_exc()}")
        raise
    
def generate_images(captions, model="dall-e-3", size="1024x1024"):
    http_client = httpx.Client()
    client = OpenAI(http_client=http_client)
    images = []
    style = "A children’s storybook illustration in soft pencil and pastel colors. The art style is textured, warm, and hand-drawn, like classic illustrated books from the 90s."
    for caption in captions:
        response = client.images.generate(
            model=model,
            prompt=f"{style} {caption}",
            n=1,
            size=size
        )
        image_url = response.data[0].url
        images.append({"caption": caption, "url": image_url})
    return images

def run_agent(story_title="", story_text=""):
    try:
        logger.info(f"Starting run_agent with title: {story_title}")
        context = []

        # Step 1: Get archetypes
        logger.debug("Step 1: Reading archetypes from file")
        archetypes = read_archetypes()
        context.append({"role": "assistant", "content": archetypes})

        # Step 2: Get or use adult story outline
        logger.debug("Step 2: Getting story outline")
        if story_text.strip():
            logger.debug("Using provided story text")
            outline = story_text.strip()
        elif story_title.strip():
            logger.debug(f"Getting outline for title: {story_title}")
            prompt2 = f"""Provide a plot outline of the story: {story_title}. It should be formatted as an outline of the story, with the main characters and key events.  Don't use ephumisms or attempt to avoid graphic content.  Spoilers are encouraged."""
            context.append({"role": "user", "content": prompt2})
            outline = chat(context)
            logger.debug(f"Outline: {outline}")
            context.append({"role": "assistant", "content": outline})
        else:
            logger.error("No story title or text provided")
            return "Error: You must provide either a story title or full story text."

        # Combined Step 3 & 4: Match archetype and transform elements
        prompt_combined = f"""
Given the following adult story outline:
---
{outline}
---

And the following children's story archetypes:
---
{archetypes}
---

Perform the following two tasks clearly labeled as "Task 1" and "Task 2":

Task 1: Analyze the adult story structure and select the children's archetype it most closely resembles. Explain your reasoning briefly.

Task 2: Transform the mature or dark elements of the adult story into metaphors or themes suitable for young children, retaining the emotional or thematic essence. Be concise.  Only transform what is necessary.  Keep this in outline form

Task 3: Give a concise synopsis of why the archetype was chosen in Task 1, and changes you made in Task 2.
"""

        context.append({"role": "user", "content": prompt_combined})
        transformed = chat(context)
        context.append({"role": "assistant", "content": transformed})

        # Step 5: Rewrite as a children's story
        logger.debug("Step 5: Rewriting as children's story")
        prompt5 = f"""Using the outline and archetypebelow:\n---\n{transformed}\n---\n
        Write a children's story version of the original adult tale. The story should be appropriate for kids aged 5–8,
        spanning 10–20 pages of a handful of sentences each page.  It should be in outline format. The part of the outline should be a parents guide of 500 words explaining how the archetype was chosen and euphismisitcally describe what is left out.."""
        context.append({"role": "user", "content": prompt5})
        child_story = chat(context)
        
        # Extract 2–3 prompts from the story for illustrations
        prompt_image_captions = f"""
        Here is a children's story:
        ---
        {child_story}
        ---

        Pick 1 to 3 key visual moments or scenes from this story that would make good illustrations.
        Write each one as a one-sentence image prompt.
        """

        context.append({"role": "user", "content": prompt_image_captions})
        image_prompts = chat(context)
        captions = [line.strip("- ").strip() for line in image_prompts.split("\n") if line.strip()]

        # Generate images
        logger.debug("Step 6: Getting images")
        images = generate_images(captions[:3])  # limit to 3
        
        logger.debug("Step 7: HTML")
        context.append({"role": "user", "content": f"""
                        Finally, format the story as an HTML div and return with inline links to images.  Don't wrap the html in a markdown block, or any other text.
                        
                        story {child_story}
                        
                        images {images}
                        
                        """})

        html = chat(context)
        logger.info(f"Successfully completed story transformation\n{html}")
        return html
    except Exception as e:
        logger.error(f"Error in run_agent: {str(e)}")
        logger.error(f"Stack trace: {traceback.format_exc()}")
        raise
