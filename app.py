import io
import time

import streamlit as st
from model import generate_metaphor, generate_image  # Your backend functions

# Minimum seconds a user must wait between "Explain" clicks. Each click can
# trigger two Hugging Face Inference API calls (text + image) against the
# free tier, so nothing was previously stopping rapid repeat-clicking from
# burning through that quota in seconds.
MIN_SECONDS_BETWEEN_REQUESTS = 12

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
            --glass-bg: rgba(255, 255, 255, 0.10);
            --glass-border: rgba(255, 255, 255, 0.35);
            --input-bg: rgba(255, 255, 255, 0.12);
        }

        /* Self-contained "magic nebula" background: a few soft radial glows
           (amber + violet, matching the primary color) over a near-black
           base. No external image -- a hotlinked Unsplash photo used to sit
           here and the specific photo ID had gone dead, which silently
           flattened the whole glassmorphic effect since blur had nothing
           to blur. This can never 404. */
        body {
            margin: 0;
            padding: 0;
            font-family: 'Inter', sans-serif;
            color: var(--color-text-main);
        }

        /* Streamlit renders the whole app inside [data-testid="stApp"], which
           paints its own OPAQUE background (from .streamlit/config.toml's
           theme.backgroundColor) directly on top of <body> -- so a gradient
           on body alone is invisible no matter what, regardless of whether
           any image in it loads. The actual background has to be applied to
           this element instead, since it's the real visible painted layer. */
        html, body, [data-testid="stApp"] {
            min-height: 100vh;
        }

        [data-testid="stApp"] {
            background:
                radial-gradient(circle at 15% 20%, rgba(255, 183, 3, 0.20), transparent 42%),
                radial-gradient(circle at 85% 15%, rgba(157, 111, 232, 0.22), transparent 45%),
                radial-gradient(circle at 50% 100%, rgba(244, 162, 97, 0.16), transparent 55%),
                linear-gradient(180deg, #0b0b0f 0%, #121212 55%, #0b0b0f 100%) !important;
            background-attachment: fixed;
        }

        [data-testid="stAppViewContainer"] .block-container {
            max-width: 680px;
            margin: 40px auto 60px auto;
            padding: 36px 32px 48px 32px !important;
            background: var(--glass-bg);
            border: 1px solid var(--glass-border);
            border-radius: 18px;
            box-shadow: 0 14px 40px rgba(0, 0, 0, 0.45), inset 0 1px 0 rgba(255, 255, 255, 0.08);
            backdrop-filter: blur(18px);
            -webkit-backdrop-filter: blur(18px);
        }

        .header {
            font-weight: 700;
            font-size: 2.8rem;
            text-align: center;
            margin-bottom: 8px;
            color: var(--color-primary);
            text-shadow: 0 0 24px rgba(255, 183, 3, 0.35);
        }

        .subheader {
            font-weight: 500;
            font-size: 1.3rem;
            font-style: italic;
            text-align: center;
            margin-bottom: 40px;
            color: var(--color-text-secondary);
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

        div.stButton > button:first-child {
            transition: transform 0.15s ease, box-shadow 0.15s ease, background-color 0.15s ease;
        }

        div.stButton > button:first-child:hover {
            background-color: var(--color-primary-hover);
            box-shadow: 0 10px 28px rgba(244, 162, 97, 0.6);
            transform: translateY(-2px);
        }

        [data-testid="stImage"] img {
            border-radius: 16px;
            border: 1px solid var(--glass-border);
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
            [data-testid="stAppViewContainer"] .block-container {
                margin: 30px 20px 40px 20px;
                padding: 28px 20px 36px 20px !important;
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

# Persist results across reruns (e.g. typing further in the text box) instead
# of losing them the moment any other widget triggers a Streamlit rerun.
if "explanation" not in st.session_state:
    st.session_state.explanation = None
if "image" not in st.session_state:
    st.session_state.image = None
if "image_error" not in st.session_state:
    st.session_state.image_error = None
if "metaphor_error" not in st.session_state:
    st.session_state.metaphor_error = None
if "last_request_time" not in st.session_state:
    st.session_state.last_request_time = 0.0

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

# Explain button logic
if st.button("Explain", type="primary"):
    seconds_since_last = time.time() - st.session_state.last_request_time
    if topic.strip() == "":
        st.error("Please enter a topic before clicking Explain.")
    elif seconds_since_last < MIN_SECONDS_BETWEEN_REQUESTS:
        wait_left = round(MIN_SECONDS_BETWEEN_REQUESTS - seconds_since_last)
        st.warning(f"Please wait {wait_left}s before generating again.")
    else:
        st.session_state.last_request_time = time.time()
        st.session_state.metaphor_error = None
        st.session_state.image_error = None

        with st.spinner("Generating metaphor..."):
            explanation = generate_metaphor(topic.strip().title())

        if explanation is None:
            # Don't chain a broken metaphor into an image request -- surface a
            # clear error instead, and don't touch any previously-shown result.
            st.session_state.metaphor_error = (
                "Couldn't generate a metaphor right now (the model may be busy or "
                "unavailable). Please try again in a moment."
            )
        else:
            st.session_state.explanation = explanation
            st.session_state.image = None
            st.session_state.image_error = None
            with st.spinner("Creating visual metaphor..."):
                image, error_image = generate_image(explanation)
            st.session_state.image = image
            st.session_state.image_error = error_image

# Surface a failed metaphor generation attempt
if st.session_state.metaphor_error:
    st.error(st.session_state.metaphor_error)

# Show explanation only if available
if st.session_state.explanation:
    st.markdown('<div class="section">', unsafe_allow_html=True)
    st.subheader("Here's your metaphor-based explanation:")
    st.write(st.session_state.explanation)
    st.markdown('</div>', unsafe_allow_html=True)

# Show image or image error if exists
if st.session_state.image:
    st.image(st.session_state.image, width='stretch')
    st.markdown(
        '<p class="image-caption">Visual metaphor created just for you 🎨 </p>',
        unsafe_allow_html=True,
    )

    image_bytes = io.BytesIO()
    st.session_state.image.save(image_bytes, format="PNG")
    st.download_button(
        label="Download image",
        data=image_bytes.getvalue(),
        file_name=f"{topic.strip().replace(' ', '_').lower() or 'magic_metaphor'}.png",
        mime="image/png",
    )
elif st.session_state.image_error:
    st.warning(st.session_state.image_error)

# Footer with your personal touch
st.markdown(
    '<div class="footer">Made with ❤️ by <strong>Sonali</strong></div>',
    unsafe_allow_html=True,
)

