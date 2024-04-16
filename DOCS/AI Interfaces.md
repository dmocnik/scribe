MIT License
Copyright (c) 2024

#### AI Interface

This script defines a class named ai_inference for interfacing with several AI models. The class provides methods for interacting with AI models to generate text based on prompts and optionally images.

## Libraries and Dependencies

The script attempts to import necessary libraries for image processing, encoding, pretty printing, and AI model usage. It also installs pretty traceback for better error messages.

## Class ai_inference

#   Constructor:
        Initializes the AI inference object with the specified model category, model name, and API key (if required).
        Sets up the appropriate AI model instance based on the provided category.

#   Methods:
        encode_image(image_path): Encodes the image located at the specified path into base64 format.
        load_api_key(api_key): Loads the API key for accessing AI models, either from the constructor or environment variables.
        add_chat(prompt, response="", init_system_message="", temperature=1.0): Adds a user prompt and response to the chat session.
        generate_text(prompt, max_chars=0, stop_char=None, temperature=1.0): Generates text based on the provided prompt.
        ask_image(prompt, image_path, max_chars=0, stop_char=None, temperature=1.0): Generates text based on the provided prompt and image.
        shutdown(): Performs shutdown tasks for the AI object.
        __del__(): Destructor method to handle object cleanup.

## Usage

    - Create an instance of the ai_inference class with the desired model category, model name, and API key (if required).
    - Use the methods of the created instance to interact with AI models for generating text based on prompts and optionally images.
    - Properly handle errors and shutdown the AI object when no longer needed.


### Example Usage of ai_inference Class

This script demonstrates the usage of the ai_inference class for interacting with AI models to generate text based on prompts. It showcases how to create an instance of the class, add prompts, and retrieve responses from the AI models.

## Libraries and Dependencies

Libraries imported are as os for environment variables and ai_inference from the provided module for AI model interaction. It also loads environment variables from a .env file using dotenv.

## Usage

#   Creating Instance:
        Instantiate the ai_inference class with the desired model category, model name, and API key (if required). You can choose between Gemini and GPT models and specify the model name accordingly.

#   Adding Prompts:
        Use the add_chat method to add prompts to the model. Optionally, provide a response if using the GPT model.

#   Generating Text:
        Use the generate_text method to ask questions or provide prompts to the model and retrieve the generated text response. You can specify parameters such as maximum characters, stop character, and temperature for response variation.

#   Garbage Collection:
        Properly clean up resources by deleting the instance of the ai_inference object, which calls the shutdown method internally.