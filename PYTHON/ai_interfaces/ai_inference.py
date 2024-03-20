# MIT License
# Copyright (c) 2024

# [ Check out the `usage.py` file for an example, as well as ``../../DOCS/AI Interfaces.md` for documentation! ]

# TODO: Chat history / multiple prompts for tuning, GPT support, ...

# Attempt to import all necessary libraries
try:
    import os # General
    import PIL.Image # Image processing
    from rich import print as rich_print # Pretty print
    from rich.traceback import install # Pretty traceback
    install() # Install traceback
except ImportError as e:
    print("[INFO] You are missing one or more libraries. Please use PIP to install any missing ones.")
    print("Try running `python3 -m pip install -r ../../requirements.txt` OR `pip install -r ../../requirements.txt`.")
    print(f"Traceback: {e}")
    quit()

# Determine the main project directory, for compatibility (the absolute path to this file)
maindirectory = os.path.join(os.path.dirname(os.path.abspath(__file__))) 

# Class to interface with several AI models
class ai_inference:
    def __init__(self, model_category="gemini", model_name="gemini-1.0-pro", api_key=""):
        print("[INFO] Initializing AI inference...")
        # Set other vars
        self.model_name = model_name
        self.model_category = model_category
        # "Switch" based on model category
        if model_category == "gemini":
            # Load imports for gemini usage
            import pathlib
            import textwrap
            import google.generativeai as genai
            # API key required
            self.load_api_key(api_key)
            # Create gemini instance
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel(self.model_name)
        else:
            print(f"[ERROR] Model {model_category} and/or {model_name} is not found")
            return False
        # Show completion message
        print('[INFO] AI inference object init successful')
        
    def load_api_key(self, api_key):
        # Set api key
        self.api_key = str(api_key)
        # If api_key is blank, attempt to find from environment variable
        if self.api_key == "":
            try:
                self.api_key = os.environ.get("AI_API_KEY")
            except Exception as e:
                print(f"[ERROR] Failed to get API key from environment vars. Output: {str(e)}")
                return False
    
    def generate_text(self, prompt, max_chars=0, stop_char=None):
        print(f"[AI] Asking model to generate text based on prompt '{prompt}'")
        # Generate text based on model
        if self.model_category == "gemini":
            # Generate text
            response_obj = self.model.generate_content(prompt)
            response = response_obj.text # Get text in response
        else:
            print(f"[ERROR] Unknown model {self.model_category} or {self.model_name}")
            return False
        # Truncate text if specified, and append stop_char if specified
        if max_chars > 0:
            if stop_char != None:
                response = response[:max_chars-1] + stop_char
            else:
                response = response[:max_chars]
        else:
            if stop_char != None:
                response = response + stop_char
        print(f"[AI] Model response: '{response}'")
        # Return response
        return response

    def generate_text_with_image(self, prompt, image_path, max_chars=0, stop_char=None):
        # Check if image path exists
        if not os.path.exists(os.path.join(image_path)):
            print(f"[ERROR] Image path {image_path} does not exist")
            return False
        print(f"[AI] Asking model to generate text based on prompt '{prompt}' and image '{image_path}'")
        # Generate text based on model
        if self.model_category == "gemini":
            # If "vision" not in model name, return error
            if "vision" not in self.model_name:
                print(f"[ERROR] Model {self.model_name} does not support image input, try adding '-vision' to the model name.")
                return False
            # Retrieve image
            input_image = PIL.Image.open(os.path.join(image_path))
            # Generate text with image
            response_obj = self.model.generate_content([prompt, input_image])
            response_obj.resolve() # Wait for response
            response = response_obj.text # Get text in response
        else:
            print(f"[ERROR] Unknown model {self.model_category} or {self.model_name}")
            return False
        # Truncate text if specified, and append stop_char if specified
        if max_chars > 0:
            if stop_char != None:
                response = response[:max_chars-1] + stop_char
            else:
                response = response[:max_chars]
        else:
            if stop_char != None:
                response = response + stop_char
        print(f"[AI] Model response: '{response}'")
        # Return response
        return response
    
    def shutdown(self):
        # Shutdown any additional items
        print("[INFO] Shutting down AI object...")
        # [Nothing here yet]
        return True

    def __del__(self):
        # Shutdown any additional items
        self.shutdown()
