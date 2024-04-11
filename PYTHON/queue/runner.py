# MIT License
# Copyright (c) 2024

# Imports
import os
import time
from queue_model import queue_model

# Create the queue model (this class shares the same queue for ALL objects!)
qm = queue_model()

# Check in every 5 seconds and execute all actions in the queue
while True:
    qm.check_in()
    time.sleep(5) # Sleep for 5 seconds
