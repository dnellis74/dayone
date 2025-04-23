import streamlit as st
from agent import run_agent

st.set_page_config(page_title="Story Transformer", layout="centered")
st.title("🧒📖 Adult-to-Children Story Transformer")

input_mode = st.radio("How would you like to provide the adult story?", ["Use a story title", "Paste story text"])

story_title = ""
story_text = ""

if input_mode == "Use a story title":
    story_title = st.text_input("Enter a well-known adult story title", "The Tell-Tale Heart")
else:
    story_text = st.text_area("Paste the full story or a detailed summary")

if st.button("Transform"):
    with st.spinner("Rewriting for young readers..."):
        try:
            result = run_agent(story_title=story_title, story_text=story_text)
            st.subheader("📚 Your Transformed Children's Story")
            for i, page in enumerate(result.split("\n"), 1):
                if page.strip():
                    st.markdown(f"**Page {i}:** {page.strip()}")
        except Exception as e:
            st.error(f"An error occurred: {e}")
