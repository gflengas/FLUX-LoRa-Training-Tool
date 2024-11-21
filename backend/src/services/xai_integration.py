import os
import base64
from openai import OpenAI
from src.config import XAI_API_KEY

def encode_image(image_path):
  with open(image_path, "rb") as image_file:
    return base64.b64encode(image_file.read()).decode('utf-8')
  
def generate_description(image_path):

    base64_image = encode_image(image_path)
    client = OpenAI(
        api_key=XAI_API_KEY,
        base_url="https://api.x.ai/v1",
    )

    messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{base64_image}",
                        "detail": "high",
                    },
                },
                {
                    "type": "text",
                    "text": """Analyze the provided image, focusing on the 
                            human subject. Describe their face and body/physique 
                            characteristics in detail but keep the response 
                            concise. Include details such as facial features, 
                            expressions, age range, body type, posture, and any 
                            notable attributes related to appearance. 
                            Avoid mentioning background details or unrelated 
                            elements. ?""",
                },
            ],
        },
    ]   

    stream = client.chat.completions.create(
        model="grok-vision-beta",
        messages=messages,
        stream=True,
        temperature=0.01,       
    )

    # Collect streamed content into a variable
    response_content = ""
    for chunk in stream:
        # print(chunk.choices[0].delta.content, end="", flush=True)
        content = chunk.choices[0].delta.content
        if content:
            response_content += content

    # Remove tabs and newlines
    cleaned_content = response_content.replace("\t", "").replace("\n", "")

    return(cleaned_content)
