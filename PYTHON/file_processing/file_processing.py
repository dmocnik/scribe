# MIT License
# Copyright (c) 2024

# TODO: convert to md and save to database, save string to database

# Attempt to import all necessary libraries
import os # General
import base64 # Base64 encoding
import re # Regular expressions
from rich import print as rich_print # Pretty print
from rich.traceback import install # Pretty traceback
import sys # System
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))
from ai_interfaces.ai_inference import ai_inference as ai # AI inference class
install() # Install traceback


# Determine the main project directory, for compatibility (the absolute path to this file)
maindirectory = os.path.join(os.path.dirname(os.path.abspath(__file__)))

# Function to take in a text file and spit out notes created using ai model
def createTopicList(fullText, model_category, model_name, api_key, chunk_size=3000, variance=100):
    """
    Function to take in a string of text and spit out notes created using ai model

    :param fullText: The full text or transcript in string format
    :param model_category: The category of the model (gemini or gpt)
    :param model_name: The name of the model to use (ex. gemini-1.0-pro-latest, gpt-3.5-turbo, ...)
    :param api_key: The api key for the model 
    :param chunk_size: The size of the chunks to split the text into (default 3000 characters)
    :param variance: The variance of the chunks

    :return: The notes created using the ai model in string format
    """

    # Create instances of the ai model for summarizing and cleaning the notes
    ai_completion = ai(model_category, model_name, api_key)
    ai_completion2 = ai(model_category, model_name, api_key)
    # ai_completion3 = ai(model_category, model_name, api_key)

    # System prompts for the ai models
    systemprompt = "You are NotesGPT, an AI language model skilled at creating detailed, concise, and easy-to-understand lists of topics and sub topics, when provided with a passage or transcript, your task is to: \n\nstart the list with a blank line\n\nCreate advanced bullet-point lists of topics and sub topics highlighting import subjects within the text.\n\ninclude all essential topics to the subject of the text, such as key ideas, concepts, which should be bolded with asterisks.\n\nRemove any extraneous language, focusing on the critical aspects of the passage or transcript.\n\nstrictly base your list of topics and sub topics on the provided information, without adding any external information. \n\nSeparate each main topic with a new line\n\nEnd the list with new blank line"

    systemprompt2 = "you are detective dupe, an AI language model skilled at finding dupes from a list of topics and sub topics, returning the best list free of dupes and keeping only one instance of the topics and subtopics and maintaining the correct information. Your task is to:\n\n- Start the list with a blank line\n\n- Clean this list up of duplicate entries of topics and sub topics maintaining the proper order of things and where they belong\n\n- Keep the topics and sub topics as original to the given text as possible, do not reword or change the content that is kept after cleaning\n\n- Do not remove any non duplicate information, remove duplicated entries, Keep an order of the topics and sub topics do not misplace or re assign topics to one they do not belong to\n\n- Only bold main topics not subtopics, and Separate each main topic with a blank new line\n\n- End the list with new blank line"

    systemprompt3 = "You are scholarGPT, a very smart and knowledgeable AI language model skilled at providing detailed information when given a list of topics and their subtopics, returning very informative and detailed explanations of each topic given and their subtopics. Your task is to: \n\n- Start the list with a blank line to signify start of the list\n\n- Take in a topic and give an explanation of the topic in a detailed and informative manner\n\n- provide informative and detailed explanations of the subtopics, giving any detail necessary to provide a full understanding \n\n- Do not provide unnecessary information to the topic, or unrelated information to what is being discussed. Supplementary information is allowed only if it helps in the explanation of a topic or subtopic\n\n- If a topic is something you cannot provide more information on like logistical information, reuse the original points provided instead\n\n- Separate each main topic with a blank new line\n\n- End the content with \n (new line) "
    
    # Variables for the chunking of the text and some parameters for the ai model
    temp = 0.75
    p = 0.95
    result = []
    current_chunk = ""

    # Splitting the text into sentences
    sentences = re.split(r'(?<=[.!?]) +', fullText)

    # Adding the system prompt to the ai model for summarizing
    ai_completion.add_chat(systemprompt)

    # Loop to chunk the text into smaller parts for the ai model to summarize
    for sentence in sentences:
    # Check if adding the next sentence exceeds the chunk size limit
        if len(current_chunk) + len(sentence) > chunk_size + variance and current_chunk:
        # Add the current chunk to the chunks list

            compl = ai_completion.generate_text(current_chunk)

            if compl:
                result.append(compl)
            else:
                print("No match found 1st")
                print(compl)

            current_chunk = sentence  # Start a new chunk with the current sentence
        else:
            # Add the sentence to the current chunk
            current_chunk += (" " + sentence if current_chunk else sentence)

     # Add the last chunk if it's not empty
    if current_chunk:

        compl = ai_completion.generate_text(current_chunk)
    
        if compl:
            result.append(compl)
        else:
            print("No match found 2nd")
            print(compl)


    # combining chunks to one single list of topics for dupe removal
    listprecleaning = ' '
    for r in result:
        listprecleaning += '\n' + r

    # prompt to clean the list of dupes using ai model
    ai_completion2.add_chat(systemprompt2)

    # cleaning the list using the Ai model completion
    finalList = ai_completion2.generate_text(listprecleaning)

    # splitting the list into chunks of topics again seperating by new line
    finalListChunked = finalList.split("\n\n")

    # test print to see how many chunks are created (too many o_o)
    print(len(finalListChunked))

    # Index intialization and final notes string to combine all the explained topics
    finalNotes = " "
    i = 0
    
    # loop to explain each topic and subtopic
    for l in finalListChunked:

        # Current index for testing (del later)
        print(i+1)

        # Modulo condition to check if the index is divisible by 10 to call the ai model object creation again
        if (i % 10 == 0):
            ai_completion3 = ai(model_category, model_name, api_key)
            ai_completion3.add_chat(systemprompt3)
            finalNotes += '\n' + ai_completion3.generate_text(l)
        else: 
            finalNotes += '\n' + ai_completion3.generate_text(l)

        i+=1
    
    return finalNotes
