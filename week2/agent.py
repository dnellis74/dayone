from openai import OpenAI
from dotenv import load_dotenv
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
    # Create a fresh client for each call
    client = OpenAI()
    response = client.chat.completions.create(
        model=model,
        temperature=temperature,
        messages=messages
    )
    return response.choices[0].message.content.strip()

def run_agent(story_title="", story_text=""):
    context = []

    # Step 1: Get archetypes
    prompt1 = """List common archetypes and story structures used in children's books. Include examples like 'The Hero's Journey', 'Overcoming the Monster', 'Rags to Riches', and explain each in 1-2 sentences."""
    context.append({"role": "user", "content": prompt1})
    archetypes = chat(context)
    context.append({"role": "assistant", "content": archetypes})

    # Step 2: Get or use adult story summary
    if story_text.strip():
        summary = story_text.strip()
    elif story_title.strip():
        prompt2 = f"""Provide a brief plot summary of the story: {story_title}. If it's in the public domain, include key elements and themes."""
        context.append({"role": "user", "content": prompt2})
        summary = chat(context)
        context.append({"role": "assistant", "content": summary})
    else:
        return "Error: You must provide either a story title or full story text."

    # Step 3: Match to children's archetype
    prompt3 = f"""Given the following adult story summary:\n---\n{summary}\n---\nAnd the following children's story archetypes:\n---\n{archetypes}\n---\nAnalyze the structure of the adult story and select the children's archetype it most closely resembles. Explain your reasoning."""
    context.append({"role": "user", "content": prompt3})
    matched_archetype = chat(context)
    context.append({"role": "assistant", "content": matched_archetype})

    # Step 4: Transform mature elements
    prompt4 = f"""Using the following adult story summary:\n---\n{summary}\n---\nTransform the more mature or dark elements into metaphors or themes suitable for young children, while retaining the emotional or thematic essence."""
    context.append({"role": "user", "content": prompt4})
    transformed = chat(context)
    context.append({"role": "assistant", "content": transformed})

    # Step 5: Rewrite as a children's story
    prompt5 = f"""Using the transformed elements below:\n---\n{transformed}\n---\nWrite a children's story version of the original adult tale. The story should be appropriate for kids aged 5–8, spanning 10–20 pages of 1–2 sentences each. Format the output as a list of short pages."""
    context.append({"role": "user", "content": prompt5})
    child_story = chat(context)

    return child_story
