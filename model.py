import os
import requests
from dotenv import load_dotenv
from huggingface_hub import InferenceClient

load_dotenv()
HF_API_KEY = os.getenv("HF_API_KEY")

client = InferenceClient(api_key=HF_API_KEY)

def clean_response(text):
    stop_phrases = [
        "Would you like", "Do you want", "Need another", "😊", "😉", "🙂"
    ]
    for phrase in stop_phrases:
        if phrase in text:
            return text.split(phrase)[0].strip()
    return text.strip()

def generate_metaphor(topic):
    prompt = (
        f"Explain the topic '{topic}' using a simple and creative metaphor for a high school student. "
        f"Give only one metaphor. Do not include emojis, follow-up questions, or suggestions."
    )
    try:
        completion = client.chat.completions.create(
            model="deepseek-ai/DeepSeek-V3-0324",
            messages=[{"role": "user", "content": prompt}],
        )
        raw_response = completion.choices[0].message["content"]
        return clean_response(raw_response)
    except Exception as e:
        return f"❌ Error generating explanation: {str(e)}"

def generate_image(prompt):
    try:
        image = client.text_to_image(
            prompt=prompt,
            model="black-forest-labs/FLUX.1-dev"
        )
        return image, None
    except Exception as e:
        return None, f"❌ Image generation failed: {e}"
