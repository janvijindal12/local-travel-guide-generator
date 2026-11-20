from pathlib import Path

import streamlit as st

from app.core import evaluate_guide, load_examples
from app.llm import NO_MATCH, generate_guide
from app.storage import GuideStore

st.set_page_config(page_title="Bellwether Bay Guidebook", page_icon="🧭", layout="centered")
st.title("Bellwether Bay Guidebook")
st.write("A small travel desk for putting together a short, interest-led day in Bellwether Bay, a fictional coastal town.")

examples = load_examples()
interests = sorted({interest for row in examples for interest in row["interests"].split(", ")})

with st.form("guide_form"):
    destination = st.text_input("Destination", value="Bellwether Bay")
    selected = st.multiselect("What sounds good?", interests, default=["seafood", "harbor"])
    extra = st.text_input("Add another interest", placeholder="For example: photography")
    submitted = st.form_submit_button("Build my mini-guide", type="primary")

if submitted:
    chosen = selected + ([extra.strip()] if extra.strip() else [])
    interest_text = ", ".join(dict.fromkeys(chosen))
    if not destination.strip() or not interest_text:
        st.error("Enter a destination and choose or add at least one interest.")
    else:
        try:
            guide, source = generate_guide(destination, interest_text)
            st.subheader(f"A few ideas for {destination.strip()}")
            st.write(guide)
            st.caption(f"Source: {source}")
            if guide != NO_MATCH:
                report = evaluate_guide(guide, destination, interest_text)
                st.caption(f"Keyword relevance: {report['relevance_score']:.0%} · {report['word_count']} words")
                GuideStore(Path("artifacts/guide_history.jsonl")).save(destination, interest_text, guide)

                with st.expander("How this score works"):
                    st.write("The score is the share of destination and interest words that also appear in the guide. It is a quick relevance signal, not a factuality or writing-quality rating.")
        except Exception as error:
            st.error(str(error))

with st.expander("About this demo"):
    st.write("The examples are hand-written for a fictional town. The sample mode works offline. Optional training uses GPT-2 with PEFT LoRA; the small dataset is for demonstrating the workflow, not for making a production travel model.")
