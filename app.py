import streamlit as st
from model import generate_metaphor, generate_image  # Your backend functions

# Set page config as first command
st.set_page_config(
    page_title="Hard Topics Explained with Metaphors",
    page_icon="🧠",
    layout="centered",
    initial_sidebar_state="collapsed",
)


# Custom CSS + Google Fonts + Animations + Responsive styles
st.markdown(
    """
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap" rel="stylesheet">

    <style>
        :root {
            --color-primary: #FFB703;  /* warm amber */
            --color-primary-hover: #F4A261;
            --color-text-main: #ffffff;
            --color-text-secondary: #e0e0e0;
            --color-muted: #bbbbbb;
            --glass-bg: rgba(255, 255, 255, 0.08);
            --glass-border: rgba(255, 255, 255, 0.25);
            --input-bg: rgba(255, 255, 255, 0.12);
        }

        body {
            margin: 0;
            padding: 0;
            font-family: 'Inter', sans-serif;
            color: var(--color-text-main);
            background: linear-gradient(to right, rgba(0,0,0,0.7), rgba(0,0,0,0.6)),
                        url('https://images.unsplash.com/photo-1518709268807-1c6d0c5b6f3e?auto=format&fit=crop&w=1600&q=80');
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
        }

        .main-container {
            max-width: 680px;
            margin: 40px auto 60px auto;
            padding: 36px 32px 48px 32px;
            background: var(--glass-bg);
            border: 1px solid var(--glass-border);
            border-radius: 18px;
            box-shadow: 0 14px 40px rgba(0, 0, 0, 0.4);
            backdrop-filter: blur(18px);
            -webkit-backdrop-filter: blur(18px);
        }

        .header {
            font-weight: 700;
            font-size: 2.8rem;
            text-align: center;
            margin-bottom: 8px;
            color: var(--color-primary);
        }

        .subheader {
            font-weight: 500;
            font-size: 1.3rem;
            font-style: italic;
            text-align: center;
            margin-bottom: 40px;
            color: #706565 ;
            text-shadow: 1px 1px 3px rgba(0, 0, 0, 0.6);
        }

        .section {
            margin-top: 32px;
            padding: 28px 24px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 16px;
            box-shadow: 0 6px 24px rgba(0, 0, 0, 0.4);
            font-size: 1.125rem;
            line-height: 1.55;
            color: var(--color-text-main);
            backdrop-filter: blur(10px);
        }

        .image-caption {
            font-size: 0.9rem;
            color: var(--color-muted);
            font-style: italic;
            text-align: center;
            margin-top: 14px;
        }

        div.stButton > button:first-child {
            background-color: var(--color-primary);
            color: #000;
            font-weight: 600;
            font-size: 1.1rem;
            padding: 0.65rem 1.5rem;
            border-radius: 12px;
            border: none;
            box-shadow: 0 8px 20px rgba(255, 183, 3, 0.4);
            width: 100%;
            max-width: 280px;
            display: block;
            margin: 30px auto 0 auto;
            cursor: pointer;
        }

        div.stButton > button:first-child:hover {
            background-color: var(--color-primary-hover);
            box-shadow: 0 10px 28px rgba(244, 162, 97, 0.6);
        }

        div.stTextInput > div > input {
            background: var(--input-bg);
            border-radius: 12px;
            border: 1.5px solid #f0f0f0;
            padding: 12px 18px;
            font-size: 1.1rem;
            color: #fff;
            box-shadow: inset 0 1px 4px rgba(255, 255, 255, 0.2);
            width: 100%;
            max-width: 600px;
            margin: 0 auto;
            display: block;
        }

        div.stTextInput > div > input::placeholder {
            color: #dddddd;
            opacity: 0.8;
        }

        div.stTextInput > div > input:focus {
            border-color: var(--color-primary);
            outline: none;
            box-shadow: 0 0 8px var(--color-primary);
        }

        .footer {
            margin-top: 72px;
            font-size: 0.85rem;
            color: var(--color-muted);
            text-align: center;
            font-weight: 500;
            font-style: italic;
        }

        @media (max-width: 720px) {
            .main-container {
                margin: 30px 20px 40px 20px;
                padding: 28px 20px 36px 20px;
            }
            .header {
                font-size: 2.2rem;
            }
            .subheader {
                font-size: 1.1rem;
            }
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# Main container start
# st.markdown('<div class="main-container">', unsafe_allow_html=True)

# Header & subheader with warm, conversational tone
st.markdown('<h1 class="header">💡✨ Let’s Turn Tough Ideas into Simple Stories with a Touch of Magic</h1>', unsafe_allow_html=True)
st.markdown(
    '<p class="subheader">Share a complex idea, and receive a clear metaphor paired with a vivid visual.</p>',
    unsafe_allow_html=True,
)

# Input
topic = st.text_input(
    "Enter a complex topic (e.g., Quantum Entanglement ):",
    max_chars=50,
    placeholder="E.g., Black Holes",
)

# Initialize variables
explanation = None
image = None
error_image = None

# Explain button logic
if st.button("Explain", type="primary"):
    if topic.strip():
        with st.spinner("Generating metaphor..."):
            explanation = generate_metaphor(topic.strip().title())
        with st.spinner("Creating visual metaphor..."):
            image, error_image = generate_image(explanation)
    else:
        st.error("Please enter a topic before clicking Explain.")

# Show explanation only if available
if explanation:
    # st.markdown('<div class="section">', unsafe_allow_html=True)
    st.subheader("Here's your metaphor-based explanation:")
    st.write(explanation)
    # st.markdown('</div>', unsafe_allow_html=True)

# Show image or image error if exists
if image:
    st.image(image, use_container_width=True)
    st.markdown(
        '<p class="image-caption">Visual metaphor created just for you 🎨 </p>',
        unsafe_allow_html=True,
    )
elif error_image:
    st.warning(error_image)

# Footer with your personal touch
st.markdown(
    '<div class="footer">Made with ❤️ by <strong>Sonali</strong></div>',
    unsafe_allow_html=True,
)

# Main container end
# st.markdown('</div>', unsafe_allow_html=True)
