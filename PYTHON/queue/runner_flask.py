# Imports
import os
import time
import json
from flask import Flask, request
from queue_model import queue_model
import threading
from waitress import serve

# Create the Flask app
app = Flask(__name__)

# Create the queue model (this class shares the same queue for ALL objects!)
qm = queue_model()

"""
Example task json:
{
    "action": "convert_mp4_wav",
    "parameters": ["input/sample_video.mp4", "output/audio.wav"]
}
"""

# Define the add_action endpoint
@app.route('/add_action', methods=['POST'])
def add_action():
    # Get the task from the request data
    task = request.get_json()
    # Add the task to the queue
    qm.add_action(task['action'], tuple(task['parameters']))
    return 'Task added to the queue', 200

# Define the function that constantly checks in
def check_in():
    while True:
        # Check in (loop until queue empty, executing each action)
        qm.check_in()
        time.sleep(5)  # Sleep for 5 seconds

# Run the check_in function in the background
threading.Thread(target=check_in, daemon=True).start()

if __name__ == '__main__':
    serve(app, host='0.0.0.0', port=8200)