import streamlit as st
from agent import run_agent

st.set_page_config(
    page_title="KidKind Classics",
    layout="centered"   
)
st.title("🧒📖 KidKind Classics")

input_mode = st.radio("How would you like to provide the adult story?", ["Use a story title", "Paste story text"])

story_title = ""
story_text = ""

if input_mode == "Use a story title":
    story_title = st.text_input("Got a tale you'd like to reimagine for little ears?", "The Tell-Tale Heart")
else:
    story_text = st.text_area("Paste the full story or a detailed summary")

if st.button("Transform"):
    with st.spinner("Rewriting for young readers..."):
        try:
            result = run_agent(story_title=story_title, story_text=story_text)
            st.subheader("📚 Story Transformation")
            # Render the HTML div safely
            st.html(result)
        except Exception as e:
            st.error(f"An error occurred: {e}")
