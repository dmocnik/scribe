# MIT License
# Copyright (c) 2024

# TODO: 

# Attempt to import all necessary libraries
import os # General
import re # Regular expressions
from rich import print as rich_print # Pretty print
from rich.traceback import install # Pretty traceback
import sys # System
import ffmpeg # Audio processing
import pydub # Audio processing
from pydub import AudioSegment # Audio segment object
import strip_markdown # Strip markdown syntax
from elevenlabs.client import ElevenLabs # Eleven labs client
from elevenlabs import save as eleven_save # Eleven labs save
from elevenlabs import VoiceSettings as eleven_voice_settings # Eleven labs voice settings
from elevenlabs import Voice as eleven_voice # Eleven labs voice
from elevenlabs import play # Eleven labs play
import tempfile
import time # Time, for sleep. delete later was used for testing temp directory
import json # Json file operations, might not need this for the function itself

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))
from ai_interfaces.ai_inference import ai_inference as ai # AI inference class

install() # Install traceback

# Determine the main project directory, for compatibility (the absolute path to this file)
maindirectory = os.path.join(os.path.dirname(os.path.abspath(__file__)))

# Function to take in a text file and spit out notes created using ai model
def generateNotes(fullText: str, model_category: str, model_name: str, chunk_size=3000, variance=100):
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
    ai_completion = ai(model_category, model_name)
    ai_completion2 = ai(model_category, model_name)
    # ai_completion3 = ai(model_category, model_name, api_key)

    # System prompts for the ai models
    systemprompt = "You are NotesGPT, an AI language model skilled at creating detailed, concise, and easy-to-understand lists of topics and sub topics, when provided with a passage or transcript, your task is to: \n\nstart the list with a blank line\n\nCreate advanced bullet-point lists of topics and sub topics highlighting import subjects within the text.\n\ninclude all essential topics to the subject of the text, such as key ideas, concepts, which should be bolded with asterisks.\n\nRemove any extraneous language, focusing on the critical aspects of the passage or transcript.\n\nstrictly base your list of topics and sub topics on the provided information, without adding any external information. \n\nSeparate each main topic with a new line\n\nEnd the list with new blank line"

    systemprompt2 = "You are detective dupe, an AI language model skilled at finding dupes from a list of topics and sub topics, returning the best list free of dupes and keeping only one instance of the topics and subtopics and maintaining the correct information. Your task is to:\n\n- Start the list with a blank line\n\n- Clean this list up of duplicate entries of topics and sub topics maintaining the proper order of things and where they belong\n\n- Keep the topics and sub topics as original to the given text as possible, do not reword or change the content that is kept after cleaning\n\n- Do not remove any non duplicate information, remove duplicated entries, Keep an order of the topics and sub topics do not misplace or re assign topics to one they do not belong to\n\n- Only bold main topics not subtopics, and Separate each main topic with a blank new line\n\n- End the list with new blank line"

    systemprompt3 = "You are scholarGPT, a very smart and knowledgeable AI language model skilled at providing detailed information when given a list of topics and their subtopics, returning very informative and detailed explanations of each topic given and their subtopics. Your task is to: \n\n- Start the list with a blank line to signify start of the list\n\n- Take in a topic and give an explanation of the topic in a detailed and informative manner\n\n- provide informative and detailed explanations of the subtopics, giving any detail necessary to provide a full understanding \n\n- Do not provide unnecessary information to the topic, or unrelated information to what is being discussed. Supplementary information is allowed only if it helps in the explanation of a topic or subtopic\n\n- If a topic is something you cannot provide more information on like logistical information, reuse the original points provided instead\n\n- Separate each main topic with a blank new line\n\n- End the content with new line "
    
    # Variables for the chunking of the text and some parameters for the ai model
    temp = 0.5
    result = []
    current_chunk = ""

    # Splitting the text into sentences
    sentences = re.split(r'(?<=[.!?]) +', fullText)

    # Adding the system prompt to the ai model for summarizing
    ai_completion.add_chat(systemprompt, temperature=temp)

    # Loop to chunk the text into smaller parts for the ai model to summarize
    for sentence in sentences:
    # Check if adding the next sentence exceeds the chunk size limit
        if len(current_chunk) + len(sentence) > chunk_size + variance and current_chunk:
        # Add the current chunk to the chunks list

            compl = ai_completion.generate_text(current_chunk, temperature=temp)

            if compl:
                result.append(compl)
            else:
                print("[ERROR] No results returned from the ai model")
                print(compl)

            current_chunk = sentence  # Start a new chunk with the current sentence
        else:
            # Add the sentence to the current chunk
            current_chunk += (" " + sentence if current_chunk else sentence)

     # Add the last chunk if it's not empty
    if current_chunk:

        compl = ai_completion.generate_text(current_chunk, temperature=temp)
    
        if compl:
            result.append(compl)
        else:
            print("[ERROR] No results returned from the ai model for the last chunk")
            print(compl)


    # combining chunks to one single list of topics for dupe removal
    listprecleaning = ' '
    for r in result:
        listprecleaning += '\n' + r

    # prompt to clean the list of dupes using ai model
    ai_completion2.add_chat(systemprompt2, temperature=temp)

    # cleaning the list using the Ai model completion
    finalList = ai_completion2.generate_text(listprecleaning, temperature=temp)

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
            ai_completion3 = ai(model_category, model_name)
            ai_completion3.add_chat(systemprompt3, temperature=temp)
            finalNotes += '\n' + ai_completion3.generate_text(l, temperature=.25)
        else: 
            finalNotes += '\n' + ai_completion3.generate_text(l, temperature=.25)

        i+=1
    
    return finalNotes



