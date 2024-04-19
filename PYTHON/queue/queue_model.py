# MIT License
# Copyright (c) 2024

# [ Check out the `usage.py` file for an example ]

# TODO: THIS REQUIRES THAT THE SYSTEM MAKE A SYSTEM USER ACCOUNT AUTOMATICALLY, WITH INFO FROM .ENV

# Attempt to import all necessary libraries
try:
    import os # General
    import queue # Actual Python queue
    from moviepy.editor import AudioFileClip # Audio processing
    import importlib.util # Used to import files from a path
    import random # Random string generation [1/2]
    import string # Random string generation [2/2]
    import requests # HTTP requests
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

# Set the "spec" variable, to be used to import our files in a parent folder
spec = importlib.util.spec_from_file_location("file_processing", os.path.join(maindirectory, "..", "file_processing", "file_processing.py"))

# Use this new method from importlib to import our custom class as "User"
file_processing = importlib.util.module_from_spec(spec)
spec.loader.exec_module(file_processing)

# Class to interface with several AI models
class queue_model:
    # Initialize queue for actions across ALL objects
    q = queue.Queue()

    def __init__(self, system_user, system_password):
        print("[INFO] Initializing queue model...")
        self.session = requests.Session()
        try:
            response = self.session.post('http://scribe_app:8000/login', json={'email': system_user, 'password': system_password})
            if response.status_code == 200:
                print("[INFO] Successfully authenticated with the Scribe App.")
            else:
                print(f"[ERROR] Failed to authenticate with the Scribe App. Status code: {response.status_code}")
        except Exception as e:
            print(f"[ERROR] Failed to authenticate with the Scribe App. Error: {e}")

    def make_request(self, url, method='get', **kwargs):
        try:
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            return response
        except Exception as e:
            print(f"[ERROR] Request failed. Error: {e}")
    
    def check_in(self):
        # Loop until queue empty
        while not self.q.empty():
            print("[QUEUE] Checking in as new action found...")
            # Get action
            action = self.q.get()
            print(f"[QUEUE] Executing action {action[0]} with parameters {action[1]}...")
            # Convert mp4 to wav
            if action[0] == 'convert_mp4_wav':
                # Create temp folder
                temp_folder = self.create_temp_folder()
                # Retrieve file
                self.retrieve_file(action[1][0], temp_folder)
                # Convert file
                filepath = self.convert_mp4_wav(os.path.join(temp_folder, os.path.basename(action[1][0])), os.path.join(temp_folder, os.path.basename(action[1][1])))
                if not filepath:
                    print(f"[ERROR] Failed to convert {action[1][0]} to {action[1][1]}.")
                    # Mark as done
                    self.q.task_done()
                    continue
                # (File Conversion Successful)
                # Put new file in the output folder, which is listed in the second parameter
                self.put_file(action[1][1], temp_folder, os.path.dirname(action[1][1]))
                # Remove temp folder
                self.remove_temp_folder(temp_folder)
            # Make transcript
            elif action[0] == 'make_transcript':
                # Create temp folder
                temp_folder = self.create_temp_folder()
                # Retrieve file
                self.retrieve_file(action[1][0], temp_folder)
                # Make transcript
                self.make_transcript(os.path.join(temp_folder, os.path.basename(action[1][0])), os.path.join(temp_folder, os.path.basename(action[1][1])), output=action[1][2], task=action[1][3], language=action[1][4], word_timestamps=action[1][5], encode=action[1][6])
                # Put new file in the output folder, which is listed in the second parameter
                self.put_file(action[1][1], temp_folder, os.path.dirname(action[1][1]))
                # Remove temp folder
                self.remove_temp_folder(temp_folder)
            # Summarize transcript
            elif action[0] == 'summarize_transcript':
                # Create temp folder
                temp_folder = self.create_temp_folder()
                # Retrieve file
                self.retrieve_file(action[1][0], temp_folder)
                # Summarize transcript
                self.summarize_transcript(os.path.join(temp_folder, os.path.basename(action[1][0])), os.path.join(temp_folder, os.path.basename(action[1][1])))
                # Put new file in the output folder, which is listed in the second parameter
                self.put_file(action[1][1], temp_folder, os.path.dirname(action[1][1]))
                # Remove temp folder
                self.remove_temp_folder(temp_folder)
            # Get audiobook
            elif action[0] == 'get_audiobook':
                # Create temp folder
                temp_folder = self.create_temp_folder()
                # Retrieve file
                self.retrieve_file(action[1][0], temp_folder)
                # Get audiobook
                self.get_audiobook(os.path.join(temp_folder, os.path.basename(action[1][0])), os.path.join(temp_folder, os.path.basename(action[1][1])), action[1][2])
                # Put new file in the output folder, which is listed in the second parameter
                self.put_file(action[1][1], temp_folder, os.path.dirname(action[1][1]))
                # Remove temp folder
                self.remove_temp_folder(temp_folder)
            # Mark as done
            self.q.task_done()
    
    def convert_mp4_wav(self, video_path, audio_path):
        # Convert a video file to an audio file
        print(f"[QUEUE] Converting video file {video_path} to audio file {audio_path}...")
        # Raise error if video file not found
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"[ERROR] Video file {video_path} not found.")
        # Create necessary folders
        os.makedirs(os.path.dirname(audio_path), exist_ok=True)
        # Make audio file and write to disk
        try:
            video = AudioFileClip(video_path)
            video.write_audiofile(audio_path, codec='pcm_s16le')
            video.close()
            return audio_path
        except Exception as e:
            print(f"[ERROR] Failed to convert {video_path} to {audio_path}. Error: {e}")
            return False
    
    def retrieve_file(self, file_path, temp_folder):
        # Retrieve a file from a path and move to a temp folder
        print(f"[QUEUE] Retrieving file {file_path} to temp folder {temp_folder}...")
        try:
            os.rename(file_path, os.path.join(temp_folder, os.path.basename(file_path)))
        except Exception as e:
            print(f"[ERROR] Failed to move {file_path} to temp folder {temp_folder}. Error: {e}")
    
    def put_file(self, file_path, temp_folder, dest_folder):
        # Put a file back from inside the temp folder to its original path
        print(f"[QUEUE] Putting file {file_path} back from temp folder {temp_folder} to destination folder {dest_folder}...")
        try:
            os.rename(os.path.join(temp_folder, os.path.basename(file_path)), os.path.join(dest_folder, os.path.basename(file_path)))
        except Exception as e:
            print(f"[ERROR] Failed to move {file_path} from temp folder {temp_folder} to destination folder {dest_folder}. Error: {e}")

    def put_file_db(self, file_path, temp_folder, project_id, media_name, media_type):
        # Put a file back from inside the temp folder to the database
        print(f"[QUEUE] Putting file {file_path} back from temp folder {temp_folder} to database...")
        try:
            response = self.make_request(f'http://scribe_app:8000/project/{project_id}', method='post', files={'media_content': open(os.path.join(temp_folder, os.path.basename(file_path)), 'rb')}, data={'media_name': media_name, 'media_type': media_type})
            print(response.text)
        except Exception as e:
            print(f"[ERROR] Failed to move {file_path} from temp folder {temp_folder} to database. Error: {e}")
    
    def retrieve_file_db(self, project_id, media_type, file_path, temp_folder):
        # Make GET request to http://scribe_app:8000/project/{project_id}/{media_type} to retrieve a file
        print(f"[QUEUE] Retrieving file from database for project {project_id} and media type {media_type}...")
        try:
            response = self.make_request(f'http://scribe_app:8000/project/{project_id}/{media_type}')
            with open(os.path.join(temp_folder, os.path.basename(file_path)), 'wb') as file:
                file.write(response.content)
        except Exception as e:
            print(f"[ERROR] Failed to retrieve file from database for project {project_id} and media type {media_type}. Error: {e}")
    
    def create_temp_folder(self):
        # Create a random folder string of 16 characters
        print("[QUEUE] Creating temp folder...")
        while True:
            folder = os.path.join(maindirectory, 'temp', ''.join(random.choices(string.ascii_letters + string.digits, k=16)))
            print(f"[QUEUE] Trying folder {folder}...")
            if not os.path.exists(folder):
                os.makedirs(folder)
                print(f"[QUEUE] Created temp folder {folder}.")
                return folder
    
    def remove_temp_folder(self, folder):
        # Remove a folder and all of its contents
        print(f"[QUEUE] Removing temp folder {folder}...")
        try:
            for root, dirs, files in os.walk(folder, topdown=False):
                for name in files:
                    os.remove(os.path.join(root, name))
                for name in dirs:
                    os.rmdir(os.path.join(root, name))
            os.rmdir(folder)
        except Exception as e:
            print(f"[ERROR] Failed to remove temp folder {folder}. Error: {e}")

    def make_transcript(self, audio_path, transcript_path, output='text', task='transcribe', language='en', word_timestamps=False, encode=True):
        # Make a transcript from an audio file by making web request to scribe_whisper:9000/asr
        # POST to /asr endpoint requires the following:
        # - output: 'text'
        # - task: 'transcribe'
        # - language: 'en'
        # - word_timestamps: false
        # - encode: true
        # - audio_file: raw audio from the audio file
        print(f"[QUEUE] Making transcript from audio file {audio_path} to transcript file {transcript_path}...")
        # Raise error if audio file not found
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"[ERROR] Audio file {audio_path} not found.")
        # Create necessary folders
        os.makedirs(os.path.dirname(transcript_path), exist_ok=True)
        # Make transcript
        try:
            with open(audio_path, 'rb') as file:
                files = {'audio_file': file}
                data = {'output': output, 'task': task, 'language': language, 'word_timestamps': word_timestamps, 'encode': encode}
                response = requests.post('http://scribe_whisper:9000/asr', files=files, data=data)
                with open(transcript_path, 'w') as transcript_file:
                    transcript_file.write(response.text)
        except Exception as e:
            print(f"[ERROR] Failed to make transcript from {audio_path} to {transcript_path}. Error: {e}")

    def summarize_transcript(self, file_path, output_path):
        # Call the generateNotes function from the file_processing module to summarize a transcript
        print(f"[QUEUE] Summarizing transcript {file_path}...")
        # Retrieve API key from environment variable
        AI_API_KEY = os.environ.get('AI_API_KEY')
        # Retrieve the file from the path
        with open(file_path, 'r') as file:
            fullText = file.read()
        # Call the function
        try:
            notes = file_processing.generateNotes(fullText, 'gpt', 'gpt-3.5-turbo')
            # Write the notes to a file
            with open(output_path, 'w') as output_file:
                output_file.write(notes)
        except Exception as e:
            print(f"[ERROR] Failed to summarize transcript {file_path}. Error: {e}")
    
    def get_audiobook(self, summary_path, audiobook_path, voice_model):
        # Call the generateAudiobook function from the file_processing module to create an audiobook
        print(f"[QUEUE] Creating audiobook from summary {summary_path} to audiobook {audiobook_path}...")
        # Retrieve the file from the path
        with open(summary_path, 'r') as file:
            fullText = file.read()
        # Call the function
        try:
            # notes: str, voice_model: str):
            clipInfo, audioBook = file_processing.textToAudio(fullText, voice_model)
            # Write the AudioSegment concatenation to a wav file
            audioBook.export(audiobook_path, format="wav")
        except Exception as e:
            print(f"[ERROR] Failed to create audiobook from summary {summary_path} to audiobook {audiobook_path}. Error: {e}")

    def add_action(self, action, param):
        # Add an action with a tuple of parameters to the queue
        print(f"[QUEUE] Adding action {action} with parameters {param} to the queue...")
        self.q.put((action, param))