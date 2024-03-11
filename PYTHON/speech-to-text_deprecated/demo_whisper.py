# MIT License
# Copyright (c) 2024

# Attempt to import all necessary libraries
try:
    import os, time # General
    from rich import print as rich_print # Pretty print
    from rich.traceback import install # Pretty traceback
    install() # Install traceback
    import whisper
except ImportError as e:
    print("[INFO] You are missing one or more libraries. Please use PIP to install any missing ones.")
    print("Try running `python3 -m pip install -r requirements.txt` OR `pip install -r requirements.txt`.")
    print(f"Traceback: {e}")
    quit()

# Determine the main project directory, for compatibility (the absolute path to this file)
maindirectory = os.path.join(os.path.dirname(os.path.abspath(__file__)))

# [ OPTIONS ]
SPEECH_MODEL = "medium" # tiny, base, small, medium (don't use large, too big for my gaming PC - not on my server rn)

# Custom low-level functions
def print(text="", log_filename="", end="\n", max_file_mb=10):
    global maindirectory
    script_name = os.path.splitext(os.path.basename(__file__))[0]
    if log_filename == "":
        log_filename = f"{script_name}.log"
    log_file_path = os.path.join(maindirectory, "LOGS", log_filename)
    if not os.path.exists(log_file_path):
        os.makedirs(os.path.dirname(log_file_path), exist_ok=True)
        open(log_file_path, 'a').close()
    if os.path.exists(log_file_path) and os.path.getsize(log_file_path) > max_file_mb * 1024 * 1024:
        try:
            with open(log_file_path, "w") as f:
                f.write("")
        except Exception as e:
            rich_print(f"[red][ERROR][/red]: {e}")
            rich_print(f"[red][ERROR][/red]: Could not clear log file at {log_file_path}.")
    try:
        with open(log_file_path, "a") as f:
            f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {text}\n")
    except Exception as e:
        rich_print(f"[red][ERROR][/red]: {e}")
        rich_print(f"[red][ERROR][/red]: Could not write to log file at {log_file_path}.")
    rich_print(text, end=end)

# [ MAIN ]
if __name__ == "__main__":
    # Welcome message
    print("Welcome! Beginning the speech-to-text_deprecated process...")
    # Load the model
    model = whisper.load_model(SPEECH_MODEL)
    # Print status
    print("Model loaded. Transcribing audio...")
    # Transcribe the audio
    result = model.transcribe(os.path.join(maindirectory, "input.wav"))
    # Success message
    print("Success! Here is the transcribed text:")
    # Print the result
    print(result["text"])