from pathlib import Path

import streamlit as st

from app.core import evaluate_guide
from app.llm import generate_guide
from app.storage import GuideStore

st.set_page_config(page_title="Local Travel Guide Generator", page_icon="🧭", layout="centered")
st.title("Local Travel Guide Generator")
st.write("Create a compact local guide shaped around a traveler's interests.")

with st.form("guide_form"):
    destination = st.text_input("Destination", placeholder="Porto")
    interests = st.text_input("Interests", placeholder="food, architecture, waterfront")
    submitted = st.form_submit_button("Make my guide", type="primary")

if submitted:
    if not destination.strip() or not interests.strip():
        st.error("Enter a destination and at least one interest.")
    else:
        try:
            guide, source = generate_guide(destination, interests)
            st.subheader(f"A short guide to {destination.strip()}")
            st.write(guide)
            st.caption(f"Generated with {source}")
            st.caption(f"Simple relevance check: {evaluate_guide(guide, destination, interests)['relevance_score']:.0%}")
            if not guide.startswith("I don't have a matching sample"):
                GuideStore(Path("artifacts/guide_history.jsonl")).save(destination, interests, guide)
        except Exception as error:
            st.error(str(error))

with st.expander("About this starter"):
    st.write("The app runs in sample mode out of the box. Optional LoRA training uses GPT-2; add the training dependencies listed in requirements.txt when you are ready.")
