# MIT License
# Copyright (c) 2024

# Imports
import os
import time
import json
from queue_model import queue_model

# Create the queue model (this class shares the same queue for ALL objects!)
qm = queue_model()

"""
Example task file:
{
    "action": "convert_mp4_wav",
    "parameters": ["input/sample_video.mp4", "output/audio.wav"]
}
"""

# Constantly check for a file containing a task to run
while True:
    if os.path.exists('task_file.json'):  # Check if the file exists
        with open('task_file.json', 'r') as task_file:
            task = json.load(task_file)  # Load the task from the file
        # Add the task to the queue
        qm.add_action(task['action'], tuple(task['parameters']))
        # Remove the task file after reading it
        os.remove('task_file.json')
    # Check in (loop until queue empty, executing each action)
    qm.check_in()
    time.sleep(5)  # Sleep for 5 seconds