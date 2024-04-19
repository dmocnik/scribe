# [ Example usage file for queue_model system ]

# MIT License
# Copyright (c) 2024

# Imports
import requests

"""
Make web request to http://scribe_app:8200/add_action endpoint
Note:
    - These relative paths are from the root of our project!
    - In addition, this request URL is specific to our Docker project. Running this code outside of our Docker project will not work.
"""

task = {
    "action": "convert_mp4_wav",
    "parameters": ["input/video.mp4", "output/audio.wav"]
}
response = requests.post('http://scribe_app:8200/add_action', json=task)
print(response.text)