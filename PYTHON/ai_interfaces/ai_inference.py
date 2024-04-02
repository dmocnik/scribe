# MIT License
# Copyright (c) 2024

# [ Check out the `usage.py` file for an example, as well as ``../../DOCS/AI Interfaces.md` for documentation! ]

# TODO: Chat history / multiple prompts for tuning, GPT support, ...

# Attempt to import all necessary libraries
try:
    import os # General
    import PIL.Image # Image processing
    import base64 # Base64 encoding
    from rich import print as rich_print # Pretty print
    from rich.traceback import install # Pretty traceback
    install() # Install traceback
    # Load imports for gpt usage
    import openai
    import requests
    # Load imports for gemini usage
    import pathlib
    import textwrap
    import google.generativeai as genai
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
            # API key required
            self.load_api_key(api_key)
            # Create gemini instance
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel(self.model_name)
        elif model_category == "gpt":
            # API key required
            self.load_api_key(api_key)
            # Create OpenAI instance
            self.model = openai.OpenAI(api_key=self.api_key)
        else:
            print(f"[ERROR] Model {model_category} and/or {model_name} is not found")
            return False
        # Show completion message
        print('[INFO] AI inference object init successful')
    
    def encode_image(self, image_path):
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    
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
    
    def add_chat(self, prompt, response="", init_system_message="", temperature=1.0):
        # Add system message to model
        if self.model_category == "gemini":
            # If user includes response here, gemini cannot use that and we should warn
            if response != "":
                print("[WARNING] Gemini model does not support response in chat message. Gemini will autogenerate a response for this.")
            # Add user prompt
            print(f"[AI] Adding user prompt '{prompt}'")
            # If chat session not initialized, create it
            if not hasattr(self, 'chat_session'):
                self.chat_session = self.model.start_chat()
            response = self.chat_session.send_message(prompt, generation_config=genai.types.GenerationConfig(temperature=temperature))
            print(f"[AI] Adding response '{response.text}'")
            return True
        elif self.model_category == "gpt":
            # Add user prompt
            temp_system = {"role": "system", "content": init_system_message}
            temp_prompt = {"role": "user", "content": prompt}
            temp_response = {"role": "assistant", "content": response}
            if not hasattr(self, 'chat_session'):
                # Create new
                self.chat_session = []
            if init_system_message != "":
                print(f"[AI] Adding system message '{init_system_message}'")
                self.chat_session.append(temp_system)
            print(f"[AI] Adding user prompt '{prompt}'")
            self.chat_session.append(temp_prompt)
            if response != "":
                print(f"[AI] Adding response '{response}'")
                self.chat_session.append(temp_response)
            return True
        else:
            print(f"[ERROR] Unknown model {self.model_category} or {self.model_name}")
            return False

    def generate_text(self, prompt, max_chars=0, stop_char=None, temperature=1.0):
        print(f"[AI] Asking model to generate text based on prompt '{prompt}'")
        # Generate text based on model
        if self.model_category == "gemini":
            # Check if chat session exists
            if not hasattr(self, 'chat_session'):
                # Start new chat_session with the prompt
                print("[AI] Starting new chat session as one does not exist")
                self.chat_session = self.model.start_chat()
            # Generate text
            response_obj = self.chat_session.send_message(prompt, generation_config=genai.types.GenerationConfig(temperature=temperature))
            response = response_obj.text # Get text in response
        elif self.model_category == "gpt":
            # Check if chat session exists
            if not hasattr(self, 'chat_session'):
                # Start new chat_session with the prompt
                print("[AI] Starting new chat session as one does not exist")
                self.chat_session = [{"role": "system", "content": "You are an assistant, designed to accurately answer questions and follow instructions to the best of your ability, without saying any unnecessary outputs."}]
            # Add prompt to chat session
            temp_prompt = {"role": "user", "content": prompt}
            self.chat_session.append(temp_prompt)
            # Generate text
            response_obj = self.model.chat.completions.create(
                model=self.model_name,
                messages=self.chat_session,
                temperature=temperature
            )
            response = response_obj.choices[0].message.content
            # Add response to chat session
            temp_response = {"role": "assistant", "content": response}
            self.chat_session.append(temp_response)
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

    def ask_image(self, prompt, image_path, max_chars=0, stop_char=None, temperature=1.0):
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
            response_obj = self.model.generate_content([prompt, input_image], generation_config=genai.types.GenerationConfig(temperature=temperature))
            response_obj.resolve() # Wait for response
            response = response_obj.text # Get text in response
        elif self.model_category == "gpt":
            # Retrieve image
            input_image = self.encode_image(os.path.join(image_path))
            # Generate text with image
            response_obj = self.model.chat.completions.create(
                model="gpt-4-vision-preview",
                messages=[{"role": "user", "content": [{"type": "text", "text": prompt}, {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{input_image}",},},],}],
                max_tokens=300,
                temperature=temperature
            )
            response = response_obj.choices[0].message.content
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
