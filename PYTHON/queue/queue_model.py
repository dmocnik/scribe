# MIT License
# Copyright (c) 2024

# [ Check out the `usage.py` file for an example, as well as ``../../DOCS/Queue Model.md` for documentation! ]

# Attempt to import all necessary libraries
try:
    import os # General
    import queue # Actual Python queue
    from moviepy.editor import AudioFileClip # Audio processing
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

# Class to interface with several AI models
class queue_model:
    # Initialize queue for actions across ALL objects
    q = queue.Queue()

    def __init__(self):
        print("[INFO] Initializing queue model...")
    
    def check_in(self):
        # Loop until queue empty
        while not self.q.empty():
            print("[QUEUE] Checking in as new action found...")
            # Get action
            action = self.q.get()
            print(f"[QUEUE] Executing action {action[0]} with parameters {action[1]}...")
            # Summarize transcript
            if action[0] == 'summarize_transcript':
                self.summarize_transcript(action[1])
            # Convert mp4 to wav
            elif action[0] == 'convert_mp4_wav':
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
                response = requests.post('http://scribe_whisper:9000/asr', data={'output': output, 'task': task, 'language': language, 'word_timestamps': word_timestamps, 'encode': encode, 'audio_file': file})
                with open(transcript_path, 'w') as transcript_file:
                    transcript_file.write(response.text)
        except Exception as e:
            print(f"[ERROR] Failed to make transcript from {audio_path} to {transcript_path}. Error: {e}")

    def summarize_transcript(self, file_path):
        # TODO: This method
        try:
            with open(file_path, 'r') as file:
                print(file.read())
        except FileNotFoundError:
            print(f"[ERROR] File {file_path} not found.")

    def add_action(self, action, param):
        # Add an action with a tuple of parameters to the queue
        print(f"[QUEUE] Adding action {action} with parameters {param} to the queue...")
        self.q.put((action, param))