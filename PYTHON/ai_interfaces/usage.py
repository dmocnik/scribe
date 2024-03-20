# [ Example usage file for ai_inference class ]

# MIT License
# Copyright (c) 2024

# Imports
import os
from ai_inference import ai_inference

# Load vars from .env file in the current directory
from dotenv import load_dotenv
load_dotenv()

# Available categories: gemini
# Available models: gemini-1.0-pro / gemini-1.0-pro-001 / gemini-1.0-pro-latest / gemini-1.0-pro-vision-latest / gemini-pro / gemini-pro-vision / gemini-1.5-pro-latest (if you are beta tester)

# Create an instance of the ai_inference class using gemini-1.0-pro
ai_inference_obj = ai_inference(model_category="gemini", model_name="gemini-1.0-pro-vision-latest", api_key=os.environ.get("AI_API_KEY"))

# Ask a basic question to test the model (prints within object)
# ai_inference_obj.generate_text("Please flip the meaning of this text: I need to shower tonight before I eat some cheese.")

# Ask a question about an image (prints within object)
ai_inference_obj.generate_text_with_image("Why is this funny?", "example.png")

# Garbage collection (calls shutdown method)
del ai_inference_obj
