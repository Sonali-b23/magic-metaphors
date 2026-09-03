import logging
import os
import time
from dotenv import load_dotenv
from huggingface_hub import InferenceClient


load_dotenv()
client = InferenceClient(api_key=os.getenv("HF_API_KEY"))

# Full exception details (which can include request/response internals from
# the HF API) go to the server-side log only -- never into a string shown to
# the user in the UI, since that would leak implementation details to anyone
# using the deployed app.
logger = logging.getLogger(__name__)
if not logger.handlers:
    logging.basicConfig(level=logging.INFO)


def generate_metaphor(topic, retries=3, backoff_seconds=1.5):
    """
    Returns a metaphor-based explanation string for `topic`, or None if every
    retry attempt failed (network blip, rate limit, model unavailable, etc.).
    Callers should check for None rather than comparing against a hardcoded
    failure string.
    """
    prompt = f"Explain '{topic}' using a simple metaphor for a high school student. No emojis or follow-up questions."

    last_error = None
    for attempt in range(retries):
        try:
            res = client.chat.completions.create(
                model="deepseek-ai/DeepSeek-V3-0324",
                messages=[{"role": "user", "content": prompt}],
            )
            # Attribute access (not res.choices[0].message["content"]): huggingface_hub's
            # response dataclasses currently also support dict-style subscripting for
            # backward compatibility, but their own docs note that's being phased out --
            # attribute access is the forward-compatible way to read it.
            content = res.choices[0].message.content
            if content:
                return content.strip()
            last_error = "Empty response from model"
        except Exception as e:
            last_error = e
            time.sleep(backoff_seconds * (attempt + 1))  # simple linear backoff

    logger.warning("generate_metaphor failed after %d attempts: %s", retries, last_error)
    return None


def generate_image(prompt):
    """
    Returns (image, error). `image` is a PIL Image on success, None on failure;
    `error` is a user-facing message on failure, None on success.
    """
    if not prompt:
        return None, "No metaphor text available to illustrate."

    try:
        img_prompt = f"A beautiful artistic illustration of: {prompt}"
        image = client.text_to_image(prompt=img_prompt, model="stabilityai/stable-diffusion-xl-base-1.0")
        return image, None
    except Exception as e:
        # Log the real exception server-side only; the user gets a generic,
        # non-leaky message (no model names, no raw API/exception text).
        logger.warning("generate_image failed: %s", e)
        return None, "Could not generate an image right now. Your metaphor is still shown below."
