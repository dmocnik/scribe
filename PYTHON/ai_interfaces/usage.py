# [ Example usage file for ai_inference class ]

# MIT License
# Copyright (c) 2024

# Imports
import os
from ai_inference import ai_inference

# Load vars from .env file in the current directory
from dotenv import load_dotenv
load_dotenv()

"""
Available categories: gemini, gpt
Available models:   gemini-1.0-pro / gemini-1.0-pro-001 / gemini-1.0-pro-latest / gemini-1.0-pro-vision-latest / gemini-pro / gemini-pro-vision / gemini-1.5-pro-latest (if you are beta tester)
                    gpt-3.5-turbo, ...
"""

# Create an instance of the ai_inference class using gemini-1.0-pro
# ai_inference_obj = ai_inference(model_category="gemini", model_name="gemini-1.0-pro-latest", api_key=os.environ.get("AI_API_KEY"))
# Create ai inference object using gpt-3.5-turbo
ai_inference_obj = ai_inference(model_category="gpt", model_name="gpt-3.5-turbo", api_key=os.environ.get("AI_API_KEY"))

# Add a system message to the model
ai_inference_obj.add_chat(prompt="Please remember that your name is PAUL.", response="Okay, my name is PAUL.") # Response isn't included with Gemini, only GPT!

# Ask a basic question to test the model (prints within object)
# response_text = ai_inference_obj.generate_text("Please flip the meaning of this text: I need to shower tonight before I eat some cheese.")
response_text = ai_inference_obj.generate_text("What is your name?")

# Ask a question, but mess with all the parameters
response_text = ai_inference_obj.generate_text("Please write a short story about a man named PAUL.", max_chars=500, stop_char="BRUH", temperature=0.5)

# Ask a question about an image (prints within object)
# response_text = ai_inference_obj.ask_image("Why is this funny?", "PYTHON/ai_interfaces/example.png")

# Garbage collection (calls shutdown method)
del ai_inference_obj
