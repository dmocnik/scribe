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
    import mimetypes # File type detection
    import json # JSON file handling
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
spec_video = importlib.util.spec_from_file_location("movie_gen", os.path.join(maindirectory, "..", "aivideo", "movie_gen.py"))

# Use this new method from importlib to import our custom class as "User"
file_processing = importlib.util.module_from_spec(spec)
movie_gen = importlib.util.module_from_spec(spec_video)
spec.loader.exec_module(file_processing)
spec_video.loader.exec_module(movie_gen)

# Class to interface with several AI models
class queue_model:
    # Initialize queue for actions across ALL objects
    q = queue.Queue()

    def __init__(self, system_user="", system_password="", host_key=""):
        print("[INFO] Initializing queue model...")
        # If host_key is not set, attempt to get from os.getenv
        if not host_key or host_key == "":
            host_key = os.getenv("HOST_KEY")
            print(f"[INFO] HOST_KEY not set. Using environment variable: '{host_key}'.")
        # If host_key is still not set, raise an error
        if not host_key:
            raise ValueError("[ERROR] HOST_KEY not set.")
        # Set the host key
        self.host_key = host_key
        try:
            response = requests.post('http://scribe_app:8000/healthcheck/internal', data={'host_key': self.host_key})
            if response.status_code == 200:
                print("[INFO] Successfully authenticated with the Scribe App.")
            else:
                print(f"[ERROR] Failed to authenticate with the Scribe App. Status code: {response.status_code}. Response: {response.text}")
        except Exception as e:
            print(f"[ERROR] Failed to authenticate with the Scribe App. Error: {e}")

    def make_request(self, url, method='get', **kwargs):
        try:
            if method == 'get':
                response = requests.get(url, **kwargs)
            elif method == 'post':
                response = requests.post(url, **kwargs)
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
                # Set options for DB upload
                project_id = action[1][7]
                media_name = os.path.basename(action[1][1])
                media_type = "transcript" # Name identifier for lecture transcript
                # Set project status to processing
                self.set_project_status_db(project_id, "Processing")
                # Create temp folder
                temp_folder = self.create_temp_folder()
                # Retrieve file
                # self.retrieve_file(action[1][0], temp_folder)
                # Retrieve file from database
                self.retrieve_file_db(project_id, 'video', action[1][0], temp_folder)
                # Make transcript
                self.make_transcript(os.path.join(temp_folder, os.path.basename(action[1][0])), os.path.join(temp_folder, os.path.basename(action[1][1])), output=action[1][2], task=action[1][3], language=action[1][4], word_timestamps=action[1][5], encode=action[1][6])
                # Put new file in the output folder, which is listed in the second parameter
                # self.put_file(action[1][1], temp_folder, os.path.dirname(action[1][1]))
                # Put new file in the database
                self.put_file_db(action[1][1], temp_folder, project_id, media_name, media_type)
                # Remove temp folder
                self.remove_temp_folder(temp_folder)
                # Set project status to Ready
                self.set_project_status_db(project_id, "Ready")
            # Summarize transcript
            elif action[0] == 'summarize_transcript':
                # Set options for DB upload
                project_id = action[1][2]
                media_name = os.path.basename(action[1][1])
                media_type = "aisummary" # Name identifier for AI generated summary
                # Set project status to processing
                self.set_project_status_db(project_id, "Processing")
                # Create temp folder
                temp_folder = self.create_temp_folder()
                # Retrieve file
                # self.retrieve_file(action[1][0], temp_folder)
                # Retrieve file from database
                self.retrieve_file_db(project_id, 'transcript', action[1][0], temp_folder)
                # Summarize transcript
                self.summarize_transcript(os.path.join(temp_folder, os.path.basename(action[1][0])), os.path.join(temp_folder, os.path.basename(action[1][1])))
                # Put new file in the output folder, which is listed in the second parameter
                # self.put_file(action[1][1], temp_folder, os.path.dirname(action[1][1]))
                # Put new file in the database
                self.put_file_db(action[1][1], temp_folder, project_id, media_name, media_type)
                # Remove temp folder
                self.remove_temp_folder(temp_folder)
                # Set project status to Ready
                self.set_project_status_db(project_id, "Ready")
            # Get audiobook
            elif action[0] == 'get_audiobook' or action[0] == 'make_video':
                # Set options for DB upload
                project_id = action[1][3]
                media_name = os.path.basename(action[1][1])
                media_name2 = os.path.basename(action[1][1]).replace('.wav', '.json')
                media_name3 = os.path.basename(action[1][1]).replace('.wav', '.mp4')
                media_type = "aiaudio" # Name identifier for audiobook
                media_type2 = "aiaudio_clips" # Name identifier for audiobook clips
                media_type3 = "aivideo" # Name identifier for video
                # Set project status to processing
                self.set_project_status_db(project_id, "Processing")
                # Create temp folder
                temp_folder = self.create_temp_folder()
                # Retrieve file
                # self.retrieve_file(action[1][0], temp_folder)
                # Retrieve file from database
                self.retrieve_file_db(project_id, 'aisummary', action[1][0], temp_folder)
                # Get audiobook
                self.get_audiobook(os.path.join(temp_folder, os.path.basename(action[1][0])), os.path.join(temp_folder, os.path.basename(action[1][1])), action[1][2])
                # Make video (here for jank purposes, since we need all little clips)
                self.make_video(os.path.join(temp_folder, os.path.basename(action[1][0]).replace('.txt', '.wav')), os.path.join(temp_folder, os.path.basename(action[1][1]).replace('.wav', '.mp4')))
                # Put new file in the output folder, which is listed in the second parameter
                # self.put_file(action[1][1], temp_folder, os.path.dirname(action[1][1]))
                # Put new file in the database
                self.put_file_db(action[1][1], temp_folder, project_id, media_name, media_type)
                # Put the clip info in the db as well
                self.put_file_db(action[1][1].replace('.wav', '.json'), temp_folder, project_id, media_name2, media_type2)
                # Put the video in the db as well
                self.put_file_db(action[1][1].replace('.wav', '.mp4'), temp_folder, project_id, media_name3, media_type3)
                # Remove temp folder
                self.remove_temp_folder(temp_folder)
                # Set project status to Ready
                self.set_project_status_db(project_id, "Ready")
            elif action[0] == 'set_project_status':
                # Set project status
                self.set_project_status_db(action[1][0], action[1][1])
            # Make video
            # elif action[0] == 'make_video':
            #     # Set options for DB upload
            #     project_id = action[1][3]
            #     media_name = os.path.basename(action[1][1])
            #     media_type = "aivideo" # Name identifier for video
            #     # Create temp folder
            #     temp_folder = self.create_temp_folder()
            #     # Retrieve file
            #     # self.retrieve_file(action[1][0], temp_folder)
            #     # Retrieve file from database
            #     self.retrieve_file_db(project_id, 'aiaudio_clips', action[1][0], temp_folder)
            #     # Retrieve file from database
            #     self.retrieve_file_db(project_id, 'aisummary', 'summary.txt', temp_folder)
            #     # Get audiobook (unfortunately here since we need all little clips)
            #     self.get_audiobook(os.path.join(temp_folder, 'summary.txt', os.path.join(temp_folder, os.path.basename(action[1][1])), action[1][2])
            #     # Make video
            #     self.make_video(os.path.join(temp_folder, os.path.basename(action[1][0])), os.path.join(temp_folder, os.path.basename(action[1][1])))
            #     # Put new file in the output folder, which is listed in the second parameter
            #     # self.put_file(action[1][1], temp_folder, os.path.dirname(action[1][1]))
            #     # Put new file in the database
            #     self.put_file_db(action[1][1], temp_folder, project_id, media_name, media_type)
            #     # Remove temp folder
            #     self.remove_temp_folder(temp_folder)
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
            file_name = os.path.basename(file_path)
            file_full_path = os.path.join(temp_folder, file_name)
            mime_type, _ = mimetypes.guess_type(file_name)
            
            with open(file_full_path, 'rb') as f:
                files = {'media_content': (file_name, f, mime_type)}
                data = {'media_name': media_name, 'media_type': media_type, 'host_key': self.host_key}
                response = self.make_request(f'http://scribe_app:8000/project/{project_id}/internal', method='post', files=files, data=data)
            
            print(response.text)
        except Exception as e:
            print(f"[ERROR] Failed to move {file_path} from temp folder {temp_folder} to database. Error: {e}")
    
    def retrieve_file_db(self, project_id, media_type, file_path, temp_folder):
        # Make GET request to http://scribe_app:8000/project/{project_id}/{media_type}/internal to retrieve a file
        print(f"[QUEUE] Retrieving file from database for project {project_id} and media type {media_type}...")
        try:
            response = self.make_request(f'http://scribe_app:8000/project/{project_id}/{media_type}/internal', method='post', data={'host_key': self.host_key})
            with open(os.path.join(temp_folder, os.path.basename(file_path)), 'wb') as file:
                file.write(response.content)
        except Exception as e:
            print(f"[ERROR] Failed to retrieve file from database for project {project_id} and media type {media_type}. Error: {e}")
    
    def set_project_status_db(self, project_id, status_string):
        # Make POST request to http://scribe_app:8000/project/{project_id}/status/internal to set the project status
        print(f"[QUEUE] Setting project status for project {project_id} to {status_string}...")
        try:
            response = self.make_request(f'http://scribe_app:8000/project/{project_id}/status/internal', method='post', data={'host_key': self.host_key, 'status_name': status_string})
            print(response.text)
        except Exception as e:
            print(f"[ERROR] Failed to set project status for project {project_id} to {status_string}. Error: {e}")

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
            # Write the clipinfo JSON to a file
            with open(audiobook_path.replace('.wav', '.json'), 'w') as json_file:
                # output_file.write(json.dumps(clipInfo))
                json.dump(clipInfo, json_file, indent = 4)
        except Exception as e:
            print(f"[ERROR] Failed to create audiobook from summary {summary_path} to audiobook {audiobook_path}. Error: {e}")
    
    def make_video(self, clips_path, video_path, width=1920, height=1080):
        # Call the make_aivideo function from the movie_gen module to create a video
        print(f"[QUEUE] Creating video...")
        try:
            movie_gen.make_aivideo(clips_path, width=width, height=height, output=video_path)
        except Exception as e:
            print(f"[ERROR] Failed to create video from clips. Error: {e}")

    def add_action(self, action, param):
        # Add an action with a tuple of parameters to the queue
        print(f"[QUEUE] Adding action {action} with parameters {param} to the queue...")
        self.q.put((action, param))