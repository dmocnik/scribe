# [ Example usage file for queue_model class ]

# MIT License
# Copyright (c) 2024

# Imports
import os
import time
from queue_model import queue_model

# Load vars from .env file in the current directory
from dotenv import load_dotenv
load_dotenv()

# Create the queue model (this class shares the same queue for ALL objects!)
qm = queue_model()

# === Add an action (can be called through objects in other files) ===
# [Action] Convert video to audio. Parameters: input file, output file
qm.add_action('convert_mp4_wav', ('input/video.mp4', 'output/audio.wav'))
# [Action] Make transcript. Parameters: input file, output file, output type, task, language, word timestamps, encode
qm.add_action('make_transcript', ('input/audio.wav', 'output/transcript.txt', 'text', 'transcribe', 'en', False, True))

# Check in (loop until queue empty, executing each action) {this would be executed in main as an async task}
while True:
    qm.check_in()
    time.sleep(5) # Sleep for 5 seconds
