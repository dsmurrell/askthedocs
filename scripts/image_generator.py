import sys
from pathlib import Path

import openai
import requests

sys.path.append(str(Path(__file__).resolve().parent.parent))

from config import config

openai.api_key = config["openai_key"]

prompt = "Stylised cartoon image of a beautiful cute yoga mom eating a sweet, full length shot. Put the image in a playing card. Make the image visibly attractive"

response = openai.Image.create(prompt=prompt, n=1, size="1024x1024")
image_url = response["data"][0]["url"]

print(image_url)

# Download the image using the requests library
response = requests.get(image_url)

# Create a valid filename from the prompt
filename = prompt.replace(" ", "_") + ".png"

# Save the image to a file
with open(filename, "wb") as image_file:
    image_file.write(response.content)

print(f"Image downloaded and saved as '{filename}'")
