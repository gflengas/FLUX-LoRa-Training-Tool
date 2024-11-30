import os
import base64
from openai import OpenAI
from src.config import XAI_API_KEY

def encode_image(image_path):
    """Encodes an image file to base64 string format.

    Takes an image file from the specified path and converts it into a base64 
    encoded string representation, which can be used for API requests requiring 
    image data in base64 format.

    Args:
        image_path (str): Path to the image file that needs to be encoded.

    Returns:
        str: Base64 encoded string representation of the input image.
    """
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')
  
def generate_description(image_path, token, type):
    """
    Generates a physical description of a person from an input image using 
    X.AI API through the openAI SDK.

    This function takes an image containing a person, encodes it to base64, 
    and uses the X.AI API to generate a concise description focusing on 
    physical characteristics relevant for image generation training.

    Args:
        image_path (str): Path to the input image file containing a person.
        token (str): Token to include in the description (e.g., "a person").
        type (str): Determines which prompt to use ("human", "pet", or "item").

    Returns:
        str: A cleaned string containing the generated description with all tabs 
            and newlines removed.
    """
    base64_image = encode_image(image_path)
    client = OpenAI(
        api_key=XAI_API_KEY,
        base_url="https://api.x.ai/v1",
    )

    # Define the prompts for different types
    if type == "human":
        prompt = """Provide a brief, objective description of the\
                    person in this image, focusing on:\
                    1. Face: shape, distinctive features, expression\
                    2. Body type/build\
                    3. Overall visual style/physique\
                    Describe only clear, observable physical\
                    attributes relevant for image generation. Start\
                    the description with: "A photo of {token}."""
        
    elif type == "pet":
        prompt = """Provide a brief, objective description of the\
                    pet in this image, focusing on:\
                    1. Species and breed (if identifiable)\
                    2. Size and physical build\
                    3. Distinctive markings, fur texture, or color\
                    4. Expression or demeanor (if observable)\
                    Describe only clear, observable physical\
                    attributes relevant for image generation. Start\
                    the description with: "A photo of {token}."""
        
    elif type == "item":
        prompt = """Provide a brief, objective description of the\
                    item in this image, focusing on:\
                    1. Shape and size\
                    2. Material and texture\
                    3. Color and any distinctive features\
                    Describe only clear, observable physical\
                    attributes relevant for image generation. Start\
                    the description with: "A photo of {token}."""
    else:
        raise ValueError("Invalid type. Choose 'human', 'pet', or 'item'.")

    # Format the prompt with the token
    formatted_prompt = prompt.format(token=token)

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
                    "text": formatted_prompt,
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
        content = chunk.choices[0].delta.content
        if content:
            response_content += content

    # Remove tabs and newlines
    cleaned_content = response_content.replace("\t", "").replace("\n", "")

    return cleaned_content