def textToAudio(notes: str, voice_model="David - British Storyteller"):

    def load_api_key(api_key=""):
        # If api_key is blank, attempt to find from environment variable
        if api_key == "":
            try:
                api_key = os.environ.get("AI_AUDIO_API_KEY")
                return api_key
            except Exception as e:
                print(f"[ERROR] Failed to get API key from environment vars. Output: {str(e)}")
                return False

    def ttsAI(text: str, voice_sample: str, file_name: str):
        # Options
        API_KEY = api_key
        # TARGET_VOICE = "Antoni"
        TARGET_VOICE = voice_sample
        # INPUT_TEXT = "meow meow meow. mmmeeeeeooooowwww"
        INPUT_TEXT = text
        # AUDIO_FILE = "output.wav"
        AUDIO_FILE = file_name
        STABILITY = 0.35
        SIMILARITY_BOOST = 0.5

        # Init client
        client = ElevenLabs(api_key=API_KEY)

        # Set key, voices, and params
        selected_voice_object = None
        eleven_available_voices = client.voices.get_all()
        for voice in eleven_available_voices.voices:
            if voice.name == TARGET_VOICE:
                selected_voice_object = voice
                break
        if selected_voice_object is None:
            raise ValueError(f"No voice found with name {TARGET_VOICE}")

        # Customize voice
        selected_voice_object = eleven_voice(
            voice_id = selected_voice_object.voice_id,
            settings = eleven_voice_settings(stability=STABILITY, similarity_boost=SIMILARITY_BOOST, style=0.0, use_speaker_boost=True)
        )

        # Speak the audio using elevenlabs
        synthesized_audio = client.generate(text=f"{INPUT_TEXT}", voice=selected_voice_object, model="eleven_turbo_v2")

        # Save the audio
        # eleven_save(audio=synthesized_audio, filename=AUDIO_FILE)

        return synthesized_audio

    api_key = load_api_key()

    # Audiobook variable to store running audiobook clips concatenated
    audioBook = None

    # List that will store the dictionary of every clips info in
    clipInfo = []

    # Strip down mark down syntax from the text
    # cleanedNotes = strip_markdown.strip_markdown(notes)

    # Split text by double new line and put into an array of text chunks
    #chunks = cleanedNotes.split("\n\n")

    chunks = [strip_markdown.strip_markdown(x) for x in notes.split("\n\n")]

    # Creating a temporary directory to do things in
    with tempfile.TemporaryDirectory() as tmpdirname:
        print('created temporary directory', tmpdirname)

        # Json file name for audiobook clip info json file
        json_file_name = "audioBookInfo.json"

        # path to json file in temp directory
        json_file_path = os.path.join(tmpdirname, json_file_name)

        # very important counter index
        i = 1

        # Iterating through every chunk of text
        for chunk in chunks:
            
            # Generate the audio clip
            audioGenerator = ttsAI(chunk, voice_model, f"{i}")

            # name of the clip in .wav
            filename = f'Clip_{i}.wav'

            # Path to where the current audio clip .wav file
            full_path = os.path.join(tmpdirname, filename)

            # Initializing clip information dict
            currentClipInfo = {}

            # converting the eleven_labs audio generator into a .wav file in temporary directory
            with open(full_path, 'wb') as file:
                for audioChunk in audioGenerator:
                    file.write(audioChunk)
            

            if i == 1: # if first clip generated
                
                # convert .wav clip into audio segment in pydub
                audioClip = AudioSegment.from_file(full_path)

                # initializing first clips time stamps
                timeStampBegin = 0
                timeStampEnd = audioClip.duration_seconds

                # storing info into dictionary about clip
                currentClipInfo = {
                    'Clip #': filename,
                    'Clip Text': chunk,
                    'Start': timeStampBegin,
                    'End': timeStampEnd
                }

                # Appending dict to list
                clipInfo.append(currentClipInfo)

                # Audio book file set to first audio clip to start
                audioBook = audioClip

                # increment index
                i += 1
            elif i > 1: # Clips after the first one generated
                # Setting current clip start time stamp to previous audiobook total length

                timeStampBegin = audioBook.duration_seconds

                # convert .wav clip into audio segment in pydub and concatenate it to the end
                # of the current audiobook file
                audioBook = audioBook + AudioSegment.from_file(full_path)

                # setting the current clips end time stamp to length of audiobook after concatenation
                timeStampEnd = audioBook.duration_seconds

                # storing info into dictionary about clip
                currentClipInfo = {
                    'Clip #': filename,
                    'Clip Text': chunk,
                    'Start': timeStampBegin,
                    'End': timeStampEnd
                }

                # appending clip info to list of dict
                clipInfo.append(currentClipInfo)

                # increment index
                i += 1
            else:
                print("What the flip is going on?!? Wheres my clips!!!!")


        # TEST STUFF TO SEE IF FILES ARE BEING CREATED, CONCATENATED, AND INFO IS BEING STORED
        # ALSO USED TO REVIEW THE FINAL AUDIOBOOK AUDIO FILE

        # After iterating through chunks of text

        # Convert list of dictionaries to json file
        # with open(json_file_path, 'w') as json_file:
            # json.dump(clipInfo, json_file, indent = 4)

        # creating file path for audiobook in .wav format, in the temp directory
        # audio_book_path = os.path.join(tmpdirname, "audiobook.wav")

        # Export audiobook file of concatenated clips as .wav with pydub
        # audioBook.export(audio_book_path, format="wav")

        # Timer to stop for 60 seconds to see what is going on in the temp directory at the end/view files
        # time.sleep(60)
    return clipInfo, audioBook

