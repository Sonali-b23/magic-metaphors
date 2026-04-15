import streamlit as st
from model import generate_metaphor, generate_image

st.set_page_config(page_title="Magic Metaphors", page_icon="🧠", layout="centered")

# --- UI Layout ---
st.title("💡 Magic Metaphors")
st.markdown("Turn tough ideas into simple stories.")

# Using a container with a border gives it that "Glass/Card" feel natively
with st.container(border=True):
    topic = st.text_input("Enter a complex topic:", placeholder="E.g., Quantum Entanglement")
    
    if st.button("Explain", type="primary"):
        if not topic.strip():
            st.error("Please enter a topic.")
        else:
            with st.spinner("Conjuring your metaphor..."):
                explanation = generate_metaphor(topic)
                st.info(explanation)
                
                with st.spinner("Painting your visual..."):
                    img, err = generate_image(explanation)
                    if img:
                        st.image(img, use_column_width=True)
                        st.caption("Visual metaphor created for you 🎨")
                    else:
                        st.warning(err)

st.markdown("<br><hr><p style='text-align: center;'>Made with ❤️ by Sonali</p>", unsafe_allow_html=True)
