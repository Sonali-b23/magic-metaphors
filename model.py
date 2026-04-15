import os
import time
from dotenv import load_dotenv
from huggingface_hub import InferenceClient

load_dotenv()
client = InferenceClient(api_key=os.getenv("HF_API_KEY"))

def generate_metaphor(topic):
    prompt = f"Explain '{topic}' using a simple metaphor for a high school student. No emojis or follow-up questions."
    
    # Retry logic
    for i in range(3):
        try:
            res = client.chat.completions.create(
                model="deepseek-ai/DeepSeek-V3-0324",
                messages=[{"role": "user", "content": prompt}]
            )
            return res.choices[0].message["content"].strip()
        except Exception:
            time.sleep(1)
    return "Could not generate metaphor at this time."

def generate_image(prompt):
    try:
        # Use a descriptive prompt for the image
        img_prompt = f"A beautiful artistic illustration of: {prompt}"
        image = client.text_to_image(prompt=img_prompt, model="stabilityai/stable-diffusion-xl-base-1.0")
        return image, None
    except Exception as e:
        return None, str(e)
